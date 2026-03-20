import os
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Security: Define base path to restrict file access
BASE_DIR = Path(__file__).parent.parent.resolve()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Simple chat endpoint mimicking AI responses."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    user_message = data['message']

    # Simple dummy response for testing
    response = f"AI Guardian received: {user_message}"

    return jsonify({'response': response})

@app.route('/api/files', methods=['GET'])
def list_files():
    """List files in the repository."""
    try:
        files = []
        for root, dirs, filenames in os.walk(BASE_DIR):
            # Skip hidden directories like .git
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for filename in filenames:
                if filename.startswith('.'):
                    continue
                file_path = Path(root) / filename
                # Use relative path from BASE_DIR
                rel_path = file_path.relative_to(BASE_DIR)
                files.append(str(rel_path))

        return jsonify({'files': sorted(files)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/files/<path:filepath>', methods=['GET', 'POST', 'PUT'])
def manage_file(filepath):
    """Read or write to a file."""
    try:
        target_path = (BASE_DIR / filepath).resolve()

        # Security check: ensure path is within BASE_DIR
        if not target_path.is_relative_to(BASE_DIR):
            return jsonify({'error': 'Access denied'}), 403

        if request.method == 'GET':
            if not target_path.exists():
                return jsonify({'error': 'File not found'}), 404
            if not target_path.is_file():
                return jsonify({'error': 'Not a file'}), 400

            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content})

        elif request.method in ['POST', 'PUT']:
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'error': 'Content is required'}), 400

            # Create parent directories if they don't exist
            target_path.parent.mkdir(parents=True, exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(data['content'])

            return jsonify({'success': True, 'message': 'File saved successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
