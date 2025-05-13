# run.py
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.file import File
from app.models.timesheet import Timesheet
from app.models.vacation import Vacation

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

if __name__ == '__main__':
    app.run(debug=True)