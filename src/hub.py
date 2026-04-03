from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from src.guardian.community_guardian import CommunityGuardian

app = Flask(__name__)
guardian_instance = CommunityGuardian()

# Base directory is the project root
BASE_DIR = Path(__file__).resolve().parent.parent



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/files', methods=['GET'])
def list_files():
    try:
        files = []
        for path in BASE_DIR.rglob('*'):
            # Skip hidden files and directories
            if any(part.startswith('.') for part in path.parts):
                continue
            # Skip __pycache__ and binary/build artifacts if needed
            if '__pycache__' in path.parts:
                continue
            if path.is_file():
                try:
                    rel_path = path.relative_to(BASE_DIR)
                    files.append({
                        'name': path.name,
                        'path': str(rel_path),
                        'type': 'file'
                    })
                except ValueError:
                    pass
        return jsonify({'status': 'success', 'files': files})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files/read', methods=['GET'])
def read_file():
    filepath = request.args.get('path')
    if not filepath:
        return jsonify({'status': 'error', 'message': 'Missing path parameter'}), 400

    try:
        # Resolve the path and explicitly check if it's within BASE_DIR
        target_path = (BASE_DIR / filepath).resolve()

        # Security check: ensure path is within BASE_DIR
        if not target_path.is_relative_to(BASE_DIR):
            return jsonify({'status': 'error', 'message': 'Invalid file path'}), 403

        if not target_path.exists() or not target_path.is_file():
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        content = target_path.read_text(encoding='utf-8')
        return jsonify({'status': 'success', 'content': content})
    except UnicodeDecodeError:
        return jsonify({'status': 'error', 'message': 'File is not a text file'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files/write', methods=['POST'])
def write_file():
    data = request.json
    if not data or 'path' not in data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Missing path or content'}), 400

    filepath = data['path']
    content = data['content']

    try:
        # Resolve the path and explicitly check if it's within BASE_DIR
        target_path = (BASE_DIR / filepath).resolve()

        # Security check: ensure path is within BASE_DIR
        if not target_path.is_relative_to(BASE_DIR):
            return jsonify({'status': 'error', 'message': 'Invalid file path'}), 403

        # Ensure parent directories exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(content, encoding='utf-8')
        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    provided_path = request.form.get('path', '').strip()
    if provided_path:
        # Apply secure_filename only to the base filename to preserve directory structure intent
        filepath = str(Path(provided_path) / secure_filename(file.filename))
    else:
        filepath = secure_filename(file.filename)

    try:
        target_path = (BASE_DIR / filepath).resolve()

        if not target_path.is_relative_to(BASE_DIR):
            return jsonify({'status': 'error', 'message': 'Invalid file path'}), 403

        target_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(str(target_path))
        return jsonify({'status': 'success', 'message': 'File uploaded successfully', 'path': str(target_path.relative_to(BASE_DIR))})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Missing message'}), 400

    user_message = data['message'].lower()

    if 'status' in user_message or 'health' in user_message:
        report = guardian_instance.generate_status_report()
        health = report['community_health']
        ai_response = f"Community Health is currently {health['health_score']} ({health['health_status']}). We have {health['active_streams']} active streams across {', '.join(health['active_platforms'])}."
    elif 'report' in user_message:
        report = guardian_instance.generate_status_report()
        saved_path = guardian_instance.save_report(report)
        ai_response = f"I have generated and saved a new status report to {saved_path}."
    elif 'archive' in user_message or 'build' in user_message:
        archive_path = guardian_instance.build_repo_archive()
        ai_response = f"I have built the AiRainbowRepo archive. You can find it at {archive_path}."
    else:
        ai_response = f"I am Physical-23, the Community Guardian. I can provide a 'status' update, generate a 'report', or 'build' the repo archive. I received your message: '{data['message']}'"

    return jsonify({
        'status': 'success',
        'response': ai_response
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000)
