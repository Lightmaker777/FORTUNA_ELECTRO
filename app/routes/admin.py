# app/routes/admin.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app import db
from app.models.user import User
from app.utils.decorators import admin_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, ValidationError

admin = Blueprint('admin', __name__)

class UserForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired(), Length(min=3, max=64)])
    password = PasswordField('Passwort', validators=[DataRequired(), Length(min=6)])
    role = SelectField('Rolle', choices=[
        ('installateur', 'Installateur'),
        ('admin', 'Administrator')
    ], validators=[DataRequired()])
    is_active = BooleanField('Aktiv', default=True)
    submit = SubmitField('Speichern')
    
    def validate_username(self, username):
        # Überprüfe bei neuen Benutzern, ob der Benutzername bereits existiert
        if self.user_id is None:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Dieser Benutzername ist bereits vergeben.')
    
    def __init__(self, user_id=None, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.user_id = user_id

@admin.route('/admin/users')
@login_required
@admin_required
def list_users():
    users = User.query.all()
    return render_template('admin/users.html', title='Mitarbeiterverwaltung', users=users)

@admin.route('/admin/user/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_user():
    form = UserForm()
    
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Benutzer "{user.username}" wurde erfolgreich erstellt!', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template('admin/user_form.html', title='Neuer Mitarbeiter', form=form)

@admin.route('/admin/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(user_id=user_id)
    
    if request.method == 'GET':
        form.username.data = user.username
        form.role.data = user.role
        form.is_active.data = user.is_active
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        user.is_active = form.is_active.data
        
        # Passwort nur ändern, wenn eines eingegeben wurde
        if form.password.data:
            user.set_password(form.password.data)
        
        db.session.commit()
        
        flash(f'Benutzer "{user.username}" wurde erfolgreich aktualisiert!', 'success')
        return redirect(url_for('admin.list_users'))
    
    return render_template(
        'admin/user_form.html',
        title='Mitarbeiter bearbeiten',
        form=form,
        user=user
    )

@admin.route('/admin/user/<int:user_id>/delete')
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Sie können sich nicht selbst löschen!', 'danger')
        return redirect(url_for('admin.list_users'))
    
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    flash(f'Benutzer "{username}" wurde erfolgreich gelöscht!', 'success')
    return redirect(url_for('admin.list_users'))