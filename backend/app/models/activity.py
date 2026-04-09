from app import db
from datetime import datetime


class ActivityLog(db.Model):
    __tablename__ = 'activity_log'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    action = db.Column(db.String(200), nullable=False)
    target_type = db.Column(db.String(50), nullable=True)  # community, event, post, etc.
    target_id = db.Column(db.Integer, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<ActivityLog {self.user_id}: {self.action}>'
