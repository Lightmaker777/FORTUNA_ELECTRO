# app\__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import active_config
import os
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
migrate = Migrate()

def create_app(config_class=active_config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    migrate = Migrate(app, db)
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
    
    # Only register custom admin routes if you need them alongside Flask-Admin
    # If Flask-Admin handles all your admin functionality, you can remove this
    from app.routes.admin import admin as admin_bp
    app.register_blueprint(admin_bp, name='custom_admin', url_prefix='/custom-admin')

    from app.routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize Flask-Admin - Make sure this is after registering all blueprints
    from app.admin import init_admin
    init_admin(app)
    
    return app