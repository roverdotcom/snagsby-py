from collections import OrderedDict


class Registry(object):
    def __init__(self):
        self._registery = OrderedDict()

    def register_handler(self, name, handler):
        self._registery[name] = handler

    def get_handler(self, name):
        return self._registery[name]

    def get_names(self):
        return self._registery.keys()

    def items(self):
        return self._registery.items()
