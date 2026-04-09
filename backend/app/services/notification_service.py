from app import db
from app.models.notification import Notification


def create_notification(user_id, message, type='info', link=None):
    notification = Notification(
        user_id=user_id,
        message=message,
        type=type,
        link=link
    )
    db.session.add(notification)
    db.session.commit()
    return notification


def get_unread_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()


def mark_all_read(user_id):
    Notification.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
    db.session.commit()


def get_notifications(user_id, limit=20):
    return Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).limit(limit).all()
