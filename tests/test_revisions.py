import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from src.hab.revisions import MAX_BYTES, compare_revisions, read_snapshot

NOW = "2026-10-10T02:00:00+00:00"


def snapshot(entries=None, when=NOW):
    return {"schema": "hab-revisions/1", "observed_at": when, "sources": entries or []}


def source(identity="repo:example:main", revision="a" * 40, status="OBSERVED"):
    return {"id": identity, "revision": revision, "status": status}


class RevisionTests(unittest.TestCase):
    def compare(self, before, after):
        return compare_revisions(before, after, now=NOW)

    def test_same_revision_ignores_push_timestamp(self):
        old, new = source(), {**source(), "pushed_at": "2099-01-01T00:00:00Z"}
        result = self.compare(snapshot([old]), snapshot([new]))
        self.assertEqual(result["counts"]["UNCHANGED"], 1)
        self.assertFalse(result["automatic_actions_enabled"])
        self.assertFalse(result["financial_actions_enabled"])

    def test_changed_branch_and_project_remain_separate(self):
        result = self.compare(snapshot([source()]), snapshot([
            source(revision="b" * 40), source("repo:example:feature"), source("replit:example")]))
        self.assertEqual(result["counts"]["CHANGED"], 1)
        self.assertEqual(result["counts"]["NEW"], 2)
        self.assertTrue(all(row["review_required"] for row in result["changes"]))

    def test_absent_source_never_means_delete(self):
        result = self.compare(snapshot([source()]), snapshot())
        self.assertEqual(result["changes"][0]["state"], "UNAVAILABLE")
        self.assertIn("NOT a deletion", result["changes"][0]["reason"])

    def test_empty_source_is_blocked(self):
        result = self.compare(snapshot(), snapshot([source(revision=None, status="EMPTY")]))
        self.assertEqual(result["counts"]["BLOCKED"], 1)

    def test_stale_and_future_observations_block(self):
        for when, reason in [("2026-10-08T02:00:00Z", "STALE_OBSERVATION"),
                             ("2026-10-11T02:00:00Z", "FUTURE_OBSERVATION")]:
            with self.subTest(when=when):
                result = self.compare(snapshot(), snapshot([source()], when))
                self.assertEqual(result["changes"][0]["reason"], reason)

    def test_invalid_id_revision_state_timestamp_and_duplicates(self):
        invalid = [
            snapshot([source(), source()]),
            snapshot([source(revision="abc")]),
            snapshot([source(identity="bad\nid")]),
            snapshot([source(status="DEPLOYED")]),
            snapshot([source(revision="a" * 40, status="EMPTY")]),
            snapshot([source()], "2026-10-10T02:00:00"),
        ]
        for value in invalid:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.compare(snapshot(), value)

    def test_bounds_and_schema(self):
        for value in [{}, snapshot([source(str(i)) for i in range(201)])]:
            with self.assertRaises(ValueError):
                self.compare(snapshot(), value)
        for age in [0, -1, True, float("nan"), float("inf"), 8761]:
            with self.assertRaises(ValueError):
                compare_revisions(snapshot(), snapshot(), now=NOW, max_age_hours=age)

    def test_bounded_file_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(snapshot()))
            self.assertEqual(read_snapshot(path)["sources"], [])
            path.write_bytes(b" " * (MAX_BYTES + 1))
            with self.assertRaises(ValueError):
                read_snapshot(path)

    def test_cli_read_only_and_refuses_output_overwrite(self):
        root = Path(__file__).resolve().parent.parent
        with tempfile.TemporaryDirectory() as directory:
            store, previous, current, output = [Path(directory) / name
                for name in ("store", "previous.json", "current.json", "report.json")]
            previous.write_text(json.dumps(snapshot()))
            current.write_text(json.dumps(snapshot()))
            command = [sys.executable, "-m", "src.hab.cli", "--store", str(store),
                       "reconcile", str(previous), str(current), "--output", str(output)]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(store.exists())
            original = output.read_bytes()
            again = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
