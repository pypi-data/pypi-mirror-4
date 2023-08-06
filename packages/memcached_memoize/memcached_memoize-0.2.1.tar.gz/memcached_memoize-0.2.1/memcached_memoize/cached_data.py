import datetime

from memcached_memoize.utils import time_string_to_seconds


class CachedData(dict):
    def __init__(self, data):
        self['data'] = data

    def __eq__(self, other):
        return self['data'].__eq__(other['data'])

    def set_expire_date(self, expires):
        try:
            expires = int(expires)
        except ValueError:
            expires = time_string_to_seconds(expires)
        now = datetime.datetime.now()
        timedelta = datetime.timedelta(seconds=expires)
        self['expire_date'] = now + timedelta

    def is_valid(self):
        expire_date = self.get('expire_date')
        return expire_date and self['expire_date'] > datetime.datetime.now()
