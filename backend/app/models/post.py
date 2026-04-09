from app import db
from datetime import datetime


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    community_id = db.Column(db.Integer, db.ForeignKey('communities.id', ondelete='SET NULL'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    bookmarks = db.relationship('Bookmark', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    reactions = db.relationship('Reaction', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    poll = db.relationship('Poll', backref='post', uselist=False, cascade='all, delete-orphan')

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def bookmark_count(self):
        return self.bookmarks.count()

    def recent_comments(self, limit=5):
        return self.comments.order_by(Comment.created_at.desc()).limit(limit).all()

    def is_liked_by(self, user):
        return self.likes.filter_by(user_id=user.id).first() is not None

    def is_bookmarked_by(self, user):
        return self.bookmarks.filter_by(user_id=user.id).first() is not None

    def get_reactions_summary(self):
        """Get reaction counts grouped by emoji type."""
        from sqlalchemy import func
        results = db.session.query(
            Reaction.emoji, func.count(Reaction.id)
        ).filter_by(post_id=self.id).group_by(Reaction.emoji).all()
        return {emoji: count for emoji, count in results}

    def user_reaction(self, user):
        """Get the user's reaction emoji for this post, or None."""
        r = self.reactions.filter_by(user_id=user.id).first()
        return r.emoji if r else None

    def __repr__(self):
        return f'<Post {self.id}>'


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comment {self.id}>'


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_like'),)

    def __repr__(self):
        return f'<Like user={self.user_id} post={self.post_id}>'


class Bookmark(db.Model):
    __tablename__ = 'bookmarks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_bookmark'),)

    def __repr__(self):
        return f'<Bookmark user={self.user_id} post={self.post_id}>'


class Reaction(db.Model):
    __tablename__ = 'reactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False)
    emoji = db.Column(db.String(10), nullable=False, default='❤️')  # ❤️ 🔥 👏 🤯 😂 🎉
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='uq_user_post_reaction'),)

    def __repr__(self):
        return f'<Reaction user={self.user_id} emoji={self.emoji}>'


class Poll(db.Model):
    __tablename__ = 'polls'

    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, unique=True)
    question = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)

    options = db.relationship('PollOption', backref='poll', lazy='dynamic', cascade='all, delete-orphan')

    def total_votes(self):
        return sum(o.vote_count() for o in self.options.all())

    def has_voted(self, user):
        for option in self.options.all():
            if option.votes.filter_by(user_id=user.id).first():
                return True
        return False

    def user_vote(self, user):
        for option in self.options.all():
            vote = option.votes.filter_by(user_id=user.id).first()
            if vote:
                return option.id
        return None

    def __repr__(self):
        return f'<Poll {self.question[:30]}>'


class PollOption(db.Model):
    __tablename__ = 'poll_options'

    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('polls.id', ondelete='CASCADE'), nullable=False)
    text = db.Column(db.String(200), nullable=False)

    votes = db.relationship('PollVote', backref='option', lazy='dynamic', cascade='all, delete-orphan')

    def vote_count(self):
        return self.votes.count()

    def percentage(self):
        total = self.poll.total_votes()
        if total == 0:
            return 0
        return round((self.vote_count() / total) * 100)

    def __repr__(self):
        return f'<PollOption {self.text}>'


class PollVote(db.Model):
    __tablename__ = 'poll_votes'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    option_id = db.Column(db.Integer, db.ForeignKey('poll_options.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'option_id', name='uq_user_poll_vote'),)

    def __repr__(self):
        return f'<PollVote user={self.user_id} option={self.option_id}>'
