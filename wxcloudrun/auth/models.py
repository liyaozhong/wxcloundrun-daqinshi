from datetime import datetime
from wxcloudrun import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    openid = db.Column(db.String(100), unique=True, nullable=False)
    nickname = db.Column(db.String(50))
    avatar_url = db.Column(db.String(255))
    is_authorized = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)