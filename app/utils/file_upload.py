import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
from app import db
from app.models.file import File

def save_uploaded_file(file, project_id, uploader_id, file_type='sonstiges'):
    """
    Save an uploaded file with a unique name and create a database record
    
    :param file: FileStorage object from Flask
    :param project_id: ID of the project the file belongs to
    :param uploader_id: ID of the user uploading the file
    :param file_type: Type of file (default: 'sonstiges')
    :return: File model instance
    """
    # Ensure upload directory exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate a unique filename
    original_filename = secure_filename(file.filename)
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Full path to save the file
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    # Create a database record
    new_file = File(
        filename=unique_filename,
        original_filename=original_filename,
        file_type=file_type,
        file_path=unique_filename,  # Store just the filename
        file_size=file_size,
        project_id=project_id,
        uploader_id=uploader_id
    )
    
    db.session.add(new_file)
    db.session.commit()
    
    return new_file

def get_file_full_path(filename):
    """
    Retrieve the full path of a stored file
    
    :param filename: Stored filename
    :return: Full path to the file
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return os.path.join(upload_folder, filename)