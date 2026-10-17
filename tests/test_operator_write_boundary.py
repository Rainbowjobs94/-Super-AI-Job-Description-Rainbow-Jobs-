"""Chat and legacy endpoints must not bypass reviewed source changes."""
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.hub import app


class OperatorWriteBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "docs/example.txt"
        self.source.parent.mkdir()
        self.original = "Keep these trailing spaces.  \n"
        self.source.write_text(self.original)
        token = "synthetic-test-" + "x" * 40
        config = patch.dict(app.config, TESTING=True, HAB_TOKEN=token,
                            HAB_LEGACY_WRITES=False)
        config.start()
        self.addCleanup(config.stop)
        base = patch("src.hub.BASE_DIR", self.root)
        base.start()
        self.addCleanup(base.stop)
        self.client = app.test_client()
        self.client.environ_base["HTTP_AUTHORIZATION"] = "Bearer " + token

    def test_fix_chat_cannot_overwrite_source(self):
        response = self.client.post("/api/chat", json={
            "message": "Please fix docs/example.txt",
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.source.read_text(), self.original)

    def test_legacy_write_remains_disabled(self):
        response = self.client.post("/api/files/write", json={
            "path": "docs/example.txt", "content": "replacement",
        })
        self.assertEqual(response.status_code, 403)
        self.assertEqual(self.source.read_text(), self.original)

    def test_upload_cannot_target_source_paths(self):
        response = self.client.post("/api/files/upload", data={
            "file": (io.BytesIO(b"replacement"), "example.txt"),
            "path": "docs/example.txt",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.source.read_text(), self.original)


if __name__ == "__main__":
    unittest.main()
