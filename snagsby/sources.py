from __future__ import absolute_import

import json
import logging
import re

import boto3
import botocore
from botocore.client import Config

from .registry import Registry

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

# Python 3 raises json.decoder.JSONDecodeError while python 2 raises ValueError
# and doesn't provide json.decoder.JSONDecodeError.
# This can be removed if and when python 2 is no longer supported.
try:
    from json.decoder import JSONDecodeError
except ImportError:
    JSONDecodeError = ValueError


logger = logging.getLogger(__name__)

SPLITTER = re.compile(r'[\s|,]+')
KEY_REGEX = re.compile(r'^\w+$')


def sanitize(obj):
    out = {}

    if not type(obj) is dict:
        return out

    for k, v in obj.items():
        k = k.upper()

        item_is_invalid = (
            not KEY_REGEX.match(k)
            or type(v) is dict
            or k == 'SNAGSBY_SOURCE'
        )
        if item_is_invalid:
            continue

        if type(v) is bool:
            out[k] = "1" if v else "0"
        else:
            out[k] = str(v)

    return out


class SnagsbySource(object):
    def __init__(self, url):
        self.url = urlparse(url)

    @property
    def options(self):
        return {
            k: v[0]
            for k, v in parse_qs(self.url.query).items()
        }

    def get_raw_data(self):
        raise NotImplementedError("Please implement get_raw_data")

    def get_data(self):
        return sanitize(self.get_raw_data())


class AWSSource(SnagsbySource):
    @property
    def region_name(self):
        return self.options.get('region')

    def get_boto3_session(self, opts=None):
        if not opts:
            opts = {}
        if self.region_name:
            opts['region_name'] = self.region_name

        return boto3.Session(**opts)


class SMSource(AWSSource):
    def get_sm_response(self):
        key = "{}{}".format(self.url.netloc, self.url.path)
        client = self.get_boto3_session().client('secretsmanager')

        try:
            return client.get_secret_value(SecretId=key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.debug("The requested secret " + key + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logger.error("The request was invalid due to: %s", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logger.error("The request had invalid params: %s", e)
            return {}

    def get_raw_data(self):
        response = self.get_sm_response()
        if 'SecretString' in response:
            try:
                return json.loads(response['SecretString'])
            except JSONDecodeError:
                return {}
        else:
            logger.debug('Response for key {}{} does not contain SecretString'.format(
                self.url.netloc,
                self.url.path,
            ))
        return {}


class S3Source(AWSSource):
    @property
    def bucket(self):
        return self.url.netloc

    @property
    def key(self):
        return self.url.path.lstrip("/")

    def get_s3_object(self):
        s3 = self.get_boto3_session().resource('s3')
        bucket = s3.Bucket(self.bucket)
        return bucket.Object(self.key).get()

    def get_s3_object_body(self):
        return self.get_s3_object()['Body'].read()

    def get_raw_data(self):
        obj = self.get_s3_object_body()
        return json.loads(obj.decode())


class SSMSource(AWSSource):
    def normalize_key(self, path, key):
        out = key[len(path):].lstrip('/').upper()
        out = out.replace("/", "_")
        return out

    def get_raw_data(self):
        client = self.get_boto3_session().client('ssm')
        pager = client.get_paginator('get_parameters_by_path')
        path = "/{}{}".format(self.url.netloc, self.url.path)
        paged_resp = pager.paginate(
            Path=path,
            Recursive=True,
            WithDecryption=True,
        )
        out = {}
        for resp in paged_resp:
            for item in resp['Parameters']:
                out[self.normalize_key(path, item['Name'])] = item['Value']
        return out


registry = Registry()
registry.register_handler('s3', S3Source)
registry.register_handler('sm', SMSource)
registry.register_handler('ssm', SSMSource)


def get_source(source):
    source_type = urlparse(source).scheme
    try:
        return registry.get_handler(source_type)(source)
    except KeyError:
        return None


def _parse_sources_str(sources_str):
    return [
        source.lstrip().rstrip()
        for source in SPLITTER.split(sources_str) if source
    ]


def parse_sources(sources_str):
    return [
        get_source(source)
        for source in _parse_sources_str(sources_str)
    ]
