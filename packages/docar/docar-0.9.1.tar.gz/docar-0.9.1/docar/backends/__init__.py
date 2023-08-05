class BackendManager(object):
    """Manage registered backends.

    The ``BackendMeta`` class registers each backend with this manager class.
    """
    backends = []

    def __new__(self, backend_type='dummy'):
        """Instantiate the requested backend and return it."""
        for backend in self.backends:
            if backend_type == backend.backend_type:
                return backend()

        return None


class BackendMeta(type):
    """Metaclass to register backends with the BackendManager.

    In order to implement a new backend, you have to use this as the metaclass
    for the backend itself, eg:

        >>> class AwesomeBackend(Backend):
        ...     backend_type = 'awesome'
    """
    def __new__(meta, classname, bases, class_dict):
        # print BackendManager
        klass = type.__new__(meta, classname, bases, class_dict)
        if classname != 'Backend':
            BackendManager.backends.append(klass)
        return klass


# See the comment in documents.py about constructing metaclasses like that.
Backend = BackendMeta('Backend', (object, ), {})


class DummyBackend(Backend):
    """This backend serves as a placeholder, in cases where no real backend
    mapping is needed."""
    backend_type = 'dummy'

    def __getattr__(self, name):
        api = ['fetch', 'save']
        if name in api:
            return
        else:
            raise AttributeError

    def __nonzero__(self):
        # Always return False, to show a similar behaviour as None.
        return False

    def __bool__(self):
        # __nonzero__ is __bool__ in python3
        return False
