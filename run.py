# run.py
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.file import File
from app.models.timesheet import Timesheet
from app.models.vacation import Vacation
from sqlalchemy import text

app = create_app()

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Erstelle Admin-Benutzer, falls keine Benutzer vorhanden sind
    if User.query.count() == 0:
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')  # In der Produktion ein sicheres Passwort verwenden
        db.session.add(admin)
        db.session.commit()

@app.before_request
def log_db_connection():
    try:
        # Test the connection before each request
        result = db.session.execute(text('SELECT 1')).scalar()
        app.logger.info(f"Database connection working: {result}")
    except Exception as e:
        app.logger.error(f"Database connection error: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)