"""
GitHub Integration Module

Provides read-only access to the public repository source code via the
GitHub REST API, allowing the AI operator to browse and load the open
codebase for application improvement.
"""

import base64
import json
import urllib.error
import urllib.request

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_OWNER = "Rainbowjobs94"
DEFAULT_REPO = "-Super-AI-Job-Description-Rainbow-Jobs-"
DEFAULT_BRANCH = "main"


class GitHubIntegration:
    """Read-only GitHub API client for browsing the open repository."""

    def __init__(self, owner=DEFAULT_OWNER, repo=DEFAULT_REPO,
                 branch=DEFAULT_BRANCH):
        self.owner = owner
        self.repo = repo
        self.branch = branch

    def _get(self, url):
        """Perform a GET request to the GitHub API and return parsed JSON."""
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "SuperAI-RainbowJobs-Hub/1.0",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise GitHubAPIError(
                f"GitHub API error {exc.code}: {exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubAPIError(
                f"Failed to reach GitHub API: {exc.reason}"
            ) from exc

    def get_repo_tree(self, path=""):
        """
        Return the list of files/directories at *path* in the repository.

        Each entry is a dict with keys: name, path, type ('file' or 'dir').
        """
        # Use the contents endpoint so we get a shallow directory listing
        url = (
            f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}"
            f"/contents/{path}?ref={self.branch}"
        )
        data = self._get(url)

        if isinstance(data, list):
            return [
                {
                    "name": item["name"],
                    "path": item["path"],
                    "type": "dir" if item["type"] == "dir" else "file",
                }
                for item in data
            ]
        # Single file returned — wrap it
        return [
            {
                "name": data["name"],
                "path": data["path"],
                "type": "dir" if data["type"] == "dir" else "file",
            }
        ]

    def get_file_content(self, path):
        """
        Return the decoded text content of a file at *path*.

        Raises GitHubAPIError if the path is a directory or on API failure.
        """
        url = (
            f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}"
            f"/contents/{path}?ref={self.branch}"
        )
        data = self._get(url)

        if isinstance(data, list):
            raise GitHubAPIError(f"'{path}' is a directory, not a file.")

        if data.get("type") != "file":
            raise GitHubAPIError(f"'{path}' is not a regular file.")

        encoding = data.get("encoding", "")
        content = data.get("content", "")

        if encoding == "base64":
            try:
                return base64.b64decode(content).decode("utf-8")
            except (ValueError, UnicodeDecodeError) as exc:
                raise GitHubAPIError(
                    f"Cannot decode file '{path}' as UTF-8 text."
                ) from exc

        return content

    def get_flat_tree(self):
        """
        Return a flat list of all files in the repository using the Git Trees
        API (recursive).  Each entry has keys: path, type.
        """
        url = (
            f"{GITHUB_API_BASE}/repos/{self.owner}/{self.repo}"
            f"/git/trees/{self.branch}?recursive=1"
        )
        data = self._get(url)
        return [
            {"path": item["path"], "type": item["type"]}
            for item in data.get("tree", [])
        ]


class GitHubAPIError(Exception):
    """Raised when a GitHub API call fails."""
