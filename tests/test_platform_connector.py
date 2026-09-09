import unittest
from unittest.mock import patch
from src.platforms.platform_connector import PlatformConnector

class TestPlatformConnector(unittest.TestCase):
    def setUp(self):
        self.mock_config = {
            "platforms": {
                "twitch": {
                    "enabled": True,
                    "features": ["feature1", "feature2"],
                    "guardian_actions": ["action1", "action2"]
                },
                "facebook": {
                    "enabled": False,
                    "features": ["feature3"],
                    "guardian_actions": ["action3"]
                },
                "instagram": {
                    "enabled": True,
                    # Missing features and guardian_actions keys
                }
            }
        }

    @patch('src.platforms.platform_connector.load_platform_config')
    def test_get_platform_features(self, mock_load):
        mock_load.return_value = self.mock_config
        connector = PlatformConnector()

        # Happy path: Enabled platform with features
        self.assertEqual(connector.get_platform_features("twitch"), ["feature1", "feature2"])

        # Edge case: Enabled platform with no features key
        self.assertEqual(connector.get_platform_features("instagram"), [])

        # Edge case: Disabled platform
        self.assertEqual(connector.get_platform_features("facebook"), [])

        # Edge case: Non-existent platform
        self.assertEqual(connector.get_platform_features("non_existent"), [])

    @patch('src.platforms.platform_connector.load_platform_config')
    def test_get_enabled_platforms(self, mock_load):
        mock_load.return_value = self.mock_config
        connector = PlatformConnector()

        enabled = connector.get_enabled_platforms()
        self.assertIn("twitch", enabled)
        self.assertIn("instagram", enabled)
        self.assertNotIn("facebook", enabled)
        self.assertEqual(len(enabled), 2)

    @patch('src.platforms.platform_connector.load_platform_config')
    def test_get_guardian_actions(self, mock_load):
        mock_load.return_value = self.mock_config
        connector = PlatformConnector()

        # Valid and enabled platform
        self.assertEqual(connector.get_guardian_actions("twitch"), ["action1", "action2"])

        # Enabled platform but missing key
        self.assertEqual(connector.get_guardian_actions("instagram"), [])

        # Disabled platform
        self.assertEqual(connector.get_guardian_actions("facebook"), [])

        # Invalid platform
        self.assertEqual(connector.get_guardian_actions("invalid"), [])

    @patch('src.platforms.platform_connector.load_platform_config')
    def test_get_all_guardian_actions(self, mock_load):
        mock_load.return_value = self.mock_config
        connector = PlatformConnector()

        all_actions = connector.get_all_guardian_actions()
        expected = {
            "twitch": ["action1", "action2"],
            "instagram": []
        }
        self.assertEqual(all_actions, expected)

    @patch('src.platforms.platform_connector.load_platform_config')
    def test_platform_summary(self, mock_load):
        mock_load.return_value = self.mock_config
        connector = PlatformConnector()

        summary = connector.platform_summary()
        self.assertEqual(len(summary), 3)

        # Check twitch summary
        twitch_summary = next(item for item in summary if item["platform"] == "twitch")
        self.assertEqual(twitch_summary["enabled"], True)
        self.assertEqual(twitch_summary["feature_count"], 2)
        self.assertEqual(twitch_summary["action_count"], 2)

        # Check facebook summary (disabled)
        facebook_summary = next(item for item in summary if item["platform"] == "facebook")
        self.assertEqual(facebook_summary["enabled"], False)
        self.assertEqual(facebook_summary["feature_count"], 1)
        self.assertEqual(facebook_summary["action_count"], 1)

        # Check instagram summary (missing keys)
        instagram_summary = next(item for item in summary if item["platform"] == "instagram")
        self.assertEqual(instagram_summary["enabled"], True)
        self.assertEqual(instagram_summary["feature_count"], 0)
        self.assertEqual(instagram_summary["action_count"], 0)

if __name__ == '__main__':
    unittest.main()
