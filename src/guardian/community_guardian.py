"""
Community Guardian Module - Physical-23 Agent

Monitors community health across connected platforms, enforces community
guidelines, and tracks engagement metrics for the Rainbow Jobs community.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent.parent / "config"
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def load_config(filename):
    """Load a JSON configuration file."""
    config_path = CONFIG_DIR / filename
    with open(config_path, "r") as f:
        return json.load(f)


def load_agent_config():
    """Load the agent configuration."""
    return load_config("agent.json")


def load_platform_config():
    """Load the platform configuration."""
    return load_config("platforms.json")


def load_community_rules():
    """Load community guidelines and rules."""
    return load_config("community_rules.json")


class CommunityGuardian:
    """Main community guardian agent that monitors and manages community health."""

    def __init__(self):
        self.agent_config = load_agent_config()
        self.platform_config = load_platform_config()
        self.community_rules = load_community_rules()
        self.agent_id = self.agent_config["agent_id"]
        self.status = self.agent_config["status"]
        self.community_health = self.agent_config["community_health"]

    def get_active_platforms(self):
        """Return list of platforms that are currently enabled."""
        connected = self.agent_config["connected_platforms"]
        return [name for name, enabled in connected.items() if enabled]

    def get_health_status(self):
        """Evaluate community health against defined thresholds."""
        thresholds = self.community_rules["community_guidelines"]["health_thresholds"]
        health = self.community_health

        if health >= thresholds["excellent"]:
            return "excellent"
        elif health >= thresholds["healthy"]:
            return "healthy"
        elif health >= thresholds["warning"]:
            return "warning"
        else:
            return "critical"

    def check_community_health(self):
        """Run a community health check and return a report."""
        return {
            "agent_id": self.agent_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "health_score": self.community_health,
            "health_status": self.get_health_status(),
            "active_platforms": self.get_active_platforms(),
            "active_streams": self.agent_config["active_streams"],
            "content_library_size": self.agent_config["content_library_size"],
            "narrative_elements": self.agent_config["narrative_elements"],
            "identified_trends": self.agent_config["identified_trends"],
        }

    def get_platform_actions(self, platform_name):
        """Get guardian actions available for a specific platform."""
        platforms = self.platform_config["platforms"]
        if platform_name in platforms:
            return platforms[platform_name].get("guardian_actions", [])
        return []

    def get_applicable_rules(self, severity=None):
        """Get community rules, optionally filtered by severity."""
        rules = self.community_rules["community_guidelines"]["rules"]
        if severity:
            return [r for r in rules if r["severity"] == severity]
        return rules

    def generate_status_report(self):
        """Generate a full status report for the community guardian."""
        health_check = self.check_community_health()
        platforms = self.get_active_platforms()

        platform_details = {}
        for platform in platforms:
            platform_details[platform] = {
                "actions": self.get_platform_actions(platform),
                "features": self.platform_config["platforms"]
                .get(platform, {})
                .get("features", []),
            }

        return {
            "report_type": "community_guardian_status",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "agent": {
                "id": self.agent_id,
                "version": self.agent_config["version"],
                "mode": self.agent_config["current_mode"],
                "status": self.status,
            },
            "community_health": health_check,
            "platform_details": platform_details,
            "rules_count": len(self.get_applicable_rules()),
            "critical_rules": len(self.get_applicable_rules("critical")),
        }

    def save_report(self, report, filename="latest_report.json"):
        """Save a report to the data directory."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        report_path = DATA_DIR / filename
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        return str(report_path)


def main():
    """Run the community guardian and generate a status report."""
    guardian = CommunityGuardian()
    report = guardian.generate_status_report()

    print(f"Community Guardian [{guardian.agent_id}] - Status Report")
    print(f"  Mode: {guardian.agent_config['current_mode']}")
    print(f"  Health: {report['community_health']['health_score']} "
          f"({report['community_health']['health_status']})")
    print(f"  Active Platforms: {', '.join(report['community_health']['active_platforms'])}")
    print(f"  Active Streams: {report['community_health']['active_streams']}")
    print(f"  Content Library: {report['community_health']['content_library_size']} items")
    print(f"  Narrative Elements: {report['community_health']['narrative_elements']}")
    print(f"  Identified Trends: {report['community_health']['identified_trends']}")
    print(f"  Community Rules: {report['rules_count']} "
          f"({report['critical_rules']} critical)")

    saved_path = guardian.save_report(report)
    print(f"\n  Report saved to: {saved_path}")

    return report


if __name__ == "__main__":
    main()
