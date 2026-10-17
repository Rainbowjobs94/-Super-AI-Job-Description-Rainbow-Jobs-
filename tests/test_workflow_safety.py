"""Regression checks for truthful, read-only PR verification."""
from pathlib import Path
import subprocess
import tempfile
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


class BuildWorkflowSafetyTests(unittest.TestCase):
    def workflow(self):
        path = ROOT / ".github/workflows/build.yml"
        return yaml.load(path.read_text(), Loader=yaml.BaseLoader)

    def test_build_is_read_only_and_does_not_persist_credentials(self):
        workflow = self.workflow()
        self.assertEqual(workflow.get("permissions"), {"contents": "read"})
        self.assertIn("pull_request", workflow["on"])
        job = workflow["jobs"]["build"]
        self.assertNotIn("permissions", job)
        checkout = next(s for s in job["steps"]
                        if s.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["persist-credentials"], "false")

    def test_python_verification_is_required_and_unconditional(self):
        job = self.workflow()["jobs"]["build"]
        self.assertNotIn("if", job)
        steps = job["steps"]
        for step in steps:
            self.assertNotIn("if", step)
        commands = "\n".join(step.get("run", "") for step in steps)
        self.assertIn("python -m pip install -r requirements-dev.txt", commands)
        self.assertIn("python -m compileall", commands)
        self.assertIn("python -m flake8", commands)
        self.assertIn("python -m unittest discover -s tests -v", commands)

    def test_build_does_not_swallow_errors(self):
        job = self.workflow()["jobs"]["build"]
        self.assertNotIn("continue-on-error", job)
        for step in job["steps"]:
            self.assertNotIn("continue-on-error", step)
            command = step.get("run", "")
            self.assertNotIn("|| true", command)
            self.assertNotIn("2>/dev/null", command)
            self.assertNotIn("exit 0", command)

    def test_install_lint_and_test_failures_propagate(self):
        # Execute only verification commands with synthetic executables:
        # no real package installation, network access, or application execution.
        steps = self.workflow()["jobs"]["build"]["steps"]
        script = "\n".join(step.get("run", "") for step in steps
                           if any(token in step.get("run", "")
                                  for token in ("pip install", "flake8", "unittest")))
        with tempfile.TemporaryDirectory() as directory:
            for name in ("python", "pip", "flake8"):
                executable = Path(directory) / name
                executable.write_text(
                    '#!/bin/sh\nname=${0##*/}\n'
                    'case " $name $* " in *" $FAIL_COMMAND "*) exit 23;; esac\n'
                    'exit 0\n'
                )
                executable.chmod(0o700)
            for command in ("pip", "flake8", "unittest"):
                with self.subTest(command=command):
                    result = subprocess.run(
                        ["/bin/bash", "-e", "-o", "pipefail", "-c", script],
                        env={"PATH": directory, "FAIL_COMMAND": command},
                        capture_output=True, text=True, timeout=5,
                    )
                    self.assertEqual(result.returncode, 23, result.stderr)


if __name__ == "__main__":
    unittest.main()
