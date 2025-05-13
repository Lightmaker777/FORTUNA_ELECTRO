# app\forms\user_forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models.user import User

class AddUserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Passwort bestätigen', 
                                   validators=[DataRequired(), EqualTo('password', message='Passwörter müssen übereinstimmen.')])
    is_admin = BooleanField('Administrator-Rechte')
    submit = SubmitField('Speichern')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Dieser Benutzername ist bereits vergeben. Bitte wählen Sie einen anderen.')

class EditUserForm(FlaskForm):
    user_id = HiddenField('User ID')
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=50)])
    is_admin = BooleanField('Administrator-Rechte')
    is_active = BooleanField('Aktiv')
    submit = SubmitField('Speichern')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and str(user.id) != self.user_id.data:
            raise ValidationError('Dieser Benutzername ist bereits vergeben. Bitte wählen Sie einen anderen.')

class ResetPasswordForm(FlaskForm):
    user_id = HiddenField('User ID')
    new_password = PasswordField('Neues Passwort', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Passwort bestätigen', 
                                   validators=[DataRequired(), EqualTo('new_password', message='Passwörter müssen übereinstimmen.')])
    submit = SubmitField('Passwort zurücksetzen')

class DeleteUserForm(FlaskForm):
    user_id = HiddenField('User ID',validators=[DataRequired()])
    submit = SubmitField('Löschen')