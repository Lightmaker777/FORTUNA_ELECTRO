import os
from dotenv import load_dotenv

if os.environ.get("FLASK_ENV") != "production":
    load_dotenv()  # Load .env only for local dev

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'gatIuc5z5xSfaB4EvQeChIppBsuke3kF')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    # Fallback for local dev
    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///elektrofirma.db'

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    if not Config.SQLALCHEMY_DATABASE_URI:
        raise RuntimeError("DATABASE_URL is not set in production environment")
    if not Config.SECRET_KEY or Config.SECRET_KEY == 'dev-secret-key':
        raise RuntimeError("SECRET_KEY is not set properly in production environment")

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

active_config = config_by_name[os.environ.get('FLASK_ENV', 'development')]
