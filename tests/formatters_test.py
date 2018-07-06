from __future__ import absolute_import

import json

from snagsby.cli import SnagsbyCli
from snagsby.exceptions import InvalidFormatterError
from snagsby.formatters import (FORMATTERS_REGSITRY, EnvFormatter,
                                JsonFormatter, get_formatter)

from . import TestCase


class JsonFormatterTests(TestCase):
    def test_output(self):
        f = JsonFormatter({'CHARLES': 'DICKENS'})
        self.assertEqual(
            json.loads(f.get_output()),
            {
                'CHARLES': 'DICKENS',
            }
        )


class EnvFormatterTests(TestCase):
    def test_env_output(self):
        f = EnvFormatter({
            'CHARLES': 'Dickens',
        })
        self.assertEqual(
            f.get_output(),
            'export CHARLES="Dickens"',
        )

    def test_quotes_escaped_in_output(self):
        f = EnvFormatter({
            'CHARLES': '"Boz" Dickens',
        })
        self.assertEqual(
            f.get_output(),
            r'export CHARLES="\"Boz\" Dickens"'
        )

    def test_multiple_values(self):
        f = EnvFormatter({
            'CHARLES': 'Dickens',
            'HELLO': 'WORLD',
        })
        expected = 'export CHARLES="Dickens"\nexport HELLO="WORLD"'
        self.assertEqual(f.get_output(), expected)


class EnvFactoryTests(TestCase):
    def test_missing_formatter_raises_invalid_formatter_error(self):
        with self.assertRaises(InvalidFormatterError):
            get_formatter('no-existy', {})

    def test_formatter_factory(self):
        for formatter, cls in FORMATTERS_REGSITRY.items():
            formatter = get_formatter(formatter, {})
            self.assertIsInstance(formatter, cls)
