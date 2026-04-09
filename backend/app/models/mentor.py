from app import db


class Mentor(db.Model):
    __tablename__ = 'mentors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    expertise = db.Column(db.String(300), nullable=False)
    availability = db.Column(db.String(200), default='Available')
    max_mentees = db.Column(db.Integer, default=5)

    def __repr__(self):
        return f'<Mentor user={self.user_id}>'
