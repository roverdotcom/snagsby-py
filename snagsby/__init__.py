from __future__ import absolute_import

import os

from .sources import parse_sources, sanitize
from .version import __version__  # noqa


def load(source=None, dest=None):
    # Default to loading into the environment
    if dest is None:
        dest = os.environ

    if source is None:
        source = os.environ.get('SNAGSBY_SOURCE', '')

    parsed_sources = parse_sources(source)

    for parsed_source in parsed_sources:
        for k, v in parsed_source.get_data().items():
            dest[k.upper()] = v


def load_object(obj, dest=None):
    if dest is None:
        dest = os.environ
    for k, v in sanitize(obj).items():
        dest[k.upper()] = str(v)
