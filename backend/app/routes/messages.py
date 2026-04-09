from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.message import Message
from app.models.user import User
from sqlalchemy import or_, and_, case

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/')
@login_required
def index():
    # Get unique conversations
    u1 = case((Message.sender_id > Message.receiver_id, Message.sender_id), else_=Message.receiver_id).label('u1')
    u2 = case((Message.sender_id < Message.receiver_id, Message.sender_id), else_=Message.receiver_id).label('u2')
    
    subq = db.session.query(
        u1, u2, db.func.max(Message.timestamp).label('last_time')
    ).filter(
        or_(Message.sender_id == current_user.id, Message.receiver_id == current_user.id)
    ).group_by('u1', 'u2').subquery()

    # Get latest messages per conversation
    conversations = []
    raw_convos = db.session.query(subq).order_by(subq.c.last_time.desc()).all()

    for conv in raw_convos:
        other_id = conv.u1 if conv.u2 == current_user.id else conv.u2
        other_user = User.query.get(other_id)
        last_msg = Message.query.filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.receiver_id == other_id),
                and_(Message.sender_id == other_id, Message.receiver_id == current_user.id)
            )
        ).order_by(Message.timestamp.desc()).first()

        unread = Message.query.filter_by(
            sender_id=other_id, receiver_id=current_user.id, is_read=False
        ).count()

        if other_user:
            conversations.append({
                'user': other_user,
                'last_message': last_msg,
                'unread': unread
            })

    return render_template('messages/index.html', conversations=conversations, active_chat=None, messages=[])


@messages_bp.route('/chat/<int:user_id>', methods=['GET', 'POST'])
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        text = request.form.get('message_text', '').strip()
        if text:
            msg = Message(sender_id=current_user.id, receiver_id=user_id, message_text=text)
            db.session.add(msg)
            db.session.commit()
        return redirect(url_for('messages.chat', user_id=user_id))

    # Mark messages as read
    Message.query.filter_by(sender_id=user_id, receiver_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()

    # Get conversation
    chat_messages = Message.query.filter(
        or_(
            and_(Message.sender_id == current_user.id, Message.receiver_id == user_id),
            and_(Message.sender_id == user_id, Message.receiver_id == current_user.id)
        )
    ).order_by(Message.timestamp.asc()).all()

    # Get conversations list for sidebar
    conversations = []
    sent_to = db.session.query(Message.receiver_id.distinct()).filter_by(sender_id=current_user.id).all()
    recv_from = db.session.query(Message.sender_id.distinct()).filter_by(receiver_id=current_user.id).all()
    user_ids = set([r[0] for r in sent_to] + [r[0] for r in recv_from])

    for uid in user_ids:
        u = User.query.get(uid)
        if u:
            last_msg = Message.query.filter(
                or_(
                    and_(Message.sender_id == current_user.id, Message.receiver_id == uid),
                    and_(Message.sender_id == uid, Message.receiver_id == current_user.id)
                )
            ).order_by(Message.timestamp.desc()).first()
            unread = Message.query.filter_by(sender_id=uid, receiver_id=current_user.id, is_read=False).count()
            conversations.append({'user': u, 'last_message': last_msg, 'unread': unread})

    conversations.sort(key=lambda x: x['last_message'].timestamp if x['last_message'] else '', reverse=True)

    return render_template('messages/index.html',
                           conversations=conversations,
                           active_chat=other_user,
                           messages=chat_messages)
