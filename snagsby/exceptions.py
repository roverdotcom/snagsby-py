class InvalidFormatterError(Exception):
    pass


# SEE https://github.com/django/django/blob/master/django/core/exceptions.py#L94
class SnagsbySourceError(Exception):
    def __init__(self, *args, **kwargs):
        self.url = kwargs.pop('url', None)
        self.raw_exception = kwargs.pop('raw_exception', None)
        super(SnagsbySourceError, self).__init__(*args)
