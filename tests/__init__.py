from __future__ import absolute_import

import os

import unittest

from httpretty import HTTPretty


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class TestCase(unittest.TestCase):
    fixture_path = os.path.abspath(
        os.path.join(BASE_DIR, './fixture_data/'))

    @classmethod
    def setUpClass(cls):
        cls.disallow_network_access()

    @classmethod
    def disallow_network_access(cls):
        HTTPretty.enable()

    def setUp(self):
        if 'SNAGSBY_SOURCE' in os.environ:
            os.environ.pop('SNAGSBY_SOURCE')

    def get_fixture_path(self, fixture):
        return os.path.join(
            self.fixture_path,
            fixture,
        )
