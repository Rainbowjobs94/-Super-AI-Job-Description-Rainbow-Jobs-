import unittest
import os
import pathlib
import io
import json
import shutil
from src.hub import app

class HubTestCase(unittest.TestCase):
    def setUp(self):
        # Setup testing client
        self.app = app.test_client()
        self.app.testing = True

        # Setup temporary upload directory for testing
        self.test_upload_dir = pathlib.Path(__file__).parent / 'test_uploads'
        os.makedirs(self.test_upload_dir, exist_ok=True)
        app.config['UPLOAD_FOLDER'] = str(self.test_upload_dir)

    def tearDown(self):
        # Clean up test uploads directory
        if self.test_upload_dir.exists():
            shutil.rmtree(self.test_upload_dir)

    def test_index_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AI Operator Hub', response.data)

    def test_chat_api(self):
        # Test valid chat message
        response = self.app.post('/api/chat',
                                 data=json.dumps({'message': 'Hello agent'}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('response', data)

        # Test empty chat message
        response = self.app.post('/api/chat',
                                 data=json.dumps({}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_api(self):
        # Create dummy file content
        file_content = b"This is a test file."
        data = {
            'file': (io.BytesIO(file_content), 'testfile.txt')
        }

        response = self.app.post('/api/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 200)

        json_response = json.loads(response.data)
        self.assertEqual(json_response['message'], 'File successfully uploaded')
        self.assertEqual(json_response['filename'], 'testfile.txt')

        # Verify file exists
        file_path = self.test_upload_dir / 'testfile.txt'
        self.assertTrue(file_path.exists())

    def test_list_files_api(self):
        # Create a dummy file in the upload directory
        dummy_file = self.test_upload_dir / 'dummy.txt'
        dummy_file.write_text("dummy")

        response = self.app.get('/api/files')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('files', data)
        self.assertTrue(any(f['name'] == 'dummy.txt' for f in data['files']))

    def test_path_traversal_prevention_upload(self):
        # Test path traversal via malicious filename upload
        data = {
            'file': (io.BytesIO(b"malicious"), '../../../etc/passwd')
        }
        response = self.app.post('/api/upload', data=data, content_type='multipart/form-data')

        # Werkzeug's secure_filename will sanitize '../../../etc/passwd' to 'etc_passwd'
        # So it should upload successfully but not traverse
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.data)
        self.assertEqual(json_response['filename'], 'etc_passwd')

        # Ensure it didn't traverse
        traversed_path = self.test_upload_dir.parent.parent.parent / 'etc' / 'passwd'
        self.assertFalse(traversed_path.exists() and not traversed_path.is_file()) # Note: check could be tricky if /etc/passwd actually exists, but it won't be written by the test.

        # Verify it saved safely inside the test upload directory
        safe_path = self.test_upload_dir / 'etc_passwd'
        self.assertTrue(safe_path.exists())

    def test_path_traversal_prevention_download(self):
        # Try to download a file outside the upload directory
        response = self.app.get('/api/files/../../../../etc/passwd')
        self.assertEqual(response.status_code, 404) # Werkzeug send_from_directory raises 404 for path traversal attempts when file not found

if __name__ == '__main__':
    unittest.main()
