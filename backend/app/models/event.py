from app import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(300), default='')
    event_type = db.Column(db.String(50), default='general')  # hackathon, workshop, seminar, meetup
    banner_image = db.Column(db.String(300), default='event_default.png')
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendees = db.relationship('EventAttendee', backref='event', lazy='dynamic', cascade='all, delete-orphan')

    def attendee_count(self):
        return self.attendees.count()

    def is_attending(self, user):
        return self.attendees.filter_by(user_id=user.id).first() is not None

    def __repr__(self):
        return f'<Event {self.title}>'


class EventAttendee(db.Model):
    __tablename__ = 'event_attendees'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'event_id', name='uq_event_attendee'),)

    def __repr__(self):
        return f'<EventAttendee user={self.user_id} event={self.event_id}>'
