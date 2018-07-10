from __future__ import absolute_import

import os

import unittest

from httpretty import HTTPretty


class TestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.disallow_network_access()

    @classmethod
    def disallow_network_access(cls):
        HTTPretty.enable()

    def setUp(self):
        if 'SNAGSBY_SOURCE' in os.environ:
            os.environ.pop('SNAGSBY_SOURCE')
