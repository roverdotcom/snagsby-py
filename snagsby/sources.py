from __future__ import absolute_import

import json
import logging
import re

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs


import boto3
import botocore
from botocore.client import Config

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


class AWSSource(object):
    def __init__(self, url_str):
        self.url = urlparse(url_str)

    @property
    def options(self):
        return {
            k: v[0]
            for k, v in parse_qs(self.url.query).items()
        }

    @property
    def region_name(self):
        return self.options.get('region')

    def get_data(self):
        return sanitize(self.get_raw_data())


class SMSource(AWSSource):
    def get_sm_response(self):
        key = "{}{}".format(self.url.netloc, self.url.path)
        session = boto3.session.Session()
        endpoint_url = "https://secretsmanager.{}.amazonaws.com".format(
            self.region_name)
        client = session.client(
            service_name='secretsmanager',
            region_name=self.region_name,
            endpoint_url=endpoint_url
        )

        try:
            return client.get_secret_value(SecretId=key)
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.debug("The requested secret " + key + " was not found")
            elif e.response['Error']['Code'] == 'InvalidRequestException':
                logger.error("The request was invalid due to:", e)
            elif e.response['Error']['Code'] == 'InvalidParameterException':
                logger.error("The request had invalid params:", e)
            return {}

    def get_raw_data(self):
        response = self.get_sm_response()
        if 'SecretString' in response:
            try:
                return json.loads(response['SecretString'])
            except ValueError as e:
                return {}
            except json.decoder.JSONDecodeError as e:
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
        s3_opts = {
            'config': Config(signature_version='s3v4'),
        }

        if self.region_name:
            s3_opts['region_name'] = self.region_name

        s3 = boto3.resource('s3', **s3_opts)
        bucket = s3.Bucket(self.bucket)
        obj = bucket.Object(self.key).get()

        return obj

    def get_s3_object_body(self):
        return self.get_s3_object()['Body'].read()

    def get_raw_data(self):
        obj = self.get_s3_object_body()
        return json.loads(obj.decode())


def _parse_sources_str(sources_str):
    return [
        source.lstrip().rstrip()
        for source in SPLITTER.split(sources_str) if source
    ]


def parse_source(source):
    if not re.match(r's[m3]:\/\/', source):
        logger.debug('Sources must start with s3:// or sm://')
    elif source.startswith('s3://'):
        return S3Source(source)
    else:
        return SMSource(source)


def parse_sources(sources_str):
    return list(filter(None, [parse_source(source) for source in _parse_sources_str(sources_str)]))
