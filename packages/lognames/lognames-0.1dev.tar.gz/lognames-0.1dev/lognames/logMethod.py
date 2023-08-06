#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging

from functools import wraps

def logMethod(method_or_name):
    def decorator(method):
        @wraps(method)
        def wrapper(object, *args, **kwargs):
            logging.log(level, "{0} {1} {2}".format(method.__name__, args, kwargs))

            return method(object, *args, **kwargs)

        return wrapper

    if callable(method_or_name):
        level = logging.INFO
        return decorator(method_or_name)

    level = method_or_name
    return decorator
