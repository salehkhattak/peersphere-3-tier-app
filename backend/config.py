import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///peersphere.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.join(basedir, 'frontend', 'static', 'uploads'))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    WTF_CSRF_ENABLED = True
