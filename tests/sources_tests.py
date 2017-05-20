from __future__ import absolute_import

import json

from mock import patch

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

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


class S3SourceTests(TestCase):
    source = urlparse("s3://my-bucket/my/file.json?region=us-west-1")

    def test_bucket(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.bucket, 'my-bucket')

    def test_key(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.key, 'my/file.json')

    def test_options(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.options, {
            'region': 'us-west-1',
        })

    def test_region_name_helper(self):
        source = sources.S3Source(self.source)
        self.assertEqual(source.region_name, 'us-west-1')

    def test_region_name_helper_none(self):
        source = sources.S3Source(urlparse("s3://bucket/file.json"))
        self.assertIsNone(source.region_name)

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


class FileSourceTests(TestCase):
    def test_get_raw_data(self):
        path = self.get_fixture_path('config.json')
        url = 'file://{}'.format(path)
        parser = sources.FileSource(urlparse(url))
        raw = parser.get_raw_data()
        self.assertEqual(raw, {
            'environment': 'test',
            'num': 1,
            'bool': False,
        })

    def test_sanitizes_data(self):
        path = self.get_fixture_path('config.json')
        url = 'file://{}'.format(path)
        parser = sources.FileSource(urlparse(url))
        raw = parser.get_data()
        self.assertEqual(raw, {
            'ENVIRONMENT': 'test',
            'NUM': '1',
            'BOOL': '0',
        })


class ParseSourcesTests(TestCase):
    def test_empty_list(self):
        self.assertEqual(sources.parse_sources(""), [])

    def test_source(self):
        out = sources.parse_sources("s3://my-bucket/file.json")
        self.assertEqual(out[0].bucket, 'my-bucket')


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
