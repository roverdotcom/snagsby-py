from __future__ import absolute_import

from snagsby.cli import SnagsbyCli

from . import TestCase


class SnagsbyCliTests(TestCase):
    def test_build_source_from_arg_combine(self):
        cli = SnagsbyCli()
        self.assertEqual(cli._build_source_from_arg(
            ['one, two', 'three']), 'one, two,three')

    def test_build_source_from_arg_none_for_falsy(self):
        cli = SnagsbyCli()
        self.assertIsNone(cli._build_source_from_arg(False))
        self.assertIsNone(cli._build_source_from_arg(''))
