from app import db


class Skill(db.Model):
    __tablename__ = 'skills'

    id = db.Column(db.Integer, primary_key=True)
    skill_name = db.Column(db.String(100), unique=True, nullable=False)

    users = db.relationship('UserSkill', backref='skill', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Skill {self.skill_name}>'


class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id', ondelete='CASCADE'), nullable=False, index=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill'),)

    def __repr__(self):
        return f'<UserSkill user={self.user_id} skill={self.skill_id}>'
