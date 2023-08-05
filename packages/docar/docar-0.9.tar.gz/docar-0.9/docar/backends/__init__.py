class BackendManager(object):
    """Manage registered backends.

    The ``BackendMeta`` class registers each backend with this manager class.
    """
    backends = []

    def __new__(self, backend_type='dummy'):
        """Instantiate the requested backend and return it."""
        for Backend in self.backends:
            if backend_type == Backend.backend_type:
                return Backend()

        return None


class BackendMeta(type):
    """Metaclass to register backends with the BackendManager.

    In order to implement a new backend, you have to use this as the metaclass
    for the backend itself, eg:

        >>> class AwesomeBackend(object):
        ...     __metaclass__ = BackendMeta
        ...     backend_type = 'awesome'
    """
    def __new__(meta, classname, bases, class_dict):
        klass = type.__new__(meta, classname, bases, class_dict)
        BackendManager.backends.append(klass)
        return klass


# class Backend(object):
#     pass


class DummyBackend(object):
    """This backend serves as a placeholder, in cases where no real backend
    mapping is needed."""
    __metaclass__ = BackendMeta
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
