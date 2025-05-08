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
import zipfile
import tempfile
import shutil
import json
from datetime import datetime

files = Blueprint('files', __name__)

ALLOWED_EXTENSIONS = {
    'foto': {
        'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'svg'
    },
    'video': {
        'mp4', 'avi', 'mov', 'wmv', 'mkv', 'webm', 'flv'
    },
    'stundenbericht': {
        'pdf'
    },
    'pruefbericht': {
        'pdf'
    },
    'sonstiges': {
        # Office-Dokumente
        'pdf', 'doc', 'docx', 'xls', 'xlsx', 'csv', 'ppt', 'pptx', 'rtf', 'odt', 'ods', 'odp',
        # Textbasierte Dateien
        'txt', 'log', 'md', 'ini', 'cfg', 'json', 'xml', 'yaml', 'yml',
        # Code-Dateien
        'py', 'java', 'c', 'cpp', 'cs', 'js', 'ts', 'html', 'htm', 'css', 'php', 'rb', 'go', 'rs', 'sh', 'bat',
        # Archivformate
        'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz', 'iso',
        # Sonstige gebräuchliche Dateitypen
        'sql', 'db', 'sqlite', 'psd', 'ai', 'eps', 'sketch', 'xd'
    }
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

@files.route('/project/<int:project_id>/download')
@login_required
def download_project(project_id):
    """
    Erstellt eine ZIP-Datei mit allen Projektdaten und Dateien
    und stellt sie zum Download bereit.
    """
    from app.models.timesheet import Timesheet  # Import Timesheet model
    
    project = Project.query.get_or_404(project_id)
    
    # Erstelle einen eigenen temporären Ordner im UPLOAD_FOLDER
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp', f'project_export_{timestamp}_{uuid.uuid4().hex}')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Hauptordner für das Projekt erstellen
        project_folder = os.path.join(temp_dir, f"{project.name}")
        os.makedirs(project_folder, exist_ok=True)
        
        # Projektinformationen als JSON-Datei speichern
        project_info = {
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "start_date": project.start_date.strftime('%Y-%m-%d') if project.start_date else None,
            "end_date": project.end_date.strftime('%Y-%m-%d') if project.end_date else None,
            "creator": project.creator.username
        }
        
        with open(os.path.join(project_folder, "projekt_info.json"), 'w', encoding='utf-8') as f:
            json.dump(project_info, f, ensure_ascii=False, indent=4)
        
        # Projektdateien in entsprechende Unterordner kopieren
        files = File.query.filter_by(project_id=project_id).all()
        
        # Kategorien für die Ordnerstruktur
        categories = ['fotos', 'videos', 'stundenberichte', 'pruefberichte', 'sonstiges']
        
        # Erstelle Ordner für jede Kategorie
        for category in categories:
            os.makedirs(os.path.join(project_folder, category), exist_ok=True)
        
        # Dateien in die entsprechenden Ordner kopieren
        for file in files:
            # Bestimme Zielordner basierend auf dem Dateityp
            if file.file_type == 'foto':
                target_folder = os.path.join(project_folder, 'fotos')
            elif file.file_type == 'video':
                target_folder = os.path.join(project_folder, 'videos')
            elif file.file_type == 'stundenbericht':
                target_folder = os.path.join(project_folder, 'stundenberichte')
            elif file.file_type == 'pruefbericht':
                target_folder = os.path.join(project_folder, 'pruefberichte')
            else:
                target_folder = os.path.join(project_folder, 'sonstiges')
            
            # Quellpfad der Datei
            source_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.file_path)
            
            # Zielpath mit Originaldateiname
            target_path = os.path.join(target_folder, file.original_filename)
            
            # Kopiere die Datei, wenn sie existiert
            if os.path.exists(source_path):
                shutil.copy2(source_path, target_path)
        
        # Zusammenfassung der Arbeitsstunden als CSV erstellen
        timesheets = Timesheet.query.filter_by(project_id=project_id).all()
        
        if timesheets:
            with open(os.path.join(project_folder, "arbeitsstunden.csv"), 'w', encoding='utf-8') as f:
                f.write("Datum,Mitarbeiter,Tätigkeit,Stunden\n")
                for ts in timesheets:
                    f.write(f"{ts.date.strftime('%Y-%m-%d')},{ts.employee.username},{ts.activity},{ts.hours}\n")
        
        # ZIP-Datei erstellen
        safe_project_name = secure_filename(project.name)
        zip_filename = f"Projekt_{safe_project_name}_{timestamp}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Datei zum Download anbieten
        response = send_from_directory(
            directory=temp_dir,
            path=zip_filename,
            as_attachment=True,
            download_name=zip_filename
        )
        
        # Cleanup-Funktion für später registrieren
        @response.call_on_close
        def cleanup():
            try:
                # Cleanup verzögern, um sicherzustellen, dass der Download abgeschlossen ist
                # Im Produktionsbetrieb sollte hier ein Task-Queue-System verwendet werden
                # oder zumindest ein Hintergrundprozess zum regelmäßigen Aufräumen alter Exporte
                import threading
                import time
                
                def delayed_cleanup():
                    time.sleep(60)  # 60 Sekunden warten, um sicherzustellen, dass der Download abgeschlossen ist
                    try:
                        if os.path.exists(temp_dir):
                            shutil.rmtree(temp_dir)
                    except Exception as e:
                        current_app.logger.error(f"Fehler beim Aufräumen von {temp_dir}: {str(e)}")
                
                thread = threading.Thread(target=delayed_cleanup)
                thread.daemon = True  # Daemon-Thread, um Flask beim Beenden nicht zu blockieren
                thread.start()
            except Exception as e:
                current_app.logger.error(f"Fehler beim Starten des Cleanup-Threads: {str(e)}")
        
        return response
        
    except Exception as e:
        # Bei einem Fehler sicherstellen, dass der temporäre Ordner aufgeräumt wird
        current_app.logger.error(f"Fehler beim Erstellen des Projekt-Downloads: {str(e)}")
        try:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            current_app.logger.error(f"Fehler beim Aufräumen nach Fehler: {str(cleanup_error)}")
        
        flash("Beim Erstellen des Projekt-Downloads ist ein Fehler aufgetreten.", "danger")
        return redirect(url_for('projects.view_project', project_id=project_id))