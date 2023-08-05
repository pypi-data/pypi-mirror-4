from nose.tools import eq_, ok_, assert_raises
from nose.exc import SkipTest
from mock import Mock, patch

from .factory import article_factory, editor_factory
from .factory import Article, Editor, Kiosk, Entrepeneur, Newspaper

from docar import fields, Document
from docar.documents import Options
from docar.backends import DummyBackend
from docar.exceptions import ValidationError, BackendDoesNotExist

import unittest


### Document API Tests

class when_a_system_interacts_with_a_document(unittest.TestCase):
    """Test the API of the document."""

    # document property access
    def it_access_properties_as_members_of_the_python_object(self):
        article = article_factory()

        # Test that the properties of article are there
        eq_(5, len(article._meta.local_fields))
        eq_(True, hasattr(article, 'id'))
        eq_(True, hasattr(article, 'title'))
        eq_(True, hasattr(article, 'slug'))
        eq_(True, hasattr(article, 'editor'))
        eq_(True, hasattr(article, 'category'))

    # foreign documents and collections are different
    def it_sets_foreign_documents_and_collections_as_manager(self):
        kiosk = Kiosk()

        eq_(True, isinstance(kiosk.owner, Entrepeneur))
        eq_(True, isinstance(kiosk.newspaper, Newspaper))

    # from_dict
    def it_can_create_itself_from_a_dict(self):
        """Populate a document by supplying a nested dictionary."""
        ### Test a simple document
        editor = Editor()
        editor_data = {
                'id': 23,
                'name': 'Jules Vernes'
                }

        editor.from_dict(editor_data)

        eq_(23, editor.id)
        eq_('Jules Vernes', editor.name)

        ### Foreign documents can be automatically created by nested dicts
        article = Article()
        article_data = {
                'id': 42,
                'slug': 'article-slug',
                'title': 'article-title',
                'editor': editor_data
                }
        article.from_dict(article_data)

        eq_(42, article.id)
        eq_(23, article.editor.id)
        eq_('Jules Vernes', article.editor.name)

        ### Now a more complex scenario
        kiosk = Kiosk()
        kiosk.from_dict({
            'newspaper': [{
                'name': 'article 1',
                'slug': 'article-slug',
                'editor': {
                    'name': 'Jules Vernes'
                    },
                'id': 45
                }, {
                'name': 'article 2',
                'slug': 'article2-slug'
                }],
            'owner': {
                'name': 'Johnny Cash',
                'cash': 50,
                'subscriptions': [{
                    'newspaper': [{
                        'title': 'Title A',
                        'slug': 'title-a',
                        'editor': {
                            'name': 'Fidel Castro'
                            }
                        }, {
                        'title': 'Title A',
                        'slug': 'title-a',
                        'editor': {
                            'name': 'Fidel Castro'
                            }
                        }
                        ]
                    }, {
                    'newspaper': [{
                        'title': 'Title A',
                        'slug': 'title-a',
                        'editor': {
                            'name': 'Fidel Castro'
                            }
                        }, {
                        'title': 'Title B',
                        'slug': 'title-b',
                        'editor': {
                            'name': 'Luiz Castro'
                            }
                        }
                        ]}
                    ]
                }
            })

        # have 2 articles in your newspaper
        eq_(2, len(kiosk.newspaper.collection_set))

        # Deep nested attribute access
        eq_('Jules Vernes', kiosk.newspaper.collection_set[0].editor.name)

        # Check the nested collections
        eq_('Luiz Castro', kiosk.owner.subscriptions.collection_set[1].newspaper.collection_set[1].editor.name)

        # Last check
        eq_('Johnny Cash', kiosk.owner.name)

    # to_dict
    def it_can_turn_the_document_into_a_dict(self):
        """Generate a dict from a document."""
        article = article_factory()

        expected = {
                'id': 1,
                'slug': 'article-slug',
                'title': 'article title',
                'editor': {
                    'id': 1,
                    'name': 'Jules Vernes'
                    }
                }

        eq_(expected, article.to_dict())

    # fetch
    def it_fetches_itself_from_a_backend(self):
        """Retrieve from the backend the document as a dict and configure."""
        data = {
                'id': 1,
                'slug': 'article-slug',
                'title': 'article title',
                'editor': {
                    'id': 1,
                    'name': 'Jules Vernes'
                    }
                }
        article = Article({'id': 1})

        # Pretend to have a fetch field for the title attribute. This maps
        # the original 'article title' to the below string.
        article.fetch_title_field = Mock()
        article.fetch_title_field.return_value = 'article post fetch'

        # The backend is mocked. backend.fetch returns a dict.
        article._meta.backend = Mock()
        article._meta.backend.fetch.return_value = data

        # arguments provided to the high level fetch method, are proxied to the
        # backend managers fetch method too.
        article.fetch(arg='some variable')

        # This should have configured the document according to the dict
        # and verify that the backend manager fetch was called.
        eq_(1, article.editor.id)
        eq_('article post fetch', article.title)
        eq_('article-slug', article.slug)

        article._meta.backend.fetch.assert_called_once_with(article,
                arg='some variable')
        article.fetch_title_field.assert_called_once_with('article title')

        #FIXME: Test for error scenarios and exception handling, also recursive
        #       fetching

    # save
    def it_can_save_the_document_to_a_backend(self):
        """Save the document to a backend."""
        data = {
                'id': 1,
                'slug': 'article-slug',
                'title': 'article post save',
                'editor': {
                    'id': 1,
                    'name': 'Jules Vernes'
                    }
                }
        article = article_factory()

        # The read_only field should get filtered out by the save method
        article.editor.security_number = 'bogus'

        # Pretend to have a save field for the title attribute. This maps
        # the original 'article title' to the below string.
        article.save_title_field = Mock()
        article.save_title_field.return_value = 'article post save'

        # For the sake of this test, just validate, please.
        article.validate = Mock()
        article.validate.return_value = True

        # The backend is mocked. backend.fetch returns a dict.
        article._meta.backend = Mock()

        # arguments provided to the high level save method, are proxied to the
        # backend managers save method too.
        article.save(arg='some variable')

        # Saving involves validation and proxying the request to the backend.
        article.validate.assert_called_once()
        article._meta.backend.save.assert_called_once_with(
                article, data, arg='some variable')
        article.save_title_field.assert_called_once_with()

        #FIXME: Test for error scenarios and exception handling

    # delete
    def it_can_delete_data_the_document_represents_from_a_backend(self):
        """Delete the documents real data from the backend."""
        article = article_factory()

        # The backend is mocked. backend.fetch returns a dict.
        article._meta.backend = Mock()

        # arguments provided to the high level save method, are proxied to the
        # backend managers save method too.
        article.delete(arg='some variable')

        # Saving involves validation and proxying the request to the backend.
        article._meta.backend.delete.assert_called_once_with(
                article, arg='some variable')

    # render
    def it_can_render_the_document_into_a_dict(self):
        """Rendering outputs a dict, that is cleaned from attributes with
        rendering off or attributes that are mapped by a render field."""
        data = {
                'slug': 'article-slug',
                'title': 'article post render',
                'editor': {
                    'name': 'Jules Vernes'
                    }
                }
        article = article_factory()

        # Pretend to have a fetch field for the title attribute. This maps
        # the original 'article title' to the below string.
        article.render_title_field = Mock()
        article.render_title_field.return_value = 'article post render'

        # render the document into a dict
        out = article.render()

        # The data should be the same as the output. the `id` fields are not
        # displayed, cause they have the rendering attribute off. So is also
        # editor.security_number, cause it has optional=True set.
        eq_(data, out)
        article.render_title_field.assert_called_once_with('article title')

        #FIXME: Test for error scenarios and exception handling

    # update
    # FIXME: update test is missing, but needs some consideration.


### Document Meta Options

class when_a_document_gets_configured(unittest.TestCase):
    # _meta
    def it_stores_meta_configuration_in_a_object_attribute(self):
        """All options are stored in the _meta attribute."""
        article = article_factory()

        eq_(True, hasattr(article, '_meta'))
        eq_(True, isinstance(article._meta, Options))

    def it_sets_the_backend_manager_on_the_met_attribute(self):
        """The correct backend is stored as a property of _meta."""
        editor = editor_factory()

        eq_(True, hasattr(editor._meta, 'backend'))
        eq_(editor._meta.backend, editor._backend_manager)

    def it_has_a_list_of_fields_in_meta(self):
        """The document keeps a list of its properties."""
        article = article_factory()

        # the fields are stored in a list of property fields
        eq_(True, isinstance(article._meta.local_fields, list))
        for field in article._meta.local_fields:
            eq_(True, isinstance(field, fields.Field))

    def it_initializes_with_many_default_values(self):
        """Check on the default values. Changing here an assertion to fix a
        broken test, means also updating the documentation!!!"""
        article = Article()

        eq_(True, not article._meta.model)
        eq_('dummy', article._meta.backend_type)
        eq_(['id'], article._meta.identifier)
        eq_([], article._meta.excludes)
        eq_([], article._meta.context)

        # Those fields are set when the properties are read out
        # eq_([], article._meta.local_fields)
        # eq_([], article._meta.related_fields)
        # eq_([], article._meta.collection_fields)

        # The bound option is tested below
        #eq_([], article._bound)

    # bound attribute
    def it_gets_bound_when_created_from_the_a_dict(self):
        """A instantiated document is not bound. creating the document from
        a dict, binds it."""
        data = {
                'id': 1,
                'slug': 'article-slug',
                'title': 'article title',
                'editor': {
                    'id': 1,
                    'name': 'Jules Vernes'
                    }
                }
        article = Article()

        # the document is unbound
        eq_(False, article._bound)

        article.from_dict(data)

        # the document is now bound
        eq_(True, article._bound)

    def it_converts_string_identifiers_to_a_list_of_identifiers(self):
        """Providing only a string for the identifier list, makes the string a
        list with one item."""
        class Doc(Document):
            name = fields.StringField()

            class Meta:
                identifier = 'name'

        d = Doc()
        eq_(['name'], d._meta.identifier)

    def it_stores_the_declared_fields_in_the_right_order(self):
        """Fields are stored in the order they are declared."""
        article = Article()

        # expect the fields to be stored in this order
        eq_('id', article._meta.local_fields[0].name)
        eq_('slug', article._meta.local_fields[1].name)
        eq_('title', article._meta.local_fields[2].name)
        eq_('editor', article._meta.local_fields[3].name)

    # FIXME: Add tests for the backend type handling


### Document Backend integration

class when_a_document_wires_data_it_uses_a_backend_manager(unittest.TestCase):
    """All data can be synced with a backend, using so called backend
    managers."""
    def it_per_default_sets_the_dummy_backend_manager(self):
        """If no backend configuration is provided, the document uses the dummy
        backend manager."""
        article = article_factory()

        eq_(False, bool(article._meta.backend))
        eq_(True, isinstance(article._meta.backend, DummyBackend))

    def it_calls_the_backends_save_method_on_save(self):
        """Saving a document calls the backends save method."""
        article = article_factory()
        article._meta.backend.save = Mock()
        article._meta.backend.save.return_value = {}

        # Arguments used here are proxied to the backend
        article.save(arg='value')

        # Calling save normalizes the document into a dict using _save
        article._meta.backend.save.assert_called_once_with(
                article, {
                    'id': 1, 'slug': 'article-slug', 'title': 'article title',
                    'editor': {'id': 1, 'name': 'Jules Vernes'}
                    },
                arg='value')

    def it_calls_the_backends_fetch_method_on_save(self):
        """Fetching a document calls the backend fetch method."""
        article = article_factory()
        article._meta.backend.fetch = Mock()
        article._meta.backend.fetch.return_value = {}

        # Arguments used here are proxied to the backend
        article.fetch(arg='value')

        article._meta.backend.fetch.assert_called_once(
                article, arg='value')


### Document Validation

class when_checking_on_the_input_of_a_document(unittest.TestCase):
    """A document has possibilities for validation."""
    def it_can_use_the_documents_validator(self):
        article = article_factory()

        eq_(True, article.validate())

        # This will trigger a validation error, cause id must be an integer.
        article.id = ''

        assert_raises(ValidationError, article.validate)

    def it_fails_validation_if_a_referenced_foreign_document_is_required_and_does_not_exist(self):
        """The validator checks if a foreign document really exists."""
        # FIXME: This test fails currently, cause the code under test is
        # commented out till a design decision is made about it. Look into the
        # `Document.validate` method for more information
        raise SkipTest
        article = article_factory()

        # In the first try, we let the fetch to the backend for editor fail
        article.editor._meta.backend.fetch = Mock()
        article.editor._meta.backend.fetch.side_effect = BackendDoesNotExist

        article.editor._bound = False

        # If the fetch to the foreign document fails, it raises a validation
        # error as expected
        assert_raises(ValidationError, article.validate)
        article.editor._meta.backend.fetch.assert_called()

        # Reset the mock, and this time don't raise the exception
        article.editor._meta.backend.fetch.reset_mock()
        article.editor._meta.backend.fetch.side_effect = None
        article.editor._bound = True

        ok_(article.validate())

    def it_validates_optional_fields_that_are_not_set(self):
        """If a field is optional and not set validation still succeeds."""
        editor = editor_factory()
        article = article_factory()

        # editor has its security_number not set, but still validates
        eq_(None, editor.security_number)
        ok_(editor.validate())

        # The article_factory doesn't set the category per default
        eq_(True, not article.category._bound)
        ok_(article.validate())


### Document Inheritance

class when_documents_inherit(unittest.TestCase):
    """Documents can inherit from each other."""
    def it_can_inherit_documents_and_not_options(self):
        """Fields are inherited, options not."""
        class DocBase(Document):
            id = fields.NumberField()
            name = fields.StringField()

            class Meta:
                identifier = ['name']

        class DocChild(DocBase):
            another = fields.StringField()

        base_doc = DocBase()
        child_doc = DocChild()

        eq_(['name'], base_doc._meta.identifier)
        eq_(['id'], child_doc._meta.identifier)
        eq_(2, len(base_doc._meta.local_fields))
        eq_(3, len(child_doc._meta.local_fields))


### Document Metaclass and Mechanics

class describe_the_documents_mechanics(unittest.TestCase):
    """Test document specific quirks and internal workings."""
    def it_calls_from_dict_when_instantiated_with_data(self):
        """Providing initial data to a document, uses from_dict to parse the
        input."""
        with patch.object(Article, 'from_dict') as mock_from:
            # from_dict is called only when the Document gets instantiated
            # with initial data
            Article()
            Article({'id': 23})

            mock_from.assert_called_once_with({'id': 23})

    def it_can_extract_the_identifier_state_from_itself(self):
        article = article_factory()
        expected = {"id": 1}

        eq_(expected, article._identifier_state())

    def it_can_lookup_a_field_when_provided_with_a_name(self):
        """Lookup a field when given a name."""
        article = article_factory()
        field = article._field('title')

        eq_(True, isinstance(field, fields.Field))

    def it_can_set_context_to_its_referenced_documents(self):
        """When supplying context, it is also supplied to its related
        documents."""
        context = {'context': 'hello'}

        article = Article()
        eq_({}, article._context)
        eq_({}, article.editor._context)

        article._set_context(context)
        eq_(context, article._context)
        eq_(context, article.editor._context)

        # Lets make sure _set_context is actually called when instantiating a
        # document
        with patch.object(Article, '_set_context') as mock_setter:
            Article(context=context)
            mock_setter.assert_called_once_with(context)

    def it_can_retrieve_context_values_as_configured_in_the_meta_attribute(self):
        """Documents can retrieve their context options depending on the
        configuration in meta."""
        context = {'context': 'hello', 'context1': 'world'}
        article = Article(context=context)

        eq_(context, article._get_context())
        eq_({'context1': 'world'}, article.editor._get_context())

    # FIXME: Add tests for the behaviour of bound
