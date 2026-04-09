from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.story import Story, StoryView
from datetime import datetime, timedelta

stories_bp = Blueprint('stories', __name__)


@stories_bp.route('/create', methods=['POST'])
@login_required
def create_story():
    text_content = request.form.get('text_content', '').strip()
    bg_gradient = request.form.get('bg_gradient', 'gradient-1')
    image_url = None

    # Handle image upload
    if 'story_image' in request.files:
        file = request.files['story_image']
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"story_{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_url = filename

    if not text_content and not image_url:
        flash('Story must have text or an image.', 'danger')
        return redirect(request.referrer or url_for('main.dashboard'))

    story = Story(
        user_id=current_user.id,
        text_content=text_content if text_content else None,
        image_url=image_url,
        bg_gradient=bg_gradient,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    db.session.add(story)
    db.session.commit()

    flash('Story added! ✨', 'success')
    return redirect(request.referrer or url_for('main.dashboard'))


@stories_bp.route('/<int:story_id>/view', methods=['POST'])
@login_required
def view_story(story_id):
    story = Story.query.get_or_404(story_id)

    if not story.is_viewed_by(current_user) and story.user_id != current_user.id:
        view = StoryView(user_id=current_user.id, story_id=story_id)
        db.session.add(view)
        db.session.commit()

    return jsonify({'success': True, 'views': story.view_count()})


@stories_bp.route('/<int:story_id>/delete', methods=['POST'])
@login_required
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    if story.user_id != current_user.id:
        flash('You cannot delete this story.', 'danger')
        return redirect(url_for('main.dashboard'))

    db.session.delete(story)
    db.session.commit()
    flash('Story deleted.', 'info')
    return redirect(url_for('main.dashboard'))
