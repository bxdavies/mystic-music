from . import db
import datetime

class User(db.Document):
    id = db.StringField(required=True, primary_key=True, null=False)
    display_name = db.StringField(required=True, unique=True, max_length=32, null=False)
    created = db.DateTimeField(required=True, default=datetime.datetime.utcnow, null=False)
    last_login = db.DateTimeField(required=True, default=datetime.datetime.utcnow, null=False)
    songs = db.ListField()

class Groups(db.Document):
    id = db.IntField(required=True, primary_key=True, null=False)
    users = db.ListField()
