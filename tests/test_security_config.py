import unittest
import os

class TestSecurityConfig(unittest.TestCase):
    def test_flask_debug_disabled(self):
        hub_path = os.path.join('src', 'hub.py')
        with open(hub_path, 'r') as f:
            content = f.read()

        self.assertNotIn('debug=True', content, "Flask debug mode should be disabled (debug=True found)")
        self.assertIn('debug=False', content, "Flask debug mode should be explicitly set to False (debug=False not found)")

if __name__ == '__main__':
    unittest.main()
