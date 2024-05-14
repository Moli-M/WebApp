from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(50), unique=True, nullable=False)
    date = db.Column(db.String(100), nullable=False)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    