from wxcloudrun import db
from datetime import datetime

class Activity(db.Model):
    __tablename__ = 'activities'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    activity_date = db.Column(db.Date, nullable=False)
    location_name = db.Column(db.String(255))
    location_latitude = db.Column(db.Numeric(10, 8))
    location_longitude = db.Column(db.Numeric(11, 8))
    organizer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    status = db.Column(db.Enum('planning', 'confirmed', 'ongoing', 'completed', 'cancelled'), 
                      default='planning')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class ActivityParticipant(db.Model):
    __tablename__ = 'activity_participants'
    
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'), primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True) 
    role = db.Column(db.Enum('organizer', 'participant', 'invited'), default='participant')
    status = db.Column(db.Enum('confirmed', 'pending', 'declined'), default='pending')
    joined_at = db.Column(db.DateTime, default=datetime.now) 