from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
import json
from pathlib import Path

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'repo_files')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Path to the agent configuration
AGENT_CONFIG_PATH = os.path.join(os.getcwd(), 'config', 'agent.json')


@app.route('/')
def index():
    agent_status = {}
    if os.path.exists(AGENT_CONFIG_PATH):
        try:
            with open(AGENT_CONFIG_PATH, 'r') as f:
                agent_status = json.load(f)
        except Exception as e:
            agent_status = {"error": str(e)}

    # List files in repo
    repo_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env'}
    for root, dirs, files in os.walk(os.getcwd()):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            repo_files.append(os.path.relpath(os.path.join(root, file), os.getcwd()))

    return render_template('index.html', status=agent_status, files=repo_files)


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')

    # Simple simulated AI response based on the message
    response = f"AI Operator Agent (Physical-23) received: '{message}'. Currently in community guardian mode. Acknowledged."

    if 'status' in message.lower():
        response += " All systems nominal. Health score is optimal."
    elif 'help' in message.lower():
        response += " I can assist with community monitoring, file management, and status updates."

    return jsonify({"response": response})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = secure_filename(file.filename)
        # Save to a safe upload directory initially, or root if we want it to be part of the repo
        # For this tool, saving to the repo root/repo_files
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        return jsonify({"success": f"File {filename} uploaded successfully to {app.config['UPLOAD_FOLDER']}"})


@app.route('/files/<path:filepath>', methods=['GET'])
def get_file(filepath):
    # Prevent directory traversal
    try:
        base_dir = Path(os.getcwd()).resolve()
        target_path = (base_dir / filepath).resolve()

        if not target_path.is_relative_to(base_dir):
            return "Access denied", 403

        if not target_path.exists() or not target_path.is_file():
            return "File not found", 404

        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/files/<path:filepath>', methods=['POST'])
def update_file(filepath):
    data = request.json
    new_content = data.get('content', '')

    try:
        base_dir = Path(os.getcwd()).resolve()
        target_path = (base_dir / filepath).resolve()

        if not target_path.is_relative_to(base_dir):
            return jsonify({"error": "Access denied"}), 403

        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return jsonify({"success": f"File {filepath} updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000)
