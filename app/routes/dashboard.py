# app/routes/dashboard.py
from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.project import Project
from app import db

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/')
@login_required
def index():
    # Projekte nach Status gruppieren
    in_progress = Project.query.filter_by(status='in_bearbeitung').order_by(Project.start_date.desc()).all()
    #completed = Project.query.filter_by(status='abgeschlossen').order_by(Project.start_date.desc()).all()
    archived = Project.query.filter_by(status='archiviert').order_by(Project.start_date.desc()).all()
    
    return render_template(
        'dashboard/index.html',
        title='Dashboard',
        in_progress=in_progress,
        #completed=completed,
        archived=archived
    )