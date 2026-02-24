"""
Content Manager Module

Manages the content library and narrative elements for the
Community Guardian agent. Tracks content across platforms and
monitors trends.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class ContentManager:
    """Manages content library, narrative elements, and trend tracking."""

    def __init__(self, agent_config):
        self.content_library_size = agent_config.get("content_library_size", 0)
        self.narrative_elements = agent_config.get("narrative_elements", 0)
        self.identified_trends = agent_config.get("identified_trends", 0)
        self._content_items = []
        self._narratives = []
        self._trends = []

    def add_content_item(self, title, content_type, platform, description=""):
        """Add an item to the content library."""
        item = {
            "id": len(self._content_items) + 1,
            "title": title,
            "type": content_type,
            "platform": platform,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._content_items.append(item)
        self.content_library_size = len(self._content_items)
        return item

    def add_narrative_element(self, name, category, description=""):
        """Add a narrative element for community storytelling."""
        element = {
            "id": len(self._narratives) + 1,
            "name": name,
            "category": category,
            "description": description,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._narratives.append(element)
        self.narrative_elements = len(self._narratives)
        return element

    def add_trend(self, name, platform, direction, description=""):
        """Record an identified trend."""
        trend = {
            "id": len(self._trends) + 1,
            "name": name,
            "platform": platform,
            "direction": direction,
            "description": description,
            "identified_at": datetime.now(timezone.utc).isoformat(),
        }
        self._trends.append(trend)
        self.identified_trends = len(self._trends)
        return trend

    def get_content_summary(self):
        """Get a summary of the content library."""
        return {
            "total_items": self.content_library_size,
            "narrative_elements": self.narrative_elements,
            "identified_trends": self.identified_trends,
            "items": self._content_items,
            "narratives": self._narratives,
            "trends": self._trends,
        }

    def save_content_data(self, filename="content_library.json"):
        """Save content data to the data directory."""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        data_path = DATA_DIR / filename
        with open(data_path, "w") as f:
            json.dump(self.get_content_summary(), f, indent=2)
        return str(data_path)
