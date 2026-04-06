import unittest
import json
import io
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


    def test_upload_file_standard(self):
        response = self.client.post(
            '/api/files/upload',
            data={
                'file': (io.BytesIO(b"test content"), 'test.txt')
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')

    def test_upload_file_custom_path(self):
        response = self.client.post(
            '/api/files/upload',
            data={
                'file': (io.BytesIO(b"test content"), 'test.txt'),
                'path': 'my folder/test file.txt'
            },
            content_type='multipart/form-data'
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'success')
        self.assertTrue('my folder/test_file.txt' in data['path'])

if __name__ == '__main__':
    unittest.main()
