from __future__ import absolute_import

import json

from .exceptions import InvalidFormatterError


class SnagsbyFormatter(object):
    def __init__(self, data):
        self.data = data

    def get_output(self):
        raise NotImplementedError("Please implement the output method")


class JsonFormatter(SnagsbyFormatter):
    def get_output(self):
        return json.dumps(self.data)


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


FORMATTERS_REGSITRY = {
    'json': JsonFormatter,
    'env': EnvFormatter,
}
DEFAULT_FORMATTER = 'env'


def get_formatter(type, data):
    """
    Formatter factory
    """
    try:
        return FORMATTERS_REGSITRY[type](data)
    except KeyError:
        raise InvalidFormatterError("Invalid formatter: {}".format(type))
