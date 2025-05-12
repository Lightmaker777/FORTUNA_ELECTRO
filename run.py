# run.py
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.file import File
from app.models.timesheet import Timesheet
from app.models.vacation import Vacation
from sqlalchemy import text
import os

app = create_app()

# Only create an admin user if running in development mode and no users exist
@app.cli.command("init-db")
def init_db_command():
    """Create initial database and seed with admin user."""
    # Create tables (this is safe to run even if tables exist)
    with app.app_context():
        db.create_all()
        
        # Only seed admin user if no users exist and we're in development
        if User.query.count() == 0:
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')  # Use a secure password in production
            db.session.add(admin)
            db.session.commit()
            print("Created admin user")
        
        print("Database initialized")

@app.before_request
def log_db_connection():
    try:
        # Test the connection before each request
        result = db.session.execute(text('SELECT 1')).scalar()
        app.logger.info(f"Database connection working: {result}")
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")

@app.route('/test-db-connection')
def test_db_connection():
    try:
        result = db.session.execute(text('SELECT 1')).scalar()
        message = f"Database connection successful: {result}"
        app.logger.error(message)  # Log with ERROR level for visibility
        return message
    except Exception as e:
        error_message = f"Database connection failed: {str(e)}"
        app.logger.error(error_message)
        return error_message, 500  # Return HTTP 500 status code

if __name__ == '__main__':
    app.run(debug=True)