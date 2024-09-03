from sqlalchemy_serializer import SerializerMixin
from config import db


class User(db.Model,SerializerMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String,nullable=False)
    phone_number = db.Column(db.String,nullable = False)
    identity = db.Column(db.String,nullable = False)
    profile_photo = db.Column(db.String,nullable = True)

