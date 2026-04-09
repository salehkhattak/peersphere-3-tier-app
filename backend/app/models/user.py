from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # student, alumni, admin
    university = db.Column(db.String(200), default='')
    department = db.Column(db.String(200), default='')
    graduation_year = db.Column(db.Integer, nullable=True)
    profile_picture = db.Column(db.String(300), default='default.png')
    bio = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Premium fields
    streak_count = db.Column(db.Integer, default=0)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)

    # Relationships
    skills = db.relationship('UserSkill', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    communities = db.relationship('Community', secondary='community_members', backref='members_list')
    communities_joined = db.relationship('CommunityMember', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    communities_created = db.relationship('Community', backref='creator', lazy='dynamic')
    sent_messages = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy='dynamic')
    events_created = db.relationship('Event', backref='organizer', lazy='dynamic')
    events_attending = db.relationship('EventAttendee', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    mentor_profile = db.relationship('Mentor', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('ActivityLog', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    stories = db.relationship('Story', backref='author', lazy='dynamic', cascade='all, delete-orphan')
    poll_votes = db.relationship('PollVote', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def username(self):
        """Generate username from email."""
        return self.email.split('@')[0] if self.email else self.name.lower().replace(' ', '')

    def get_skill_names(self):
        from app.models.skill import Skill, UserSkill
        return [us.skill.skill_name for us in self.skills.all()]

    def update_streak(self):
        """Update login streak."""
        from datetime import timedelta
        now = datetime.utcnow()
        if self.last_active:
            diff = (now.date() - self.last_active.date()).days
            if diff == 1:
                self.streak_count += 1
            elif diff > 1:
                self.streak_count = 1
        else:
            self.streak_count = 1
        self.last_active = now

    def profile_completion(self):
        fields = [self.name, self.email, self.university, self.department, self.bio, self.profile_picture != 'default.png']
        filled = sum(1 for f in fields if f)
        skill_count = self.skills.count()
        if skill_count > 0:
            filled += 1
        total = len(fields) + 1  # +1 for skills
        return int((filled / total) * 100)

    def __repr__(self):
        return f'<User {self.name}>'
