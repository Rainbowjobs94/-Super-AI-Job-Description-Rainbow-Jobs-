"""Offline tests for the split, fail-closed auto-merge workflows.

All GitHub API calls are mocked. No token, network call, or real merge is used.
"""
import copy
import json
from pathlib import Path
import subprocess
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
MERGE_WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/pr-auto-merge.yml").read_text(encoding="utf-8")
)
QUALITY_WORKFLOW = yaml.safe_load(
    (ROOT / ".github/workflows/pr-review.yml").read_text(encoding="utf-8")
)
HEAD = "a" * 40
BASE = "b" * 40
REPO = {"owner": "Rainbowjobs94", "repo": "-Super-AI-Job-Description-Rainbow-Jobs-"}
FULL_NAME = "/".join(REPO.values())
PR = {
    "state": "open",
    "merged": False,
    "draft": False,
    "mergeable": True,
    "title": "Test candidate",
    "labels": [],
    "head": {"sha": HEAD, "ref": "feature", "repo": {"full_name": FULL_NAME}},
    "base": {"sha": BASE, "ref": "main"},
}
RUN = {
    "id": 100,
    "workflow_id": 42,
    "head_sha": HEAD,
    "name": "PR Quality Checks",
    "path": ".github/workflows/pr-review.yml",
    "event": "pull_request",
    "status": "completed",
    "conclusion": "success",
    "repository": {"full_name": FULL_NAME},
    "head_repository": {"full_name": FULL_NAME},
    "pull_requests": [{
        "number": 1,
        "head": {"sha": HEAD, "ref": "feature", "repo": {"full_name": FULL_NAME}},
    }],
}
FIXTURE = {
    "pr": PR,
    "run": RUN,
    "workflows": [{
        "id": 42,
        "name": "PR Quality Checks",
        "path": ".github/workflows/pr-review.yml",
    }],
    "reviews": [{
        "state": "APPROVED",
        "commit_id": HEAD,
        "submitted_at": "2026-01-01T00:00:00Z",
        "user": {"login": "Rainbowjobs94"},
    }],
    "jobs": [{
        "name": "Quality checks",
        "status": "completed",
        "conclusion": "success",
    }],
    "checks": [{
        "name": "Quality checks",
        "status": "completed",
        "conclusion": "success",
    }],
    "statuses": [],
    "runs": [{
        "id": 100,
        "workflow_id": 42,
        "status": "completed",
        "conclusion": "success",
    }],
    "merge_result": {"merged": True},
    "fail_endpoint": None,
}

HARNESS = r"""
const fs = require('fs');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const f = input.fixture;
const calls = [], outputs = {};
const endpoint = kind => Object.assign(async args => {
  calls.push({kind, args});
  if (f.fail_endpoint === kind) throw new Error('Mocked API denial');
  if (kind === 'get') {
    const count = calls.filter(c => c.kind === 'get').length;
    return {data: count > 1 && f.fresh_pr ? f.fresh_pr : f.pr};
  }
  if (kind === 'run') return {data: f.run};
  if (kind === 'workflows') return {data: {workflows: f.workflows}};
  if (kind === 'merge') return {data: f.merge_result};
}, {kind});
const github = {rest: {
  actions: {
    getWorkflowRun: endpoint('run'),
    listRepoWorkflows: endpoint('workflows'),
    listJobsForWorkflowRun: {kind:'jobs'},
    listWorkflowRunsForRepo: {kind:'runs'}
  },
  pulls: {
    get: endpoint('get'),
    listReviews: {kind:'reviews'},
    merge: endpoint('merge')
  },
  repos: {
    listCommitStatusesForRef: {kind:'statuses'}
  },
  checks: {listForRef: {kind:'checks'}}
}, paginate: async (method, args) => {
  calls.push({kind:method.kind, args});
  if (f.fail_endpoint === method.kind) throw new Error('Mocked API denial');
  return f[method.kind];
}};
const summary = {addHeading(){return this}, addRaw(){return this}, async write(){}};
const core = {setOutput:(k,v)=>{outputs[k]=v}, summary};
const context = {
  repo: input.repo,
  actor: 'Rainbowjobs94',
  eventName: 'workflow_run',
  runId: 999,
  payload: {workflow_run: f.run}
};
(async () => {
  try {
    const AsyncFunction = Object.getPrototypeOf(async function(){}).constructor;
    await new AsyncFunction('github','context','core','process',input.script)(
      github,context,core,{env:{PR_NUMBER:'1',EXPECTED_HEAD_SHA:'a'.repeat(40),EXPECTED_BASE_SHA:'b'.repeat(40)}}
    );
    process.stdout.write(JSON.stringify({ok:true,calls,outputs}));
  } catch (e) {
    process.stdout.write(JSON.stringify({ok:false,error:e.message,calls,outputs}));
  }
})();
"""


class AutoMergeWorkflowTests(unittest.TestCase):
    def run_script(self, job, fixture=None):
        fixture = copy.deepcopy(fixture or FIXTURE)
        steps = MERGE_WORKFLOW["jobs"][job]["steps"]
        step_id = "resolve" if job == "resolve" else "merge"
        step = next(s for s in steps if s.get("id") == step_id)
        result = subprocess.run(
            ["node", "-e", HARNESS],
            input=json.dumps({
                "script": step["with"]["script"],
                "fixture": fixture,
                "repo": REPO,
            }),
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
        return json.loads(result.stdout)

    def assert_blocked(self, fixture, job="merge-pr"):
        result = self.run_script(job, fixture)
        self.assertFalse(result["ok"], result)
        self.assertFalse(
            any(c["kind"] == "merge" for c in result["calls"]),
            result,
        )

    def test_privileged_workflow_only_accepts_trusted_workflow_run(self):
        self.assertIn("workflow_run", MERGE_WORKFLOW["on"])
        self.assertNotIn("workflow_dispatch", MERGE_WORKFLOW["on"])
        self.assertNotIn("pull_request", MERGE_WORKFLOW["on"])
        self.assertEqual(MERGE_WORKFLOW["permissions"]["contents"], "read")
        self.assertEqual(MERGE_WORKFLOW["jobs"]["merge-pr"]["permissions"]["contents"], "write")
        self.assertFalse(any(
            "checkout" in step.get("uses", "")
            for step in MERGE_WORKFLOW["jobs"]["merge-pr"]["steps"]
        ))

    def test_untrusted_quality_workflow_is_read_only(self):
        self.assertIn("pull_request", QUALITY_WORKFLOW["on"])
        self.assertEqual(QUALITY_WORKFLOW["permissions"]["contents"], "read")
        self.assertEqual(QUALITY_WORKFLOW["permissions"]["pull-requests"], "read")
        for job in QUALITY_WORKFLOW["jobs"].values():
            self.assertNotIn("write", job.get("permissions", {}).values())
        self.assertTrue(any(
            step.get("with", {}).get("persist-credentials") is False
            for step in QUALITY_WORKFLOW["jobs"]["quality"]["steps"]
            if step.get("uses", "").startswith("actions/checkout@")
        ))

    def test_yaml_has_no_unsafe_pull_request_target_or_dispatch_write_path(self):
        self.assertNotIn("pull_request_target", QUALITY_WORKFLOW["on"])
        self.assertIn("workflow_dispatch", QUALITY_WORKFLOW["on"])
        self.assertNotIn("workflow_dispatch", MERGE_WORKFLOW["on"])
        self.assertNotIn("pull_request_target", MERGE_WORKFLOW["on"])
        self.assertEqual(
            MERGE_WORKFLOW["jobs"]["merge-pr"]["if"],
            "${{ needs.resolve.outputs.approved_merge == 'true' }}",
        )

    def test_exact_owner_approval_preserves_auto_merge(self):
        result = self.run_script("resolve")
        self.assertTrue(result["ok"], result)
        self.assertEqual(result["outputs"]["approved_merge"], "true")
        result = self.run_script("merge-pr")
        self.assertTrue(result["ok"], result)
        merges = [c for c in result["calls"] if c["kind"] == "merge"]
        self.assertEqual(len(merges), 1)
        self.assertEqual(merges[0]["args"]["sha"], HEAD)

    def test_dispatch_run_is_never_a_merge_authorization(self):
        f = copy.deepcopy(FIXTURE)
        f["run"]["event"] = "workflow_dispatch"
        self.assert_blocked(f, "resolve")

    def test_wrong_workflow_run_is_rejected(self):
        for field, value in [
            ("name", "Untrusted lookalike"),
            ("conclusion", "failure"),
            ("event", "push"),
            ("workflow_id", 1000),
        ]:
            f = copy.deepcopy(FIXTURE)
            if field == "workflow_id":
                f["workflows"][0]["id"] = value
            else:
                f["run"][field] = value
            with self.subTest(field=field):
                self.assert_blocked(f, "resolve")

    def test_owner_approval_must_match_exact_current_head_and_be_latest(self):
        variants = [
            [],
            [{
                "state": "APPROVED", "commit_id": "c" * 40,
                "submitted_at": "2026-01-01T00:00:00Z",
                "user": {"login": "Rainbowjobs94"},
            }],
            [{
                "state": "APPROVED", "commit_id": HEAD,
                "submitted_at": "2026-01-01T00:00:00Z",
                "user": {"login": "another-user"},
            }],
            [
                copy.deepcopy(FIXTURE["reviews"][0]),
                {
                    "state": "CHANGES_REQUESTED", "commit_id": HEAD,
                    "submitted_at": "2026-01-02T00:00:00Z",
                    "user": {"login": "Rainbowjobs94"},
                },
            ],
        ]
        for reviews in variants:
            f = copy.deepcopy(FIXTURE)
            f["reviews"] = reviews
            with self.subTest(reviews=reviews):
                self.assert_blocked(f, "resolve")
                self.assert_blocked(f, "merge-pr")

    def test_closed_draft_held_fork_stacked_or_changed_pr_is_rejected(self):
        variants = [
            {"state": "closed"},
            {"merged": True},
            {"draft": True},
            {"mergeable": False},
            {"head": {"sha": "c" * 40, "ref": "feature", "repo": {"full_name": FULL_NAME}}},
            {"base": {"sha": BASE, "ref": "other-branch"}},
            {"head": {"sha": HEAD, "ref": "feature", "repo": {"full_name": "fork/other"}}},
        ]
        for label in [
            "do-not-merge", "release-hold", "review-hold", "runtime-hold",
            "operator:hold", "operator:stop",
        ]:
            variants.append({"labels": [{"name": label}]})
        for changes in variants:
            f = copy.deepcopy(FIXTURE)
            f["pr"].update(changes)
            with self.subTest(changes=changes):
                self.assert_blocked(f, "resolve")
                self.assert_blocked(f, "merge-pr")

    def test_quality_job_must_have_actually_passed(self):
        variants = [
            [],
            [{"name": "Quality checks", "status": "completed", "conclusion": "failure"}],
            [{"name": "Quality checks", "status": "in_progress", "conclusion": None}],
            [{"name": "Other job", "status": "completed", "conclusion": "success"}],
        ]
        for jobs in variants:
            f = copy.deepcopy(FIXTURE)
            f["jobs"] = jobs
            with self.subTest(jobs=jobs):
                self.assert_blocked(f, "resolve")

    def test_unavailable_trusted_job_metadata_fails_closed(self):
        f = copy.deepcopy(FIXTURE)
        f["fail_endpoint"] = "jobs"
        self.assert_blocked(f, "resolve")

    def test_sha_pinned_merge_leaves_branch_rule_enforcement_to_github(self):
        merge_script = MERGE_WORKFLOW["jobs"]["merge-pr"]["steps"][0]["with"]["script"]
        self.assertIn("sha: expectedHead", merge_script)
        self.assertNotIn("administration", MERGE_WORKFLOW["jobs"]["merge-pr"]["permissions"])

    def test_pending_failed_skipped_or_unknown_checks_deny_merge(self):
        for status, conclusion in [
            ("in_progress", None),
            ("completed", "failure"),
            ("completed", "skipped"),
            ("completed", None),
        ]:
            f = copy.deepcopy(FIXTURE)
            f["checks"][0].update(status=status, conclusion=conclusion)
            with self.subTest(status=status, conclusion=conclusion):
                self.assert_blocked(f)

    def test_failed_commit_status_denies_merge(self):
        f = copy.deepcopy(FIXTURE)
        f["statuses"] = [{"context": "external", "state": "failure"}]
        self.assert_blocked(f)

    def test_pending_or_failed_additional_workflow_denies_merge(self):
        for status, conclusion in [
            ("in_progress", None),
            ("completed", "failure"),
        ]:
            f = copy.deepcopy(FIXTURE)
            f["runs"] = [{
                "id": 99, "workflow_id": 10,
                "status": status, "conclusion": conclusion,
            }]
            with self.subTest(status=status, conclusion=conclusion):
                self.assert_blocked(f)

    def test_pr_change_during_final_validation_denies_merge(self):
        f = copy.deepcopy(FIXTURE)
        f["fresh_pr"] = copy.deepcopy(f["pr"])
        f["fresh_pr"]["head"]["sha"] = "c" * 40
        self.assert_blocked(f)

    def test_github_api_errors_fail_closed(self):
        for endpoint_name in [
            "run", "workflows", "jobs", "get", "reviews",
            "checks", "statuses", "runs",
        ]:
            f = copy.deepcopy(FIXTURE)
            f["fail_endpoint"] = endpoint_name
            with self.subTest(endpoint=endpoint_name):
                self.assert_blocked(f, "resolve" if endpoint_name in ("run", "workflows", "jobs") else "merge-pr")

    def test_unconfirmed_merge_is_not_reported_as_success(self):
        f = copy.deepcopy(FIXTURE)
        f["merge_result"] = {"merged": False}
        result = self.run_script("merge-pr", f)
        self.assertFalse(result["ok"])
        self.assertIn("did not confirm", result["error"])


if __name__ == "__main__":
    unittest.main()
