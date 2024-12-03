from datetime import datetime
from wxcloudrun import db

class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.String(255), nullable=False)  # 云存储文件ID
    type = db.Column(db.String(10), nullable=False)  # image/video
    tags = db.Column(db.JSON, nullable=False, default=list)  # 标签数组
    favorites = db.Column(db.JSON, nullable=False, default=list)  # 收藏用户ID数组
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 