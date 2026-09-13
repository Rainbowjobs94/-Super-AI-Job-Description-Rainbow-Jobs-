import unittest
from pathlib import Path

class TestSecurityConfig(unittest.TestCase):
    def test_flask_debug_disabled(self):
        hub_path = Path('src/hub.py')
        content = hub_path.read_text()

        # We want debug=False to be present
        self.assertIn('debug=False', content, "Flask debug mode should be explicitly set to False")

        # We want debug=True to be absent
        self.assertNotIn('debug=True', content, "Flask debug mode should not be enabled")

if __name__ == '__main__':
    unittest.main()
