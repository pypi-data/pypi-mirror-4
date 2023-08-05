.. python-docar documentation master file, created by
   sphinx-quickstart on Sat Dec 17 18:44:13 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

========================================
Welcome to python-docar's documentation!
========================================

A lot of web services provide nowadays a REST interface and clients can
communicate and manipulate state on the server by exchanging messages.
``python-docar`` provides a declarative style of defining those messages as
documents, and makes it possible to resue the definitions on the server as well
as on the client side.

A document maps to a resource, whereas it doesn't matter how this resource is
stored. ``python-docar`` implements at the moment a backend for django models
and a backend for a http endpoint. A `MongoDB backend`_ is in the making.

* Each message is declared as a python class that subclasses
  :class:`docar.Document`.
* Each attribute of the document represents one field in the message.
* Other documents can be referenced and handled inline.
* More than one document of the same type can be managed in collections.
* You can reuse the same document declarations and only replace the backend.

.. _`MongoDB backend`: https://github.com/crito/docar-backend-mongodb

A quick example
===============

.. code-block:: python

    >>> # The document declaration
    >>> from docar import Document, fields
    >>> from docar.serializers import JsonSerializer, DropinJsonSerializer
    >>> from djangoproject.newspaper import ArticleModel

    >>> class Article(Document):
    ...     id = fields.NumberField()
    ...     name = fields.StringField()
    ...
    ...     class Meta:
    ...         backend_type = 'django'
    ...         model = ArticleModel

    >>> # A server example
    >>> article = Article({'id': 1})
    >>> article.fetch()  # Fetch this document from the backend

    >>> # The DropinJsonSerializer is an old format I keep for compatibility
    >>> # issues for an project of mine.
    >>> DropinJsonSerializer.dump(article)
    {
        "id": 1,
        "name": "Headline",
        "link": {
            "rel": "self",
            "href": "http://example.org/article/1/"
        }
    }

    >>> # There is also a simple json serializer available.
    >>> # The following line is the same as json.dumps(article.render())
    >>> JsonSerializer.dump(article)
    {
        "id": 1,
        "name": "Headline"
    }

    >>> article.headline = "Another Headline"
    >>> article.save()  # Save the document to the backend model
    >>> DropinJsonSerializer.dump(article)
    {
        "id": 1,
        "name": "Another Headline",
        "link": {
            "rel": "self",
            "href": "http://example.org/article/1/"
        }
    }

    >>> # A client example taling to a remote API endpoint
    >>> article = Article()
    >>> article.name = "Next Headline"
    >>> article.save(username='user', password='pass')

    >>> # You can also declare a collection of documents
    >>> from docar import Collection
    >>> class NewsPaper(Collection):
    ...     document = Article

    >>> newspaper = NewsPaper()
    >>> newspaper.add(article)
    >>> DropinJsonSerializer.dump(article)
    [{
        "id": 1,
        "headline": "Headline"
        "link": {
            "rel": "self",
            "href": "http://example.org/article/1/"
        }
    }]

All documents inherit from the :class:`docar.Document` class. It acts as a
representation of a resource. A resource maps to a datastructure that is stored
in a backend, see the section about `Backends`_ for more information. Each
attribute of the document maps to a field of the resource in the backend.

.. toctree::
    :maxdepth: 1

    documents
    fields
    mapping_fields
    backends

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

