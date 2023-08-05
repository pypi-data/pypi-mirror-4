from .collections import Collection
from .documents import Document
from .compat import py3k

__all__ = [
        'Document',
        'Collection'
        ]

if py3k:
    from .compat import normalize_string_type
    import json

    # This handles a bug of the json.loads method in python 3.2, see:
    # http://bugs.python.org/issue10976 for more information. Should be fixed
    # in python3
    json.loads = normalize_string_type(json.loads)
