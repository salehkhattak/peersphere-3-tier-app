from app import db
from datetime import datetime, timedelta


class Story(db.Model):
    __tablename__ = 'stories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    image_url = db.Column(db.String(300), nullable=True)
    text_content = db.Column(db.String(500), nullable=True)
    bg_gradient = db.Column(db.String(100), default='gradient-1')  # CSS class for background
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))

    views = db.relationship('StoryView', backref='story', lazy='dynamic', cascade='all, delete-orphan')

    def is_expired(self):
        return datetime.utcnow() > self.expires_at

    def view_count(self):
        return self.views.count()

    def is_viewed_by(self, user):
        return self.views.filter_by(user_id=user.id).first() is not None

    def __repr__(self):
        return f'<Story {self.id} by user {self.user_id}>'


class StoryView(db.Model):
    __tablename__ = 'story_views'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id', ondelete='CASCADE'), nullable=False)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'story_id', name='uq_user_story_view'),)

    def __repr__(self):
        return f'<StoryView user={self.user_id} story={self.story_id}>'
