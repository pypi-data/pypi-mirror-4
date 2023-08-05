Fields
======

Documents declare their attributes using fields set as class attributes. The
name of a field maps straight to the name of a field of the underlying
resource. See `Mapping Fields`_ for a way to use a different field name for the
document and the resource.

Example

.. code-block:: python

    class Message(Document):
        id = fields.NumberField()
        name = fields.StringField()

Field Options
-------------

``optional``
~~~~~~~~~~~~

.. py:attribute:: Field.optional

When set to ``True``, This field can be optional and will be ignored if not set
to a value. Default is ``False``.

``default``
~~~~~~~~~~~

.. py:attribute:: Field.default

Specify a default value for this field. If no value is set by the user, the
default value is used when interacting with the backend.

``scaffold``
~~~~~~~~~~~~

.. py:attribute:: Fields.scaffold

Control whether to scaffold this field. Defaults to ``True``.

``render``
~~~~~~~~~~

.. py:attribute:: Fields.render

If set to ``False`` the field gets ignored when the document gets rendered.
Defaults to ``True``.

``read_only``
~~~~~~~~~~~~~

.. py:attribute:: Field.read_only

If set to ``True``, the field value will not be saved, whatever it is set to.
The responsible backend manager will not have the value available. Defaults to
``False``.

``inline``
~~~~~~~~~~

Normally ``ForeignDocuments`` and ``CollectionFields`` render as a reference
with a resource URI link and a relation attribute. When you specify the
``inline`` field option, you can force the field to render as an inline
element.

Example

.. code-block:: python

    class Doc1(Document):
        id = fields.NumberField()
        name = fields.StringField()

        def uri(self):
            return "http://example.org/doc/%s" % self.id

    class Doc2(Document):
        id = fields.NumberField()
        doc_inline = fields.ForeignDocument(Doc1, inline=True)
        doc1 = fields.ForeignDocument(Doc1)

    d = Doc2()
    d.fetch()
    d.render()
    {
        "id": 1,
        "doc1": {
            "id": 1,
            "rel": "related",
            "href": "http://example.org/doc/1/"
            },
        "doc_inline": {
            "id": 2,
            "name": "doc_inline"
            }
    }

``validate``
~~~~~~~~~~~~

Specify whether to validate the field or not. Defaults to ``True``. If
disabled, validation is skipped for this field.

``validators``
~~~~~~~~~~~~~~

You can add a list of functions that will be called when validating the field.
For details on those functions see the section about `Validation`_.

Example

.. code-block:: python

    def validate_name(value):
        # Do something

    class Article(Document):
        id = fields.NumberField()
        name = fields.StringField(validators=[validate_name])

Field Types
-----------

``NumberField``
~~~~~~~~~~~~~~~

.. py:class:: NumberField(**options)

``StringField``
~~~~~~~~~~~~~~~

.. py:class:: StringField(**options)

``BooleanField``
~~~~~~~~~~~~~~~~

.. py:class:: BooleanField(**options)

``StaticField``
~~~~~~~~~~~~~~~

.. py:class:: StaticField(**options)

``ForeignDocument``
~~~~~~~~~~~~~~~~~~~

.. py:class:: ForeignDocument(**options)

``CollectionField``
~~~~~~~~~~~~~~~~~~~

.. py:class:: CollectionField(**options)

