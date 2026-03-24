from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path

app = Flask(__name__)

# Configure upload folder
UPLOAD_FOLDER = Path('data/uploads').resolve()
# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message']

    # Very simple echo bot logic
    ai_response = f"I received your message: {user_message}. How can I assist you further?"

    return jsonify({'response': ai_response})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        save_path = app.config['UPLOAD_FOLDER'] / filename

        # Security check: Ensure the resolved path is within the designated upload folder
        if not save_path.resolve().is_relative_to(app.config['UPLOAD_FOLDER']):
             return jsonify({'error': 'Invalid file path'}), 400

        try:
            file.save(str(save_path))
            return jsonify({'message': f'File {filename} successfully uploaded'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Do not use debug=True with host='0.0.0.0' for security
    app.run(host='0.0.0.0', port=5000, debug=False)
