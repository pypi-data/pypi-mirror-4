from nose.tools import eq_
from mock import patch
from docar import fields, Document
from docar.serializers import (
        SerializerMeta,
        Serializer,
        # JsonSerializer,
        MEDIA_TYPES)
from docar.serializers import list_media_types, register_media_type

import unittest
import json

# We clean the media-type/serializer mapping
MEDIA_TYPES.clear()


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


# class when_the_old_json_serializer_is_used(unittest.TestCase):
#     """The JsonSerializer at this point is a replacement for the old to_json
#     method."""
#     def it_produces_the_same_to_json_output(self):
#         """Compare the outputs of the old to_json method and this serializer."""
#         class Doc(Document):
#             id = fields.NumberField()
#             name = fields.StringField()

#             def uri(self):
#                 return 'doc uri'

#         d = Doc({'id': 13, 'name': 'doc name'})
#         eq_(d.to_json(), JsonSerializer.dump(d))

#     def it_restores_equivalent_objects_from_json(self):
#         """Check on the restored object fields."""
#         class Doc(Document):
#             id = fields.NumberField()
#             name = fields.StringField()

#             def uri(self):
#                 return 'doc uri'

#         t = json.dumps({'id': 13, 'name': 'doc name'})

#         obj = JsonSerializer.load(Doc(), t)
#         eq_(13, obj.id)
#         eq_('doc name', obj.name)
