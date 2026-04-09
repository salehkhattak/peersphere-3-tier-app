from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db, bcrypt
from app.models.user import User
from app.models.activity import ActivityLog

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', 'student')
        university = request.form.get('university', '').strip()
        department = request.form.get('department', '').strip()
        grad_year = request.form.get('graduation_year', None)

        # Validation
        if not name or not email or not password:
            flash('Please fill in all required fields.', 'danger')
            return render_template('auth/register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Try logging in!', 'danger')
            return render_template('auth/register.html')

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(
            name=name,
            email=email,
            password_hash=hashed_pw,
            role=role,
            university=university,
            department=department,
            graduation_year=int(grad_year) if grad_year and grad_year.isdigit() else None,
            streak_count=1
        )
        db.session.add(user)
        db.session.commit()

        # Log activity
        activity = ActivityLog(user_id=user.id, action='Account created', target_type='user', target_id=user.id)
        db.session.add(activity)
        db.session.commit()

        login_user(user)
        flash('Welcome to PeerSphere! 🎉', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            user.update_streak()
            db.session.commit()
            login_user(user, remember=request.form.get('remember'))
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.name.split()[0]}! 👋', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.landing'))
