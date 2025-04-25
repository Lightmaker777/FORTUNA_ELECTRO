# app/models/project.py
from app import db
from datetime import datetime

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)  # Adresse als Projektname
    description = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='in_bearbeitung')  # 'in_bearbeitung', 'abgeschlossen', 'archiviert'
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Beziehungen
    files = db.relationship('File', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    timesheets = db.relationship('Timesheet', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'