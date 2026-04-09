from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.activity import ActivityLog

profile_bp = Blueprint('profile', __name__)


@profile_bp.route('/<int:user_id>')
@login_required
def view(user_id):
    user = User.query.get_or_404(user_id)
    skills = [us.skill for us in user.skills.all()]
    communities = [cm.community for cm in user.communities_joined.all()]
    recent_posts = user.posts.order_by(db.text('created_at DESC')).limit(5).all()
    
    saved_posts = []
    if current_user.id == user.id:
        from app.models.post import Bookmark
        saved_posts = [b.post for b in user.bookmarks.order_by(Bookmark.created_at.desc()).all()]

    return render_template('profile/view.html',
                           user=user,
                           skills=skills,
                           communities=communities,
                           recent_posts=recent_posts,
                           saved_posts=saved_posts)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    if request.method == 'POST':
        current_user.name = request.form.get('name', current_user.name).strip()
        current_user.university = request.form.get('university', '').strip()
        current_user.department = request.form.get('department', '').strip()
        current_user.bio = request.form.get('bio', '').strip()

        grad_year = request.form.get('graduation_year', '')
        if grad_year:
            try:
                current_user.graduation_year = int(grad_year)
            except ValueError:
                pass

        # Handle profile picture upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename:
                import os
                from werkzeug.utils import secure_filename
                filename = secure_filename(f"user_{current_user.id}_{file.filename}")
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                current_user.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully! ✨', 'success')
        return redirect(url_for('profile.view', user_id=current_user.id))

    all_skills = Skill.query.order_by(Skill.skill_name).all()
    user_skill_ids = [us.skill_id for us in current_user.skills.all()]
    return render_template('profile/edit.html', all_skills=all_skills, user_skill_ids=user_skill_ids)


@profile_bp.route('/skills/add', methods=['POST'])
@login_required
def add_skill():
    skill_id = request.form.get('skill_id')
    new_skill_name = request.form.get('new_skill', '').strip()

    if new_skill_name:
        skill = Skill.query.filter_by(skill_name=new_skill_name).first()
        if not skill:
            skill = Skill(skill_name=new_skill_name)
            db.session.add(skill)
            db.session.commit()
        skill_id = skill.id

    if skill_id:
        existing = UserSkill.query.filter_by(user_id=current_user.id, skill_id=int(skill_id)).first()
        if not existing:
            user_skill = UserSkill(user_id=current_user.id, skill_id=int(skill_id))
            db.session.add(user_skill)
            db.session.commit()
            flash('Skill added! 💪', 'success')
        else:
            flash('You already have this skill.', 'info')

    return redirect(url_for('profile.edit'))


@profile_bp.route('/skills/remove/<int:skill_id>', methods=['POST'])
@login_required
def remove_skill(skill_id):
    user_skill = UserSkill.query.filter_by(user_id=current_user.id, skill_id=skill_id).first()
    if user_skill:
        db.session.delete(user_skill)
        db.session.commit()
        flash('Skill removed.', 'info')
    return redirect(url_for('profile.edit'))
