from __future__ import absolute_import

from snagsby.registry import Registry
from snagsby.sources import SnagsbySource

from . import TestCase


class RegistryTests(TestCase):
    class MockHandler(SnagsbySource):
        def get_raw_data(self):
            return {'hello': 'world'}

    def test_get_handler(self):
        registry = Registry()
        registry.register_handler('charles', self.MockHandler)
        self.assertEqual(registry.get_handler('charles'), self.MockHandler)

    def test_raises_key_error_on_missing_handler(self):
        registry = Registry()
        with self.assertRaises(KeyError):
            registry.get_handler('no_here')

    def test_get_names(self):
        registry = Registry()
        registry.register_handler('charles', self.MockHandler)
        registry.register_handler('dickens', self.MockHandler)
        self.assertEqual(list(registry.get_names()), ['charles', 'dickens'])
