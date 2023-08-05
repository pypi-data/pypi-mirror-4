from docar import fields, Document, Collection

try:
    import json
except ImportError:
    import simplejson as json

MEDIA_TYPES = {}


def register_media_type(media_type, serializer):
    """Register a media types with their handlers.

    :param media_type: The media type, eg: 'application/json'
    :param serializer: docar.serializer.Serializer The serializer class to use.

    """
    MEDIA_TYPES[media_type] = serializer


def list_media_types():
    """Return a list with all registered media types."""
    return MEDIA_TYPES.keys()


def get_media_type(media_type):
    """Fetch the serializer, for a certain media type.

    :param media_type: string The media type, eg: "application/json"
    """
    if not media_type in MEDIA_TYPES:
        # FIXME: Be more specific, explain whats happening here
        raise Exception('Unknown media type.')
    return MEDIA_TYPES[media_type]


class SerializerMeta(type):
    """Metaclass for serializer plugins.

    It registers serializers and media types with docar.
    """
    def __new__(meta, classname, bases, class_dict):
        klass = type.__new__(meta, classname, bases, class_dict)
        media_types = class_dict.get('media_types')
        for media_type in media_types:
            register_media_type(media_type, klass)
        return klass


class Serializer(object):
    """Base class for all serializers. Inherit your specific serializer from
    this."""
    pass


class DropinJsonSerializer(Serializer):
    """This serializer should function as a dropin replacement for the json
    serialization of the 0.5.6 branch and should provide an upgrade path. Don't
    use it if you can, it will be removed anytime soon.

    """
    __metaclass__ = SerializerMeta
    media_types = ['application/json']

    @classmethod
    def dump(cls, obj):
        """Serialize a docar document or collection.

        :param obj: ``Document`` or ``Collection``.
        """
        serializer = cls()

        # we render differently whether its a document or a collection
        if isinstance(obj, Document):
            msg = serializer._serialize_document(obj)
        elif isinstance(obj, Collection):
            msg = serializer._serialize_collection(obj)

        return json.dumps(msg)

    def _serialize_collection(self, obj):
        msg = {'link': {
            'rel': 'self', 'href': obj.uri()},
            'size': 0,
            'items': []
            }

        for item in obj.collection_set:
            cleaned = item.render()
            cleaned['link'] = {
                    'rel': 'item',
                    'href': item.uri()
                    }
            msg['items'].append(cleaned)
            msg['size'] += 1

        return msg

    def _serialize_document(self, obj):
        cleaned = obj.render()
        msg = {'link': {
            'rel': 'self', 'href': obj.uri()}}

        for field in obj._meta.local_fields:
            if isinstance(field, fields.ForeignDocument):
                relation = getattr(obj, field.name)
                if field.inline:
                    msg[field.name] = cleaned[field.name]
                else:
                    msg[field.name] = {
                        'rel': 'related',
                        'href': relation.uri()
                        }
            elif isinstance(field, fields.CollectionField):
                collection = getattr(obj, field.name)
                if field.inline:
                    # msg[field.name] = DropinJsonSerializer.dump(collection)
                    msg[field.name] = cleaned[field.name]
                else:
                    a = []
                    for document in collection.collection_set:
                        a.append(json.loads(DropinJsonSerializer.dump(collection)))
                    msg[field.name] = a
            else:
                msg[field.name] = cleaned[field.name]

        return msg

    @classmethod
    def load(self, obj, data):
        """Restore a docar document or collection from a serialized state.

        :param obj: ``Document`` or ``Collection``.
        :param data: string Serialized state.
        """
        data = json.loads(data)
        obj.from_dict(data)
        return obj

    @classmethod
    def error(self, message=None, status=None, code=None):
        """Serialize an error."""
        msg = {}
        if message:
            msg['message'] = message
        if code:
            msg['code'] = code
        if status:
            msg['status'] = status

        if msg:
            return json.dumps(msg)
        else:
            return ''


class CollectionJsonSerializer(Serializer):
    __metaclass__ = SerializerMeta
    media_types = ['application/vnd.collection+json']

    @classmethod
    def error(cls, status, message=None, title=None):
        msg = {'collection': {'error': {}}}
        msg['collection']['error']['code'] = int(status)
        if message:
            msg['collection']['error']['message'] = message
        if title:
            msg['collection']['error']['title'] = title

        return json.dumps(msg)

    @classmethod
    def dump(cls, obj):
        msg = {'collection': {}}

        serializer = cls()
        # cache the rendered state of the object
        serializer._render = obj.render()
        # if isinstance(serializer._render, dict):
        #     serializer._render = [serializer._render]

        msg['collection']['items'] = serializer._items(obj)
        return json.dumps(msg)

    def _items(self, obj):
        def _item_row(doc, render):
            data = []
            links = []
            item = {}
            item['href'] = doc.uri()

            for field in doc._meta.local_fields:
                if field.name not in render:
                    continue
                if isinstance(field, fields.ForeignDocument):
                    links.append({
                        'rel': 'item',
                        'href': getattr(doc, field.name).uri()
                        })
                else:
                    data.append({
                        'name': field.name,
                        'value': render[field.name]
                        })

            if data:
                item['data'] = data
            if links:
                item['links'] = links
            return item

        items = []

        # We cycle through each row of the rendered state, and apply some
        # serialization.
        if isinstance(self._render, dict):
            # Thats a single document
            items.append(_item_row(obj, self._render))
        elif isinstance(self._render, list):
            # We found a collection
            for item in obj.collection_set:
                items.append(_item_row(item, item.render()))

        return items
