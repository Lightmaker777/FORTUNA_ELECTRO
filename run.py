
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
    
    else:
        # Update existing admin with new credentials
        if os.getenv('ADMIN_USERNAME') and os.getenv('ADMIN_PASSWORD'):
            # First find the admin user by checking if a user with the current env username exists
            admin_username = os.getenv('ADMIN_USERNAME')
            existing_user = User.query.filter_by(username=admin_username).first()
            
            if existing_user:
                # If a user with this username already exists, just update the password
                existing_user.set_password(os.getenv('ADMIN_PASSWORD'))
                db.session.commit()
                print(f"Updated password for existing user: {admin_username}")
            else:
                # Find admin user and update both username and password
                admin = User.query.filter_by(role='admin').first()
                if admin:
                    admin.username = admin_username
                    admin.set_password(os.getenv('ADMIN_PASSWORD'))
                    db.session.commit()
                    print(f"Updated admin user to: {admin_username}")
                else:
                    print("No admin user found to update")

if __name__ == '__main__':
    app.run(debug=True)