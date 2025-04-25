# app/forms/file_forms.py

from flask_wtf import FlaskForm
from wtforms import FileField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class FileUploadForm(FlaskForm):
    file = FileField('Datei auswählen', validators=[DataRequired()])
    file_type = SelectField('Dateityp auswählen', choices=[
        ('foto', 'Foto'),
        ('video', 'Video'),
        ('stundenbericht', 'Stundenbericht'),
        ('pruefbericht', 'Prüfbericht'),
        ('sonstiges', 'Sonstiges')
    ], validators=[DataRequired()])
    description = TextAreaField('Beschreibung (optional)')
    submit = SubmitField('Hochladen')
