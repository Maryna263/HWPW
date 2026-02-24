from mongoengine import Document, StringField, ListField, ReferenceField, CASCADE

class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()
    meta = {"collection": "authors"}

class Quote(Document):
    # Використовуємо ReferenceField для зберігання ObjectID автора
    author = ReferenceField(Author, reverse_delete_rule=CASCADE)
    tags = ListField(StringField())
    quote = StringField(required=True)
    meta = {"collection": "quotes"}