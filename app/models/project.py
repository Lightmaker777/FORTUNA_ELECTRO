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
        
    
        
    # Ergänzung für app/models/project.py

    def get_remaining_hours(self):
        """Berechnet die verbleibenden Stunden bis zum Projektende."""
        if not self.end_date:
            return None
            
        now = datetime.now()
        time_diff = self.end_date - now
        
        # Wenn das Projekt bereits überfällig ist
        if time_diff.total_seconds() <= 0:
            return 0
            
        # Gesamtstunden berechnen
        total_hours = time_diff.total_seconds() / 3600
        return round(total_hours, 1)  # Auf eine Dezimalstelle runden

    def is_overdue(self):
        """
        Check if the project is overdue (end date is in the past).
        Returns True if overdue, False otherwise.
        """
        if not self.end_date:
            return False
        return self.end_date < datetime.now()

    def days_remaining(self):
        """
        Calculate the number of days remaining until the project end date.
        Returns:
            int: Number of days remaining (negative if overdue)
        """
        if not self.end_date:
            return None
            
        today = datetime.now()
        # Convert to date for proper day calculation
        delta = (self.end_date.date() - today.date()).days
        return delta

    def get_progress_percentage(self):
        """Berechnet den Fortschritt des Projekts in Prozent."""
        if not self.end_date or not self.start_date:
            return 0
            
        now = datetime.now()
        
        # Make sure we're working with datetime objects
        if isinstance(self.start_date, datetime) and isinstance(self.end_date, datetime):
            total_duration = (self.end_date - self.start_date).total_seconds()
            elapsed_time = (now - self.start_date).total_seconds()
        else:
            # Handle possible date objects by converting to datetime
            start_datetime = datetime.combine(self.start_date, datetime.min.time()) if not isinstance(self.start_date, datetime) else self.start_date
            end_datetime = datetime.combine(self.end_date, datetime.min.time()) if not isinstance(self.end_date, datetime) else self.end_date
            
            total_duration = (end_datetime - start_datetime).total_seconds()
            elapsed_time = (now - start_datetime).total_seconds()
        
        # Falls Endzeit bereits überschritten
        if elapsed_time >= total_duration:
            return 100
            
        # Fortschritt berechnen (als Prozentsatz)
        progress = (elapsed_time / total_duration) * 100
        return round(progress, 1)  # Auf eine Dezimalstelle runden
            
    def __repr__(self):
        return f'<Project {self.name}>'