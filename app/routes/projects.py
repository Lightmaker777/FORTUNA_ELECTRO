# app/routes/projects.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.utils.decorators import admin_required
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField
from wtforms.validators import DataRequired
import os
# Nachträglicher Import für create_project_folders Funktion
from flask import current_app
from app.models.timesheet import Timesheet

projects = Blueprint('projects', __name__)

class ProjectForm(FlaskForm):
    name = StringField('Projektname (Adresse)', validators=[DataRequired()])
    description = TextAreaField('Beschreibung')
    submit = SubmitField('Speichern')

class ProjectStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('in_bearbeitung', 'In Bearbeitung'),
        ('abgeschlossen', 'Abgeschlossen'),
        ('archiviert', 'Archiviert')
    ], validators=[DataRequired()])
    submit = SubmitField('Status aktualisieren')

@projects.route('/project/new', methods=['GET', 'POST'])
@login_required
def new_project():
    form = ProjectForm()
    if form.validate_on_submit():
        project = Project(
            name=form.name.data,
            description=form.description.data,
            creator_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # Projektordnerstruktur erstellen
        create_project_folders(project.id)
        
        flash(f'Projekt "{project.name}" wurde erfolgreich erstellt!', 'success')
        return redirect(url_for('projects.view_project', project_id=project.id))
    
    return render_template('projects/new.html', title='Neues Projekt', form=form)

@projects.route('/project/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    # Dateien nach Typ gruppieren
    photos = project.files.filter_by(file_type='foto').all()
    videos = project.files.filter_by(file_type='video').all()
    timesheets = project.files.filter_by(file_type='stundenbericht').all()
    reports = project.files.filter_by(file_type='pruefbericht').all()
    other_files = project.files.filter_by(file_type='sonstiges').all()
    
    # Stundenberichte
    timesheets_data = project.timesheets.order_by(Timesheet.date.desc()).all()
    
    status_form = ProjectStatusForm()
    status_form.status.data = project.status
    
    return render_template(
        'projects/view.html',
        title=project.name,
        project=project,
        photos=photos,
        videos=videos,
        timesheets=timesheets,
        reports=reports,
        other_files=other_files,
        timesheets_data=timesheets_data,
        status_form=status_form
    )

@projects.route('/project/<int:project_id>/status', methods=['POST'])
@login_required
def update_status(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectStatusForm()
    
    if form.validate_on_submit():
        new_status = form.status.data
        
        # Nur Admins dürfen auf "archiviert" setzen
        if new_status == 'archiviert' and not current_user.is_admin():
            flash('Nur Administratoren dürfen Projekte archivieren.', 'danger')
            return redirect(url_for('projects.view_project', project_id=project.id))
        
        project.status = new_status
        db.session.commit()
        flash(f'Projektstatus wurde auf "{dict(form.status.choices).get(new_status)}" aktualisiert!', 'success')
    
    return redirect(url_for('projects.view_project', project_id=project.id))

def create_project_folders(project_id):
    # Hauptordner für das Projekt
    project_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'project_{project_id}')
    os.makedirs(project_folder, exist_ok=True)
    
    # Unterordner erstellen
    folder_types = ['fotos', 'videos', 'stundenberichte', 'pruefberichte', 'sonstiges']
    for folder_type in folder_types:
        os.makedirs(os.path.join(project_folder, folder_type), exist_ok=True)
    
    return project_folder

