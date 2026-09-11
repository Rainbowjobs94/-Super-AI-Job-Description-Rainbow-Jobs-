from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from src.guardian.community_guardian import CommunityGuardian
from src.github_integration import GitHubIntegration, GitHubAPIError

app = Flask(__name__)
guardian_instance = CommunityGuardian()
github_client = GitHubIntegration()

# Base directory is the project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Allowed file extensions for write/upload operations
ALLOWED_EXTENSIONS = {'txt', 'json', 'md', 'py', 'html', 'js', 'css', 'yml', 'yaml', 'sol', 'csv', 'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _get_safe_path(filepath: str) -> Path:
    """Validate and resolve file path within BASE_DIR to prevent path traversal."""
    filepath = filepath.lstrip('/\\')
    path_obj = Path(filepath)
    if path_obj.is_absolute():
        try:
            path_obj = path_obj.relative_to(path_obj.anchor)
        except ValueError:
            raise ValueError('Invalid file path')

    target_path = (BASE_DIR / path_obj).resolve()
    if not target_path.is_relative_to(BASE_DIR):
        raise ValueError('Invalid file path')
    return target_path


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/files', methods=['GET'])
def list_files():
    """List files in the project workspace."""
    files = []
    try:
        for p in BASE_DIR.rglob('*'):
            if p.is_file() and not any(part.startswith('.') or part in ['venv', '__pycache__'] for part in p.parts):
                rel_path = p.relative_to(BASE_DIR)
                files.append({
                    'name': p.name,
                    'path': str(rel_path),
                    'type': 'file'
                })
        return jsonify({'status': 'success', 'files': files})
    except OSError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/files/read', methods=['GET'])
def read_file():
    """Read content of a specified file."""
    filepath = request.args.get('path', '')
    if not filepath:
        return jsonify({'status': 'error', 'message': 'Missing path parameter'}), 400

    try:
        target_path = _get_safe_path(filepath)
        if not target_path.exists():
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        with open(target_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({'status': 'success', 'content': content})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except OSError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/files/write', methods=['POST'])
def write_file():
    """Write content to a specified file."""
    data = request.get_json()
    if not data or 'path' not in data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Missing path or content'}), 400

    try:
        target_path = _get_safe_path(data['path'])
        if not allowed_file(target_path.name):
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])

        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except OSError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    """Handle file upload and save to workspace."""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'No selected file'}), 400

    provided_path = request.form.get('path', '').strip()
    if provided_path:
        filepath = provided_path
    else:
        filepath = secure_filename(file.filename)

    try:
        target_path = _get_safe_path(filepath)
        if not allowed_file(target_path.name):
            return jsonify({'status': 'error', 'message': 'File type not allowed'}), 400

        target_path.parent.mkdir(parents=True, exist_ok=True)
        file.save(target_path)
        return jsonify({'status': 'success', 'path': str(target_path.relative_to(BASE_DIR))})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except OSError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint interacting with Physical-23 Community Guardian."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Missing message'}), 400

    user_msg = data['message'].lower()
    if 'status' in user_msg or 'health' in user_msg:
        report = guardian_instance.generate_status_report()
        ai_response = f"Community Guardian Status: Mode={report['agent']['mode']}, Health Score={report['community_health']['score']} ({report['community_health']['status']}). Active Platforms: {', '.join(report['platform_details']['active_platforms'])}"
    elif 'report' in user_msg:
        report_path = guardian_instance.save_report()
        ai_response = f"Generated new community status report at: {report_path}"
    elif 'build' in user_msg or 'archive' in user_msg:
        archive_path = guardian_instance.build_repo_archive()
        ai_response = f"I have built the AiRainbowRepo archive. You can find it at {archive_path}."
    else:
        ai_response = f"I am Physical-23, the Community Guardian. I can provide a 'status' update, generate a 'report', or 'build' the repo archive. I received your message: '{data['message']}'"

    return jsonify({
        'status': 'success',
        'response': ai_response
    })


@app.route('/api/repo/tree', methods=['GET'])
def repo_tree():
    """List files/directories in the GitHub repository at an optional path."""
    path = request.args.get('path', '')
    try:
        entries = github_client.get_repo_tree(path)
        return jsonify({'status': 'success', 'entries': entries})
    except GitHubAPIError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 502


@app.route('/api/repo/file', methods=['GET'])
def repo_file():
    """Return the text content of a file in the GitHub repository."""
    path = request.args.get('path', '')
    if not path:
        return jsonify({'status': 'error', 'message': 'Missing path parameter'}), 400
    try:
        content = github_client.get_file_content(path)
        return jsonify({'status': 'success', 'path': path, 'content': content})
    except GitHubAPIError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 502


@app.route('/api/repo/all-files', methods=['GET'])
def repo_all_files():
    """Return a flat list of every file in the GitHub repository (recursive)."""
    try:
        tree = github_client.get_flat_tree()
        files = [item for item in tree if item['type'] == 'blob']
        return jsonify({'status': 'success', 'files': files})
    except GitHubAPIError as exc:
        return jsonify({'status': 'error', 'message': str(exc)}), 502


if __name__ == '__main__':
    app.run(debug=False, port=5000)
