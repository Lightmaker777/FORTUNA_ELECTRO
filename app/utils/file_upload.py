import os
import uuid
from werkzeug.utils import secure_filename

def save_uploaded_file(file, upload_folder):
    # Ensure upload directory exists
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate a unique filename
    original_filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    
    # Full path to save the file
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    return unique_filename