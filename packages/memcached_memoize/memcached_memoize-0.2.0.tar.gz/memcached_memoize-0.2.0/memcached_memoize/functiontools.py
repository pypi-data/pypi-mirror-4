import inspect

from collections import OrderedDict


class FunctionTools(object):

    def __init__(self, function):
        self.function = function
        self.argspec = inspect.getargspec(self.function)

    @property
    def argspec_args(self):
        return self.argspec.args or []

    def get_declared_args(self, *args, **kwargs):
        kwargs.update(OrderedDict(zip(self.argspec_args, args)))
        return filter(lambda item: item[0] in self.argspec_args, kwargs.items())

    def get_arbitrary_args(self, *args):
        arbitrary_args = []
        if self.argspec.varargs:
            declared_args_length = len(self.argspec_args or [])
            arbitrary_args = args[declared_args_length:]
        return arbitrary_args

    def get_arbitrary_kwargs(self, **kwargs):
        arbitrary_kwargs = []
        if self.argspec.keywords:
            arbitrary_kwargs = self.filter_arbitrary_kwargs_items(kwargs.items())
        return arbitrary_kwargs

    def filter_arbitrary_kwargs_items(self, kwargs_items):
        for key, value in kwargs_items:
            if key not in self.argspec_args:
                yield key, value
