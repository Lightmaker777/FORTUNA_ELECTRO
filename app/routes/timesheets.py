# app/routes/timesheets.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.models.timesheet import Timesheet
from app.models.file import File
from app.utils.pdf_generator import generate_fortuna_timesheet
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange
from datetime import datetime
import os
import uuid
import json  # Für die Verarbeitung von JSON-String-Daten

timesheets = Blueprint('timesheets', __name__)

ACTIVITY_CHOICES = [
    ('steckdosen', 'Steckdosen installieren'),
    ('leuchten', 'Leuchten installieren'),
    ('kabel', 'Kabel verlegen'),
    ('waende', 'Wände fräsen'),
    ('fehlersuche', 'Fehlersuche / Reparatur'),
    ('andere', 'Andere Tätigkeit')
]

class TimesheetForm(FlaskForm):
    activity = SelectField('Tätigkeit', choices=ACTIVITY_CHOICES, validators=[DataRequired()])
    other_activity = StringField('Andere Tätigkeit (bitte angeben)')
    hours = FloatField('Stunden', validators=[DataRequired(), NumberRange(min=0.25, max=24)])
    date = DateField('Datum', format='%Y-%m-%d', validators=[DataRequired()])
    notes = TextAreaField('Notizen')
    submit = SubmitField('PDF erstellen und speichern')

@timesheets.route('/project/<int:project_id>/timesheet/new', methods=['GET', 'POST'])
@login_required
def new_timesheet(project_id):
    project = Project.query.get_or_404(project_id)
    form = TimesheetForm()

    # Heutiges Datum als Standardwert
    if not form.date.data:
        form.date.data = datetime.utcnow().date()

    if form.validate_on_submit():
        try:
            # Daten aus dem Formular extrahieren
            date = form.date.data
            hours = form.hours.data
            notes = form.notes.data
            
            # Arbeitseinsatz und Material-Daten aus JSON extrahieren
            arbeitseinsatz_string = request.form.get('arbeitseinsatz_data', '[]')
            material_string = request.form.get('material_data', '[]')
            
            # JSON-Strings in Listen von Dictionaries konvertieren
            try:
                arbeitseinsatz_data = json.loads(arbeitseinsatz_string)
            except json.JSONDecodeError:
                arbeitseinsatz_data = []
                
            try:
                material_data = json.loads(material_string)
            except json.JSONDecodeError:
                material_data = []
                
            an_abreise = request.form.get('an_abreise', '')
            arbeitskraft = request.form.get('arbeitskraft', current_user.username)
            
            # Bestimme die tatsächliche Aktivität
            activity_text = form.activity.data
            if activity_text == 'andere' and form.other_activity.data:
                activity_text = form.other_activity.data
            else:
                # Hole den angezeigten Text für die ausgewählte Aktivität
                activity_text = dict(ACTIVITY_CHOICES).get(activity_text, activity_text)

            # Stundenbericht erstellen
            timesheet = Timesheet(
                date=date,
                activity=activity_text,
                hours=hours,
                notes=notes,
                project_id=project.id,
                user_id=current_user.id
            )

            db.session.add(timesheet)
            db.session.commit()

            # Erstelle PDF und speichere es
            pdf_filename = f"stundenbericht_{project.id}_{timesheet.id}_{uuid.uuid4().hex}.pdf"
            pdf_folder = os.path.join(
                current_app.config['UPLOAD_FOLDER'],
                f'project_{project.id}',
                'stundenberichte'
            )
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_path = os.path.join(pdf_folder, pdf_filename)

            # Formatiere das Datum als String für den PDF-Generator
            date_string = date.strftime("%d.%m.%Y")

            # PDF generieren mit den vollständigen Formular-Daten
            generate_fortuna_timesheet(
                pdf_path,
                datum=date_string,  # Hier das Datum als String übergeben
                bauvorhaben=project.name,
                arbeitskraft=arbeitskraft,
                an_abreise=an_abreise,
                arbeitseinsatz=arbeitseinsatz_data,
                material_list=material_data
            )

            # Relative Pfadangabe für die Datenbank
            relative_pdf_path = os.path.join(f'project_{project.id}', 'stundenberichte', pdf_filename)

            # PDF-Pfad zur Stundenbericht-Tabelle hinzufügen
            timesheet.pdf_path = relative_pdf_path

            # PDF auch in der Dateitabelle erfassen
            pdf_file = File(
                filename=pdf_filename,
                original_filename=f"Stundenbericht_{timesheet.date.strftime('%Y-%m-%d')}.pdf",
                file_type='stundenbericht',
                file_path=relative_pdf_path,
                file_size=os.path.getsize(pdf_path),
                project_id=project.id,
                uploader_id=current_user.id
            )
            db.session.add(pdf_file)
            db.session.commit()

            flash('Stundenbericht wurde erfolgreich erstellt und als PDF gespeichert!', 'success')
            return redirect(url_for('projects.view_project', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Fehler beim Speichern des Stundenberichts: {str(e)}", "danger")
            return redirect(url_for('projects.view_project', project_id=project.id))

    # Hier sollte das spezielle Template für Fortuna verwendet werden
    return render_template(
        'timesheets/new_fortuna.html',  # Verwenden Sie das Fortuna-Template
        title='Neuer Bau-Tagesbericht',
        form=form,
        project=project
    )