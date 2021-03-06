from __future__ import absolute_import

import json
import logging
import os

from mock import patch
from testfixtures import LogCapture, log_capture

from snagsby import sources

from . import TestCase


class SplitSourcesTests(TestCase):
    def test_newline_split(self):
        s = """

                s3://test-bucket/one.json

            s3://test-bucket/two.json


        """
        out = sources._parse_sources_str(s)
        self.assertEqual(out, [
            's3://test-bucket/one.json',
            's3://test-bucket/two.json',
        ])

    def test_comma_and_pipe_split(self):
        s = "s3://s/one.json |  s3://s/two.json , s3://s/three.json"
        out = sources._parse_sources_str(s)
        self.assertEqual(out, [
            "s3://s/one.json",
            "s3://s/two.json",
            "s3://s/three.json",
        ])

    def test_comma_split(self):
        s = "s3://s/one.json,s3://s/two.json,s3://s/three.json"
        out = sources._parse_sources_str(s)
        self.assertEqual(out, [
            "s3://s/one.json",
            "s3://s/two.json",
            "s3://s/three.json",
        ])

    def test_empty_string(self):
        s = ""
        out = sources._parse_sources_str(s)
        self.assertEqual(out, [])


class AWSSourceTests(TestCase):
    source = "s3://my-bucket/my/file.json?region=us-west-1"

    def test_options(self):
        source = sources.AWSSource(self.source)
        self.assertEqual(source.options, {
            'region': 'us-west-1',
        })

    def test_region_name_helper(self):
        source = sources.AWSSource(self.source)
        self.assertEqual(source.region_name, 'us-west-1')

    def test_region_name_helper_default(self):
        source = sources.AWSSource("s3://bucket/file.json")
        self.assertEqual(source.region_name, None)

    @patch.dict(os.environ, {'AWS_DEFAULT_REGION': 'us-west-1'})
    def test_session_gets_region(self):
        source = sources.AWSSource("s3://bucket/file.json?region=us-east-2")
        session = source.get_boto3_session()
        self.assertEqual(session.region_name, 'us-east-2')


class S3SourceTests(TestCase):
    source = "s3://my-bucket/my/file.json?region=us-west-1"

    def test_bucket(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.bucket, 'my-bucket')

    def test_key(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.key, 'my/file.json')

    @patch.object(sources.S3Source, 'get_raw_data')
    def test_hi(self, mock):
        mock.return_value = {
            'no': False,
        }
        source = sources.S3Source("s3://bucket/file.json")
        out = source.get_data()
        self.assertEqual(out['NO'], '0')

    @patch.object(sources.S3Source, 'get_s3_object_body')
    def test_json_decoding_in_get_raw_data(self, mock):
        mock.return_value = b'{"TEST":"VALUE"}'
        source = sources.S3Source("s3://bucket/file.json")
        out = source.get_raw_data()
        self.assertEqual(out, {
            "TEST": "VALUE",
        })


class SMSourceTests(TestCase):
    source = "sm://some/key/path?region=us-west-1"

    @patch.object(sources.SMSource, 'get_sm_response')
    def test_get_raw_data(self, mock):
        mock.return_value = {"SecretString": '{"TEST":"VALUE"}'}
        source = sources.SMSource("sm://some/key/path")
        out = source.get_raw_data()
        self.assertEqual(out, {"TEST": "VALUE", })

    @patch.object(sources.SMSource, 'get_sm_response')
    def test_get_raw_data_returns_empty_map_for_invalid_json(self, mock):
        mock.return_value = {"SecretString": '{"TEST_BROKEN_JSON:"VALUE"}'}
        source = sources.SMSource("sm://some/key/path")
        self.assertEqual(source.get_raw_data(), {})

    @patch.object(sources.SMSource, 'get_sm_response')
    @log_capture()
    def test_get_raw_data_logs_sources_do_not_have_SecretString(self, l, mock):
        mock.return_value = {"SecretBinary": '{"TEST":"VALUE"}'}
        source = sources.SMSource("sm://some/key/path")
        source.get_raw_data()
        l.check(
            ('snagsby.sources', 'DEBUG',
             'Response for key some/key/path does not contain SecretString'),
        )


class ParseSourcesTests(TestCase):
    def test_empty_list(self):
        self.assertEqual(sources.parse_sources(""), [])

    def test_source(self):
        out = sources.parse_sources("s3://my-bucket/file.json")
        self.assertEqual(out[0].bucket, 'my-bucket')

    def test_source_identifies_s3(self):
        out = sources.parse_sources("s3://my-bucket/file.json")
        self.assertEqual(type(out[0]).__name__, 'S3Source')

    def test_source_identifies_sm(self):
        out = sources.parse_sources("sm://my/key/path")
        self.assertEqual(type(out[0]).__name__, 'SMSource')


class SanitizeTests(TestCase):
    def _sanitize(self, obj):
        return sources.sanitize(obj)

    def test_defaults_to_dict(self):
        self.assertEqual(self._sanitize("HI"), {})

    def test_changes_boolean(self):
        out = self._sanitize({
            'yes': True,
            'no': False,
        })
        self.assertEqual(out['YES'], "1")
        self.assertEqual(out['NO'], "0")

    def test_numeric_to_str(self):
        out = self._sanitize(json.loads(r'{"num":7.777}'))
        self.assertEqual(out['NUM'], '7.777')

    def test_reject_bad_keys(self):
        out = self._sanitize(json.loads(r'{"bad key": "test"}'))
        self.assertIsNone(out.get('BAD KEY'))

    def test_no_nested_objects(self):
        raw = '''
        {
            "HELLO": "test",
            "NESTED": {
                "object": "test"
            }
        }
        '''
        out = self._sanitize(json.loads(raw))
        self.assertIsNone(out.get('NESTED'))

    def test_snagsby_source_is_omitted(self):
        raw = '''
        {
            "SNAGSBY_SOURCE": "s3://123",
            "HELLO": "World"
        }
        '''
        out = self._sanitize(json.loads(raw))
        self.assertNotIn('SNAGSBY_SOURCE', out)
        self.assertEqual(out['HELLO'], 'World')
