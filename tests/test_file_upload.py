import unittest
import json
from src.hub import app

class TestFileUpload(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_upload_file_sanitization(self):
        from io import BytesIO
        data = {
            'file': (BytesIO(b"test"), 'unsafe file name.txt'),
            'path': 'my folder/unsafe file name.txt'
        }
        response = self.client.post(
            '/api/files/upload',
            data=data,
            content_type='multipart/form-data'
        )
        resp_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(resp_data['path'].endswith('my folder/unsafe_file_name.txt'))

if __name__ == '__main__':
    unittest.main()
