import os
from werkzeug.utils import secure_filename

def handle_upload(files, entity_id, folder):
    upload_path = f'static/uploads/{folder}/{entity_id}/'
    os.makedirs(upload_path, exist_ok=True)
    for file in files:
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_path, filename))

def paginate(query, page, per_page=10):
    return query.paginate(page=page, per_page=per_page, error_out=False)

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, folder):
    if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
        filename = secure_filename(file.filename)
        upload_path = os.path.join('static/uploads', folder)
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        return filename
    return None
