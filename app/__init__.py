# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import os
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    # Ordner für Uploads erstellen, falls nicht vorhanden
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Blueprints registrieren
    from app.routes.auth import auth as auth_bp
    app.register_blueprint(auth_bp)
    
    from app.routes.dashboard import dashboard as dashboard_bp
    app.register_blueprint(dashboard_bp)
    
    from app.routes.projects import projects as projects_bp
    app.register_blueprint(projects_bp)
    
    from app.routes.files import files as files_bp
    app.register_blueprint(files_bp)
    
    from app.routes.timesheets import timesheets as timesheets_bp
    app.register_blueprint(timesheets_bp)
    
    from app.routes.admin import admin as admin_bp
    app.register_blueprint(admin_bp)
    
    return app