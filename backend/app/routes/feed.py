from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.post import Post, Comment, Like, Bookmark, Reaction, Poll, PollOption, PollVote
from app.models.notification import Notification
from app.models.activity import ActivityLog
from app.models.story import Story
from datetime import datetime

feed_bp = Blueprint('feed', __name__)


@feed_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=15, error_out=False)

    # Get active stories
    active_stories = Story.query.filter(
        Story.expires_at > datetime.utcnow()
    ).order_by(Story.created_at.desc()).all()

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

    return render_template('feed/index.html', posts=posts, story_users=story_users)


@feed_bp.route('/create', methods=['POST'])
@login_required
def create_post():
    content = request.form.get('content', '').strip()
    community_id = request.form.get('community_id', None, type=int)

    if not content:
        flash('Post content cannot be empty.', 'danger')
        return redirect(request.referrer or url_for('feed.index'))

    post = Post(user_id=current_user.id, content=content, community_id=community_id)

    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename:
            import os
            from werkzeug.utils import secure_filename
            filename = secure_filename(f"post_{current_user.id}_{file.filename}")
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            post.image_url = filename

    db.session.add(post)
    db.session.flush()  # Get post.id for poll

    # Handle poll creation
    poll_question = request.form.get('poll_question', '').strip()
    poll_options = request.form.getlist('poll_options[]')
    poll_options = [o.strip() for o in poll_options if o.strip()]

    if poll_question and len(poll_options) >= 2:
        poll = Poll(post_id=post.id, question=poll_question)
        db.session.add(poll)
        db.session.flush()
        for option_text in poll_options:
            option = PollOption(poll_id=poll.id, text=option_text)
            db.session.add(option)

    db.session.commit()

    flash('Post created! 📝', 'success')
    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)

        if post.user_id != current_user.id:
            notification = Notification(
                user_id=post.user_id,
                message=f'{current_user.name} liked your post',
                type='like',
                link=url_for('feed.index')
            )
            db.session.add(notification)

        db.session.commit()
        liked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'liked': liked, 'count': post.like_count()})

    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    post = Post.query.get_or_404(post_id)
    comment_text = request.form.get('comment_text', '').strip()

    if not comment_text:
        flash('Comment cannot be empty.', 'danger')
        return redirect(request.referrer or url_for('feed.index'))

    comment = Comment(user_id=current_user.id, post_id=post_id, comment_text=comment_text)
    db.session.add(comment)

    if post.user_id != current_user.id:
        notification = Notification(
            user_id=post.user_id,
            message=f'{current_user.name} commented on your post',
            type='comment',
            link=url_for('feed.index')
        )
        db.session.add(notification)

    db.session.commit()
    flash('Comment added! 💬', 'success')
    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/<int:post_id>/bookmark', methods=['POST'])
@login_required
def bookmark_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing = Bookmark.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        bookmarked = False
    else:
        bookmark = Bookmark(user_id=current_user.id, post_id=post_id)
        db.session.add(bookmark)
        db.session.commit()
        bookmarked = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'bookmarked': bookmarked})

    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/<int:post_id>/react', methods=['POST'])
@login_required
def react_post(post_id):
    post = Post.query.get_or_404(post_id)
    emoji = request.form.get('emoji', '❤️')

    valid_emojis = ['❤️', '🔥', '👏', '🤯', '😂', '🎉']
    if emoji not in valid_emojis:
        emoji = '❤️'

    existing = Reaction.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if existing:
        if existing.emoji == emoji:
            db.session.delete(existing)
            db.session.commit()
            reacted = False
            current_emoji = None
        else:
            existing.emoji = emoji
            db.session.commit()
            reacted = True
            current_emoji = emoji
    else:
        reaction = Reaction(user_id=current_user.id, post_id=post_id, emoji=emoji)
        db.session.add(reaction)

        if post.user_id != current_user.id:
            notification = Notification(
                user_id=post.user_id,
                message=f'{current_user.name} reacted {emoji} to your post',
                type='reaction',
                link=url_for('feed.index')
            )
            db.session.add(notification)

        db.session.commit()
        reacted = True
        current_emoji = emoji

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'reacted': reacted,
            'emoji': current_emoji,
            'summary': post.get_reactions_summary()
        })

    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/<int:post_id>/poll/vote', methods=['POST'])
@login_required
def vote_poll(post_id):
    post = Post.query.get_or_404(post_id)
    if not post.poll:
        flash('No poll found.', 'danger')
        return redirect(request.referrer or url_for('feed.index'))

    option_id = request.form.get('option_id', type=int)
    option = PollOption.query.get_or_404(option_id)

    if option.poll_id != post.poll.id:
        flash('Invalid poll option.', 'danger')
        return redirect(request.referrer or url_for('feed.index'))

    if post.poll.has_voted(current_user):
        flash('You already voted!', 'warning')
        return redirect(request.referrer or url_for('feed.index'))

    vote = PollVote(user_id=current_user.id, option_id=option_id)
    db.session.add(vote)
    db.session.commit()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        results = {}
        for opt in post.poll.options.all():
            results[opt.id] = {'text': opt.text, 'votes': opt.vote_count(), 'percentage': opt.percentage()}
        return jsonify({
            'success': True,
            'total_votes': post.poll.total_votes(),
            'results': results
        })

    flash('Vote recorded! 🗳️', 'success')
    return redirect(request.referrer or url_for('feed.index'))


@feed_bp.route('/api/posts')
@login_required
def api_posts():
    """Infinite scroll JSON endpoint."""
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=10, error_out=False)

    posts_data = []
    for post in posts.items:
        posts_data.append({
            'id': post.id,
            'author': {
                'id': post.author.id,
                'name': post.author.name,
                'username': post.author.username,
                'profile_picture': post.author.profile_picture,
                'is_verified': post.author.is_verified,
            },
            'content': post.content,
            'image_url': post.image_url,
            'created_at': post.created_at.strftime('%B %d, %Y'),
            'like_count': post.like_count(),
            'comment_count': post.comment_count(),
            'is_liked': post.is_liked_by(current_user),
            'is_bookmarked': post.is_bookmarked_by(current_user),
            'reactions': post.get_reactions_summary(),
            'user_reaction': post.user_reaction(current_user),
        })

    return jsonify({
        'posts': posts_data,
        'has_next': posts.has_next,
        'page': posts.page
    })


@feed_bp.route('/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        flash('You cannot delete this post.', 'danger')
        return redirect(url_for('feed.index'))

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'info')
    return redirect(url_for('feed.index'))
