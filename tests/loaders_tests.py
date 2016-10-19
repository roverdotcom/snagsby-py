from __future__ import absolute_import

from mock import patch

import snagsby
import snagsby.sources

from . import TestCase


class SnagsbyLoadTests(TestCase):
    @patch('snagsby.sanitize')
    def test_load_noop(self, mock):
        snagsby.load()
        self.assertFalse(mock.call_count)

    @patch.object(snagsby.sources.S3Source, 'get_raw_data')
    def test_load_integration(self, mock):
        mock.return_value = {
            'test': 'config',
        }
        out = {}
        snagsby.load(
            source='s3://dummy/config.json',
            dest=out,
        )
        self.assertEqual(out['TEST'], 'config')


class SnagsbyLoadObjectTests(TestCase):
    def test_load_object_sanitizes(self):
        obj = {
            'test': 'config',
            'num': 7.77,
        }
        out = {}
        snagsby.load_object(obj, dest=out)
        self.assertEqual(out['TEST'], 'config')
        self.assertEqual(out['NUM'], '7.77')
