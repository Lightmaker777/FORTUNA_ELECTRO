# app/forms.py
from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, SubmitField, HiddenField
from wtforms.validators import DataRequired
from datetime import datetime

# ... Existierende Form-Definitionen ...

class ProjectStatusForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('in_bearbeitung', 'In Bearbeitung'),
        ('archiviert', 'Archiviert')
    ], validators=[DataRequired()])

class ProjectEndDateForm(FlaskForm):
    end_date = DateField('Enddatum', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Speichern')