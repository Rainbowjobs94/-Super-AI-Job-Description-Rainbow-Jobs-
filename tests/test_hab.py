import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from src.hab.core import (Store, validated_members, safe_name, deterministic_zip,
                          plan_merge, apply_merge, rollback_merge, proof_record)
from src.hub import app


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = Store(self.root / "store")

    def tearDown(self):
        self.tmp.cleanup()

    def test_same_bytes_preserve_aliases(self):
        first = self.store.ingest("first.txt", b"same")
        second = self.store.ingest("second.txt", b"same")
        self.assertEqual(first["id"], second["id"])
        self.assertEqual(second["aliases"], ["first.txt", "second.txt"])
        self.assertEqual(len(self.store.sources()), 1)

    def test_paths(self):
        for path in ("../bad", "/bad", "a\\bad", "a/../bad", "C:bad", "a//bad",
                     "CON.txt", "a.", "a/b\x00", "a/\x01", "a/e\u0301"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                safe_name(path)

    def test_zip_traversal_and_collision(self):
        for names in (["../bad"], ["a.txt", "A.txt"]):
            raw = io.BytesIO()
            with zipfile.ZipFile(raw, "w") as z:
                for name in names:
                    z.writestr(name, b"hello")
            with self.assertRaises(ValueError):
                validated_members(raw.getvalue())

    def test_symlink_and_nested_archive(self):
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as z:
            info = zipfile.ZipInfo("link")
            info.external_attr = 0o120777 << 16
            z.writestr(info, "target")
        with self.assertRaises(ValueError):
            validated_members(raw.getvalue())
        with self.assertRaises(ValueError):
            validated_members(deterministic_zip({"nested.zip": b"not executed"}))

    def test_zip_ratio_limit(self):
        with self.assertRaises(ValueError):
            validated_members(deterministic_zip({"bomb.txt": b"a" * 1000000}))

    def test_nonportable_archive_name_preserved_without_filesystem_extraction(self):
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as z:
            z.writestr("docs/Love: Vision.pdf", b"source")
        source = self.store.ingest("source.zip", raw.getvalue())
        self.assertEqual(source["entries"][0]["original_path"], "docs/Love: Vision.pdf")
        self.assertEqual(source["entries"][0]["path"], "docs/Love%3A Vision.pdf")
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as z:
            z.writestr("C:/drive.txt", b"blocked")
        with self.assertRaises(ValueError):
            self.store.ingest("drive.zip", raw.getvalue())

    def test_nonportable_encoding_collision_rejected(self):
        raw = io.BytesIO()
        with zipfile.ZipFile(raw, "w") as z:
            z.writestr("docs/a:b.txt", b"first")
            z.writestr("docs/a%3Ab.txt", b"second")
        with self.assertRaises(ValueError):
            self.store.ingest("collision.zip", raw.getvalue())

    def test_export_deterministic_and_secrets_excluded(self):
        raw = deterministic_zip({"a.txt": b"visible", ".env": b"secret",
                                 "key.txt": b"-----BEGIN " + b"PRIVATE KEY-----"})
        source = self.store.ingest("source.zip", raw)
        export = self.store.export([source["id"]])
        self.assertEqual(export, self.store.export([source["id"]]))
        with zipfile.ZipFile(io.BytesIO(export)) as archive:
            manifest = json.loads(archive.read("MANIFEST.ltpkg.json"))
            self.assertEqual(len(manifest["exclusions"]), 2)
            self.assertEqual(len(manifest["files"]), 1)

    def test_corrupt_object_blocks_export(self):
        source = self.store.ingest("source.txt", b"original")
        (self.store.objects / source["entries"][0]["sha256"]).write_bytes(b"changed")
        with self.assertRaises(ValueError):
            self.store.export([source["id"]])

    def test_merge_requires_conflict_approval_and_rollback(self):
        source = self.store.ingest("source.zip", deterministic_zip({"a.txt": b"new"}))
        destination = self.root / "destination"
        destination.mkdir()
        (destination / "a.txt").write_bytes(b"old")
        plan = plan_merge(self.store, source["id"], destination, {"a.txt": "a.txt"})
        self.assertEqual(plan["entries"][0]["status"], "CONFLICT")
        with self.assertRaises(ValueError):
            apply_merge(self.store, plan, plan["approval_sha256"])
        apply_merge(self.store, plan, plan["approval_sha256"], allow_conflicts=True)
        self.assertEqual((destination / "a.txt").read_bytes(), b"new")
        rollback_merge(self.store, plan["approval_sha256"])
        self.assertEqual((destination / "a.txt").read_bytes(), b"old")

    def test_changed_destination_blocks_apply(self):
        source = self.store.ingest("a.txt", b"new")
        destination = self.root / "destination"
        destination.mkdir()
        plan = plan_merge(self.store, source["id"], destination, {"a.txt": "a.txt"})
        (destination / "a.txt").write_bytes(b"concurrent")
        with self.assertRaises(ValueError):
            apply_merge(self.store, plan, plan["approval_sha256"])

    def test_changed_destination_blocks_rollback(self):
        source = self.store.ingest("a.txt", b"new")
        destination = self.root / "destination"
        destination.mkdir()
        plan = plan_merge(self.store, source["id"], destination, {"a.txt": "a.txt"})
        apply_merge(self.store, plan, plan["approval_sha256"])
        (destination / "a.txt").write_bytes(b"external edit")
        with self.assertRaises(ValueError):
            rollback_merge(self.store, plan["approval_sha256"])

    def test_partial_failure_recoverable(self):
        source = self.store.ingest("source.zip",
                                   deterministic_zip({"a.txt": b"a", "b.txt": b"b"}))
        destination = self.root / "destination"
        destination.mkdir()
        plan = plan_merge(self.store, source["id"], destination,
                          {"a.txt": "a.txt", "b.txt": "b.txt"})
        import src.hab.core as core
        original = core.os.replace
        def fail_second(a, b):
            if Path(b).name == "b.txt":
                raise OSError("synthetic interruption")
            return original(a, b)
        with patch("src.hab.core.os.replace", side_effect=fail_second):
            with self.assertRaises(OSError):
                apply_merge(self.store, plan, plan["approval_sha256"])
        journal = rollback_merge(self.store, plan["approval_sha256"])
        self.assertEqual(journal["status"], "ROLLED_BACK")
        self.assertFalse((destination / "a.txt").exists())
        self.assertFalse((destination / "b.txt").exists())

    def test_duplicate_deployment_and_no_live_certification(self):
        body = {"id": "rc", "chain_id": 137, "address": "0x" + "a" * 40,
                "role": "rc-token", "status": "OBSERVED"}
        self.assertFalse(self.store.record("deployment", body)["live_verified"])
        with self.assertRaises(ValueError):
            self.store.record("deployment", {**body, "id": "rc-copy"})
        with self.assertRaises(ValueError):
            self.store.record("deployment", {**body, "status": "DEPLOYED"})

    def test_budget_checkpoint_reuse_and_limit(self):
        result = self.store.plan_request("archiveallfilesmergeskills", "request-123", limit=1)
        self.assertTrue(result["requires_clarification"])
        self.assertFalse(result["execution_authorized"])
        self.assertEqual(result, self.store.plan_request(result["original"], "request-123", limit=1))
        with self.assertRaises(ValueError):
            self.store.plan_request("new request", "request-456", limit=1)
        with self.assertRaises(ValueError):
            self.store.plan_request("different input", "request-123", limit=100)

    def test_proof_not_value_or_zk(self):
        proof = proof_record(b"asset", "Acknowledged", "consent-ref")
        self.assertFalse(proof["signed"])
        self.assertFalse(proof["zero_knowledge_proof"])
        self.assertFalse(proof["market_value_verified"])

    def test_symlink_destination_rejected(self):
        source = self.store.ingest("a.txt", b"new")
        destination = self.root / "destination"
        destination.mkdir()
        (destination / "link").symlink_to(self.root)
        with self.assertRaises(ValueError):
            plan_merge(self.store, source["id"], destination, {"a.txt": "link/a.txt"})

    def test_source_quota(self):
        with patch("src.hab.core.MAX_STORAGE", 1):
            with self.assertRaises(ValueError):
                self.store.ingest("a.txt", b"too big")
        self.assertEqual(self.store.sources(), [])

    def test_malformed_records_and_export(self):
        for body in ({"id": "bad", "status": []}, {"id": "bad", "url": 1},
                     {"id": "bad", "url": "https://example.org", "retrieved_on": "2026-02-30"}):
            with self.assertRaises(ValueError):
                self.store.record("research", body)
        with self.assertRaises(ValueError):
            self.store.export([[]])


class WebTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = {key: app.config.get(key) for key in ("HAB_TOKEN", "HAB_STORE", "TESTING")}
        app.config.update(TESTING=True, HAB_TOKEN="test-" + "x" * 40,
                          HAB_STORE=self.tmp.name)
        self.client = app.test_client()
        self.auth = {"Authorization": "Bearer " + app.config["HAB_TOKEN"]}

    def tearDown(self):
        app.config.update(self.old)
        self.tmp.cleanup()

    def test_auth_closed(self):
        self.assertEqual(self.client.get("/api/hab/catalog").status_code, 401)
        app.config["HAB_TOKEN"] = ""
        self.assertEqual(self.client.get("/api/hab/catalog").status_code, 503)

    def test_index_public_without_data(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"IA Guardian Hab", response.data)
        self.assertEqual(response.headers["Cache-Control"], "no-store")
        self.assertIn("frame-ancestors 'none'", response.headers["Content-Security-Policy"])

    def test_malformed_json_blocked(self):
        response = self.client.post("/api/hab/parse", json=["wrong"], headers=self.auth)
        self.assertEqual(response.status_code, 400)
        response = self.client.post("/api/chat", json={"message": []}, headers=self.auth)
        self.assertEqual(response.status_code, 400)

    def test_corrupt_zip_returns_safe_error(self):
        response = self.client.post("/api/hab/intake", headers=self.auth,
                                    data={"file": (io.BytesIO(b"not zip"), "source.zip")})
        self.assertEqual(response.status_code, 400)

    def test_intake_export_and_preview(self):
        response = self.client.post("/api/hab/intake", headers=self.auth,
                                    data={"file": (io.BytesIO(b"hello"), "a.txt")})
        source = response.json["source"]
        response = self.client.post("/api/hab/export", headers=self.auth,
                                    json={"source_ids": [source["id"]]})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data.startswith(b"PK"))
        self.assertEqual(self.client.post("/api/hab/apply", headers=self.auth,
                                         json={}).status_code, 404)

    def test_restricted_reads_and_disabled_writes(self):
        for path in (".env", ".git/config", "data/hab/catalog.sqlite3"):
            self.assertEqual(self.client.get("/api/files/read?path="+path,
                                             headers=self.auth).status_code, 403)
        response = self.client.post("/api/files/write", headers=self.auth,
                                    json={"path": "src/hub.py", "content": "overwrite"})
        self.assertEqual(response.status_code, 403)

    def test_legacy_upload_cannot_overwrite(self):
        response = self.client.post("/api/files/upload", headers=self.auth,
                                    data={"path": "src/hub.py",
                                          "file": (io.BytesIO(b"overwrite"), "a.txt")})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
