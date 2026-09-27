import unittest
import json
from src.hub import app

class TestHubChat(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_chat_endpoint_success(self):
        response = self.client.post(
            '/api/chat',
            data=json.dumps({'message': 'Hello AI'}),
            content_type='application/json'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertIn("I am Physical-23", data['response'])
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

    def test_chat_endpoint_fix_file(self):
        # Create a temporary file with trailing whitespace
        import os
        test_file = 'test_fix.txt'
        with open(test_file, 'w') as f:
            f.write('line 1 \nline 2\t\nline 3  ')

        try:
            response = self.client.post(
                '/api/chat',
                data=json.dumps({'message': f'Please fix {test_file}'}),
                content_type='application/json'
            )
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['status'], 'success')
            self.assertIn(f"I have fixed {test_file}", data['response'])

            with open(test_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, 'line 1\nline 2\nline 3\n')
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

class TestHubFiles(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

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
