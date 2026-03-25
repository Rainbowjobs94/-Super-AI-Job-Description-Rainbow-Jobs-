import unittest
import json
import io
import os
import shutil
from pathlib import Path
from src.hub import app

class TestHubApp(unittest.TestCase):
    def setUp(self):
        """Set up test client and temporary upload folder."""
        app.config['TESTING'] = True

        # Override the upload folder to use a temporary directory for testing
        self.test_upload_dir = Path('data/test_uploads').resolve()
        self.test_upload_dir.mkdir(parents=True, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = self.test_upload_dir

        self.client = app.test_client()

    def tearDown(self):
        """Clean up the temporary upload folder."""
        if self.test_upload_dir.exists():
            shutil.rmtree(self.test_upload_dir)

    def test_index_route(self):
        """Test the main hub interface."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Operator Hub Space', response.data)

    def test_chat_endpoint_valid(self):
        """Test the chat endpoint with a valid message."""
        data = {'message': 'Hello AI'}
        response = self.client.post('/api/chat',
                                    data=json.dumps(data),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.data)
        self.assertIn('response', response_data)
        self.assertIn('Hello AI', response_data['response'])

    def test_chat_endpoint_invalid(self):
        """Test the chat endpoint with missing message."""
        response = self.client.post('/api/chat',
                                    data=json.dumps({}),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_upload_file_valid(self):
        """Test uploading a valid file."""
        data = {
            'file': (io.BytesIO(b"dummy text content"), 'test.txt')
        }
        response = self.client.post('/api/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)

        # Verify file exists
        expected_path = self.test_upload_dir / 'test.txt'
        self.assertTrue(expected_path.exists())

    def test_upload_file_invalid_extension(self):
        """Test uploading a file with an invalid extension."""
        data = {
            'file': (io.BytesIO(b"executable content"), 'test.exe')
        }
        response = self.client.post('/api/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'File type not allowed', response.data)

    def test_list_files(self):
        """Test listing uploaded files."""
        # Create a dummy file first
        test_file = self.test_upload_dir / 'dummy.txt'
        test_file.write_text("hello")

        response = self.client.get('/api/files')
        self.assertEqual(response.status_code, 200)

        response_data = json.loads(response.data)
        self.assertIn('files', response_data)
        self.assertEqual(len(response_data['files']), 1)
        self.assertEqual(response_data['files'][0]['name'], 'dummy.txt')

if __name__ == '__main__':
    unittest.main()
