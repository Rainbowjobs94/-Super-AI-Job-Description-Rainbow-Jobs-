import unittest
from unittest.mock import patch, mock_open, MagicMock
from src.content.content_manager import ContentManager

class TestContentManager(unittest.TestCase):
    def setUp(self):
        self.agent_config = {
            "content_library_size": 10,
            "narrative_elements": 5,
            "identified_trends": 2
        }
        self.manager = ContentManager(self.agent_config)

    def test_init(self):
        self.assertEqual(self.manager.content_library_size, 10)
        self.assertEqual(self.manager.narrative_elements, 5)
        self.assertEqual(self.manager.identified_trends, 2)
        self.assertEqual(self.manager._content_items, [])
        self.assertEqual(self.manager._narratives, [])
        self.assertEqual(self.manager._trends, [])

    def test_init_default(self):
        manager = ContentManager({})
        self.assertEqual(manager.content_library_size, 0)
        self.assertEqual(manager.narrative_elements, 0)
        self.assertEqual(manager.identified_trends, 0)

    def test_add_content_item(self):
        item = self.manager.add_content_item("Test Title", "video", "youtube", "Test Description")
        self.assertEqual(len(self.manager._content_items), 1)
        self.assertEqual(self.manager.content_library_size, 1)
        self.assertEqual(item["title"], "Test Title")
        self.assertEqual(item["type"], "video")
        self.assertEqual(item["platform"], "youtube")
        self.assertEqual(item["description"], "Test Description")
        self.assertEqual(item["id"], 1)
        self.assertIn("created_at", item)

    def test_add_narrative_element(self):
        element = self.manager.add_narrative_element("Test Narrative", "educational", "Test Description")
        self.assertEqual(len(self.manager._narratives), 1)
        self.assertEqual(self.manager.narrative_elements, 1)
        self.assertEqual(element["name"], "Test Narrative")
        self.assertEqual(element["category"], "educational")
        self.assertEqual(element["description"], "Test Description")
        self.assertEqual(element["id"], 1)
        self.assertIn("created_at", element)

    def test_add_trend(self):
        trend = self.manager.add_trend("Test Trend", "twitch", "up", "Test Description")
        self.assertEqual(len(self.manager._trends), 1)
        self.assertEqual(self.manager.identified_trends, 1)
        self.assertEqual(trend["name"], "Test Trend")
        self.assertEqual(trend["platform"], "twitch")
        self.assertEqual(trend["direction"], "up")
        self.assertEqual(trend["description"], "Test Description")
        self.assertEqual(trend["id"], 1)
        self.assertIn("identified_at", trend)

    def test_get_content_summary(self):
        self.manager.add_content_item("Title 1", "type1", "platform1")
        self.manager.add_narrative_element("Narrative 1", "cat1")
        self.manager.add_trend("Trend 1", "platform1", "dir1")

        summary = self.manager.get_content_summary()
        self.assertEqual(summary["total_items"], 1)
        self.assertEqual(summary["narrative_elements"], 1)
        self.assertEqual(summary["identified_trends"], 1)
        self.assertEqual(len(summary["items"]), 1)
        self.assertEqual(len(summary["narratives"]), 1)
        self.assertEqual(len(summary["trends"]), 1)

    @patch("src.content.content_manager.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_save_content_data(self, mock_json_dump, mock_file, mock_mkdir):
        path = self.manager.save_content_data("test.json")
        mock_mkdir.assert_called()
        mock_file.assert_called()
        mock_json_dump.assert_called()
        self.assertIn("test.json", path)

if __name__ == "__main__":
    unittest.main()
