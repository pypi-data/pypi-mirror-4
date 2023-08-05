Mapping Fields
==============

``map_FIELD_field``
-------------------

You can map a field name between the document and the underlying resource by
implementing a :meth:`map_FIELD_field` method where ``FIELD`` is the name of
the document field. The method returns a string with the actual name of the
resource field.

.. code-block:: python

    # We define a simple django model
    class ArticleModel(models.Model):
        long_title = models.CharField(max_length=200)

    # We define a document where we want to use name as a field name instead of
    # long_title
    class Article(Document):
        id = fields.NumberField()
        name = fields.StringField()

        class Meta:
            backend_type = 'django'
            model = ArticleModel

        map_name_field(self):
            return "long_title"

In the above example the document defines a field ``name``. For any operation
with the underlying resource, it will map ``name`` to ``long_title``.

``fetch_FIELD_field``
---------------------

You can map values that are fetched from a backend and set a different value on
the document. Specify a ``fetch_FIELD_field`` method on the document, and it
will be called whenever a representation gets fetched.

The method takes only one argument, which is the value originaly fetched from
the backend.

.. code-block:: python

    class Article(Document):
        id = fields.NumberField()
        name = fields.StringField()

        class Meta:
            backend_type = 'http'

        fetch_name_field(self, value):
            if value == "some string":
                return value
            else:
                return "UNKNOWN"

    >>> art = Article({'id': 1})
    >>> # this fetches a resource that looks like that:
    >>> # {"id": 1, "name": "something"}
    >>> art.fetch()
    >>> art.name
    UNKNOWN

``save_FIELD_field``
--------------------

You can as well map field values before sending the document to the backend
for saving the resource. It works the same as for fetching field described
above, you only specify a ``save_FIELD_field`` method on the document.

``render_FIELD_field``
----------------------

To change the rendering of the field use a ``render_FIELD_field`` method. Use
it the same as fetch or save mapping method described above.
