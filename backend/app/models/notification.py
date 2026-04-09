from app import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), default='info')  # info, like, comment, follow, event, community
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f'<Notification {self.user_id}: {self.message[:30]}>'
