from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from config import Config
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
import os

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()
socketio = SocketIO(cors_allowed_origins="*", manage_session=False)

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def create_app(config_class=Config):
    template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'templates')
    static_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend', 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    socketio.init_app(app)

    # Import models so they're registered with SQLAlchemy
    from app.models import user, skill, community, post, message, event, mentor, activity, notification, story

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.profile import profile_bp
    from app.routes.communities import communities_bp
    from app.routes.feed import feed_bp
    from app.routes.messages import messages_bp
    from app.routes.events import events_bp
    from app.routes.mentors import mentors_bp
    from app.routes.search import search_bp
    from app.routes.stories import stories_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(profile_bp, url_prefix='/profile')
    app.register_blueprint(communities_bp, url_prefix='/communities')
    app.register_blueprint(feed_bp, url_prefix='/feed')
    app.register_blueprint(messages_bp, url_prefix='/messages')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(mentors_bp, url_prefix='/mentors')
    app.register_blueprint(search_bp, url_prefix='/search')
    app.register_blueprint(stories_bp, url_prefix='/stories')

    os.makedirs(app.config.get('UPLOAD_FOLDER', 'app/static/uploads'), exist_ok=True)

    return app

# Store online users: {user_id: sid}
online_users = {}

def get_chat_room(user1_id, user2_id):
    """Return a consistent room name for two users."""
    return f"chat_{min(user1_id, user2_id)}_{max(user1_id, user2_id)}"

@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        online_users[current_user.id] = request.sid
        emit("user_online", {"user_id": current_user.id}, broadcast=True)

@socketio.on("join")
def handle_join(data):
    if not current_user.is_authenticated:
        return
    receiver_id = data.get("receiver_id")
    if receiver_id:
        room = get_chat_room(current_user.id, receiver_id)
        join_room(room)
        emit("user_status", {"user_id": current_user.id, "online": True}, room=room)

@socketio.on("send_message")
def handle_send_message(data):
    if not current_user.is_authenticated:
        return
    from app.models.message import Message
    receiver_id = data.get("receiver_id")
    message_text = data.get("message", "").strip()
    if not receiver_id or not message_text:
        return

    new_msg = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        message_text=message_text,
        timestamp=datetime.utcnow()
    )
    db.session.add(new_msg)
    db.session.commit()

    room = get_chat_room(current_user.id, receiver_id)
    message_data = {
        "id": new_msg.id,
        "sender_id": current_user.id,
        "message": message_text,
        "time": new_msg.timestamp.strftime("%I:%M %p"),
        "receiver_id": receiver_id
    }
    emit("receive_message", message_data, room=room)

@socketio.on("typing")
def handle_typing(data):
    if not current_user.is_authenticated:
        return
    receiver_id = data.get("receiver_id")
    if receiver_id:
        room = get_chat_room(current_user.id, receiver_id)
        emit("user_typing", {"user_id": current_user.id, "typing": data.get("typing", False)},
             room=room, include_self=False)

@socketio.on("disconnect")
def handle_disconnect():
    if current_user.is_authenticated:
        online_users.pop(current_user.id, None)
        emit("user_offline", {"user_id": current_user.id}, broadcast=True)