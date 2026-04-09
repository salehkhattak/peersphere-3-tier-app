from flask import Blueprint, render_template, request
from flask_login import login_required
from app import db
from app.models.user import User
from app.models.community import Community
from app.models.event import Event
from app.models.skill import Skill

search_bp = Blueprint('search', __name__)


@search_bp.route('/')
@login_required
def index():
    query = request.args.get('q', '').strip()
    tab = request.args.get('tab', 'people')

    users = []
    communities = []
    events = []
    skills = []

    if query:
        users = User.query.filter(
            db.or_(
                User.name.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
                User.university.ilike(f'%{query}%'),
                User.department.ilike(f'%{query}%')
            )
        ).limit(20).all()

        communities = Community.query.filter(
            db.or_(
                Community.name.ilike(f'%{query}%'),
                Community.description.ilike(f'%{query}%')
            )
        ).limit(20).all()

        events = Event.query.filter(
            db.or_(
                Event.title.ilike(f'%{query}%'),
                Event.description.ilike(f'%{query}%')
            )
        ).limit(20).all()

        skills = Skill.query.filter(Skill.skill_name.ilike(f'%{query}%')).limit(20).all()

    return render_template('search/results.html',
                           query=query,
                           tab=tab,
                           users=users,
                           communities=communities,
                           events=events,
                           skills=skills)
