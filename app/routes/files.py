# app/routes/files.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.file import File
from app.utils.decorators import admin_required
from werkzeug.utils import secure_filename
from app.forms.file_forms import FileUploadForm
import os
import uuid

files = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {
    'foto': {'png', 'jpg', 'jpeg', 'gif'},
    'video': {'mp4', 'avi', 'mov', 'wmv'},
    'stundenbericht': {'pdf'},
    'pruefbericht': {'pdf'},
    'sonstiges': {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt'}
}

def allowed_file(filename, file_type):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS.get(file_type, {})

@files.route('/project/<int:project_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_file(project_id):
    project = Project.query.get_or_404(project_id)
    
    form = FileUploadForm()

    if form.validate_on_submit():
        file = form.file.data
        file_type = form.file_type.data

        if file and allowed_file(file.filename, file_type):
            original_filename = secure_filename(file.filename)
            filename = f"{uuid.uuid4().hex}_{original_filename}"

            file_path = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                f'project_{project_id}',
                file_type + 's',
                filename
            )
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            file.save(file_path)

            db_file = File(
                filename=filename,
                original_filename=original_filename,
                file_type=file_type,
                file_path = os.path.join(f'project_{project_id}', file_type + 's', filename).replace("\\", "/")
,
                file_size=os.path.getsize(file_path),
                project_id=project_id,
                uploader_id=current_user.id
            )
            db.session.add(db_file)
            db.session.commit()

            flash(f'Datei "{original_filename}" wurde erfolgreich hochgeladen!', 'success')
            return redirect(url_for('projects.view_project', project_id=project_id))
        else:
            flash(f'Nicht unterstütztes Dateiformat! Erlaubte Formate für {file_type}: {", ".join(ALLOWED_EXTENSIONS[file_type])}', 'danger')

    
    return render_template('files/upload.html', title='Datei hochladen', project=project, form=form)

@files.route('/files/<path:filename>')
@login_required
def view_file(filename):
    filename = filename.replace("\\", "/")
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)

@files.route('/file/<int:file_id>/delete')
@login_required
def delete_file(file_id):
    file = File.query.get_or_404(file_id)
    project_id = file.project_id
    
    # Prüfen, ob Benutzer Admin ist oder der Uploader der Datei
    if not current_user.is_admin() and file.uploader_id != current_user.id:
        flash('Sie haben nicht die Berechtigung, diese Datei zu löschen!', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    # Datei vom Dateisystem löschen
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Datei aus Datenbank löschen
    db.session.delete(file)
    db.session.commit()
    
    flash('Datei wurde erfolgreich gelöscht!', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))