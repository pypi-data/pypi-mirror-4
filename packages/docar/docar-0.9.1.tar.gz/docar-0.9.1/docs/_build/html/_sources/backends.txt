.. _Backends:

========
Backends
========

The backends are the real meat of the documents. Where the document defines what
you can do, the backends implement the how of it. Documents and backends use
dictionaries to communicate with each other. A backend expects a dictionary
representation of the document, applies it as needed, and returns the resource
as a dictionary again. Each backend must implement the following methods:

``fetch``
  Fetch the resource from the underlying backend. Returns a dictionary.

``save``
  Save the document to the resource in the underlying backend. Expects a
  dictionary representation of the document.

``delete``
  Delete the resource from the underlying backend.

``docar`` comes with its own backend registry, which you can choose to use. But
you can also supply the document with any class that will be used as a backend.

HTTP Backend
============

The HTTP backend uses the ``requests`` library to communicate to remote
backends over HTTP. It assumes currently JSON as exchange protocol. The
document methods map the following way to the HTTP backend:

- :meth:`~Document.fetch` --> HTTP GET
- :meth:`~Document.save` --> HTTP POST (on create)
- :meth:`~Document.save` --> HTTP PUT (on update)
- :meth:`~Document.delete` --> HTTP DELET

uri methods
-----------

This backend uses the :meth:`~Document.uri` method to determine its API
endpoint. You can implement specific uri methods for each HTTP verb to be more
precise. If a http specific uri method is not found, it will fallback to the
default :meth:`~Document.uri` method. The form of those methods is
``verb_uri``.

.. code-block:: python

    class Article(Document):
        id = fields.NumberField()

        def post_uri(self):
            # Use this method for POST requests
            return "http://post_location"

        def uri(self):
            # The default uri location for all other HTTP requests
            return "http://location"

Django Backend
==============

The django backend stores and retrieves resources using the `Django ORM`_.

.. _`Django ORM`: http://djangoproject.org

Writing your own Backends
=========================

Its very easy to implement your own backends to use with docar. A backend is
always a class. If you want to use the builtin backend manager, this class has
to inherit from ``docar.backends.Backend`` and must be imported before using
it. But you can supply the class itself to the document too. The following
example shows the two possible ways to supply a document with a backend:

.. code-block:: python

    class MyBackend(Backend):
        backend_type = 'mybackend'

    # Supply a class as a backend
    class MyDocument(Document):
        class Meta:
            backend_type = MyBackend

    # Reference the backend by name
    class MyDocument(Document):
        class Meta:
            backend_type = 'mybackend'

A backend must implement the following interface:

- ``fetch(doc, *args, **kwargs)``
- ``save(doc, data, *args, **kwargs)``
- ``delete(doc, *args, **kwargs)``

eg:

.. code-block:: python

    from docar.backends import Backend

    class MyBackend(Backend):
        name = 'mybackend'

        def fetch(self, document, *args, **kwargs):
            pass

        def save(self, document, data, *args, **kwargs):
            pass

        def delete(self, document, *args, **kwargs):
            pass

``fetch``
---------

The first argument must be the document itself. You can use it to retrieve more
information about the fields if needed. ``*args`` and ``**kwargs`` are
additional parameters that can be consumed by the backend, eg: username and
password are optional arguments of the http backend. ``fetch`` *must* return
the document as a dict type.

``save``
--------

The first argument is again the document itself. The second argument is the
normalized data as a dict that should be saved. This method must implement the
logic to distinguish between an existing and a new document. The document class
itself has no knowledge about that.

``delete``
----------

The first argument is the document itself. This purges the mapped document from
the specified backend.
