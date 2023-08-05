Backends
========

The backends are the real meat of the documents. Where the document defines what
you can do, the backends implement the how of it. Documents and backends use
dictionary to communicate to each other. A backend expects a dictionary
representation of the document, applies it as needed, and returns the resource
as a dictionary again. Each backend must implement the following methods:

``fetch``
  Fetch the resource from the underlying backend. Returns a dictionary.

``save``
  Save the document to the resource in the underlying backend. Expects a
  dictionary representation of the document.

``delete``
  Delete the resource from the underlying backend.

HTTP Backend
------------

The HTTP backend uses the ``requests`` library to communicate to remote
backends over HTTP. It assumes currently JSON as exchange protocol. The
document methods map the following way to the HTTP backend:

- :meth:`~Document.fetch` --> HTTP GET
- :meth:`~Document.save` --> HTTP POST (on create)
- :meth:`~Document.save` --> HTTP PUT (on update)
- :meth:`~Document.delete` --> HTTP DELET

uri methods
~~~~~~~~~~~

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
--------------

The django backend stores and retrieves resources using the `Django ORM`_.

.. _`Django ORM`: http://djangoproject.org
