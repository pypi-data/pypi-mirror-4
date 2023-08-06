# coding: utf8

from memcached_memoize.decorators.base import BaseMemcached
from memcached_memoize.utils import MAX_TIMEOUT

OPEN_STATE = 'open'
CLOSED_STATE = 'closed'


class MemcachedCircuitBreaker(BaseMemcached):

    def __init__(self, max_fail, stale_expires=None, instance_ids=[]):
        expires = '0s'
        super(MemcachedCircuitBreaker, self).__init__(expires, stale_expires, instance_ids)
        self.max_fail = max_fail
        self.fail_count = 0
        self.state = CLOSED_STATE

    def wrapper(self, *args, **kwargs):
        memcached_key = self.get_key(*args, **kwargs)
        if self.state == OPEN_STATE:
            cached = self.cache.get(memcached_key)
            if not cached or not cached.is_valid():
                self.state = CLOSED_STATE
        else:
            cached = None

        if self.state == CLOSED_STATE:
            try:
                data = self.function(*args, **kwargs)
            except Exception, e:
                self.fail_count += 1
                if not cached:
                    cached = self.cache.get(memcached_key)
                if cached is None:
                    raise e
            else:
                cached = self.cache_method(data)
                self.fail_count = 0

            if self.fail_count >= self.max_fail:
                self.state = OPEN_STATE
                cached.set_expire_date(self.stale_expires)
                self.fail_count = 0
            else:
                cached.set_expire_date(self.expires)

            self.cache.set(memcached_key, cached, MAX_TIMEOUT)

        return cached['data']


memcached_circuit_breaker = MemcachedCircuitBreaker
