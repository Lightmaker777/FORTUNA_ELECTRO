# config.py
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'elektrofirma-geheimer-schluessel'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///elektrofirma.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 20 MB maximale Upload-Größe


