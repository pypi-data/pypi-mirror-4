from abc import ABCMeta, abstractmethod
import inspect

from functools import wraps

from django.core.cache import cache
from django.template.defaultfilters import slugify

from memcached_memoize.cached_data import CachedData
from memcached_memoize.functiontools import FunctionTools
from memcached_memoize.utils import MAX_TIMEOUT, time_string_to_seconds


def dict_item_cmp_by_key(item1, item2):
    return cmp(item1[0], item2[0])


class BaseMemcached(object):
    __metaclass__ = ABCMeta

    def __init__(self, expires, stale_expires=None, instance_ids=[]):
        self.expires = time_string_to_seconds(expires)
        self.stale_expires = self.expires if not stale_expires else time_string_to_seconds(stale_expires)
        self.cache = cache
        self.cache_method = CachedData
        self.instance_ids = instance_ids

    def __call__(self, func):
        self.function = func

        @wraps(self.function)
        def wrap(*args, **kwargs):
            return self.wrapper(*args, **kwargs)

        wrap._pointer = self.function
        return wrap

    @abstractmethod
    def wrapper(self, *args, **kwargs):
        raise NotImplementedError

    def get_key(self, *args, **kwargs):
        ftools = FunctionTools(self.function)
        values = []

        instance_id = self.get_instance_identifier(args)
        if instance_id:
            values.insert(0, instance_id)

        declared_kwargs = ftools.get_declared_args(*args, **kwargs)
        for key, value in sorted(declared_kwargs, cmp=dict_item_cmp_by_key):
            if not key in ('self', 'cls'):
                values.append(slugify(value))

        for value in ftools.get_arbitrary_args(*args):
            values.append(slugify(value))

        arbitrary_kwargs = ftools.get_arbitrary_kwargs(**kwargs)
        arbitrary_kwargs = sorted(arbitrary_kwargs, cmp=dict_item_cmp_by_key)
        for key, value in arbitrary_kwargs:
            values.append('%s=%s' % (slugify(key), slugify(value)))

        memcached_prefix = self.get_memcached_prefix(args)
        return '{0}:{1}'.format(memcached_prefix, ':'.join(values))

    def get_instance_identifier(self, args):
        if not self.is_instancemethod(self.function, args):
            return ''

        instance = self.get_first_arg(args)
        values = []
        for identifier in self.instance_ids:
            value = getattr(instance, identifier)
            if callable(value):
                value = value()
            value = slugify(value)
            values.append(value)

        return ':'.join(values)

    def is_instancemethod(self, func, args):
        cls = self.get_class_from_first_arg(args)
        if cls:
            method = getattr(cls, '__dict__', {}).get(func.func_name)
            if method:
                return getattr(method, '_pointer') == func
        return False

    def get_class_from_first_arg(self, args):
        first_arg = self.get_first_arg(args)
        if not inspect.isclass(first_arg):
            first_arg = first_arg.__class__
        return first_arg

    def get_first_arg(self, args):
        if len(args) > 0:
            return args[0]
        return None

    def get_memcached_prefix(self, args):
        if self.is_instancemethod(self.function, args):
            cls = self.get_class_from_first_arg(args)
            return '.'.join([
                self.function.__module__,
                cls.__name__,
                slugify(self.function.__name__)
            ])
        return '.'.join([
            self.function.__module__,
            slugify(self.function.__name__)
        ])


class Memcached(BaseMemcached):

    def wrapper(self, *args, **kwargs):
        memcached_key = self.get_key(*args, **kwargs)
        cached = self.cache.get(memcached_key)

        if not cached or not cached.is_valid():
            try:
                data = self.function(*args, **kwargs)
            except Exception, e:
                if cached is None:
                    raise e
                else:
                    cached.set_expire_date(self.stale_expires)
            else:
                cached = self.cache_method(data)
                cached.set_expire_date(self.expires)

            self.cache.set(memcached_key, cached, MAX_TIMEOUT)

        return cached['data']

memcached = Memcached
