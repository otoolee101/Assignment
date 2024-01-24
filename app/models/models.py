from app.extensions import db
from flask_login import UserMixin

"""Creating database to store user login details"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    tickets = db.relationship('ticket', backref='user')
    contact = db.relationship('contact', backref='user')