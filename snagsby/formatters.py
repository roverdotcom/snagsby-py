from __future__ import absolute_import

import json

from .exceptions import InvalidFormatterError
from .registry import Registry


class SnagsbyFormatter(object):
    def __init__(self, data):
        self.data = data

    def get_output(self):
        raise NotImplementedError("Please implement the get_output method")


class JsonFormatter(SnagsbyFormatter):
    def get_output(self):
        return json.dumps(self.data, sort_keys=True)


class EnvFormatter(SnagsbyFormatter):
    def _sanitize_value(self, value):
        return value.replace('"', '\\"')

    def _format_line(self, key, value):
        value = self._sanitize_value(value)
        template = 'export {key}="{value}"'
        return template.format(key=key, value=value)

    def get_output(self):
        lines = [
            self._format_line(key, value)
            for key, value in self.data.items()
        ]

        return "\n".join(sorted(lines))


registry = Registry()
registry.register_handler('json', JsonFormatter)
registry.register_handler('env', EnvFormatter)

DEFAULT_FORMATTER = 'env'


def get_formatter(type, data):
    """
    Formatter factory
    """
    try:
        return registry.get_handler(type)(data)
    except KeyError:
        raise InvalidFormatterError("Invalid formatter: {}".format(type))
