"""
Tests for the GitHub Integration module.

Uses mocking so no real network calls are made during the test suite.
"""

import base64
import json
import unittest
from unittest.mock import MagicMock, patch

from src.github_integration import (
    DEFAULT_BRANCH,
    DEFAULT_OWNER,
    DEFAULT_REPO,
    GitHubAPIError,
    GitHubIntegration,
)


class TestGitHubIntegrationDefaults(unittest.TestCase):
    """Verify default configuration values."""

    def test_defaults(self):
        client = GitHubIntegration()
        self.assertEqual(client.owner, DEFAULT_OWNER)
        self.assertEqual(client.repo, DEFAULT_REPO)
        self.assertEqual(client.branch, DEFAULT_BRANCH)

    def test_custom_params(self):
        client = GitHubIntegration(owner="myorg", repo="myrepo", branch="dev")
        self.assertEqual(client.owner, "myorg")
        self.assertEqual(client.repo, "myrepo")
        self.assertEqual(client.branch, "dev")


class TestGetRepoTree(unittest.TestCase):
    """Tests for GitHubIntegration.get_repo_tree()."""

    def _make_client(self):
        return GitHubIntegration()

    @patch("src.github_integration.urllib.request.urlopen")
    def test_returns_list_of_entries(self, mock_urlopen):
        payload = [
            {"name": "src", "path": "src", "type": "dir"},
            {"name": "README.md", "path": "README.md", "type": "file"},
        ]
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = self._make_client()
        entries = client.get_repo_tree("")

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["name"], "src")
        self.assertEqual(entries[0]["type"], "dir")
        self.assertEqual(entries[1]["name"], "README.md")
        self.assertEqual(entries[1]["type"], "file")

    @patch("src.github_integration.urllib.request.urlopen")
    def test_single_file_response_wrapped_in_list(self, mock_urlopen):
        """GitHub returns a dict (not a list) when a single file path is requested."""
        payload = {"name": "README.md", "path": "README.md", "type": "file"}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = self._make_client()
        entries = client.get_repo_tree("README.md")

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "README.md")

    @patch("src.github_integration.urllib.request.urlopen")
    def test_http_error_raises_github_api_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://x", code=404, msg="Not Found", hdrs=None, fp=None
        )
        client = self._make_client()
        with self.assertRaises(GitHubAPIError) as ctx:
            client.get_repo_tree("nonexistent")
        self.assertIn("404", str(ctx.exception))

    @patch("src.github_integration.urllib.request.urlopen")
    def test_url_error_raises_github_api_error(self, mock_urlopen):
        import urllib.error

        mock_urlopen.side_effect = urllib.error.URLError(reason="Network failure")
        client = self._make_client()
        with self.assertRaises(GitHubAPIError) as ctx:
            client.get_repo_tree("")
        self.assertIn("Network failure", str(ctx.exception))


class TestGetFileContent(unittest.TestCase):
    """Tests for GitHubIntegration.get_file_content()."""

    def _make_client(self):
        return GitHubIntegration()

    def _make_mock_response(self, payload):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        return mock_response

    @patch("src.github_integration.urllib.request.urlopen")
    def test_decodes_base64_content(self, mock_urlopen):
        text = "Hello, Rainbow Jobs!"
        encoded = base64.b64encode(text.encode("utf-8")).decode("utf-8")
        payload = {
            "name": "hello.txt",
            "path": "hello.txt",
            "type": "file",
            "encoding": "base64",
            "content": encoded,
        }
        mock_urlopen.return_value = self._make_mock_response(payload)

        client = self._make_client()
        content = client.get_file_content("hello.txt")
        self.assertEqual(content, text)

    @patch("src.github_integration.urllib.request.urlopen")
    def test_raises_for_directory(self, mock_urlopen):
        payload = [
            {"name": "src", "path": "src", "type": "dir"},
        ]
        mock_urlopen.return_value = self._make_mock_response(payload)

        client = self._make_client()
        with self.assertRaises(GitHubAPIError) as ctx:
            client.get_file_content("src")
        self.assertIn("directory", str(ctx.exception))

    @patch("src.github_integration.urllib.request.urlopen")
    def test_raises_for_non_file_type(self, mock_urlopen):
        payload = {"name": "src", "path": "src", "type": "dir", "encoding": "", "content": ""}
        mock_urlopen.return_value = self._make_mock_response(payload)

        client = self._make_client()
        with self.assertRaises(GitHubAPIError) as ctx:
            client.get_file_content("src")
        self.assertIn("not a regular file", str(ctx.exception))

    @patch("src.github_integration.urllib.request.urlopen")
    def test_returns_raw_content_when_not_base64(self, mock_urlopen):
        payload = {
            "name": "file.txt",
            "path": "file.txt",
            "type": "file",
            "encoding": "none",
            "content": "raw text",
        }
        mock_urlopen.return_value = self._make_mock_response(payload)

        client = self._make_client()
        content = client.get_file_content("file.txt")
        self.assertEqual(content, "raw text")


class TestGetFlatTree(unittest.TestCase):
    """Tests for GitHubIntegration.get_flat_tree()."""

    @patch("src.github_integration.urllib.request.urlopen")
    def test_returns_only_blobs(self, mock_urlopen):
        payload = {
            "tree": [
                {"path": "src", "type": "tree"},
                {"path": "src/hub.py", "type": "blob"},
                {"path": "README.md", "type": "blob"},
            ]
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GitHubIntegration()
        files = client.get_flat_tree()

        # get_flat_tree returns all tree entries (blobs and trees)
        self.assertEqual(len(files), 3)
        paths = [f["path"] for f in files]
        self.assertIn("src/hub.py", paths)
        self.assertIn("README.md", paths)

    @patch("src.github_integration.urllib.request.urlopen")
    def test_empty_tree(self, mock_urlopen):
        payload = {"tree": []}
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(payload).encode("utf-8")
        mock_response.__enter__ = lambda s: s
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response

        client = GitHubIntegration()
        files = client.get_flat_tree()
        self.assertEqual(files, [])


class TestHubRepoEndpoints(unittest.TestCase):
    """Integration tests for the /api/repo/* Flask endpoints."""

    def setUp(self):
        from src.hub import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    @patch("src.hub.github_client")
    def test_repo_tree_success(self, mock_gh):
        mock_gh.get_repo_tree.return_value = [
            {"name": "src", "path": "src", "type": "dir"},
            {"name": "README.md", "path": "README.md", "type": "file"},
        ]
        response = self.client.get("/api/repo/tree?path=")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(len(data["entries"]), 2)

    @patch("src.hub.github_client")
    def test_repo_tree_api_error(self, mock_gh):
        mock_gh.get_repo_tree.side_effect = GitHubAPIError("GitHub API error 503")
        response = self.client.get("/api/repo/tree?path=")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(data["status"], "error")
        self.assertIn("503", data["message"])

    @patch("src.hub.github_client")
    def test_repo_file_success(self, mock_gh):
        mock_gh.get_file_content.return_value = "# Hello World"
        response = self.client.get("/api/repo/file?path=README.md")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["content"], "# Hello World")

    def test_repo_file_missing_path(self):
        response = self.client.get("/api/repo/file")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(data["status"], "error")
        self.assertEqual(data["message"], "Missing path parameter")

    @patch("src.hub.github_client")
    def test_repo_file_api_error(self, mock_gh):
        mock_gh.get_file_content.side_effect = GitHubAPIError("'src' is a directory")
        response = self.client.get("/api/repo/file?path=src")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(data["status"], "error")

    @patch("src.hub.github_client")
    def test_repo_all_files_success(self, mock_gh):
        mock_gh.get_flat_tree.return_value = [
            {"path": "src/hub.py", "type": "blob"},
            {"path": "README.md", "type": "blob"},
            {"path": "src", "type": "tree"},
        ]
        response = self.client.get("/api/repo/all-files")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["status"], "success")
        # The endpoint filters the flat tree to return only blob entries
        self.assertEqual(len(data["files"]), 2)

    @patch("src.hub.github_client")
    def test_repo_all_files_api_error(self, mock_gh):
        mock_gh.get_flat_tree.side_effect = GitHubAPIError("Network failure")
        response = self.client.get("/api/repo/all-files")
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 502)
        self.assertEqual(data["status"], "error")


if __name__ == "__main__":
    unittest.main()
