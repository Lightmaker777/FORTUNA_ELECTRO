# run.py
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.file import File
from app.models.timesheet import Timesheet
from app.models.vacation import Vacation
from dotenv import load_dotenv
import os

app = create_app()

load_dotenv()

@app.before_first_request
def create_tables():
    db.create_all()
    
    # Erstelle Admin-Benutzer, falls keine Benutzer vorhanden sind
    if User.query.count() == 0:
        # Prüfe, ob Umgebungsvariablen existieren
        if os.getenv('ADMIN_USERNAME') and os.getenv('ADMIN_PASSWORD'):
            admin = User(username=os.getenv('ADMIN_USERNAME'), 
                        role='admin')
            admin.set_password(os.getenv('ADMIN_PASSWORD'))
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)