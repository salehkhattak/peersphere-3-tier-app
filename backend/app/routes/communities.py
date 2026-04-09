from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.community import Community, CommunityMember
from app.models.post import Post
from app.models.activity import ActivityLog

communities_bp = Blueprint('communities', __name__)


@communities_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    query = request.args.get('q', '')

    communities_query = Community.query
    if query:
        communities_query = communities_query.filter(Community.name.ilike(f'%{query}%'))

    communities = communities_query.order_by(Community.created_at.desc()).paginate(page=page, per_page=12, error_out=False)

    # Get trending
    trending = db.session.query(
        Community, db.func.count(CommunityMember.id).label('cnt')
    ).join(CommunityMember).group_by(Community.id).order_by(db.text('cnt DESC')).limit(5).all()

    return render_template('communities/list.html',
                           communities=communities,
                           query=query,
                           trending=trending)


@communities_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()

        requires_approval = request.form.get('requires_approval') == 'on'

        if not name:
            flash('Community name is required.', 'danger')
            return render_template('communities/create.html')

        community = Community(name=name, description=description, requires_approval=requires_approval, created_by=current_user.id)
        db.session.add(community)
        db.session.commit()

        # Auto-join as admin
        member = CommunityMember(user_id=current_user.id, community_id=community.id, role='admin')
        db.session.add(member)

        activity = ActivityLog(user_id=current_user.id, action='Created community', target_type='community', target_id=community.id)
        db.session.add(activity)
        db.session.commit()

        flash(f'Community "{name}" created! 🎉', 'success')
        return redirect(url_for('communities.detail', community_id=community.id))

    return render_template('communities/create.html')


@communities_bp.route('/<int:community_id>')
@login_required
def detail(community_id):
    community = Community.query.get_or_404(community_id)
    is_member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    from sqlalchemy import not_
    members = [cm.user for cm in community.members.filter(not_(CommunityMember.role == 'pending')).limit(20).all()]
    posts = Post.query.filter_by(community_id=community_id).order_by(Post.created_at.desc()).limit(20).all()

    return render_template('communities/detail.html',
                           community=community,
                           is_member=is_member,
                           members=members,
                           posts=posts)


@communities_bp.route('/<int:community_id>/join', methods=['POST'])
@login_required
def join(community_id):
    community = Community.query.get_or_404(community_id)
    existing = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not existing:
        if community.requires_approval:
            member = CommunityMember(user_id=current_user.id, community_id=community_id, role='pending')
            db.session.add(member)
            db.session.commit()
            flash(f'Request to join {community.name} sent! Awaiting admin approval. ⏳', 'info')
        else:
            member = CommunityMember(user_id=current_user.id, community_id=community_id)
            db.session.add(member)

            activity = ActivityLog(user_id=current_user.id, action='Joined community', target_type='community', target_id=community_id)
            db.session.add(activity)
            db.session.commit()
            flash(f'You joined {community.name}! 🙌', 'success')
    return redirect(url_for('communities.detail', community_id=community_id))


@communities_bp.route('/<int:community_id>/leave', methods=['POST'])
@login_required
def leave(community_id):
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
        flash('You left the community.', 'info')
    return redirect(url_for('communities.detail', community_id=community_id))


@communities_bp.route('/<int:community_id>/manage_members')
@login_required
def manage_members(community_id):
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not member or member.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('communities.detail', community_id=community_id))
    
    members = CommunityMember.query.filter_by(community_id=community_id).all()
    return render_template('communities/manage_members.html', community=community, members=members)


@communities_bp.route('/<int:community_id>/promote/<int:user_id>', methods=['POST'])
@login_required
def promote_member(community_id, user_id):
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not member or member.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('communities.detail', community_id=community_id))
    
    target_member = CommunityMember.query.filter_by(user_id=user_id, community_id=community_id).first()
    if target_member and target_member.role == 'member':
        target_member.role = 'moderator'
        db.session.commit()
        flash(f'Promoted {target_member.user.name} to moderator.', 'success')
    return redirect(url_for('communities.manage_members', community_id=community_id))


@communities_bp.route('/<int:community_id>/demote/<int:user_id>', methods=['POST'])
@login_required
def demote_member(community_id, user_id):
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not member or member.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('communities.detail', community_id=community_id))
    
    target_member = CommunityMember.query.filter_by(user_id=user_id, community_id=community_id).first()
    if target_member and target_member.role == 'moderator':
        target_member.role = 'member'
        db.session.commit()
        flash(f'Demoted {target_member.user.name} to member.', 'success')
    return redirect(url_for('communities.manage_members', community_id=community_id))


@communities_bp.route('/<int:community_id>/remove_member/<int:user_id>', methods=['POST'])
@login_required
def remove_member(community_id, user_id):
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not member or member.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('communities.detail', community_id=community_id))
    
    target_member = CommunityMember.query.filter_by(user_id=user_id, community_id=community_id).first()
    if target_member and target_member.user_id != current_user.id:  # Can't remove self
        db.session.delete(target_member)
        db.session.commit()
        if target_member.role == 'pending':
            flash(f'Rejected join request from {target_member.user.name}.', 'info')
        else:
            flash(f'Removed {target_member.user.name} from community.', 'success')
    return redirect(url_for('communities.manage_members', community_id=community_id))

@communities_bp.route('/<int:community_id>/accept/<int:user_id>', methods=['POST'])
@login_required
def accept_member(community_id, user_id):
    community = Community.query.get_or_404(community_id)
    member = CommunityMember.query.filter_by(user_id=current_user.id, community_id=community_id).first()
    if not member or member.role != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('communities.detail', community_id=community_id))

    target_member = CommunityMember.query.filter_by(user_id=user_id, community_id=community_id).first()
    if target_member and target_member.role == 'pending':
        target_member.role = 'member'
        activity = ActivityLog(user_id=target_member.user_id, action='Joined community', target_type='community', target_id=community_id)
        db.session.add(activity)
        db.session.commit()
        flash(f'Accepted {target_member.user.name} into the community!', 'success')
    return redirect(url_for('communities.manage_members', community_id=community_id))

