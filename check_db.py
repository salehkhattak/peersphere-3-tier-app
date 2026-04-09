import os
import sys

# Add the current directory to the path so we can import 'app'
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    users = User.query.all()
    print("Listing users and their profile pictures:")
    for u in users:
        print(f"ID: {u.id}, Name: {u.name}, Profile Picture: '{u.profile_picture}'")
