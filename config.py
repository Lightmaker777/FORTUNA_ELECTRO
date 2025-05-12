# config.py
import os
from dotenv import load_dotenv

if os.environ.get("FLASK_ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()
  # Load environment variables from .env file

class Config:
    
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gatIuc5z5xSfaB4EvQeChIppBsuke3kF' )
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024  # 20 MB maximale Upload-Größe
    
    # Additional SQLAlchemy connection pool settings
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 10
    SQLALCHEMY_ECHO = False  # Set to True to enable SQL query logging

    # Fix for Render PostgreSQL URL format (if needed)
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    
    # Fallback to SQLite for local development
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///elektrofirma.db'

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///elektrofirma.db'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    # Production config uses the DATABASE_URL from environment
    
    # Set secret key from environment with a fallback
    SECRET_KEY = os.environ.get('SECRET_KEY', 'temporary-secret-key-please-change')
    if not SECRET_KEY or SECRET_KEY == 'temporary-secret-key-please-change':
        import warnings
        warnings.warn("Using temporary SECRET_KEY in production, please set a proper SECRET_KEY environment variable", UserWarning)

# Choose the appropriate configuration based on environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

# Set the active configuration
active_config = config_by_name[os.environ.get('FLASK_ENV', 'development')]