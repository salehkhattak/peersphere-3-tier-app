from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.mentor import Mentor
from app.models.user import User

mentors_bp = Blueprint('mentors', __name__)


@mentors_bp.route('/')
@login_required
def index():
    query = request.args.get('q', '')
    mentors_query = Mentor.query.join(User)

    if query:
        mentors_query = mentors_query.filter(
            db.or_(
                Mentor.expertise.ilike(f'%{query}%'),
                User.name.ilike(f'%{query}%')
            )
        )

    mentors = mentors_query.all()
    return render_template('mentors/index.html', mentors=mentors, query=query)


@mentors_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if current_user.role not in ['alumni', 'admin']:
        flash('Only alumni can register as mentors.', 'warning')
        return redirect(url_for('mentors.index'))

    existing = Mentor.query.filter_by(user_id=current_user.id).first()
    if existing:
        flash('You are already registered as a mentor.', 'info')
        return redirect(url_for('mentors.index'))

    if request.method == 'POST':
        expertise = request.form.get('expertise', '').strip()
        availability = request.form.get('availability', 'Available').strip()

        if not expertise:
            flash('Expertise is required.', 'danger')
            return render_template('mentors/register.html')

        mentor = Mentor(user_id=current_user.id, expertise=expertise, availability=availability)
        db.session.add(mentor)
        db.session.commit()
        flash('You are now a mentor! 🌟', 'success')
        return redirect(url_for('mentors.index'))

    return render_template('mentors/register.html')
