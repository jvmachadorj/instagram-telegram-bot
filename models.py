import peewee
from peewee import *

db = peewee.SqliteDatabase('instagram.db')


class Image(Model):
    name = CharField()
    url = CharField()
    path = CharField()
    pixabay_id = IntegerField()
    created_at = DateTimeField()
    tags = CharField()
    status = CharField()
    caption = CharField()

    class Meta:
        database = db
