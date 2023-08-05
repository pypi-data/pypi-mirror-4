from docar import fields, Document, Collection


### First define the document structure used in this example
class Category(Document):
    name = fields.StringField()

    class Meta:
        identifier = 'name'


class Editor(Document):
    id = fields.NumberField(default=1, render=False)
    name = fields.StringField()
    security_number = fields.StringField(read_only=True, optional=True)

    class Meta:
        context = ['context1']

    def uri(self):
        return 'editor-uri'


class Article(Document):
    id = fields.NumberField(default=1, render=False)
    slug = fields.StringField()
    title = fields.StringField()
    editor = fields.ForeignDocument(Editor)
    category = fields.ForeignDocument(Category, optional=True)

    def uri(self):
        return 'article-uri'


class Newspaper(Collection):
    document = Article

    def uri(self):
        return 'newpaper-uri'


class Publication(Document):
    newspaper = fields.CollectionField(Newspaper)


class Subscription(Collection):
    document = Publication


class Entrepeneur(Document):
    name = fields.StringField()
    cash = fields.NumberField(optional=True)
    subscriptions = fields.CollectionField(Subscription)

    class Meta:
        identifier = 'name'

    def uri(self):
        return 'entrepeneur-uri'


class Kiosk(Document):
    newspaper = fields.CollectionField(Newspaper)
    owner = fields.ForeignDocument(Entrepeneur)

    def uri(self):
        return 'kiosk-uri'


### Configure some factory functions, to produce reliable fixtures
def set_field(name, default, kwargs):
    return default if name not in kwargs else kwargs[name]


def editor_factory(**kwargs):
    editor = Editor({'name': set_field('name', 'Jules Vernes', kwargs)})
    return editor


def article_factory(**kwargs):
    article = Article({
        'slug': set_field('slug', 'article-slug', kwargs),
        'title': set_field('title', 'article title', kwargs),
        })
    article.editor = editor_factory()
    return article


def collection_factory(size=2):
    article1 = article_factory()
    article2 = article_factory(title='article 2 title')
    article3 = article_factory(title='article 3 title')
    article3.editor = editor_factory(name='H.G. Wells')

    collection = Newspaper()
    collection.add(article1)
    collection.add(article2)
    collection.add(article3)

    return collection
