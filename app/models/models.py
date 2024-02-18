from app.extensions import db
from flask_login import UserMixin

"""Creating database to store user login details"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    registration = db.Column(db.String(9), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    role = db.Column(db.String(5), nullable=False, default='user')
    authorised =db.Column(db.String(1), nullable=False, default='N')
    failed_login_attempts = db.Column(db.Integer,nullable=False, default=0)
    reservation = db.relationship('reserve', backref='user')
    

"""Creating database to store the resolve ticket details in"""
class reserve(db.Model):
    __tablename__ = 'reserve'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(20), db.ForeignKey('user.id'), nullable=False)
    registration = db.Column(db.String(9), nullable=False)
    date = db.Column(db.Integer,nullable=False)
    cancelled = db.Column(db.String(1), nullable=False, default='N')
    
