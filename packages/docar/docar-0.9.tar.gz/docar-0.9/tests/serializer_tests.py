from nose.tools import eq_
from mock import patch
from docar import Document, Collection, fields
from docar.serializers import (
        SerializerMeta,
        Serializer,
        DropinJsonSerializer,
        CollectionJsonSerializer,
        MEDIA_TYPES)
from docar.serializers import list_media_types, register_media_type

from .factory import article_factory, collection_factory

import unittest

try:
    import json
except ImportError:
    import simplejson as json


# Make a stripped down version of documents found in libthirty,
# this serves the purpose to test the dropin serializer
# FIXME: Add an inline foreign document and a collection that is not inline
class Postgres(Document):
    id = fields.NumberField()

    def uri(self):
        return 'postgres_uri'


class User(Document):
    name = fields.StringField()


class Instance(Document):
    id = fields.NumberField()

    def uri(self):
        return 'instance_uri'


class Instances(Collection):
    document = Instance

    def uri(self):
        return 'instance_collection_uri'


class Cname(Document):
    record = fields.StringField()


class CnameCollection(Collection):
    document = Cname


class App(Document):
    instances = fields.NumberField()
    label = fields.StringField()
    published = fields.BooleanField()
    user = fields.ForeignDocument(User, inline=True)
    postgres = fields.ForeignDocument(Postgres)
    cnames = fields.CollectionField(CnameCollection, inline=True)

    def uri(self):
        return 'app_uri'

# We clean the media-type/serializer mapping
MEDIA_TYPES.clear()


### The actual test classes
class when_a_serializer_gets_defined(unittest.TestCase):
    def setUp(self):
        MEDIA_TYPES.clear()

    def it_can_store_media_types(self):
        """Register media types and map them to serializers."""
        register_media_type('store/media', 'serializer')

        eq_(True, 'store/media' in MEDIA_TYPES)
        eq_('serializer', MEDIA_TYPES['store/media'])

    def it_registers_the_media_type(self):
        """Declaring the class, registers the serializer."""
        with patch('docar.serializers.register_media_type') as mock_register:
            class TestSerializer(Serializer):
                __metaclass__ = SerializerMeta
                media_types = ['application/json']

            mock_register.assert_called_once()

    def it_stores_the_serializers_media_type(self):
        """Declaring the class, registers the serializer."""
        class TestSerializer(Serializer):
            __metaclass__ = SerializerMeta
            media_types = ['media/type']

        eq_(True, 'media/type' in MEDIA_TYPES)
        eq_(TestSerializer, MEDIA_TYPES['media/type'])

    def it_lists_the_media_types_as_a_list(self):
        """Get a list of all media types registered."""
        class TestSerializer(Serializer):
            __metaclass__ = SerializerMeta
            media_types = ['media/type']

        media_types = list_media_types()

        eq_(True, 'media/type' in media_types)


class when_the_old_json_serializer_is_used(unittest.TestCase):
    """The JsonSerializer at this point is a replacement for the old to_json
    method."""
    expected = {
        "cnames": [{'record': 'aa.record'}],
        "instances": 2,
        "label": "app",
        "published": True,
        "link": {
            "href": "app_uri",
            "rel": "self"
            },
        "postgres": {
            "href": "postgres_uri",
            "rel": "related"
            },
        "user": {
            "name": "crito"
            }
        }

    expected_collection = {
        "items": [
            {"id": 1, "link": {"rel": "item", "href": "instance_uri"}}
            ],
        "size": 1,
        "link": {"rel": "self", "href": "instance_collection_uri"}
        }

    fixture = {
        'cnames': [{'record': 'aa.record'}],
        'instances': 2,
        'label': 'app',
        'published': True,
        'postgres': {'id': 1},
        'user': {'name': 'crito'}
        }

    collection_fixture = {'id': 1}

    def it_serializes_a_document_correctly(self):
        """Dump the document in tis weird json format."""
        app = App(self.fixture)

        eq_(json.dumps(self.expected), DropinJsonSerializer.dump(app))

    def it_serializes_a_collection_correctly(self):
        """Dump the collection in this weird json format."""
        instances = Instances()
        instances.add(Instance({'id': 1}))

        eq_(json.dumps(self.expected_collection),
                DropinJsonSerializer.dump(instances))

    def it_populates_a_document_from_a_serialized_string(self):
        """Load a populated document from a json string."""
        obj = App()

        app = DropinJsonSerializer.load(obj, json.dumps(self.fixture))

        eq_(self.fixture, app.render())
        eq_(app, obj)


class when_collection_plus_json_serialization_is_needed(unittest.TestCase):
    """Serialize documents and collections into the collection+json media
    type."""
    def it_serializes_errors(self):
        expected = {
                'collection': {
                    'error': {
                        'title': 'Error title',
                        'code': 404,
                        'message': 'Not found'
                        }
                    }
                }
        j = CollectionJsonSerializer.error(status=404, message='Not found',
                title='Error title')

        eq_(expected, json.loads(j))

    def it_serializes_a_document_to_json(self):
        article = article_factory()

        expected = {
                'collection': {
                    'items': [{
                        'data': [
                            {'name': 'slug', 'value': 'article-slug'},
                            {'name': 'title', 'value': 'article title'}
                            ],
                        'links': [
                            {'href': 'editor-uri', 'rel': 'item'}
                            ],
                        'href': 'article-uri'
                        }
                    ]}
                }

        eq_(expected, json.loads(CollectionJsonSerializer.dump(article)))

    def it_serializes_a_collection_to_json(self):
        newspaper = collection_factory()

        expected = {
                'collection': {
                    'items': [{
                        'data': [
                            {'name': 'slug', 'value': 'article-slug'},
                            {'name': 'title', 'value': 'article title'}
                            ],
                        'links': [
                            {'href': 'editor-uri', 'rel': 'item'}
                            ],
                        'href': 'article-uri'
                        }, {
                        'data': [
                            {'name': 'slug', 'value': 'article-slug'},
                            {'name': 'title', 'value': 'article 2 title'}
                            ],
                        'links': [
                            {'href': 'editor-uri', 'rel': 'item'}
                            ],
                        'href': 'article-uri'
                        }, {
                        'data': [
                            {'name': 'slug', 'value': 'article-slug'},
                            {'name': 'title', 'value': 'article 3 title'}
                            ],
                        'links': [
                            {'href': 'editor-uri', 'rel': 'item'}
                            ],
                        'href': 'article-uri'
                        }


                    ]}
                }

        eq_(expected, json.loads(CollectionJsonSerializer.dump(newspaper)))

    def it_serializes_a_json_string_to_a_document(self):
        pass

    def it_serializes_a_json_string_to_a_collection(self):
        pass

    def it_raises_an_exception_when_having_an_error(self):
        pass
