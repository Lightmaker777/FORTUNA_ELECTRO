from app import create_app, db
from app.models.user import User
from app.models.project import Project
from sqlalchemy import text
import os

app = create_app()

@app.before_first_request
def create_initial_data():
    try:
        # Ensure all tables exist
        db.create_all()

        # Check if any users exist before creating an initial user
        if User.query.count() == 0:
            # Create initial admin user
            admin = User(
                username='admin', 
                role='admin', 
                is_active=True
            )
            admin.set_password('admin123')  # Use a secure password
            db.session.add(admin)
            db.session.commit()

    except Exception as e:
        app.logger.error(f"Error initializing data: {str(e)}")

# Optional: Route to test database connection
@app.route('/test-db-connection')
def test_db_connection():
    try:
        result = db.session.execute(text('SELECT 1')).scalar()
        return f"Database connection successful: {result}"
    except Exception as e:
        return f"Database connection failed: {str(e)}", 500

# Ensure uploads directory exists
uploads_dir = app.config.get('UPLOAD_FOLDER')
if uploads_dir:
    os.makedirs(uploads_dir, exist_ok=True)