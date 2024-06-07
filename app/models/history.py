from datetime import datetime
from . import db

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    uid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __init__(self, result, uid):
        self.result = result
        self.uid = uid
        self.date = datetime.utcnow()