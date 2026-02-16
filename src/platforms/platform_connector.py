"""
Platform Connector Module

Manages connections to external platforms (Twitch, Facebook, Instagram,
YouTube, LTF) and provides a unified interface for community guardian actions.
"""

import json
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"


def load_platform_config():
    """Load the platform configuration."""
    config_path = CONFIG_DIR / "platforms.json"
    with open(config_path, "r") as f:
        return json.load(f)


class PlatformConnector:
    """Manages connections and interactions with external platforms."""

    def __init__(self):
        self.config = load_platform_config()
        self.platforms = self.config["platforms"]

    def get_enabled_platforms(self):
        """Return names of all enabled platforms."""
        return [name for name, cfg in self.platforms.items() if cfg.get("enabled")]

    def get_platform_features(self, platform_name):
        """Get available features for a platform."""
        platform = self.platforms.get(platform_name)
        if platform and platform.get("enabled"):
            return platform.get("features", [])
        return []

    def get_guardian_actions(self, platform_name):
        """Get guardian actions available on a platform."""
        platform = self.platforms.get(platform_name)
        if platform and platform.get("enabled"):
            return platform.get("guardian_actions", [])
        return []

    def get_all_guardian_actions(self):
        """Get all guardian actions across all enabled platforms."""
        actions = {}
        for name in self.get_enabled_platforms():
            actions[name] = self.get_guardian_actions(name)
        return actions

    def platform_summary(self):
        """Generate a summary of all platform connections."""
        summary = []
        for name, cfg in self.platforms.items():
            summary.append({
                "platform": name,
                "enabled": cfg.get("enabled", False),
                "feature_count": len(cfg.get("features", [])),
                "action_count": len(cfg.get("guardian_actions", [])),
            })
        return summary
