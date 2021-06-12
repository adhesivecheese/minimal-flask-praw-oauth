from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
	password = db.Column(db.String(100))
	name = db.Column(db.String(20))
	token = db.Column(db.String(1000))
	state = db.Column(db.String(1000))