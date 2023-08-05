from bisect import bisect

from .fields import (ForeignDocument,
        CollectionField,
        StaticField,
        NOT_PROVIDED)

from .backends import BackendManager
from .exceptions import ValidationError, BackendDoesNotExist


DEFAULT_NAMES = ('identifier', 'model', 'excludes', 'backend_type', 'context',
        'render')


def clean_meta(Meta):
    """Clean the Meta class from internal attributes."""
    if not Meta:
        return
    CleanedMeta = Meta.__dict__.copy()
    for name in Meta.__dict__:
        if name.startswith('_'):
            del CleanedMeta[name]

    return CleanedMeta


class Options(object):
    """A option class used to initiate documents in a sane state."""
    def __init__(self, meta):
        # Initialize some default values
        self.model = None
        self.backend_type = 'dummy'
        self.identifier = ['id']
        # FIXME: Do some type checking
        self.excludes = []
        self.context = []
        self.local_fields = []
        self.related_fields = []
        self.collection_fields = []

        self.meta = meta

    def add_field(self, field):
        """Insert field into this documents fields."""
        self.local_fields.insert(bisect(self.local_fields, field), field)

    def add_related_field(self, field):
        """Insert a related field into the documents fields."""
        self.related_fields.insert(bisect(self.related_fields, field), field)

    def add_collection_field(self, field):
        """Insert a collection field into the documents fields."""
        self.collection_fields.insert(bisect(self.collection_fields, field),
                field)

    def contribute_to_class(self, cls, name):
        # This is bluntly stolen from the django orm
        # Set first the default values
        cls._meta = self

        # Then override it with values from the ``Meta`` class
        if self.meta:
            meta_attrs = self.meta

            # We should make sure that `identifier` is a list
            if 'identifier' in meta_attrs:
                if isinstance(meta_attrs['identifier'], str):
                    # we assume the identifier has been specified as a string
                    meta_attrs['identifier'] = [meta_attrs['identifier']]

            for attr_name in DEFAULT_NAMES:
                if attr_name in meta_attrs:
                    setattr(self, attr_name, meta_attrs.pop(attr_name))
                #elif hasattr(self.meta, attr_name):
                #    setattr(self, attr_name, getattr(self.meta, attr_name))


class DocumentBase(type):
    """Metaclass for the Document class."""

    def __new__(meta, name, bases, attrs):
        klass = super(DocumentBase, meta).__new__(meta, name, bases, attrs)
        parents = [b for b in bases if isinstance(b, DocumentBase)]

        attr_meta = attrs.pop('Meta', None)
        meta_attrs = clean_meta(attr_meta)

        # set the defaults
        klass.add_to_class('_meta', Options(meta_attrs))

        # set all attributes to the class
        for name, obj in attrs.items():
            klass.add_to_class(name, obj)

        for base in parents:
            for field in base._meta.local_fields:
                klass.add_to_class(field.name, field)

        # create the fields on the instance document
        for field in klass._meta.local_fields:
            if isinstance(field, CollectionField):
                collection = field.Collection()
                collection._bound = False
                setattr(klass, field.name, collection)
            elif isinstance(field, ForeignDocument):
                document = field.Document()
                document._bound = False
                setattr(klass, field.name, document)
            elif field.default == NOT_PROVIDED:
                setattr(klass, field.name, None)
            elif isinstance(field, StaticField):
                setattr(klass, field.name, field.value)
            else:
                setattr(klass, field.name, field.default)

        # Add the model manager if a model is set
        klass._backend_manager = BackendManager(
            klass._meta.backend_type)
        if klass._meta.backend_type in 'django':
            klass._backend_manager._model = klass._meta.model
        klass._meta.backend = klass._backend_manager

        return klass

    def add_to_class(cls, name, obj):
        """If the obj provides its own contribute method, call it, otherwise
        attach this object to the class."""
        if hasattr(obj, 'contribute_to_class'):
            obj.contribute_to_class(cls, name)
        else:
            setattr(cls, name, obj)


class Document(object):
    """A document is a representation."""
    __metaclass__ = DocumentBase

    # _context = {}
    # bound = False

    def __init__(self, data=None, context={}):
        """Create a new document presentation of a resource.

        :param data: Initial values to use for this document. Specify at least
                     the identifier to be able to fetch the resource.
        :type data: dict
        :param context: Add additional context that can be used by the backend.
                        Use this to provide extra values to be used by a
                        backend that are not set in the representation.
        :type context: dict

        """
        self._set_context(context)
        self._bound = False

        # If we have some initial data, populate the document
        if (data and
                isinstance(data, dict)):
            self.from_dict(data)

    def _field(self, name):
        """Lookup the field with this name and return it if it exists."""
        field = None

        fields = [f for f in self._meta.local_fields
                if f.name == name]
        if len(fields) > 0:
            field = fields[0]

        return field

    def _set_context(self, context):
        """Set the supplied context recursively to this document and all
        referenced documents."""
        self._context = context
        for field in self._meta.local_fields:
            if isinstance(field, ForeignDocument):
                document = getattr(self, field.name)
                document._set_context(context)

    def _get_context(self):
        """Retrieve the context options for this document."""
        if len(self._meta.context) < 1:
            # If we have no context meta option set, just return it as it is
            return self._context

        obj = {}
        for field in self._meta.context:
            obj[field] = self._context[field]

        return obj

    def to_dict(self):
        """Return the document as a python dictionary. This method recursively
        turns related documents and items of collections into dictionaries
        too."""
        data = {}

        for field in self._meta.local_fields:
            if field.optional and not getattr(self, field.name):
                # The field is optional and none, ignore it
                continue
            if (field.optional is True
                    and (isinstance(field, ForeignDocument)
                        or isinstance(field, CollectionField))
                    and (getattr(getattr(self, field.name),
                        '_bound') is False)):
                # The field is optional and not bound, so we ignore it for the
                # backend state. This should only be done for foreign documents
                # and collections
                continue
            if isinstance(field, ForeignDocument):
                related = getattr(self, field.name)
                data[field.name] = related.to_dict()
            elif isinstance(field, CollectionField):
                col = getattr(self, field.name)
                data[field.name] = []
                for item in col.collection_set:
                    data[field.name].append(item.to_dict())
            elif isinstance(field, StaticField):
                data[field.name] = field.value
            else:
                data[field.name] = getattr(self, field.name)

        return data

    def from_dict(self, obj):
        """Create the document from a dict structure. It recursively builds
        also related documents and collections from a dictionary input."""
        for item, value in obj.iteritems():
            field = self._field(item)
            if not field:
                continue
            if isinstance(value, dict):
                Document = field.Document
                # Lets create a new relation
                document = Document(value, context=self._context)
                setattr(self, item, document)
            elif isinstance(value, list):
                # a collection
                collection = field.Collection()
                collection.collection_set = []
                Document = collection.document
                for elem in value:
                    document = Document(elem, context=self._context)
                    collection.add(document)
                if len(collection.collection_set) > 0:
                    # If we have at least one member in the collection, we
                    # regard it as bound
                    collection._bound = True
                setattr(self, item, collection)
            else:
                setattr(self, item, value)
        self._bound = True

    def _from_model(self, model):
        """Fill the document from a django model."""
        #FIXME: Add some type checking whether `model` truly is a django model
        for field in self._meta.local_fields:
            name = field.name
            mapped_name = name

            # We map document field names to names of fields on the backend
            # models.
            if hasattr(self, "map_%s_field" % name):
                map_method = getattr(self, "map_%s_field" % name)
                mapped_name = map_method()

            # skip fields that are not set on the model
            if not hasattr(model, mapped_name):
                continue

            # detect fetch fields and use them
            if hasattr(self, "fetch_%s_field" % name):
                fetch_method = getattr(self, "fetch_%s_field" % name)
                value = fetch_method(getattr(model, mapped_name))
                setattr(self, name, value)
                continue

            if isinstance(field, ForeignDocument):
                related_model = getattr(model, mapped_name)

                # If related_model == None, we dont create the relation
                if not related_model:
                    continue

                foreign_document = field.Document({},
                        context=self._context)
                foreign_document._from_model(related_model)
                setattr(self, name, foreign_document)

            elif isinstance(field, CollectionField):
                m2m = getattr(model, mapped_name)
                collection = field.Collection()
                collection._from_queryset(m2m.all())
                setattr(self, name, collection)

            elif hasattr(model, mapped_name):
                setattr(self, name, getattr(model, mapped_name))

        self._bound = True

    def _render(self, obj):
        data = {}

        for item, value in obj.iteritems():
            field = self._field(item)
            if not field or not field.render:
                continue
            if hasattr(self, "render_%s_field" % item):
                render_field = getattr(self, "render_%s_field" % item)
                value = render_field(value)
            if isinstance(value, dict):
                # Lets create a new relation
                document = getattr(self, item)
                #value = document._fetch(value)
                #data[item] = value
                data[item] = document.render()
            elif isinstance(value, list):
                # we render a collection
                collection = getattr(self, item)
                data[item] = collection.render()
            else:
                data[item] = value

        return data

    # def _render(self, obj):
    #     data = {}

    #     for item, value in obj.iteritems():
    #         field = self._field(item)
    #         if not field or not field.render:
    #             continue
    #         if hasattr(self, "render_%s_field" % item):
    #             render_field = getattr(self, "render_%s_field" % item)
    #             value = render_field(value)
    #         if isinstance(value, dict):
    #             # Lets create a new relation
    #             document = getattr(self, item)
    #             #value = document._fetch(value)
    #             #data[item] = value
    #             if field.inline:
    #                 # we render the field inline
    #                 data[item] = document.render()
    #             else:
    #                 data[item] = {
    #                         'rel': 'related',
    #                         'href': document.uri()}
    #                 # FIXME: Deprecated
    #                 #        Decisions like those, are done in the serializer.
    #                 # Also add the identifier fields into the rendered output
    #                 # identifiers = {}
    #                 # for id_field in document._meta.identifier:
    #                 #     identifiers[id_field] = getattr(document, id_field)
    #                 # data[item].update(identifiers)
    #         elif isinstance(value, list):
    #             # we render a collection
    #             collection = getattr(self, item)
    #             if field.inline:
    #                 data[item] = collection.render(inline=True)
    #             else:
    #                 data[item] = collection.render()
    #         else:
    #             data[item] = value

    #     return data

    def _save(self):
        data = {}
        obj = self.to_dict()

        for item, value in obj.iteritems():
            field = self._field(item)
            if not field or field.read_only:
                continue
            if hasattr(self, "save_%s_field" % item):
                # We apply a save field
                save_field = getattr(self, "save_%s_field" % item)
                data[item] = save_field()
                continue
            if isinstance(value, dict):
                # Lets follow a relation
                document = getattr(self, item)
                data[item] = document._save()
            elif isinstance(value, list):
                # we dissovle a collection
                collection = getattr(self, item)
                data[item] = []
                for document in collection.collection_set:
                    data[item].append(document._save())
            else:
                data[item] = value

        return data

    def _fetch(self, obj):
        data = {}

        for item, value in obj.iteritems():
            field = self._field(item)
            if not field:
                continue
            if hasattr(self, "fetch_%s_field" % item):
                fetch_field = getattr(self, "fetch_%s_field" % item)
                value = fetch_field(value)
                # obj[item] = value
            if isinstance(value, dict):
                # Lets create a new relation
                document = field.Document(value, context=self._context)
                data[item] = document._fetch(value)
            elif isinstance(value, list):
                # we fetch a collection
                collection = field.Collection()
                data[item] = []
                Document = collection.document
                for elem in value:
                    document = Document(elem, context=self._context)
                    data[item].append(document._fetch(elem))
            else:
                data[item] = value

        return data

    def _identifier_state(self):
        data = {}
        for elem in self._meta.identifier:
            # if hasattr(self, "fetch_%s_field" % elem):
            #     fetch_field = getattr(self, "fetch_%s_field" % elem)
            #     data[elem] = fetch_field(getattr(self, elem))
            if hasattr(self, "save_%s_field" % elem):
                save_field = getattr(self, "save_%s_field" % elem)
                data[elem] = save_field()
            else:
                data[elem] = getattr(self, elem)
        return data

    def render(self):
        """Return the document in render state. This includes URI links to
        related resources and the document itself."""
        obj = self._render(self.to_dict())

        return obj

    def validate(self, *args, **kwargs):
        """Validate the state of the document and throw a ``ValidationError``
        if validation fails."""
        errors = {}

        for field in self._meta.local_fields:
            try:
                if (isinstance(getattr(self, field.name), type(None))
                        and field.optional):
                    continue
                elif isinstance(field, ForeignDocument):
                    document = getattr(self, field.name)

                    # FIXME: This needs a design decision. If I validate a
                    # document but reference an existing document by
                    # identifier, I can't validate it, since I might not have
                    # all information available for the relation. But I wonder
                    # if that is a wanted behaviour.

                    # In cases were want to reference already existing
                    # documents, we will raise an validation error if
                    # we reference the document only by identifier. So
                    # lets fetch it to see if this is the case
                    # if not document._bound and not field.optional:
                    #     # We check if the document actually also exists
                    #     try:
                    #         document.fetch(*args, **kwargs)
                    #     except BackendDoesNotExist:
                    #         raise ValidationError('Referenced document %s '
                    #         'does not exist.' % field.name)
                    try:
                        document.validate()
                    except ValidationError as e:
                        if field.optional and not document._bound:
                            continue
                        else:
                            raise e
                elif isinstance(field, CollectionField):
                    collection = getattr(self, field.name)
                    for document in collection.collection_set:
                        document.validate()
                else:
                    value = getattr(self, field.name)
                    if ((isinstance(value, type(None))
                            or (isinstance(value, str) and value in ""))
                            and field.optional):
                        # we don't validate optional fields that are not set
                        continue
                    field.clean(value)
            except ValidationError as e:
                errors[field.name] = e

        if errors:
            raise ValidationError(errors)

        return True

    def save(self, *args, **kwargs):
        """Save the document to a backend. Any arguments given to this method
        is used when calling the underlying backend method. The backend
        receives the actual document and a normalized version as a dict of the
        document."""
        self.validate(*args, **kwargs)

        self._meta.backend.save(self, self._save(), *args, **kwargs)

    def update(self, data, *args, **kwargs):
        """Update a document from a dictionary. This is a convenience
        method."""
        self.fetch(*args, **kwargs)

        # First update the own document state with the new values
        self.from_dict(data)

        # save the representation to the model
        self.save(*args, **kwargs)

    def fetch(self, *args, **kwargs):
        """Fetch the model from the backend to create the representation of
        this resource."""
        # Retrieve the object from the backend
        obj = self._meta.backend.fetch(self, *args, **kwargs)
        obj = self._fetch(obj)
        self.from_dict(obj)

    def delete(self, *args, **kwargs):
        """Delete a model instance associated with this document."""
        self._meta.backend.delete(self, *args, **kwargs)

    def uri(self):
        """Return the absolute uri for this resource.

        :return: The URI of this resource.
        :rtype: string

        Implement this method on your document if you have special needs for
        the form of the URI.

        .. note::

            This method should always return the absolute URI as a string.

        """
        if hasattr(self._backend_manager, 'uri'):
            return self._backend_manager.uri()
