from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models.post import Post
from app.models.community import Community, CommunityMember
from app.models.event import Event
from app.models.notification import Notification
from app.models.story import Story
from app.services.recommendation import get_recommended_users, get_recommended_communities
from datetime import datetime

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('main/landing.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Update streak on visit
    current_user.update_streak()
    db.session.commit()

    # Get user's communities and recent posts from those communities
    communities = current_user.communities
    community_ids = [c.id for c in communities]

    posts = Post.query.filter(
        (Post.community_id.in_(community_ids)) | (Post.user_id == current_user.id)
    ).order_by(Post.created_at.desc()).limit(10).all()

    unread_notifications = current_user.notifications.filter_by(is_read=False).all()
    trending_communities = Community.query.limit(5).all()

    # Get upcoming events
    upcoming_events = Event.query.filter(
        Event.date >= datetime.utcnow()
    ).order_by(Event.date.asc()).limit(5).all()

    # Get active stories (not expired)
    active_stories = Story.query.filter(
        Story.expires_at > datetime.utcnow()
    ).order_by(Story.created_at.desc()).all()

    # Group stories by user
    story_users = {}
    for story in active_stories:
        if story.user_id not in story_users:
            story_users[story.user_id] = {
                'user': story.author,
                'stories': [],
                'has_unviewed': False
            }
        story_users[story.user_id]['stories'].append(story)
        if not story.is_viewed_by(current_user):
            story_users[story.user_id]['has_unviewed'] = True

    return render_template('main/dashboard.html',
                           posts=posts,
                           unread_notifications=unread_notifications,
                           trending_communities=trending_communities,
                           upcoming_events=upcoming_events,
                           story_users=story_users)
