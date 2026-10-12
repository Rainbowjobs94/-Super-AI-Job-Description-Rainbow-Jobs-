"""Bounded source intake, deterministic bundles and human-approved local merges.

No subprocess execution, chain signing, provider SDKs or automatic deployments.
The object store is private local operator data, not a public asset service.
"""
import hashlib
from datetime import date
import io
import json
import os
import re
import sqlite3
import stat
import unicodedata
import zipfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

MAX_FILE = 16 * 1024 * 1024
MAX_EXPANDED = 64 * 1024 * 1024
MAX_MEMBERS = 4096
MAX_STORAGE = 256 * 1024 * 1024
MAX_RATIO = 100
HASH = re.compile(r"^[a-f0-9]{64}$")
SECRET_PATTERNS = (
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"\b(?:ghp_|github_pat_|sk_live_|sk-proj-)[A-Za-z0-9_]{16,}"),
    re.compile(rb'(?i)(?:private_key|api_key|auth_token|password)\s*[:=]\s*["\']?[A-Za-z0-9+/=_-]{24,}'),
)
BLOCKED_NAMES = {".env", ".git", ".venv", ".pythonlibs", "__pycache__",
                 "node_modules", "profile.md", ".ds_store", ".git-credentials", ".gitconfig"}
STATES = {"PROPOSED", "OBSERVED", "IMPLEMENTED", "TESTED", "BLOCKED"}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    """Conservative portable path policy, including Windows and Unicode hazards."""
    if not isinstance(name, str) or not name or len(name) > 1024:
        raise ValueError("Invalid path")
    if "\\" in name or any(c in name for c in ':?*"<>|\x00') or name.startswith("/"):
        raise ValueError("Unsafe path")
    if unicodedata.normalize("NFC", name) != name:
        raise ValueError("Non-canonical path")
    parts = name.split("/")
    reserved = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10))}
    if len(parts) > 32 or any(len(p) > 240 or p in ("", ".", "..") or p.endswith((" ", ".")) or
           any(ord(c) < 32 for c in p) or p.split(".")[0].upper() in reserved
           for p in parts):
        raise ValueError("Unsafe path")
    return str(PurePosixPath(name))


def private_path(name):
    return any(p.casefold() in BLOCKED_NAMES or p.casefold().startswith(".env")
               for p in PurePosixPath(name).parts)


def flags_for(name, data):
    flags = []
    if private_path(name):
        flags.append("restricted_path")
    if any(pattern.search(data) for pattern in SECRET_PATTERNS):
        flags.append("possible_secret")
    return flags


def archive_name(name):
    """Retain original member names as metadata; encode nonportable punctuation.

    This never normalizes traversal, backslashes, drive paths or symlinks.
    Percent signs are not decoded by Hab; collisions after encoding are rejected.
    """
    if re.match(r"^[a-zA-Z]:", name):
        raise ValueError("Windows drive member rejected")
    mapped = "".join(f"%{ord(c):02X}" if c in ':?*"<>|' else c for c in name)
    return safe_name(mapped)


def validated_members(data):
    """Return validated bytes without extracting a ZIP onto the filesystem."""
    if len(data) > MAX_EXPANDED:
        raise ValueError("Archive input exceeds limit")
    result, seen, expanded = [], set(), 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        infos = archive.infolist()
        if len(infos) > MAX_MEMBERS:
            raise ValueError("Archive member limit exceeded")
        for info in infos:
            mode = info.external_attr >> 16
            name = archive_name(info.filename.rstrip("/") if info.is_dir() else info.filename)
            key = name.casefold()
            if key in seen:
                raise ValueError("Duplicate or case-colliding archive path")
            seen.add(key)
            if info.flag_bits & 1 or stat.S_ISLNK(mode):
                raise ValueError("Encrypted or symlink member rejected")
            if mode and stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                raise ValueError("Special file rejected")
            if info.is_dir():
                continue
            expanded += info.file_size
            if info.file_size > MAX_FILE or expanded > MAX_EXPANDED:
                raise ValueError("Expanded archive limit exceeded")
            if info.file_size / max(info.compress_size, 1) > MAX_RATIO:
                raise ValueError("Compression ratio limit exceeded")
            if name.lower().endswith((".zip", ".tar", ".gz", ".7z", ".rar")):
                raise ValueError("Nested archives require separate explicit intake")
            content = archive.read(info)  # validates ZIP CRC
            if len(content) != info.file_size:
                raise ValueError("Archive size mismatch")
            result.append((name, content))
    return result


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.objects = self.root / "objects"
        self.objects.mkdir(parents=True, exist_ok=True)
        self.database = self.root / "catalog.sqlite3"
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sources(
                  id TEXT PRIMARY KEY, manifest TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS aliases(
                  source_id TEXT, name TEXT, UNIQUE(source_id, name));
                CREATE TABLE IF NOT EXISTS records(
                  kind TEXT, id TEXT, body TEXT, PRIMARY KEY(kind,id));
                CREATE TABLE IF NOT EXISTS budget(
                  singleton INTEGER PRIMARY KEY CHECK(singleton=1),
                  used INTEGER NOT NULL);
                INSERT OR IGNORE INTO budget VALUES(1,0);
                CREATE TABLE IF NOT EXISTS checkpoints(
                  request_id TEXT PRIMARY KEY, result TEXT NOT NULL);
            """)

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.database, timeout=10)
        db.execute("PRAGMA busy_timeout=10000")
        try:
            with db:
                yield db
        finally:
            db.close()

    def read_object(self, sha):
        if not isinstance(sha, str) or not HASH.fullmatch(sha):
            raise ValueError("Invalid object ID")
        path = self.objects / sha
        if path.is_symlink():
            raise ValueError("Object symlink rejected")
        data = path.read_bytes()
        if digest(data) != sha:
            raise ValueError("Object integrity failure")
        return data

    def ingest(self, name, data):
        portable_name = archive_name(name)
        if not isinstance(data, bytes) or len(data) > MAX_EXPANDED:
            raise ValueError("Source input exceeds limit")
        members = validated_members(data) if name.lower().endswith(".zip") else [(portable_name, data)]
        if not name.lower().endswith(".zip") and len(data) > MAX_FILE:
            raise ValueError("File exceeds limit")
        source_id = digest(data)
        entries = [{"path": path, "sha256": digest(content), "bytes": len(content),
                    "flags": flags_for(path, content)} for path, content in members]
        if name.lower().endswith(".zip"):
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                original_names = {archive_name(i.filename): i.filename for i in archive.infolist()
                                  if not i.is_dir()}
            for entry in entries:
                entry["original_path"] = original_names[entry["path"]]
        else:
            entries[0]["original_path"] = name
        entries.sort(key=lambda x: x["path"])
        manifest = {"format": "ltpkg-source/1", "id": source_id,
                    "license_status": "UNREVIEWED", "evidence": "OBSERVED",
                    "entries": entries}
        # Exclusive DB transaction serializes quota and catalog modifications.
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            blobs = {digest(content): content for _, content in members}
            blobs[source_id] = data
            needed = {sha: b for sha, b in blobs.items() if not (self.objects / sha).exists()}
            stored = sum(p.stat().st_size for p in self.objects.iterdir() if p.is_file())
            if stored + sum(map(len, needed.values())) > MAX_STORAGE:
                raise ValueError("Local storage budget exhausted")
            for sha, content in blobs.items():
                path = self.objects / sha
                if path.exists():
                    self.read_object(sha)
                else:
                    with path.open("xb") as out:
                        out.write(content)
            db.execute("INSERT OR IGNORE INTO sources VALUES(?,?)",
                       (source_id, canonical(manifest).decode()))
            db.execute("INSERT OR IGNORE INTO aliases VALUES(?,?)", (source_id, name))
        return self.source(source_id)

    def source(self, source_id):
        if not isinstance(source_id, str) or not HASH.fullmatch(source_id):
            raise ValueError("Invalid source ID")
        with self.connect() as db:
            row = db.execute("SELECT manifest FROM sources WHERE id=?", (source_id,)).fetchone()
            aliases = db.execute("SELECT name FROM aliases WHERE source_id=? ORDER BY name",
                                 (source_id,)).fetchall()
        if row is None:
            raise ValueError("Source not found")
        return {**json.loads(row[0]), "aliases": [a[0] for a in aliases]}

    def sources(self):
        with self.connect() as db:
            ids = [r[0] for r in db.execute("SELECT id FROM sources ORDER BY id")]
        return [self.source(source_id) for source_id in ids]

    def export(self, source_ids):
        if not isinstance(source_ids, list) or not source_ids or len(source_ids) > 100:
            raise ValueError("Select 1–100 source IDs")
        if any(not isinstance(sha, str) or not HASH.fullmatch(sha) for sha in source_ids):
            raise ValueError("Invalid source IDs")
        files, exclusions, provenance = {}, [], []
        for source_id in sorted(set(source_ids)):
            source = self.source(source_id)
            provenance.append(source)
            for entry in source["entries"]:
                output = f"sources/{source_id}/{entry['path']}"
                if entry["flags"]:
                    exclusions.append({"path": output, "flags": entry["flags"]})
                    continue
                files[output] = self.read_object(entry["sha256"])
        total = sum(map(len, files.values()))
        if total > MAX_EXPANDED:
            raise ValueError("Bundle exceeds export limit; split into source bundles")
        manifest = {"format": "ltpkg/1", "sources": provenance,
                    "exclusions": exclusions, "redistribution": "REVIEW_REQUIRED",
                    "files": {p: digest(b) for p, b in sorted(files.items())}}
        files["MANIFEST.ltpkg.json"] = canonical(manifest)
        return deterministic_zip(files)

    def record(self, kind, body):
        if kind not in {"task", "feature", "deployment", "research"} or not isinstance(body, dict):
            raise ValueError("Unsupported record kind")
        record_id = body.get("id")
        if not isinstance(record_id, str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", record_id):
            raise ValueError("Record ID must be an ASCII slug")
        status = body.get("status", "PROPOSED")
        if not isinstance(status, str) or status not in STATES:
            raise ValueError("Unsupported evidence status; no self-certified DEPLOYED status")
        if status in {"IMPLEMENTED", "TESTED"} and not body.get("evidence"):
            raise ValueError("Evidence reference required")
        result = {**body, "status": status}
        if len(canonical(result)) > 16384:
            raise ValueError("Record exceeds size limit")
        if kind == "research":
            if not isinstance(body.get("url"), str):
                raise ValueError("Research requires HTTPS source URL")
            parsed = urlparse(body.get("url", ""))
            if parsed.scheme != "https" or not parsed.hostname or parsed.username:
                raise ValueError("Research requires HTTPS source URL")
            retrieved = body.get("retrieved_on", "")
            if not isinstance(retrieved, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", retrieved):
                raise ValueError("Retrieval date required")
            try:
                date.fromisoformat(retrieved)
            except ValueError:
                raise ValueError("Invalid retrieval date") from None
            result["live_verified"] = False
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            exists = db.execute("SELECT 1 FROM records WHERE kind=? AND id=?",
                                (kind, record_id)).fetchone()
            if not exists and db.execute("SELECT COUNT(*) FROM records").fetchone()[0] >= 1000:
                raise ValueError("Registry record limit reached")
            if kind == "deployment":
                chain = body.get("chain_id")
                address = body.get("address", "")
                role = body.get("role", "")
                if (type(chain) is not int or chain <= 0 or not isinstance(role, str) or
                        not role or not isinstance(address, str) or
                        not re.fullmatch(r"0x[0-9a-fA-F]{40}", address)):
                    raise ValueError("Deployment candidate needs chain ID, role and EVM address")
                result["address"] = address.lower()
                result["live_verified"] = False
                # Neither same chain/address nor same logical role may be duplicated.
                for row in db.execute("SELECT id,body FROM records WHERE kind='deployment'"):
                    existing = json.loads(row[1])
                    if row[0] != record_id and existing["chain_id"] == chain and (
                            existing["address"] == address.lower() or existing["role"] == role):
                        raise ValueError("Duplicate deployment candidate; reconcile existing record")
            db.execute("INSERT INTO records VALUES(?,?,?) ON CONFLICT(kind,id) DO UPDATE SET body=excluded.body",
                       (kind, record_id, canonical(result).decode()))
        return result

    def records(self, kind):
        if kind not in {"task", "feature", "deployment", "research"}:
            raise ValueError("Unsupported record kind")
        with self.connect() as db:
            return [json.loads(r[0]) for r in db.execute(
                "SELECT body FROM records WHERE kind=? ORDER BY id", (kind,))]

    def plan_request(self, raw, request_id, limit=100):
        if not isinstance(raw, str) or not raw.strip() or len(raw) > 12000:
            raise ValueError("Request must contain 1–12000 characters")
        if not isinstance(request_id, str) or not re.fullmatch(r"[a-zA-Z0-9-]{8,80}", request_id):
            raise ValueError("Valid idempotency key required")
        if type(limit) is not int or limit < 0:
            raise ValueError("Invalid budget limit")
        fingerprint = digest(raw.encode())
        with self.connect() as db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute("SELECT result FROM checkpoints WHERE request_id=?", (request_id,)).fetchone()
            if prior:
                result = json.loads(prior[0])
                if result["fingerprint"] != fingerprint:
                    raise ValueError("Idempotency key reused with different input")
                return result
            cost = max(1, (len(raw) + 999) // 1000)
            used = db.execute("SELECT used FROM budget WHERE singleton=1").fetchone()[0]
            if used + cost > limit:
                raise ValueError("Planning budget exhausted; checkpoint preserved, no paid fallback")
            result = extract_request(raw)
            result.update({"request_id": request_id, "fingerprint": fingerprint,
                           "planning_units": cost, "used": used + cost, "limit": limit,
                           "external_model_calls": 0})
            db.execute("UPDATE budget SET used=used+? WHERE singleton=1", (cost,))
            db.execute("INSERT INTO checkpoints VALUES(?,?)", (request_id, canonical(result).decode()))
        return result


def deterministic_zip(files):
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in sorted(files.items()):
            safe_name(name)
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return output.getvalue()


def extract_request(raw):
    normalized = unicodedata.normalize("NFKC", raw)
    normalized = re.sub(r"([a-z])([A-Z])", r"\1 \2", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    text = normalized.casefold()
    keywords = {
        "archive": ("archive", "zip", "download", "package"),
        "merge": ("merge", "sync", "transfer", "migration"),
        "review": ("review", "audit", "security"),
        "skills": ("skill", "agent"),
        "research": ("research", "regulation", "laws", "tax"),
        "financial": ("mint", "deploy", "liquidity", "treasury", "trade", "mining"),
    }
    candidates = [{"kind": kind, "matched_terms": [term for term in terms if term in text],
                   "status": "PROPOSED", "requires_review": True}
                  for kind, terms in keywords.items() if any(term in text for term in terms)]
    return {"original": raw, "normalized": normalized, "candidates": candidates,
            "method": "local-keyword-candidates",
            "requires_clarification": not candidates or (" " not in raw.strip() and len(raw) > 20),
            "execution_authorized": False,
            "note": "Candidates are not commands. Unspaced text and negation require human review."}


def proof_record(asset, acknowledgement, consent_reference):
    if not acknowledgement or not consent_reference:
        raise ValueError("Acknowledgment and consent reference required")
    return {"format": "ltproof/1", "asset_sha256": digest(asset),
            "acknowledgement": acknowledgement, "consent_reference": consent_reference,
            "claim_type": "unverified_contribution_statement", "signed": False,
            "market_value_verified": False, "tax_deduction_verified": False,
            "zero_knowledge_proof": False}


def target_path(root, name):
    name = safe_name(name)
    if private_path(name) or any(p.startswith(".") for p in PurePosixPath(name).parts):
        raise ValueError("Restricted destination")
    root = Path(root).resolve()
    candidate = root / name
    for parent in [candidate, *candidate.parents]:
        if parent == root:
            break
        if parent.is_symlink():
            raise ValueError("Destination symlink rejected")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError("Destination escapes root")
    return candidate


def plan_merge(store, source_id, destination, mappings):
    if not isinstance(mappings, dict) or not mappings or len(mappings) > MAX_MEMBERS:
        raise ValueError("Explicit source-to-destination mappings required")
    source = store.source(source_id)
    entries = {e["path"]: e for e in source["entries"]}
    plan, seen = [], set()
    for origin, name in sorted(mappings.items()):
        if origin not in entries:
            raise ValueError("Unknown source path")
        entry = entries[origin]
        if entry["flags"]:
            raise ValueError("Restricted source cannot be merged")
        store.read_object(entry["sha256"])
        target = target_path(destination, name)
        key = name.casefold()
        if key in seen:
            raise ValueError("Duplicate destination")
        seen.add(key)
        if target.exists() and (not target.is_file() or target.stat().st_size > MAX_FILE):
            raise ValueError("Unsupported destination file")
        before = digest(target.read_bytes()) if target.exists() else None
        status = "ADD" if before is None else "IDENTICAL" if before == entry["sha256"] else "CONFLICT"
        plan.append({"source": origin, "destination": name, "before": before,
                     "after": entry["sha256"], "status": status})
    body = {"format": "ltmerge/1", "source_id": source_id,
            "destination_root": str(Path(destination).resolve()), "entries": plan}
    return {**body, "approval_sha256": digest(canonical(body))}


@contextmanager
def merge_lock(store):
    # POSIX-local workflow; unsupported platforms fail rather than run unlocked.
    import fcntl
    with (store.root / "merge.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


def atomic_json(path, body):
    temp = path.with_suffix(".tmp")
    temp.write_bytes(canonical(body))
    os.replace(temp, path)


def apply_merge(store, plan, approval, allow_conflicts=False):
    body = {k: v for k, v in plan.items() if k != "approval_sha256"}
    if digest(canonical(body)) != approval or plan.get("approval_sha256") != approval:
        raise ValueError("Plan approval hash mismatch")
    if any(e["status"] == "CONFLICT" for e in plan["entries"]) and not allow_conflicts:
        raise ValueError("Conflicts require explicit overwrite approval")
    mappings = {e["source"]: e["destination"] for e in plan["entries"]}
    journal_path = store.root / f"merge-{approval}.json"
    with merge_lock(store):
        if journal_path.exists():
            raise ValueError("Merge already journaled; inspect or rollback before retry")
        refreshed = plan_merge(store, plan["source_id"], plan["destination_root"], mappings)
        if refreshed != plan:
            raise ValueError("Destination changed since preview")
        journal = {"plan": plan, "status": "APPLYING", "written": [], "backups": {}}
        # Commit backups and intended write list before touching destination files.
        backup_bytes = 0
        for entry in plan["entries"]:
            if entry["status"] != "IDENTICAL":
                target = target_path(plan["destination_root"], entry["destination"])
                old = target.read_bytes() if target.exists() else None
                if old is not None:
                    backup_bytes += len(old)
                    if backup_bytes > MAX_EXPANDED:
                        raise ValueError("Rollback backup limit exceeded")
                    old_hash = digest(old)
                    backup_path = store.root / ("backup-" + old_hash)
                    if not backup_path.exists():
                        backup_path.write_bytes(old)
                    journal["backups"][entry["destination"]] = old_hash
                else:
                    journal["backups"][entry["destination"]] = None
        atomic_json(journal_path, journal)
        try:
            for entry in plan["entries"]:
                if entry["status"] == "IDENTICAL":
                    continue
                target = target_path(plan["destination_root"], entry["destination"])
                actual = digest(target.read_bytes()) if target.exists() else None
                if actual != entry["before"]:
                    raise ValueError("Destination changed during merge")
                target.parent.mkdir(parents=True, exist_ok=True)
                # Journal intent before atomic replace to support interrupted recovery.
                journal["written"].append(entry["destination"])
                atomic_json(journal_path, journal)
                temp = target.with_name(target.name + ".hab-" + approval[:12])
                with temp.open("xb") as out:
                    out.write(store.read_object(entry["after"]))
                os.replace(temp, target)
            journal["status"] = "COMPLETE"
        except Exception:
            journal["status"] = "FAILED"
            raise
        finally:
            atomic_json(journal_path, journal)
    return journal_path


def rollback_merge(store, approval):
    if not HASH.fullmatch(approval):
        raise ValueError("Invalid approval hash")
    path = store.root / f"merge-{approval}.json"
    with merge_lock(store):
        journal = json.loads(path.read_text())
        if journal["status"] == "ROLLED_BACK":
            return journal
        plan = journal["plan"]
        entries = {e["destination"]: e for e in plan["entries"]}
        # Preflight every target before changing anything.
        for name in journal["written"]:
            entry = entries[name]
            target = target_path(plan["destination_root"], name)
            actual = digest(target.read_bytes()) if target.exists() else None
            if actual not in (entry["before"], entry["after"]):
                raise ValueError("Rollback blocked: destination changed after merge")
            backup = journal["backups"][name]
            if backup is not None and digest((store.root / ("backup-" + backup)).read_bytes()) != backup:
                raise ValueError("Backup integrity failure")
        for name in reversed(journal["written"]):
            target = target_path(plan["destination_root"], name)
            backup = journal["backups"][name]
            if backup is None:
                target.unlink(missing_ok=True)
            else:
                content = (store.root / ("backup-" + backup)).read_bytes()
                if digest(content) != backup:
                    raise ValueError("Backup integrity failure")
                temp = target.with_name(target.name + ".hab-rollback")
                with temp.open("xb") as out:
                    out.write(content)
                os.replace(temp, target)
        journal["status"] = "ROLLED_BACK"
        atomic_json(path, journal)
    return journal
