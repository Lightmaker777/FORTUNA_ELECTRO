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

from app.forms.forms import ProjectStatusForm, ProjectEndDateForm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from flask import jsonify


projects = Blueprint('projects', __name__)

class ProjectForm(FlaskForm):
    name = StringField('Projektname (Adresse)', validators=[DataRequired()])
    description = TextAreaField('Beschreibung')
    submit = SubmitField('Speichern')

class ProjectStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('in_bearbeitung', 'In Bearbeitung'),
        
        ('archiviert', 'Archiviert')
    ], validators=[DataRequired()])
    submit = SubmitField('Status aktualisieren')

@projects.route('/<int:project_id>/update_end_date', methods=['POST'])
@login_required
def update_end_date(project_id):
    """Aktualisiert das Enddatum eines Projekts."""
    project = Project.query.get_or_404(project_id)
    
    # Überprüfen, ob der Benutzer das Projekt bearbeiten darf (Admin oder Ersteller)
    if project.creator != current_user and not current_user.is_admin:
        flash('Sie haben keine Berechtigung, dieses Projekt zu bearbeiten.', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    end_date_str = request.form.get('end_date')
    end_time_str = request.form.get('end_time', '00:00')  # Standardwert 00:00 falls nicht gesetzt
    
    if not end_date_str:
        flash('Bitte geben Sie ein gültiges Enddatum ein.', 'warning')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    try:
        # Datum und Zeit kombinieren
        if end_time_str:
            date_time_str = f"{end_date_str} {end_time_str}"
            end_date = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
        else:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Überprüfen, ob das Enddatum nach dem Startdatum liegt
        if end_date < project.start_date:
            flash('Das Enddatum muss nach dem Startdatum liegen.', 'warning')
            return redirect(url_for('projects.view_project', project_id=project_id))
        
        project.end_date = end_date
        db.session.commit()
        flash('Projekt-Enddatum erfolgreich aktualisiert.', 'success')
    except ValueError as e:
        flash(f'Ungültiges Datums- oder Zeitformat: {str(e)}', 'danger')
    
    return redirect(url_for('projects.view_project', project_id=project_id))


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
    status_form = ProjectStatusForm(obj=project)
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

    # Formular für die Enddatum-Änderung
    end_date_form = ProjectEndDateForm()
    if project.end_date:
        end_date_form.end_date.data = project.end_date
    
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
        status_form=status_form,
        end_date_form=end_date_form,
        now=datetime.now(),
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

@projects.route('/project/<int:project_id>/adjust_end_date', methods=['POST'])
@login_required
def adjust_end_date(project_id):
    project = Project.query.get_or_404(project_id)

    # Berechtigungsprüfung
    if project.creator != current_user and not current_user.is_admin:
        flash('Sie haben keine Berechtigung!', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    adjustment_type = request.form.get('unit')  # 'hour', 'day', etc.
    adjustment_value = int(request.form.get('value', 1))  # Standardwert ist 1
    
    print(f"Adjusting end date: {adjustment_value} {adjustment_type}")
    
    # Setze Enddatum auf jetzt, falls noch keins vorhanden
    if not project.end_date:
        project.end_date = datetime.now()
    
    # Zeit je nach Einheit hinzufügen
    if adjustment_type == 'hour':
        project.end_date += timedelta(hours=adjustment_value)
    elif adjustment_type == 'day':
        project.end_date += timedelta(days=adjustment_value)
    elif adjustment_type == 'week':
        project.end_date += timedelta(days=adjustment_value * 7)
    elif adjustment_type == 'month':
        project.end_date += relativedelta(months=adjustment_value)
    else:
        flash('Ungültiger Anpassungstyp.', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    db.session.commit()

    unit_display = {
        'hour': 'Stunde(n)',
        'day': 'Tag(e)',
        'week': 'Woche(n)',
        'month': 'Monat(e)'
    }
    
    flash(f'Enddatum wurde um {adjustment_value} {unit_display.get(adjustment_type)} nach hinten verschoben.', 'success')
    return redirect(url_for('projects.view_project', project_id=project.id))

# Modifizierte get_remaining_time Funktion - immer "info" Status zurückgeben
@projects.route('/api/project/<int:project_id>/remaining-time', methods=['GET'])
def get_remaining_time(project_id):
    project = Project.query.get_or_404(project_id)
    
    if not project.end_date:
        return jsonify({
            'error': 'Kein Enddatum gesetzt',
            'remaining': 'Kein Enddatum',
            'remaining_detailed': 'Kein Enddatum gesetzt',
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'total_seconds': 0,
            'status': 'info',  # Immer Info statt secondary
            'end_date': None,
            'formatted_end_date': 'Nicht festgelegt'
        }), 200

    now = datetime.now()
    time_diff = project.end_date - now
    
    # Negative Zeit abfangen
    if time_diff.total_seconds() < 0:
        return jsonify({
            'remaining': 'Fällig',
            'remaining_detailed': 'Projekt ist überfällig',
            'days': 0,
            'hours': 0,
            'minutes': 0,
            'total_seconds': 0,
            'status': 'info',  # Immer blau (info) statt danger
            'end_date': project.end_date.strftime('%Y-%m-%d %H:%M:%S'),
            'formatted_end_date': project.end_date.strftime('%d.%m.%Y %H:%M')
        })

    # Berechnung der einzelnen Zeitkomponenten
    total_seconds = int(time_diff.total_seconds())
    days = time_diff.days
    weeks = days // 7
    days_remainder = days % 7
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    
    # Status immer auf info (blau) setzen, unabhängig von der verbleibenden Zeit
    status = 'info'
    
    # Formatierte Anzeige
    remaining_parts = []
    detailed_parts = []
    
    # Wochen hinzufügen
    if weeks > 0:
        remaining_parts.append(f"{weeks} {'Wochen' if weeks != 1 else 'Woche'}")
        detailed_parts.append(f"{weeks} {'Wochen' if weeks != 1 else 'Woche'}")
    
    # Tage hinzufügen (nach Wochen)
    if days_remainder > 0 or (weeks == 0 and days > 0):
        days_to_show = days_remainder if weeks > 0 else days
        remaining_parts.append(f"{days_to_show} {'Tage' if days_to_show != 1 else 'Tag'}")
        detailed_parts.append(f"{days_to_show} {'Tage' if days_to_show != 1 else 'Tag'}")
    
    # Stunden hinzufügen, wenn weniger als 2 Tage oder keine Tage
    if days < 2 or (weeks == 0 and days == 0):
        remaining_parts.append(f"{hours} {'Stunden' if hours != 1 else 'Stunde'}")
        detailed_parts.append(f"{hours} {'Stunden' if hours != 1 else 'Stunde'}")
    
    # Minuten hinzufügen für kurze Zeiträume
    if days == 0 and hours < 2:
        detailed_parts.append(f"{minutes} {'Minuten' if minutes != 1 else 'Minute'}")
        if hours == 0:
            remaining_parts.append(f"{minutes} {'Minuten' if minutes != 1 else 'Minute'}")
    
    # Kompakte und detaillierte Anzeige zusammenstellen
    if not remaining_parts:
        remaining = "Weniger als 1 Minute"
    else:
        remaining = ", ".join(remaining_parts[:2])  # Maximal 2 Einheiten für kompakte Anzeige
    
    remaining_detailed = ", ".join(detailed_parts) if detailed_parts else "Weniger als 1 Minute"

    return jsonify({
        'remaining': remaining,
        'remaining_detailed': remaining_detailed,
        'weeks': weeks,
        'days': days,
        'days_remainder': days_remainder,
        'hours': hours,
        'minutes': minutes,
        'total_seconds': total_seconds,
        'status': status,  # Immer 'info' für blau
        'end_date': project.end_date.strftime('%Y-%m-%d %H:%M:%S'),
        'formatted_end_date': project.end_date.strftime('%d.%m.%Y %H:%M')
    })