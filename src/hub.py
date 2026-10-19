from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path
from src.guardian.community_guardian import CommunityGuardian
from src.github_integration import GitHubIntegration, GitHubAPIError
from src.hab.web import api as hab_api
from src.hab.core import flags_for, private_path, safe_name
import os
import hmac

app = Flask(__name__)
app.config.update(
    HAB_TOKEN=os.environ.get("HAB_OPERATOR_TOKEN", ""),
    HAB_STORE=os.environ.get("HAB_STORE", "data/hab"),
    HAB_DESTINATION="data/transfer-preview",
    HAB_PLANNING_LIMIT=int(os.environ.get("HAB_PLANNING_LIMIT", "100")),
    HAB_LEGACY_WRITES=False,
    MAX_CONTENT_LENGTH=16 * 1024 * 1024,
)
app.register_blueprint(hab_api)
guardian_instance = CommunityGuardian()
github_client = GitHubIntegration()

# Base directory is the project root
BASE_DIR = Path(__file__).resolve().parent.parent

@app.before_request
def protect_operator_api():
    if request.path.startswith("/api/"):
        expected = app.config["HAB_TOKEN"]
        if not expected or len(expected) < 32:
            return jsonify(status="error", message="Operator access is not provisioned"), 503
        supplied = request.headers.get("Authorization", "")
        if not hmac.compare_digest(supplied.encode(), ("Bearer " + expected).encode()):
            return jsonify(status="error", message="Operator authorization required"), 401
        if request.is_json and not isinstance(request.get_json(silent=True), dict):
            return jsonify(status="error", message="JSON object required"), 400


@app.after_request
def private_response(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'"
    return response


@app.errorhandler(413)
def too_large(error):
    return jsonify(status="error", message="Upload exceeds the 16 MiB request limit"), 413


def _get_safe_path(filepath):
    """
    Resolves the given filepath relative to BASE_DIR and ensures it is within BASE_DIR.
    Raises ValueError if the path is invalid or outside BASE_DIR.
    """
    if not isinstance(filepath, str):
        raise ValueError("Invalid file path")
    try:
        safe_name(filepath)
    except ValueError:
        raise ValueError("Invalid file path") from None
    if private_path(filepath) or any(p.startswith(".") for p in Path(filepath).parts):
        raise ValueError("Invalid file path")
    if Path(filepath).parts[0] not in {"src", "docs", "tests", "README.md", "SKILLS.md"}:
        raise ValueError("Invalid file path")
    target_path = BASE_DIR / filepath
    if any(p.is_symlink() for p in [target_path, *target_path.parents] if p != BASE_DIR):
        raise ValueError("Invalid file path")
    target_path = target_path.resolve()

    if not target_path.is_relative_to(BASE_DIR):
        raise ValueError("Invalid file path")

    return target_path

@app.route('/')
def index():
    return render_template('hab.html')


@app.route('/legacy')
def legacy():
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
                    _get_safe_path(str(rel_path))
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
        target_path = _get_safe_path(filepath)

        if not target_path.exists() or not target_path.is_file():
            return jsonify({'status': 'error', 'message': 'File not found'}), 404

        if target_path.stat().st_size > 256 * 1024:
            return jsonify(status="error", message="Text preview exceeds 256 KiB"), 400
        if flags_for(filepath, target_path.read_bytes()):
            return jsonify(status="error", message="Restricted content excluded from preview"), 403
        content = target_path.read_text(encoding='utf-8')
        return jsonify({'status': 'success', 'content': content})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
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
        target_path = _get_safe_path(filepath)

        if not app.config["HAB_LEGACY_WRITES"]:
            return jsonify(status="error", message="Legacy source writes disabled; use reviewed CLI merge"), 403
        if not isinstance(content, str) or len(content.encode()) > 256 * 1024:
            return jsonify(status="error", message="Invalid content"), 400
        if flags_for(filepath, content.encode()):
            return jsonify(status="error", message="Restricted content"), 403
        # Ensure parent directories exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        target_path.write_text(content, encoding='utf-8')
        return jsonify({'status': 'success', 'message': 'File saved successfully'})
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 403
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    # Legacy upload now uses quarantine intake, never project overwrite.
    from src.hab.web import intake
    if request.form.get("path"):
        return jsonify(status="error", message="Upload cannot write project paths; use reviewed mappings"), 400
    return intake()


@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'status': 'error', 'message': 'Missing message'}), 400

    if not isinstance(data["message"], str) or len(data["message"]) > 12000:
        return jsonify(status="error", message="Invalid message"), 400
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
        ai_response = "Use the Hab catalog to export inspected source bytes. Imported code is never executed. The historical AiRainbowRepo generator remains a legacy example, not deployment evidence."
    elif user_message.startswith('please fix '):
        file_to_fix = data['message'][11:].strip() # extract the file path case-preserving
        try:
            target_path = _get_safe_path(file_to_fix)
            if target_path.exists() and target_path.is_file():
                try:
                    content = target_path.read_text(encoding='utf-8')
                    fixed_lines = [line.rstrip() for line in content.splitlines()]
                    fixed_content = '\n'.join(fixed_lines) + '\n'
                    target_path.write_text(fixed_content, encoding='utf-8')
                    ai_response = f"Fixed file {file_to_fix} successfully."
                except UnicodeDecodeError:
                    ai_response = f"Error: {file_to_fix} is not a text file."
            else:
                ai_response = f"Error: File {file_to_fix} not found."
        except ValueError as e:
            ai_response = f"Error: {str(e)}"
    else:
        ai_response = f"I am IA Guardian Hab (legacy agent: Physical-23). Use the request planner for candidate tasks; it does not run a general AI model. I received your message: '{data['message']}'"

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
