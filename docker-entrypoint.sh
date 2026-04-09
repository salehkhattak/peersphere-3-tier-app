#!/bin/sh
set -e

echo "🚀 Starting PeerSphere..."

# Initialize the database (creates tables if they don't exist)
python - <<'EOF'
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("✅ Database initialised.")
EOF

# Run with Gunicorn in production, Flask dev server if FLASK_DEBUG=1
if [ "$FLASK_DEBUG" = "1" ]; then
    echo "⚡ Running in development mode..."
    exec python run.py
else
    echo "🏭 Running in production mode with Gunicorn..."
    exec gunicorn \
        --bind 0.0.0.0:5000 \
        --workers 2 \
        --threads 2 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        "run:app"
fi
