import unittest
from unittest.mock import patch
from src.guardian.community_guardian import CommunityGuardian

class TestCommunityGuardian(unittest.TestCase):
    def setUp(self):
        self.mock_agent_config = {
            "agent_id": "Test-Agent",
            "version": "1.0",
            "status": "active",
            "current_mode": "community_guardian",
            "connected_platforms": {
                "twitch": True,
                "facebook": False,
                "instagram": True
            },
            "community_health": 0.75,
            "active_streams": 1,
            "content_library_size": 10,
            "narrative_elements": 5,
            "identified_trends": 2
        }
        self.mock_platform_config = {
            "platforms": {
                "twitch": {
                    "enabled": True,
                    "guardian_actions": ["action1", "action2"]
                },
                "instagram": {
                    "enabled": True,
                    "guardian_actions": ["action3"]
                }
            }
        }
        self.mock_community_rules = {
            "community_guidelines": {
                "health_thresholds": {
                    "critical": 0.3,
                    "warning": 0.5,
                    "healthy": 0.7,
                    "excellent": 0.9
                },
                "rules": [
                    {"id": "R1", "severity": "critical"},
                    {"id": "R2", "severity": "high"},
                    {"id": "R3", "severity": "critical"}
                ]
            }
        }

    @patch('src.guardian.community_guardian.load_agent_config')
    @patch('src.guardian.community_guardian.load_platform_config')
    @patch('src.guardian.community_guardian.load_community_rules')
    def test_get_health_status(self, mock_rules, mock_platforms, mock_agent):
        mock_agent.return_value = self.mock_agent_config
        mock_platforms.return_value = self.mock_platform_config
        mock_rules.return_value = self.mock_community_rules

        guardian = CommunityGuardian()

        # Test excellent
        guardian.community_health = 0.95
        self.assertEqual(guardian.get_health_status(), "excellent")
        guardian.community_health = 0.9
        self.assertEqual(guardian.get_health_status(), "excellent")

        # Test healthy
        guardian.community_health = 0.85
        self.assertEqual(guardian.get_health_status(), "healthy")
        guardian.community_health = 0.7
        self.assertEqual(guardian.get_health_status(), "healthy")

        # Test warning
        guardian.community_health = 0.65
        self.assertEqual(guardian.get_health_status(), "warning")
        guardian.community_health = 0.5
        self.assertEqual(guardian.get_health_status(), "warning")

        # Test at_risk (critical threshold <= health < warning threshold)
        # Wait, the code says:
        # if health >= thresholds["excellent"]: return "excellent"
        # elif health >= thresholds["healthy"]: return "healthy"
        # elif health >= thresholds["warning"]: return "warning"
        # elif health >= thresholds["critical"]: return "at_risk"
        # else: return "critical"

        guardian.community_health = 0.45
        self.assertEqual(guardian.get_health_status(), "at_risk")
        guardian.community_health = 0.3
        self.assertEqual(guardian.get_health_status(), "at_risk")

        # Test critical
        guardian.community_health = 0.25
        self.assertEqual(guardian.get_health_status(), "critical")
        guardian.community_health = 0.0
        self.assertEqual(guardian.get_health_status(), "critical")

    @patch('src.guardian.community_guardian.load_agent_config')
    @patch('src.guardian.community_guardian.load_platform_config')
    @patch('src.guardian.community_guardian.load_community_rules')
    def test_get_active_platforms(self, mock_rules, mock_platforms, mock_agent):
        mock_agent.return_value = self.mock_agent_config
        mock_platforms.return_value = self.mock_platform_config
        mock_rules.return_value = self.mock_community_rules

        guardian = CommunityGuardian()
        active = guardian.get_active_platforms()
        self.assertIn("twitch", active)
        self.assertIn("instagram", active)
        self.assertNotIn("facebook", active)
        self.assertEqual(len(active), 2)

    @patch('src.guardian.community_guardian.load_agent_config')
    @patch('src.guardian.community_guardian.load_platform_config')
    @patch('src.guardian.community_guardian.load_community_rules')
    def test_get_applicable_rules(self, mock_rules, mock_platforms, mock_agent):
        mock_agent.return_value = self.mock_agent_config
        mock_platforms.return_value = self.mock_platform_config
        mock_rules.return_value = self.mock_community_rules

        guardian = CommunityGuardian()

        all_rules = guardian.get_applicable_rules()
        self.assertEqual(len(all_rules), 3)

        critical_rules = guardian.get_applicable_rules(severity="critical")
        self.assertEqual(len(critical_rules), 2)
        for rule in critical_rules:
            self.assertEqual(rule["severity"], "critical")

        high_rules = guardian.get_applicable_rules(severity="high")
        self.assertEqual(len(high_rules), 1)
        self.assertEqual(high_rules[0]["severity"], "high")

    @patch('src.guardian.community_guardian.load_agent_config')
    @patch('src.guardian.community_guardian.load_platform_config')
    @patch('src.guardian.community_guardian.load_community_rules')
    def test_get_platform_actions(self, mock_rules, mock_platforms, mock_agent):
        mock_agent.return_value = self.mock_agent_config
        mock_platforms.return_value = self.mock_platform_config
        mock_rules.return_value = self.mock_community_rules

        guardian = CommunityGuardian()

        twitch_actions = guardian.get_platform_actions("twitch")
        self.assertEqual(twitch_actions, ["action1", "action2"])

        instagram_actions = guardian.get_platform_actions("instagram")
        self.assertEqual(instagram_actions, ["action3"])

        unknown_actions = guardian.get_platform_actions("unknown")
        self.assertEqual(unknown_actions, [])

    def test_load_config_path_traversal(self):
        """Test that load_config correctly blocks path traversal attempts."""
        from src.guardian.community_guardian import load_config

        # Test with a path that attempts to go outside CONFIG_DIR
        traversal_filenames = [
            "../secret.json",
            "../../etc/passwd",
            "/etc/passwd",
            "config/../../secret.json"
        ]

        for filename in traversal_filenames:
            with self.subTest(filename=filename):
                with self.assertRaises(ValueError) as cm:
                    load_config(filename)
                self.assertIn("Path traversal detected", str(cm.exception))

if __name__ == '__main__':
    unittest.main()
