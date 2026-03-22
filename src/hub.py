import os
import pathlib
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import sys

# Ensure ai_operator_agent can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from ai_operator_agent import Physical23Agent, OperationalMode
except ImportError:
    pass

app = Flask(__name__, template_folder='templates')

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = pathlib.Path(__file__).parent.parent / 'data' / 'uploads'
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize AI Agent
try:
    agent = Physical23Agent(agent_id="Physical-23-Web")
    agent.activate()
    agent.set_mode(OperationalMode.COMMUNITY_GUARDIAN)
except Exception as e:
    print(f"Warning: Could not initialize AI agent: {e}")
    agent = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']

    if agent:
        # Simulate agent processing the message
        # In a real scenario, we'd pass this to an LLM or specific agent method
        # Here we just use the community guardian's assessment as a response mock
        if 'health' in user_message.lower():
            health = agent.assess_community_health()
            response = f"Community Health: {health['overall_score']:.0%}. Status: {health['status']}."
        elif 'trend' in user_message.lower():
            trends = agent.identify_trends()
            if trends:
                response = f"Top trend: {trends[0]['trend']} (Confidence: {trends[0]['confidence']:.0%})"
            else:
                response = "No recent trends identified."
        else:
            response = f"Agent Physical-23 received your message: '{user_message}'. I am monitoring the community."
    else:
        response = f"Echo: {user_message} (Agent not initialized)"

    return jsonify({'response': response})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)

        # Path traversal prevention
        upload_path = pathlib.Path(app.config['UPLOAD_FOLDER']).resolve()
        file_path = (upload_path / filename).resolve()

        if not file_path.is_relative_to(upload_path):
            return jsonify({'error': 'Invalid file path'}), 400

        try:
            file.save(str(file_path))
            return jsonify({
                'message': 'File successfully uploaded',
                'filename': filename,
                'path': f"/api/files/{filename}"
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/api/files', methods=['GET'])
def list_files():
    files = []
    upload_path = pathlib.Path(app.config['UPLOAD_FOLDER'])
    if upload_path.exists():
        for file_path in upload_path.iterdir():
            if file_path.is_file():
                files.append({
                    'name': file_path.name,
                    'size': file_path.stat().st_size,
                    'url': f"/api/files/{file_path.name}"
                })
    return jsonify({'files': files})

@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    # Path traversal prevention
    upload_path = pathlib.Path(app.config['UPLOAD_FOLDER']).resolve()
    file_path = (upload_path / filename).resolve()

    if not file_path.is_relative_to(upload_path):
        return jsonify({'error': 'Invalid file path'}), 400

    if not file_path.exists() or not file_path.is_file():
        return jsonify({'error': 'File not found'}), 404

    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Using host='127.0.0.1' and debug=False for security
    app.run(host='127.0.0.1', port=5000, debug=False)
