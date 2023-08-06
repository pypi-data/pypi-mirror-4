#-*- coding: utf-8 -*-

from functools import wraps

def register_url(url=None, use_inline_data=False):
    def method(function):
        function.extra_admin_url = url or (function.__name__ + r'/$')
        function.use_inline_data = use_inline_data

        @wraps(function)
        def inner(*args, **kwargs):
            return function(*args, **kwargs)
        return inner
    return method
