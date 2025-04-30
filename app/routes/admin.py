from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import AddUserForm, EditUserForm, ResetPasswordForm, DeleteUserForm
from app.utils.decorators import admin_required
from app import db

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.route('/users', methods=['GET'])
@login_required
@admin_required
def list_users():
    """Display list of all users."""
    users = User.query.all()
    add_user_form = AddUserForm()
    edit_user_form = EditUserForm()
    reset_password_form = ResetPasswordForm()
    delete_user_form = DeleteUserForm()
    
    return render_template('admin/users.html', 
                          title='Mitarbeiterverwaltung', 
                          users=users,
                          add_user_form=add_user_form,
                          edit_user_form=edit_user_form,
                          reset_password_form=reset_password_form,
                          delete_user_form=delete_user_form)

@admin.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    form = AddUserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            is_admin=form.is_admin.data,
            is_active=True
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Benutzer {form.username.data} wurde erfolgreich erstellt.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    return redirect(url_for('admin.list_users'))

@admin.route('/users/edit', methods=['POST'])
@login_required
@admin_required
def edit_user():
    """Edit an existing user."""
    form = EditUserForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)
        user.username = form.username.data
        user.is_admin = form.is_admin.data
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f'Benutzer {user.username} wurde erfolgreich aktualisiert.', 'success')
    return redirect(url_for('admin.list_users'))

@admin.route('/users/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password():
    """Reset user's password."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(f'Das Passwort für Benutzer {user.username} wurde zurückgesetzt.', 'success')
    return redirect(url_for('admin.list_users'))

@admin.route('/users/delete', methods=['POST'])
@login_required
@admin_required
def delete_user():
    """Delete a user."""
    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)
        if user.id == current_user.id:
            flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
        else:
            username = user.username
            db.session.delete(user)
            db.session.commit()
            flash(f'Benutzer {username} wurde erfolgreich gelöscht.', 'success')
    return redirect(url_for('admin.list_users'))