# 📘 PeerSphere — Developer Workbook

> **Version:** 1.0 | **Stack:** Flask · SQLite · Jinja2 · Bootstrap 5 · Docker

---

## 1. What is PeerSphere?

PeerSphere is a **campus social networking platform** where students, alumni, and mentors can connect, share posts, join communities, attend events, and directly message each other — all inside one web application.

---

## 2. Project Layout

```
peersphere/
├── backend/                  ← Flask application (all Python code)
│   ├── app/
│   │   ├── __init__.py       ← App factory (creates Flask app, registers extensions)
│   │   ├── models/           ← SQLAlchemy database models (tables)
│   │   ├── routes/           ← URL handlers (blueprints)
│   │   ├── services/         ← Business logic (recommendation engine etc.)
│   │   └── utils/            ← Helper utilities
│   ├── config.py             ← Configuration (secret key, DB URL, upload path)
│   ├── run.py                ← Entry point (starts Flask or Gunicorn)
│   └── instance/
│       └── peersphere.db     ← SQLite database file (auto-created)
│
├── frontend/
│   ├── templates/            ← Jinja2 HTML templates
│   │   ├── base.html         ← Master layout (navbar, toast, scripts)
│   │   ├── main/             ← Landing page + Dashboard
│   │   ├── auth/             ← Login + Register pages
│   │   ├── profile/          ← View + Edit profile
│   │   ├── feed/             ← Post feed
│   │   ├── communities/      ← Groups & communities
│   │   ├── events/           ← Campus events
│   │   ├── messages/         ← Direct messages
│   │   ├── mentors/          ← Mentor listings
│   │   └── search/           ← Search results
│   └── static/
│       ├── css/style.css     ← Complete design system (all UI styles)
│       ├── js/app.js         ← Global JavaScript (themes, toasts, stories)
│       ├── img/              ← Static assets (SVG avatars)
│       └── uploads/          ← User-uploaded files (profile pictures, post images)
│
├── Dockerfile                ← Container build instructions
├── docker-compose.yml        ← One-command local runner
├── docker-entrypoint.sh      ← Init DB → start server on container boot
├── requirements.txt          ← Python dependencies
└── .env                      ← Environment variables (secret key, DB URL)
```

---

## 3. Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Web Framework** | Flask 3.0 | Lightweight Python framework, easy routing via Blueprints |
| **Database ORM** | Flask-SQLAlchemy | Maps Python classes to database tables automatically |
| **Database** | SQLite (dev) | Zero-config, single file, ships with Python |
| **Authentication** | Flask-Login | Session management, `current_user`, `@login_required` |
| **Password Hashing** | Flask-Bcrypt | Secure bcrypt hashing (never store plain-text passwords) |
| **Forms & CSRF** | Flask-WTF | CSRF token on every form to prevent cross-site attacks |
| **DB Migrations** | Flask-Migrate (Alembic) | Evolve schema over time without losing data |
| **Templating** | Jinja2 (built into Flask) | Server-side HTML rendering with variables and loops |
| **Frontend CSS** | Vanilla CSS (custom design system) | Full control, no framework lock-in |
| **Frontend JS** | Vanilla JS (app.js) | Theme toggle, toasts, story modal, image preview |
| **UI Components** | Bootstrap 5 (grid only) | Responsive grid system + collapse/dropdown |
| **Icons** | Bootstrap Icons v1.11 | CDN-loaded SVG icon font |
| **Fonts** | Google Fonts (Plus Jakarta Sans, Inter) | Premium typography |
| **Image Handling** | Pillow (PIL) | Required for image processing |
| **Server (prod)** | Gunicorn | WSGI production server (multi-worker) |
| **Containerisation** | Docker + Docker Compose | Reproducible, one-command deployment |

---

## 4. How the App Works — Request Flow

```
Browser Request
    │
    ▼
Flask Router (run.py → create_app())
    │
    ├── Matches URL → Blueprint → Route function (routes/*.py)
    │       │
    │       ├── Queries database via SQLAlchemy model
    │       ├── Applies business logic (e.g. update streak)
    │       └── Calls render_template() with data
    │
    ▼
Jinja2 Template Engine
    │   ├── Extends base.html (navbar, toast container, scripts)
    │   ├── Fills {% block content %} with page HTML
    │   └── Renders {{ variables }} from Python
    │
    ▼
HTML Response → Browser renders page
    │
    └── Browser loads static files:
            ├── /static/css/style.css   (design system)
            ├── /static/js/app.js       (interactivity)
            └── /static/uploads/*.jpg   (user images)
```

---

## 5. Database Models (Tables)

| Model | File | What it stores |
|-------|------|---------------|
| `User` | `models/user.py` | Account info, bio, profile picture, streak, role |
| `Post` | `models/post.py` | Text posts, image URL, community link, poll flag |
| `Comment` | `models/post.py` | Comments on posts |
| `Like` | `models/post.py` | Which user liked which post |
| `Bookmark` | `models/post.py` | Saved posts per user |
| `Reaction` | `models/post.py` | Emoji reactions (❤️🔥👏🤯😂🎉) |
| `Community` | `models/community.py` | Group name, description, creator |
| `CommunityMember` | `models/community.py` | Many-to-many: user ↔ community |
| `Event` | `models/event.py` | Title, date, location, organiser |
| `EventAttendee` | `models/event.py` | Who is attending which event |
| `Message` | `models/message.py` | DMs between sender and receiver |
| `Mentor` | `models/mentor.py` | Mentor profile linked to a User |
| `Skill` | `models/skill.py` | Skill names |
| `UserSkill` | `models/skill.py` | Many-to-many: user ↔ skill |
| `Story` | `models/story.py` | 24-hour ephemeral stories with expiry |
| `Notification` | `models/notification.py` | In-app alerts per user |
| `ActivityLog` | `models/activity.py` | Audit log of user actions |

---

## 6. URL Routes (Blueprints)

| Blueprint | Prefix | Key Routes |
|-----------|--------|-----------|
| `main_bp` | `/` | `GET /` landing, `GET /dashboard` |
| `auth_bp` | `/` | `GET/POST /login`, `GET/POST /register`, `GET /logout` |
| `profile_bp` | `/profile` | `GET /profile/<id>`, `GET/POST /profile/edit` |
| `feed_bp` | `/feed` | `GET /feed/`, `POST /feed/create`, `POST /feed/<id>/like` |
| `communities_bp` | `/communities` | Index, detail, create, join |
| `events_bp` | `/events` | Index, detail, create, attend |
| `messages_bp` | `/messages` | Index, chat with user |
| `mentors_bp` | `/mentors` | Index, become mentor |
| `search_bp` | `/search` | `GET /search/?q=...` |
| `stories_bp` | `/stories` | Create story, view story |

---

## 7. Authentication Flow

```
1. User submits login form (email + password + csrf_token)
2. auth.py route: looks up User by email via SQLAlchemy
3. bcrypt.check_password_hash(user.password_hash, password)
4. If valid → user.update_streak() → login_user(user) → session cookie set
5. Flask-Login injects current_user into every template automatically
6. @login_required decorator redirects unauthenticated users to /login
```

---

## 8. File Upload Flow

```
User selects image in form
    │
    ▼
Form POST (multipart/form-data) → profile.edit route
    │
    ├── werkzeug.secure_filename() → sanitise filename
    ├── Save file to UPLOAD_FOLDER (frontend/static/uploads/)
    └── Store filename in user.profile_picture column
    
Template displays image:
    url_for('static', filename='uploads/' + user.profile_picture)
```

---

## 9. Design System (style.css)

The entire UI is driven by CSS custom properties (variables):

```css
:root[data-theme="light"] {
    --primary: #6C5CE7;        /* Purple brand colour */
    --secondary: #E84393;      /* Pink accent */
    --gradient-primary: linear-gradient(135deg, #6C5CE7, #E84393);
    --surface: #FFFFFF;        /* Card backgrounds */
    --background: #FAFAFA;     /* Page background */
    --text-main: #1A1A2E;      /* Primary text */
    --radius-lg: 16px;         /* Border radius tokens */
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.12);
}
```

Switching to dark mode just changes the same variable names via `data-theme="dark"`.

---

## 10. Running Locally (without Docker)

```bash
cd peersphere/backend
python -m venv ../venv
../venv/Scripts/activate        # Windows
pip install -r ../requirements.txt
python run.py
# → http://localhost:5000
```

## 11. Running with Docker (one command)

```bash
# First time (builds image):
docker-compose up --build

# Next time (faster, no rebuild):
docker-compose up

# Stop:
docker-compose down

# View logs:
docker-compose logs -f
```

> **Note:** Use `docker-compose` (with hyphen) — your Docker version is v28 with Compose v2.37.

---

## 12. 🔧 Future Work — Production Readiness

### 🔴 Critical (Must-do before going live)

| Task | Why |
|------|-----|
| **Switch SQLite → PostgreSQL** | SQLite can't handle concurrent writes; PostgreSQL scales to many users |
| **Move uploads to cloud (AWS S3 / Cloudflare R2)** | Container restarts wipe local files; cloud storage is persistent & CDN-cached |
| **Set a real `SECRET_KEY`** | Current key is a placeholder; a leaked key allows session forgery |
| **Disable `FLASK_DEBUG=1`** | Debug mode exposes an interactive console to anyone |
| **Add rate limiting** | Prevent brute-force login attacks (use `flask-limiter`) |
| **HTTPS / TLS** | Run behind nginx + Let's Encrypt certificate |

### 🟡 Important (Improves reliability)

| Task | Why |
|------|-----|
| **Add proper password reset** | Currently no "Forgot password" flow |
| **Email verification on register** | Prevents fake accounts |
| **Async task queue (Celery + Redis)** | Offload email sending, notifications |
| **Logging & error monitoring (Sentry)** | Know when things break in production |
| **Database backups** | Scheduled SQLite/Postgres dumps to cloud |
| **Input sanitisation** | Strip HTML from user content to prevent XSS |
| **Pagination** | Feed/communities load all rows; must paginate for performance |

### 🟢 Feature Roadmap

| Feature | Description |
|---------|------------|
| **OAuth login** | Google / Microsoft SSO (buttons already in the UI) |
| **Real-time notifications** | WebSockets via Flask-SocketIO |
| **Image compression** | Resize uploads with Pillow before saving |
| **Full-text search** | Use SQLite FTS5 or Postgres `tsvector` |
| **Mobile app** | React Native or Flutter consuming a Flask REST API |
| **Admin panel** | Moderate posts, manage users, view analytics |

---

*Generated: April 2026 | PeerSphere v1.0*
