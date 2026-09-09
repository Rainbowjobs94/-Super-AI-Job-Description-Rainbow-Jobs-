import unittest
import os

class TestSecurityConfig(unittest.TestCase):
    def test_flask_debug_disabled(self):
        """Verify that Flask debug mode is disabled in src/hub.py."""
        hub_path = os.path.join(os.path.dirname(__file__), '..', 'src', 'hub.py')
        with open(hub_path, 'r') as f:
            content = f.read()

        self.assertIn('debug=False', content, "Flask debug mode should be explicitly set to False in src/hub.py")
        self.assertNotIn('debug=True', content, "Flask debug mode should not be set to True in src/hub.py")

if __name__ == '__main__':
    unittest.main()
