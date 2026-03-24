import unittest
import json
import io
import os
import tempfile
from pathlib import Path
from src.hub import app

class HubTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Override upload folder for testing
        self.test_dir = tempfile.TemporaryDirectory()
        app.config['UPLOAD_FOLDER'] = Path(self.test_dir.name).resolve()

    def tearDown(self):
        self.test_dir.cleanup()

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_chat_success(self):
        test_message = "Hello AI"
        response = self.app.post('/chat',
                                 data=json.dumps({'message': test_message}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)
        self.assertIn(test_message, data['response'])

    def test_chat_no_message(self):
        response = self.app.post('/chat',
                                 data=json.dumps({}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_success(self):
        test_file_content = b"my test file content"
        test_filename = "test_upload.txt"

        data = {
            'file': (io.BytesIO(test_file_content), test_filename)
        }

        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertIn('message', response_data)
        self.assertIn(test_filename, response_data['message'])

        # Verify file is on disk
        saved_file = app.config['UPLOAD_FOLDER'] / test_filename
        self.assertTrue(saved_file.exists())
        with open(saved_file, 'rb') as f:
            self.assertEqual(f.read(), test_file_content)

    def test_upload_no_file_part(self):
        response = self.app.post('/upload', data={}, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

    def test_upload_no_selected_file(self):
        data = {
            'file': (io.BytesIO(b""), "")
        }
        response = self.app.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    unittest.main()
