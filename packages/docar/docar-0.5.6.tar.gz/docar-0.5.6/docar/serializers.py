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
