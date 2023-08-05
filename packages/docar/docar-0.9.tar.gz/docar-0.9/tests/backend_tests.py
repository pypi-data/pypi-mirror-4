import unittest

from nose.tools import eq_, ok_
# from mock import Mock

from docar.backends import (
        DummyBackend,
        # Backend,
        BackendMeta,
        BackendManager)
        # DjangoBackendManager,
        # HttpBackendManager)
from docar import Document, fields


class when_a_backend_gets_declared(unittest.TestCase):
    def setUp(self):
        self.backends_copy = BackendManager.backends
        BackendManager.backends = []

    def tearDown(self):
        BackendManager.backends = self.backends_copy

    def it_stores_the_backend_in_the_backend_manager(self):
        """Using a metaclass, backends are registered with the backend
        manager."""
        class NewBackend(object):
            __metaclass__ = BackendMeta

        eq_(1, len(BackendManager.backends))
        eq_(NewBackend, BackendManager.backends[0])

    def it_can_be_retrieved_by_the_backend_manager(self):
        """The backend manager returns requested backend manager instances."""
        class NewBackend(object):
            __metaclass__ = BackendMeta
            backend_type = 'new'

        eq_(True, isinstance(BackendManager('new'), NewBackend))


class when_a_backend_gets_instantiated(unittest.TestCase):
    # def setUp(self):
    #     self.backends_copy = BackendManager.backends
    #     BackendManager.backends = []
    #
    #     class NewBackend(Backend):
    #         __metaclass__ = BackendMeta
    #         backend_type = 'new'
    #
    #
    # def tearDown(self):
    #     BackendManager.backends = self.backends_copy
    #
    # def it_can_provide_a_link_using_the_django_model(self):
    #     mock_model = Mock()
    #     mock_model.get_absolute_url.return_value = "link"
    #
    #     manager = BackendManager('django')
    #     manager.instance = mock_model
    #
    #     eq_("link", manager.uri())
    #     eq_(True, mock_model.get_absolute_url.called)
    def it_takes_the_backend_type_as_an_argument(self):
        manager = BackendManager('dummy')
        eq_('dummy', manager.backend_type)

    def it_defaults_to_the_django_backend_type(self):
        manager = BackendManager()
        eq_('dummy', manager.backend_type)

    # def it_abstracts_a_specific_backend_manager(self):
    #     manager = BackendManager('django')
    #     ok_(isinstance(manager, DjangoBackendManager))

    #     manager = BackendManager('http')
    #     ok_(isinstance(manager, HttpBackendManager))

    def it_can_specify_the_backend_type_as_a_meta_option(self):
        class Doc(Document):
            id = fields.NumberField()

            class Meta:
                backend_type = 'dummy'

        doc = Doc()
        ok_(isinstance(doc._backend_manager, DummyBackend))

        # class Doc(Document):
        #     id = fields.NumberField()

        #     class Meta:
        #         backend_type = 'http'

        # doc = Doc()
        # ok_(isinstance(doc._backend_manager, HttpBackendManager))
