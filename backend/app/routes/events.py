from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.event import Event, EventAttendee
from app.models.activity import ActivityLog
from datetime import datetime

events_bp = Blueprint('events', __name__)


@events_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'upcoming')

    if filter_type == 'past':
        events = Event.query.filter(Event.date < datetime.utcnow()).order_by(Event.date.desc()).paginate(page=page, per_page=12, error_out=False)
    elif filter_type == 'my':
        event_ids = [ea.event_id for ea in EventAttendee.query.filter_by(user_id=current_user.id).all()]
        events = Event.query.filter(Event.id.in_(event_ids)).order_by(Event.date.desc()).paginate(page=page, per_page=12, error_out=False)
    else:
        events = Event.query.filter(Event.date >= datetime.utcnow()).order_by(Event.date.asc()).paginate(page=page, per_page=12, error_out=False)

    return render_template('events/index.html', events=events, filter_type=filter_type)


@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '')
        location = request.form.get('location', '').strip()
        event_type = request.form.get('event_type', 'general')

        if not title or not date_str:
            flash('Title and date are required.', 'danger')
            return render_template('events/create.html')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('events/create.html')

        event = Event(
            title=title,
            description=description,
            date=date,
            location=location,
            event_type=event_type,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        # Auto-attend
        attendee = EventAttendee(user_id=current_user.id, event_id=event.id)
        db.session.add(attendee)

        activity = ActivityLog(user_id=current_user.id, action='Created event', target_type='event', target_id=event.id)
        db.session.add(activity)
        db.session.commit()

        flash(f'Event "{title}" created! 🎊', 'success')
        return redirect(url_for('events.detail', event_id=event.id))

    return render_template('events/create.html')


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    event = Event.query.get_or_404(event_id)
    is_attending = EventAttendee.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    attendees = [ea.user for ea in event.attendees.limit(20).all()]
    return render_template('events/detail.html', event=event, is_attending=is_attending, attendees=attendees)


@events_bp.route('/<int:event_id>/join', methods=['POST'])
@login_required
def join(event_id):
    event = Event.query.get_or_404(event_id)
    existing = EventAttendee.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if not existing:
        attendee = EventAttendee(user_id=current_user.id, event_id=event_id)
        db.session.add(attendee)

        activity = ActivityLog(user_id=current_user.id, action='Joined event', target_type='event', target_id=event_id)
        db.session.add(activity)
        db.session.commit()
        flash(f'You are attending {event.title}! 🎉', 'success')
    return redirect(url_for('events.detail', event_id=event_id))


@events_bp.route('/<int:event_id>/leave', methods=['POST'])
@login_required
def leave(event_id):
    attendee = EventAttendee.query.filter_by(user_id=current_user.id, event_id=event_id).first()
    if attendee:
        db.session.delete(attendee)
        db.session.commit()
        flash('You left the event.', 'info')
    return redirect(url_for('events.detail', event_id=event_id))
