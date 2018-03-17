# -*- coding:utf-8 -*-
import time

import pickle
import hashlib
from functools import wraps


_cache = {}


def _is_obsolete(entry, duration):
    if duration == -1:  # 永不过期
        return False
    return time.time() - entry['time'] > duration


def _compute_key(function, args, kw):
    key = pickle.dumps((function.__name__, args, kw))
    return hashlib.sha1(key).hexdigest()


def cache(duration=-1):
    def _memoize(function):
        @wraps(function)
        def __memoize(*args, **kw):
            key = _compute_key(function, args, kw)

            if key in _cache:
                if _is_obsolete(_cache[key], duration) is False:
                    return _cache[key]['value']
            result = function(*args, **kw)
            _cache[key] = {
                'value': result,
                'time': time.time()
            }
            return result

        return __memoize

    return _memoize