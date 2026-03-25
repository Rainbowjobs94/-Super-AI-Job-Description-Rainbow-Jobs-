import os
import logging
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__, template_folder='templates')

UPLOAD_FOLDER = Path('data/uploads').resolve()
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'md', 'json', 'py'}

# Ensure upload directory exists
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Serve the main hub interface."""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages with the AI operator."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']

    # Simple simulated response for now
    response_text = f"Received your message: '{user_message}'. I am the AI operator ready to assist you."

    return jsonify({'response': response_text}), 200

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file uploads securely."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        if not filename:
            return jsonify({'error': 'Invalid filename'}), 400

        file_path = (app.config['UPLOAD_FOLDER'] / filename).resolve()

        # Security check: Ensure the path is within the upload folder
        if not file_path.is_relative_to(app.config['UPLOAD_FOLDER']):
             return jsonify({'error': 'Invalid file path'}), 400

        try:
            file.save(str(file_path))
            return jsonify({'message': f'File {filename} successfully uploaded.'}), 200
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return jsonify({'error': 'Failed to save file'}), 200

    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/api/files', methods=['GET'])
def list_files():
    """List uploaded files."""
    try:
        files = []
        for file_path in app.config['UPLOAD_FOLDER'].iterdir():
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size
                })
        return jsonify({'files': files}), 200
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': 'Failed to list files'}), 200

if __name__ == '__main__':
    # DO NOT use debug=True combined with host='0.0.0.0'
    # Binding to localhost for development
    app.run(host='127.0.0.1', port=2000)
