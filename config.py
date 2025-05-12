# config.py
import os

class Config:
    # Fix for Render PostgreSQL connection strings
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///elektrofirma.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gatIuc5z5xSfaB4EvQeChIppBsuke3kF'
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB maximale Upload-Größe
    
    # Additional SQLAlchemy connection pool settings
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_ECHO = False  # Set to True to enable SQL query logging



