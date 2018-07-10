from __future__ import absolute_import

import argparse
import sys

from . import get as snagsby_get
from .formatters import DEFAULT_FORMATTER, get_formatter
from .formatters import registry as formatters_registry
from .version import __version__


class SnagsbyCli(object):
    def _build_source_from_arg(self, source_arg):
        """
        Puts a single source string together from a list of source strings
        that would come from argparser.
        """
        if not source_arg:
            return None
        return ",".join(source_arg)

    def get_data(self, source):
        return snagsby_get(source=self._build_source_from_arg(source))

    def main(self, args):
        data = self.get_data(args['source'])
        sys.stdout.write(get_formatter(args['output'], data).get_output())
        sys.stdout.flush()
        return 0


def main():
    parser = argparse.ArgumentParser(description='Snagsby')
    parser.add_argument('source', nargs='*')
    parser.add_argument('-v', '--version', action='version',
                        version='snagsby-py: {}'.format(__version__))
    parser.add_argument('-o', '--output', default=DEFAULT_FORMATTER,
                        choices=formatters_registry.get_names())
    cli = SnagsbyCli()
    sys.exit(cli.main(vars(parser.parse_args())))


if __name__ == '__main__':
    main()
