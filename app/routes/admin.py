# app\routes\admin.py - Verbesserte Version mit zusätzlichem Schutz
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models.user import User
from app.forms.user_forms import AddUserForm, EditUserForm, ResetPasswordForm, DeleteUserForm
from app.utils.decorators import admin_required
from app import db

# Define the blueprint with a more specific name to avoid conflicts with Flask-Admin
admin = Blueprint('custom_admin', __name__, url_prefix='/custom-admin')

@admin.before_request
def check_admin():
    if not current_user.is_authenticated or not current_user.is_admin():
        flash('Sie benötigen Administratorrechte, um auf diese Seite zuzugreifen.', 'danger')
        return redirect(url_for('auth.login'))

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
                          delete_user_form=delete_user_form,
                          current_user=current_user)

@admin.route('/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    """Add a new user."""
    form = AddUserForm()
    if form.validate_on_submit():
        # Setze die Rolle basierend auf der Checkbox
        role = 'admin' if form.is_admin.data else 'installateur'
        
        user = User(
            username=form.username.data,
            role=role,  # Rolle direkt setzen
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
    return redirect(url_for('custom_admin.list_users'))

@admin.route('/users/edit', methods=['POST'])
@login_required
@admin_required
def edit_user():
    """Edit an existing user."""
    form = EditUserForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)
        
        # Verhindern, dass der Standard-Admin-Account (username='admin') bearbeitet wird
        if user.username == 'admin' and user.username != form.username.data:
            flash('Der Hauptadministrator-Account kann nicht umbenannt werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
            
        # Verhindern, dass der Standard-Admin-Account deaktiviert wird
        if user.username == 'admin' and not form.is_active.data:
            flash('Der Hauptadministrator-Account kann nicht deaktiviert werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
            
        # Verhindern, dass dem Standard-Admin-Account die Admin-Rechte entzogen werden
        if user.username == 'admin' and not form.is_admin.data:
            flash('Dem Hauptadministrator-Account können die Admin-Rechte nicht entzogen werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
        
        user.username = form.username.data
        
        # Setze die Rolle basierend auf der Checkbox
        user.role = 'admin' if form.is_admin.data else 'installateur'
        
        user.is_active = form.is_active.data
        db.session.commit()
        flash(f'Benutzer {user.username} wurde erfolgreich aktualisiert.', 'success')
    return redirect(url_for('custom_admin.list_users'))

@admin.route('/users/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password():
    """Reset user's password."""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.get_or_404(form.user_id.data)
        
        # NEUE PRÜFUNG: Verhindern, dass das Passwort des Standard-Admin-Accounts zurückgesetzt wird
        if user.username == 'admin':
            flash('Das Passwort des Hauptadministrator-Accounts kann nicht geändert werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
            
        user.set_password(form.new_password.data)
        db.session.commit()
        flash(f'Das Passwort für Benutzer {user.username} wurde zurückgesetzt.', 'success')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{getattr(form, field).label.text}: {error}', 'danger')
    
    return redirect(url_for('custom_admin.list_users'))

@admin.route('/users/delete', methods=['POST'])
@login_required
@admin_required
def delete_user():
    """Delete a user."""
    if 'user_id' in request.form:
        user_id = request.form.get('user_id')
        
        try:
            user = User.query.get_or_404(user_id)
            
            # Prüfen, ob es sich um den Hauptadmin-Account handelt
            if user.username == 'admin':
                flash('Der Hauptadministrator-Account kann nicht gelöscht werden.', 'danger')
                return redirect(url_for('custom_admin.list_users'))
            
            # Prüfen, ob der Benutzer sich selbst löschen möchte
            if user.id == current_user.id:
                flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
                return redirect(url_for('custom_admin.list_users'))
            
            # Prüfen, ob der zu löschende Benutzer Administrator ist
            if user.is_admin():
                flash('Administratoren können nicht gelöscht werden.', 'danger')
                return redirect(url_for('custom_admin.list_users'))
            
            username = user.username
            db.session.delete(user)
            db.session.commit()
            flash(f'Benutzer {username} wurde erfolgreich gelöscht.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Fehler beim Löschen des Benutzers: {str(e)}', 'danger')
    else:
        flash('User ID nicht gefunden!', 'danger')
    
    return redirect(url_for('custom_admin.list_users'))

# Alternative direct URL approach - improved with the same safety checks
@admin.route('/users/delete-direct/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def delete_user_direct(user_id):
    """Delete a user directly via URL."""
    try:
        user = User.query.get_or_404(user_id)
        
        # Prüfen, ob es sich um den Hauptadmin-Account handelt
        if user.username == 'admin':
            flash('Der Hauptadministrator-Account kann nicht gelöscht werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
        
        # Prüfen, ob der Benutzer sich selbst löschen möchte
        if user.id == current_user.id:
            flash('Sie können Ihren eigenen Benutzer nicht löschen.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
        
        # Prüfen, ob der zu löschende Benutzer Administrator ist
        if user.is_admin():
            flash('Administratoren können nicht gelöscht werden.', 'danger')
            return redirect(url_for('custom_admin.list_users'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        flash(f'Benutzer {username} wurde erfolgreich gelöscht.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Fehler beim Löschen des Benutzers: {str(e)}', 'danger')
    
    return redirect(url_for('custom_admin.list_users'))