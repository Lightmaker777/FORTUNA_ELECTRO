# app/models/file.py
from app import db
from datetime import datetime
import os

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(128), nullable=False)
    original_filename = db.Column(db.String(128), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # 'foto', 'video', 'stundenbericht', 'pruefbericht', 'sonstiges'
    file_path = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f'<File {self.original_filename}>'