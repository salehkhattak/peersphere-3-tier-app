from app import db
from datetime import datetime


class Community(db.Model):
    __tablename__ = 'communities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, default='')
    banner_image = db.Column(db.String(300), default='community_default.png')
    requires_approval = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('CommunityMember', backref='community', lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='community', lazy='dynamic')

    def member_count(self):
        return self.members.count()

    def active_member_count(self):
        from sqlalchemy import not_
        return self.members.filter(not_(CommunityMember.role == 'pending')).count()

    def __repr__(self):
        return f'<Community {self.name}>'


class CommunityMember(db.Model):
    __tablename__ = 'community_members'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id', ondelete='CASCADE'), nullable=False, index=True)
    role = db.Column(db.String(20), default='member')  # admin, moderator, member
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'community_id', name='uq_community_member'),)

    def __repr__(self):
        return f'<CommunityMember user={self.user_id} community={self.community_id}>'
