import unittest
import json
import tempfile
import os
from pathlib import Path
from src.hub import app, BASE_DIR

class HubTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        # Keep track of temporary files to clean up
        self.test_files = []

    def tearDown(self):
        # Clean up any created files
        for f in self.test_files:
            try:
                os.remove(f)
            except OSError:
                pass

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Operator Hub', response.data)

    def test_chat_success(self):
        response = self.client.post('/api/chat', json={'message': 'Hello test'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertEqual(data['response'], 'AI Guardian received: Hello test')

    def test_chat_missing_message(self):
        response = self.client.post('/api/chat', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_list_files(self):
        response = self.client.get('/api/files')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('files', data)
        # Assuming src/hub.py always exists now
        self.assertIn('src/hub.py', data['files'])
        # Also .git files shouldn't be listed
        for f in data['files']:
            self.assertFalse(f.startswith('.git'))

    def test_manage_file_read(self):
        response = self.client.get('/api/files/src/hub.py')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('content', data)
        self.assertIn('app = Flask(__name__)', data['content'])

    def test_manage_file_read_not_found(self):
        response = self.client.get('/api/files/does_not_exist.txt')
        self.assertEqual(response.status_code, 404)

    def test_manage_file_write(self):
        test_file_path = 'src/test_temp_write.txt'
        full_path = str(BASE_DIR / test_file_path)
        self.test_files.append(full_path)

        response = self.client.post(f'/api/files/{test_file_path}', json={'content': 'test data'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data.get('success'))

        # Verify file was actually written
        with open(full_path, 'r') as f:
            self.assertEqual(f.read(), 'test data')

    def test_manage_file_security(self):
        # Attempt path traversal
        response = self.client.get('/api/files/../etc/passwd')
        self.assertEqual(response.status_code, 403)

if __name__ == '__main__':
    unittest.main()
