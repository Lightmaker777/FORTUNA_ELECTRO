# app/admin.py

from flask import redirect, url_for, flash, Markup, request, abort
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user
from wtforms import PasswordField, SelectField
from wtforms.validators import Optional, DataRequired
from datetime import datetime
from app import db
from app.models.user import User
from app.models.project import Project
from app.models.timesheet import Timesheet
from app.models.vacation import Vacation
from app.models.file import File
from flask import flash
from werkzeug.exceptions import HTTPException
from sqlalchemy.orm.exc import NoResultFound

# Base secure model view with access control
class SecureModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin()

    def inaccessible_callback(self, name, **kwargs):
        flash('Sie benötigen Administratorrechte, um auf diese Seite zuzugreifen.', 'danger')
        return redirect(url_for('auth.login'))

# Helper function for date formatting
def date_format(view, context, model, name):
    value = getattr(model, name)
    if value:
        return value.strftime('%d.%m.%Y')
    return ''

# Helper for formatting status
def status_formatter(view, context, model, name):
    status_map = {
        'in_bearbeitung': 'In Bearbeitung',
        'abgeschlossen': 'Abgeschlossen',
        'archiviert': 'Archiviert'
    }
    return status_map.get(model.status, model.status)

# Custom AdminIndexView with access control and dashboard statistics
class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Sie benötigen Administratorrechte, um auf diese Seite zuzugreifen.', 'danger')
            return redirect(url_for('auth.login'))
        
        # Sammle Statistiken für das Dashboard
        stats = {
            'user_count': User.query.count(),
            'project_count': Project.query.count(),
            'timesheet_count': Timesheet.query.count(),
            'active_projects': Project.query.filter_by(status='in_bearbeitung').count(),
            'vacation_count': Vacation.query.count(),
            'file_count': File.query.count(),
            'recent_users': User.query.order_by(User.created_at.desc()).limit(5).all(),
            'recent_projects': Project.query.order_by(Project.start_date.desc()).limit(5).all()
        }
        
        return self.render('admin/index.html', stats=stats)

class UserModelView(SecureModelView):
    column_list = ['username', 'role', 'is_active', 'created_at']
    column_labels = {
        'username': 'Benutzername',
        'role': 'Rolle',
        'is_active': 'Aktiv',
        'created_at': 'Erstellt am'
    }
    column_formatters = {
        'created_at': date_format
    }
    column_filters = ['username', 'role', 'is_active']
    column_searchable_list = ['username']
    column_sortable_list = ['username', 'role', 'created_at']
    form_excluded_columns = ['password_hash', 'projects', 'files', 'timesheets', 'password']

    # Prevent deletion of the admin user and self-deletion
    can_delete = True  # Allow deletion in general

    # Korrekte Formular-Definition für das Role-Feld
    form_overrides = {
        'role': SelectField
    }

    form_args = {
        'role': {
            'choices': [
                ('installateur', 'Installateur'),
                ('admin', 'Administrator')
            ],
            'coerce': str
        }
    }

    def scaffold_form(self):
        form_class = super(UserModelView, self).scaffold_form()
        form_class.password = PasswordField('Passwort', validators=[Optional()],
                                           description='Leer lassen, um das Passwort nicht zu ändern')
        return form_class

    def create_form(self, obj=None):
        """Überschreibt create_form und stellt sicher, dass alle Felder korrekt initialisiert sind."""
        form = super(UserModelView, self).create_form(obj)
        # Wir stellen sicher, dass das Passwortfeld für neue Benutzer erforderlich ist
        form.password.validators = [DataRequired(message='Ein Passwort ist erforderlich')]
        return form

    def edit_form(self, obj=None):
        """Überschreibt edit_form und stellt sicher, dass alle Felder korrekt initialisiert sind."""
        form = super(UserModelView, self).edit_form(obj)
        # Für existierende Benutzer ist das Passwort optional
        form.password.validators = [Optional()]
        return form

    def delete_model(self, model):
        """Überschreibe die Standard-Löschmethode mit sicherer Exception-Behandlung"""
        try:
            # Überprüfe, ob es sich um den Admin-Account handelt
            if model.username == 'admin':
                flash('Der Hauptadministrator-Account kann nicht gelöscht werden.', 'danger')
                return False
                
            # Überprüfe, ob der Benutzer sich selbst löschen möchte
            if model.id == current_user.id:
                flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
                return False
                
            # Standard-Löschen durchführen, wenn kein besonderer Fall vorliegt
            return super(UserModelView, self).delete_model(model)
            
        except Exception as e:
            flash(f'Der Benutzer konnte nicht gelöscht werden: {str(e)}', 'danger')
            return False

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)
            
        if is_created and not form.password.data:
            flash('Ein Passwort ist für neue Benutzer erforderlich.', 'warning')
            raise ValueError('Passwort ist erforderlich')

    # Abfangen der Löschaktion und korrektes Umleiten
    @expose('/delete/', methods=('POST',))
    def delete_view(self):
        """Überschreibe die Standard-Löschansicht um Exceptions besser zu handhaben"""
        return_url = request.form.get('url') or url_for('admin.index')
        
        if not self.can_delete:
            flash('Löschen ist nicht erlaubt', 'error')
            return redirect(return_url)
            
        id = request.form.get('id')
        if id is None:
            flash('Keine ID angegeben', 'error')
            return redirect(return_url)
            
        model = self.get_one(id)
        if model is None:
            flash('Datensatz wurde nicht gefunden', 'error')
            return redirect(return_url)
            
        # Überprüfe, ob es sich um den Admin-Account handelt
        if hasattr(model, 'username') and model.username == 'admin':
            flash('Der Hauptadministrator-Account kann nicht gelöscht werden.', 'danger')
            return redirect(return_url)
            
        # Überprüfe, ob der Benutzer sich selbst löschen möchte
        if hasattr(model, 'id') and model.id == current_user.id:
            flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
            return redirect(return_url)
            
        try:
            self.delete_model(model)
            flash('Datensatz wurde erfolgreich gelöscht', 'success')
        except Exception as ex:
            flash(f'Der Benutzer konnte nicht gelöscht werden: {str(ex)}', 'danger')
            
        return redirect(return_url)

# Enhanced Project view
class ProjectModelView(SecureModelView):
    column_list = ['name', 'status', 'start_date', 'end_date', 'creator.username']
    column_labels = {
        'name': 'Projektname',
        'status': 'Status',
        'start_date': 'Startdatum',
        'end_date': 'Enddatum',
        'creator.username': 'Erstellt von'
    }
    column_formatters = {
        'start_date': date_format,
        'end_date': date_format,
        'status': status_formatter,
        'creator.username': lambda v, c, m, p: m.creator.username if m.creator else ''
    }
    column_filters = ['name', 'status', 'start_date', 'end_date']
    column_searchable_list = ['name', 'description']
    column_sortable_list = ['name', 'status', 'start_date', 'end_date']
    
    # Korrekte Form-Definition für Status-Feld
    form_overrides = {
        'status': SelectField
    }

    form_args = {
        'status': {
            'choices': [
                ('in_bearbeitung', 'In Bearbeitung'),
                ('abgeschlossen', 'Abgeschlossen'),
                ('archiviert', 'Archiviert')
            ],
            'coerce': str
        }
    }
    
    def on_model_change(self, form, model, is_created):
        if is_created and not model.creator:
            model.creator = current_user

# Enhanced Timesheet view
class TimesheetModelView(SecureModelView):
    column_list = ['date', 'activity', 'hours', 'project.name', 'employee.username']
    column_labels = {
        'date': 'Datum',
        'activity': 'Tätigkeit',
        'hours': 'Stunden',
        'project.name': 'Projekt',
        'employee.username': 'Mitarbeiter'
    }
    column_formatters = {
        'date': date_format,
        'project.name': lambda v, c, m, p: m.project.name if m.project else '',
        'employee.username': lambda v, c, m, p: m.employee.username if m.employee else ''
    }
    column_filters = ['date', 'activity', 'hours', 'project_id', 'user_id']
    column_searchable_list = ['activity', 'notes']
    column_sortable_list = ['date', 'hours']

# Enhanced Vacation view
class VacationModelView(SecureModelView):
    column_list = ['name', 'start_date', 'end_date', 'type']
    column_labels = {
        'name': 'Name',
        'start_date': 'Startdatum',
        'end_date': 'Enddatum',
        'type': 'Art'
    }
    column_formatters = {
        'start_date': date_format,
        'end_date': date_format
    }
    column_filters = ['name', 'start_date', 'end_date', 'type']
    column_searchable_list = ['name', 'type']
    column_sortable_list = ['name', 'start_date', 'end_date']
    
    # Korrekte Definition für Type-Feld
    form_overrides = {
        'type': SelectField
    }

    form_args = {
        'type': {
            'choices': [
                ('urlaub', 'Urlaub'),
                ('krank', 'Krankheit'),
                ('sonstiges', 'Sonstiges')
            ],
            'coerce': str
        }
    }

# Enhanced File view
class FileModelView(SecureModelView):
    column_list = ['original_filename', 'file_type', 'upload_date', 'project.name', 'uploader.username']
    column_labels = {
        'original_filename': 'Dateiname',
        'file_type': 'Dateityp',
        'upload_date': 'Hochgeladen am',
        'project.name': 'Projekt',
        'uploader.username': 'Hochgeladen von'
    }
    column_formatters = {
        'upload_date': date_format,
        'project.name': lambda v, c, m, p: m.project.name if m.project else '',
        'uploader.username': lambda v, c, m, p: m.uploader.username if m.uploader else ''
    }
    column_filters = ['original_filename', 'file_type', 'upload_date', 'project_id', 'uploader_id']
    column_searchable_list = ['original_filename', 'file_type']
    column_sortable_list = ['original_filename', 'file_type', 'upload_date']
    
    # Korrekte Definition für file_type-Feld
    form_overrides = {
        'file_type': SelectField
    }

    form_args = {
        'file_type': {
            'choices': [
                ('foto', 'Foto'),
                ('video', 'Video'),
                ('stundenbericht', 'Stundenbericht'),
                ('pruefbericht', 'Prüfbericht'),
                ('sonstiges', 'Sonstiges')
            ],
            'coerce': str
        }
    }

# Error Handler für Flask-Admin
class AdminErrorHandler(HTTPException):
    def __init__(self, description=None, response=None):
        super(AdminErrorHandler, self).__init__(description, response)
        self.code = 400

def init_admin(app):
    """Initialize Flask-Admin with proper configuration."""
    # Create the Admin instance
    admin = Admin(
        app, 
        name='Admin Panel',
        template_mode='bootstrap4',
        index_view=MyAdminIndexView(),
        url='/admin',
        base_template='admin/master.html'
    )
    
    # Add model views
    admin.add_view(UserModelView(User, db.session, name='Benutzer'))
    admin.add_view(ProjectModelView(Project, db.session, name='Projekte'))
    admin.add_view(TimesheetModelView(Timesheet, db.session, name='Arbeitszeiten'))
    admin.add_view(VacationModelView(Vacation, db.session, name='Urlaub'))
    admin.add_view(FileModelView(File, db.session, name='Dateien'))
    
    # Add menu link
    admin.add_link(MenuLink(name='Zurück zur Anwendung', url='/'))
    
    # Füge globale Fehlerbehandlung für Flask-Admin hinzu
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        if "Der Hauptadministrator-Account kann nicht gelöscht werden" in str(e):
            flash('Der Hauptadministrator-Account kann nicht gelöscht werden.', 'danger')
            return redirect(request.referrer or url_for('admin.index'))
        elif "Sie können Ihren eigenen Benutzer nicht löschen" in str(e):
            flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
            return redirect(request.referrer or url_for('admin.index'))
        # Für andere ValueError-Exceptions
        flash(f'Fehler: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin.index'))
        
    # Fehlerbehandlung für AttributeError (wie 'tuple' object has no attribute 'items')
    @app.errorhandler(AttributeError)
    def handle_attribute_error(e):
        flash(f'Ein Systemfehler ist aufgetreten. Bitte kontaktieren Sie den Administrator: {str(e)}', 'danger')
        return redirect(request.referrer or url_for('admin.index'))
    
    return admin