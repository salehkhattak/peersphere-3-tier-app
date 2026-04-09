from app import db
from app.models.user import User
from app.models.skill import Skill, UserSkill
from app.models.community import Community, CommunityMember


def get_recommended_users(current_user, limit=6):
    """
    Recommend users based on:
    1. Shared skills
    2. Same department
    3. Same university
    """
    user_skill_ids = [us.skill_id for us in current_user.skills.all()]

    recommended = set()
    scores = {}

    if user_skill_ids:
        # Users with shared skills
        shared_skill_users = db.session.query(
            UserSkill.user_id,
            db.func.count(UserSkill.skill_id).label('shared_count')
        ).filter(
            UserSkill.skill_id.in_(user_skill_ids),
            UserSkill.user_id != current_user.id
        ).group_by(UserSkill.user_id).all()

        for uid, count in shared_skill_users:
            scores[uid] = scores.get(uid, 0) + count * 3  # skill match weight

    # Same department
    if current_user.department:
        dept_users = User.query.filter(
            User.department == current_user.department,
            User.id != current_user.id
        ).all()
        for u in dept_users:
            scores[u.id] = scores.get(u.id, 0) + 2

    # Same university
    if current_user.university:
        uni_users = User.query.filter(
            User.university == current_user.university,
            User.id != current_user.id
        ).all()
        for u in uni_users:
            scores[u.id] = scores.get(u.id, 0) + 1

    # Sort by score and return top users
    sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:limit]

    result = []
    for uid in sorted_ids:
        user = User.query.get(uid)
        if user:
            # Calculate match percentage
            max_score = (len(user_skill_ids) * 3) + 2 + 1 if user_skill_ids else 3
            match_pct = min(int((scores[uid] / max(max_score, 1)) * 100), 100)
            result.append({'user': user, 'match': match_pct, 'score': scores[uid]})

    return result


def get_recommended_communities(current_user, limit=6):
    """
    Recommend communities the user hasn't joined,
    based on communities that similar-skill users are in.
    """
    # Communities user already joined
    joined_ids = [cm.community_id for cm in current_user.communities_joined.all()]
    user_skill_ids = [us.skill_id for us in current_user.skills.all()]

    if not user_skill_ids:
        # Fallback: just return popular communities not joined
        popular = db.session.query(
            Community, db.func.count(CommunityMember.id).label('cnt')
        ).join(CommunityMember).filter(
            ~Community.id.in_(joined_ids) if joined_ids else True
        ).group_by(Community.id).order_by(db.text('cnt DESC')).limit(limit).all()
        return [{'community': c, 'match': 50} for c, cnt in popular]

    # Find users with similar skills
    similar_users = db.session.query(UserSkill.user_id).filter(
        UserSkill.skill_id.in_(user_skill_ids),
        UserSkill.user_id != current_user.id
    ).distinct().all()
    similar_user_ids = [u[0] for u in similar_users]

    if not similar_user_ids:
        popular = db.session.query(
            Community, db.func.count(CommunityMember.id).label('cnt')
        ).join(CommunityMember).filter(
            ~Community.id.in_(joined_ids) if joined_ids else True
        ).group_by(Community.id).order_by(db.text('cnt DESC')).limit(limit).all()
        return [{'community': c, 'match': 40} for c, cnt in popular]

    # Find communities those users are in
    community_scores = db.session.query(
        CommunityMember.community_id,
        db.func.count(CommunityMember.user_id).label('cnt')
    ).filter(
        CommunityMember.user_id.in_(similar_user_ids),
        ~CommunityMember.community_id.in_(joined_ids) if joined_ids else True
    ).group_by(CommunityMember.community_id).order_by(db.text('cnt DESC')).limit(limit).all()

    result = []
    for cid, cnt in community_scores:
        community = Community.query.get(cid)
        if community:
            match = min(int((cnt / max(len(similar_user_ids), 1)) * 100), 95)
            result.append({'community': community, 'match': match})

    return result
