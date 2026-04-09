# PeerSphere Walkthrough

## Overview

PeerSphere is a full-stack university networking platform designed to connect students, alumni, and mentors. It functions as a specialized social network tailored for university ecosystems, featuring skill-based matchmaking, communities, event management, and mentorship. The application is built using a modern Python/Flask stack with a premium, responsive glassmorphism UI.

## Architecture

The project follows a modular Flask pattern, ensuring maintainability and scalability:

*   **[app/](file:///d:/peersphere/app/__init__.py#19-59)**: The main application package.
    *   **`models/`**: SQLAlchemy ORM models ([user.py](file:///d:/peersphere/app/models/user.py), [post.py](file:///d:/peersphere/app/models/post.py), [community.py](file:///d:/peersphere/app/models/community.py), etc.).
    *   **`routes/`**: Flask blueprints for various features ([auth.py](file:///d:/peersphere/app/routes/auth.py), [feed.py](file:///d:/peersphere/app/routes/feed.py), [communities.py](file:///d:/peersphere/app/routes/communities.py), [profile.py](file:///d:/peersphere/app/routes/profile.py), etc.).
    *   **`services/`**: Business logic, including the SQL-based recommendation engine for matchmaking.
    *   **`templates/`**: HTML Jinja2 templates for the frontend views.
    *   **`static/`**: Custom CSS ([style.css](file:///d:/peersphere/app/static/css/style.css)), JavaScript ([app.js](file:///d:/peersphere/app/static/js/app.js)), images, and user uploads.
    *   **[sql/](file:///d:/peersphere/app/sql/views.sql)**: PostgreSQL-compatible advanced SQL logic (triggers, views, procedures) and the [seed.py](file:///d:/peersphere/app/sql/seed.py) data generation script.
    *   **`utils/`**: Helper functions and decorators ([decorators.py](file:///d:/peersphere/app/utils/decorators.py) for role-based access).
*   **[run.py](file:///d:/peersphere/run.py)**: The application entry point.
*   **[config.py](file:///d:/peersphere/config.py)**: Environment-based configuration settings.
*   **[requirements.txt](file:///d:/peersphere/requirements.txt)**: Project dependencies.

## Key Features Implemented

1.  **Authentication & Roles**: Secure registration/login using `bcrypt`. Support for different roles: `student`, `alumni`, and `admin`.
2.  **Profiles & Skills**: Users can generate profiles, track completion strength, and add skills. The platform uses these traits for matching.
3.  **Smart Recommendations**: A custom recommendation service suggests relevant users to connect with based on shared skills, departments, and universities.
4.  **Social Feed**: A central feed where users can post updates (with images), like, and comment on peers' posts.
5.  **Communities**: Topic-specific groups where users can join, explore trending spaces, and participate in community-specific discussions.
6.  **Events**: Event discovery and RSVP system categorized by type (hackathons, workshops, seminars).
7.  **Mentorship**: A dedicated portal where experienced alumni can register as mentors and students can find guidance based on expertise and availability.
8.  **Direct Messaging**: A real-time chat interface mimicking modern messaging apps for one-on-one communication.
9.  **Premium UI/UX**:
    *   **Glassmorphism**: Elegant, frosted-glass card components (`.card-glass`).
    *   **Dark Mode**: A fully integrated, persistent Dark Mode/Light Mode toggle.
    *   **Responsive Layouts**: 3-column dashboard layout on desktop, condensing neatly on mobile devices.
    *   **Dynamic Elements**: Micro-animations on hover, smooth transitions, and colorful category badges.

## Verification & Execution

The development process concluded with the following verification steps:

1.  **Dependency Alignment**: We finalized the [requirements.txt](file:///d:/peersphere/requirements.txt) to seamlessly install necessary libraries (removing strict binary compilations for maximum cross-platform compatibility).
2.  **Database Seeding**: The [app/sql/seed.py](file:///d:/peersphere/app/sql/seed.py) script was executed within the Flask application context. It successfully created:
    *   20 baseline skills.
    *   10 dummy users (students and alumni).
    *   8 active communities with members.
    *   Over a dozen posts, comments, and likes to simulate engagement.
    *   5 upcoming events with registered attendees.
    *   Mentorship profiles.
3.  **Local Server**: The application is actively running on the local Flask development server at `http://127.0.0.1:5000/`. The user has successfully opened the browser to verify the interface.

## Next Steps

If moving to production, the development SQLite database ([instance/peersphere.db](file:///d:/peersphere/instance/peersphere.db)) should be swapped out by configuring the `DATABASE_URL` in [.env](file:///d:/peersphere/.env) to point to a PostgreSQL instance. The advanced SQL scripts inside `app/sql/` (triggers, views, and procedures) can then be run directly against the PostgreSQL database to unlock the powerful native database features we designed.
