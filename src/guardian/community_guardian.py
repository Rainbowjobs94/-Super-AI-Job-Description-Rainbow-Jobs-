"""
Community Guardian Module - Physical-23 Agent

Monitors community health across connected platforms, enforces community
guidelines, and tracks engagement metrics for the Rainbow Jobs community.
"""

import json
import os
import zipfile
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
        elif health >= thresholds["critical"]:
            return "at_risk"
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

        # Security: Prevent path traversal by resolving the path and checking it's within DATA_DIR
        report_path = (DATA_DIR / filename).resolve()
        if not report_path.is_relative_to(DATA_DIR.resolve()):
            raise ValueError(f"Invalid filename: {filename}. Path traversal detected.")

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        return str(report_path)

    def build_repo_archive(self, output_dir=None):
        """Build the AiRainbowRepo archive with all project artifacts."""
        project_number = "123-7104"
        date_str = datetime.now().strftime("%Y%m%d")
        version = "v1.1"
        zip_filename = f"AiRainbowRepo-{date_str}-{project_number}-{version}.zip"

        if output_dir is None:
            output_dir = str(DATA_DIR)
        os.makedirs(output_dir, exist_ok=True)

        directories = [
            "AiRainbowRepo/docs",
            "AiRainbowRepo/code/backend",
            "AiRainbowRepo/code/frontend",
            "AiRainbowRepo/security",
            "AiRainbowRepo/blockchain",
            "AiRainbowRepo/media",
        ]

        files = {
            "AiRainbowRepo/README.md": (
                "# Love Transcends Reality: Shift Nexus Protocol v3\n"
                "**Project**: 123-7104\n"
                "**Type**: Font Miner Architecture & Proof of Concept\n"
                "**Description**: Layer 2 architecture for Decentralized Type Foundry. "
                "Miners compute vector optimization math to generate artist-signed, "
                "blockchain-encrypted typography.\n"
            ),
            "AiRainbowRepo/CHANGELOG.md": (
                "# Changelog\n"
                "- **v1.1 (2026-02-19)**: Regenerated archive locally to bypass sandbox "
                "expiration. Added FontNexusProtocol.sol and font_miner_core.py.\n"
                "- **v1.0 (2026-02-18)**: Initial conceptualization of Shift Nexus "
                "Protocol v3 (Font Miner Edition).\n"
            ),
            "AiRainbowRepo/LTAiCollab-WATERMARK.txt": (
                "=========================================\n"
                "PROPERTY OF LOVE TRANSCENDS REALITY LLC\n"
                "\u00a9 2013-2026 Rainbow Strongman / John Strongman\n"
                "Patents Pending. All Rights Reserved.\n"
                "Project 123-7104\n"
                "=========================================\n"
                "This code and its output bear the LTAiCollab Watermark for IP Protection.\n"
            ),
            "AiRainbowRepo/blockchain/FontNexusProtocol.sol": (
                "// SPDX-License-Identifier: MIT\n"
                "pragma solidity ^0.8.0;\n"
                "contract FontNexusProtocol {\n"
                '    string public constant WATERMARK = "LTAiCollab-123-7104";\n'
                "    mapping(bytes32 => address) public fontOwners;\n"
                "\n"
                "    event FontMined(address indexed miner, bytes32 fontHash, string glyphData);\n"
                "    function registerMinedFont(bytes32 _fontHash, string memory _glyphData) public {\n"
                '        require(fontOwners[_fontHash] == address(0), "Font already mined!");\n'
                "        fontOwners[_fontHash] = msg.sender;\n"
                "        emit FontMined(msg.sender, _fontHash, _glyphData);\n"
                "    }\n"
                "}\n"
            ),
            "AiRainbowRepo/code/backend/font_miner_core.py": (
                "import hashlib\n"
                "import json\n"
                "import random\n"
                "class FontMinerV3:\n"
                "    def __init__(self, miner_address, difficulty=4):\n"
                "        self.miner_address = miner_address\n"
                "        self.difficulty = difficulty\n"
                '        self.target = "0" * difficulty\n'
                "        self.font_data = {"
                '"Family": "NexusSerif", "Glyphs": [], '
                '"Watermark": "LTAiCollab-123-7104"}\n'
                "    def mine_glyph(self, char, previous_hash):\n"
                "        nonce = 0\n"
                "        print(f\"Mining Glyph '{char}'...\")\n"
                "        while True:\n"
                "            data_string = f\"{char}{previous_hash}{self.miner_address}{nonce}\"\n"
                "            block_hash = hashlib.sha256(data_string.encode()).hexdigest()\n"
                "            if block_hash.startswith(self.target):\n"
                "                print(f\"Glyph '{char}' Mined! Hash: {block_hash}\")\n"
                "                return block_hash\n"
                "            nonce += 1\n"
                'if __name__ == "__main__":\n'
                '    miner = FontMinerV3(miner_address="0xRainbowLTR", difficulty=4)\n'
                '    miner.mine_glyph("A", "0000000000000000")\n'
            ),
        }

        # Build in a temp working area inside output_dir
        build_root = os.path.join(output_dir, "AiRainbowRepo")

        # 1. Create directories
        for d in directories:
            os.makedirs(os.path.join(output_dir, d), exist_ok=True)

        # 2. Create files
        for filepath, content in files.items():
            full_path = os.path.join(output_dir, filepath)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        # 3. Zip everything
        zip_path = os.path.join(output_dir, zip_filename)
        print(f"  Generating {zip_filename}...")
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files_in_dir in os.walk(build_root):
                for file in files_in_dir:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, output_dir)
                    zipf.write(file_path, arcname=arcname)

        print(f"  Archive created: {zip_path}")
        return zip_path


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

    # Build AiRainbowRepo archive
    print("\n  Building AiRainbowRepo archive...")
    archive_path = guardian.build_repo_archive()
    print(f"  Build complete: {archive_path}")

    return report


if __name__ == "__main__":
    main()
