from __future__ import absolute_import

import re
import json

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs


import boto3
from botocore.client import Config


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


class S3Source(object):
    def __init__(self, url_str):
        self.url = urlparse(url_str)

    @property
    def bucket(self):
        return self.url.netloc

    @property
    def key(self):
        return self.url.path.lstrip("/")

    @property
    def options(self):
        return {
            k: v[0]
            for k, v in parse_qs(self.url.query).items()
        }

    @property
    def region_name(self):
        return self.options.get('region')

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

    def get_data(self):
        return sanitize(self.get_raw_data())


def _parse_sources_str(sources_str):
    return [
        source.lstrip().rstrip()
        for source in SPLITTER.split(sources_str) if source
    ]


def parse_sources(sources_str):
    return [
        S3Source(source)
        for source in _parse_sources_str(sources_str)
    ]
