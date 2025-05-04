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
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Beziehungen
    files = db.relationship('File', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    timesheets = db.relationship('Timesheet', backref='project', lazy='dynamic', cascade='all, delete-orphan')
    
    
    
    def get_remaining_time(self):
        """Calculate and return the remaining time in a human-readable format."""
        if not self.end_date:
            return "Kein Enddatum"
            
        now = datetime.now()
        time_diff = self.end_date - now
        
        # If the deadline has passed
        if time_diff.total_seconds() <= 0:
            return "Fällig"
            
        days = time_diff.days
        hours = time_diff.seconds // 3600
        
        if days > 0:
            return f"{days} Tage" if days > 1 else "1 Tag"
        else:
            return f"{hours} STUNDEN" if hours > 1 else "1 STUNDE"
        
    
        
    def get_progress_percentage(self):
        """Calculate the project progress as a percentage."""
        if not self.end_date or not self.start_date:
            return 0
            
        now = datetime.now()
        
        # If project hasn't started yet
        if now < self.start_date:
            return 0
            
        # If project is overdue
        if now > self.end_date:
            return 100
            
        total_duration = (self.end_date - self.start_date).total_seconds()
        elapsed_time = (now - self.start_date).total_seconds()
        
        # Avoid division by zero
        if total_duration == 0:
            return 100
            
        progress = (elapsed_time / total_duration) * 100
        return min(round(progress), 100)  # Ensure we don't exceed 100%
    
    def get_remaining_hours(self):
        """Get the remaining time specifically in hours for consistent display."""
        if not self.end_date:
            return None
            
        now = datetime.now()
        time_diff = self.end_date - now
        
        # Convert to hours
        total_hours = int(time_diff.total_seconds() / 3600)
        
        # Handle negative values (overdue projects)
        if total_hours < 0:
            return 0
            
        return total_hours
    
    def __repr__(self):
        return f'<Project {self.name}>'