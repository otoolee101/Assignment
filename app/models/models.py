from app.extensions import db
from flask_login import UserMixin

"""Creating database to store user login details"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    

"""Creating database to store the resolve ticket details in"""
class registration(db.Model):
    __tablename__ = 'registration'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    registration = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Integer,nullable=False)