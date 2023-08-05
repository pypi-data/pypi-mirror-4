from .documents import Document
from .exceptions import CollectionNotBound


class Collection(object):
    """A collection is a container for a list of documents.

    In JSON terms this would be the structural datatype ``Array``. It provides
    methods to manipulate the collection. The collection itself is stored as a
    list. A collection always has to be mapped to a document. You can do hat by
    declaring the ``document`` class variable upon declaration of this class.

    Upon instantiation you can provide a list of documents to add to the
    collection set.

    :param documents: A list of documents.
    :type documents: Document

    """
    document = None
    _bound = False
    _context = {}

    def __init__(self, documents=None):
        if not self.document:
            # A collection must declared for a document
            raise CollectionNotBound

        self.collection_set = []
        if documents:
            # Add the supplied documents to the collection
            for doc in documents:
                self.add(doc)

    def from_dict(self, data):
        """Populate a collection from a dictionary.

        :param data: The data to populate the collection.
        :type data: list

        """
        if not isinstance(data, list):
            return
        for item in data:
            document = self.document(item)
            self.add(document)

    def to_dict(self):
        """Serialize the collection into a dictionary."""
        return [document.to_dict() for document in self.collection_set]

    def add(self, doc):
        """Add a document to the collection.

        :param doc: The document to add to the collection.
        :type doc: Document

        """
        if not isinstance(doc, Document):
            # we only add real documents to the collection set
            return
        else:
            # Append the document
            self.collection_set.append(doc)
            self.bound = True

    def delete(self, identifier):
        """Delete a document from the collection.

        :param identifier: Specify identifier state using a dict.
        :type identifier: dict

        """
        new_collection = []
        for doc in self.collection_set:
            doc_id = doc._identifier_state()
            for k, v in identifier.iteritems():
                if v != doc_id[k]:
                    new_collection.append(doc)

        self.collection_set = new_collection
        if len(self.collection_set) < 1:
            self.bound = False

    def render(self):
        """Normalize the collection when rendering."""
        return [document.render() for document in self.collection_set]

    # FIXME: This should move into the backend
    def _from_queryset(self, qs):
        for model in qs:
            doc = self.document()
            doc._from_model(model)
            self.add(doc)
