import unittest
import json
from src.hub import app

class TestHubChat(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['HAB_TOKEN'] = 'test-' + 'x' * 40
        self.client = app.test_client()
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + app.config['HAB_TOKEN']

    def test_chat_endpoint_success(self):
        response = self.client.post(
            '/api/chat',
            data=json.dumps({'message': 'Hello AI'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn("IA Guardian Hab", data['response'])
        self.assertIn("Hello AI", data['response'])

    def test_chat_endpoint_missing_message(self):
        response = self.client.post(
            '/api/chat',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Missing message')

    def test_chat_endpoint_fix_command(self):
        import tempfile
        import os
        from pathlib import Path

        # Create a temp file inside docs/ since it's an allowed directory
        base_dir = Path(__file__).resolve().parent.parent
        docs_dir = base_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)

        with tempfile.NamedTemporaryFile(dir=docs_dir, delete=False, suffix='.txt') as f:
            f.write(b"line 1 \nline 2\t\n")
            temp_path = Path(f.name)

        try:
            rel_path = temp_path.relative_to(base_dir)
            response = self.client.post(
                '/api/chat',
                data=json.dumps({'message': f'Please fix {rel_path}'}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertIn("Fixed", data['response'])

            fixed_content = temp_path.read_text()
            self.assertEqual(fixed_content, "line 1\nline 2\n")
        finally:
            if temp_path.exists():
                os.remove(temp_path)

class TestHubFiles(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['HAB_TOKEN'] = 'test-' + 'x' * 40
        self.client = app.test_client()
        self.client.environ_base['HTTP_AUTHORIZATION'] = 'Bearer ' + app.config['HAB_TOKEN']

    def test_list_files(self):
        response = self.client.get('/api/files')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIsInstance(data['files'], list)

        # Check if 'src/hub.py' is in the files list
        file_paths = [f['path'] for f in data['files']]
        self.assertIn('src/hub.py', file_paths)

    def test_read_file_success(self):
        response = self.client.get('/api/files/read?path=src/hub.py')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn('from flask import Flask', data['content'])

    def test_read_file_missing_path(self):
        response = self.client.get('/api/files/read')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Missing path parameter')

    def test_read_file_path_traversal(self):
        response = self.client.get('/api/files/read?path=../etc/passwd')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid file path')

    def test_write_file_path_traversal(self):
        response = self.client.post(
            '/api/files/write',
            data=json.dumps({
                'path': '../test_out_of_bounds.txt',
                'content': 'test'
            }),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['message'], 'Invalid file path')

if __name__ == '__main__':
    unittest.main()
