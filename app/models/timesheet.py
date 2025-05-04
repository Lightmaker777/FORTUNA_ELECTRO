# app/models/timesheet.py
from app import db
from datetime import datetime

class Timesheet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    activity = db.Column(db.String(64), nullable=False)
    hours = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    pdf_path = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<Timesheet {self.date} {self.hours}h>'