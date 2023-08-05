""" compat.py - Python2/3 compatibility layer."""
import sys
from functools import wraps


# set this flag to switch to python 3 compatibility
py3k = sys.version_info >= (3,)


def normalize_string_type(func):
    """Normalize the input string for the json decoder."""
    def inner(value, *args, **kwargs):
        if py3k:
            if isinstance(value, bytes):
                value = value.decode('utf-8')
        return func(value, *args, **kwargs)
    return wraps(func)(inner)
