from peewee import CharField, BigIntegerField, DateTimeField, BooleanField
from datetime import datetime
from ..connect import db, BaseModel


class Users (BaseModel):
   id=BigIntegerField(primary_key=True)
   username = CharField(default=None, null=True)
   language = CharField(default='en')
   role=CharField(default='user')
   alert = BooleanField(default=True)
   created_at = DateTimeField(default=lambda: datetime.utcnow())

db.create_tables([Users])