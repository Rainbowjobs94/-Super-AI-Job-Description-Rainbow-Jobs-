"""Regression checks for truthful, read-only PR verification."""
from pathlib import Path
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]


class WorkflowSafetyTests(unittest.TestCase):
    def workflow(self):
        path = ROOT / ".github/workflows/pr-auto-merge.yml"
        return yaml.load(path.read_text(), Loader=yaml.BaseLoader)

    def test_workflow_is_valid_yaml_and_checks_pull_requests(self):
        workflow = self.workflow()
        self.assertIn("pull_request", workflow["on"])
        self.assertNotIn("pull_request_target", workflow["on"])

    def test_verification_has_no_write_or_merge_authority(self):
        workflow = self.workflow()
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        self.assertEqual(set(workflow["jobs"]), {"verify"})
        job = workflow["jobs"]["verify"]
        self.assertNotIn("permissions", job)
        for step in job["steps"]:
            self.assertNotIn("continue-on-error", step)
            command = step.get("run", "")
            self.assertNotIn("|| true", command)
            self.assertNotIn("exit 0", command)
            self.assertNotIn("pulls.merge", str(step))
            self.assertNotIn("gh pr merge", str(step))

    def test_dependencies_lint_and_tests_are_required(self):
        steps = self.workflow()["jobs"]["verify"]["steps"]
        commands = "\n".join(step.get("run", "") for step in steps)
        self.assertIn("pip install -r requirements-dev.txt", commands)
        self.assertIn("python -m flake8", commands)
        self.assertIn("python -m unittest discover -s tests -v", commands)
        checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")


if __name__ == "__main__":
    unittest.main()
