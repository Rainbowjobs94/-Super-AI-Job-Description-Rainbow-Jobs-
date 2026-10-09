"""Deterministic owner-local packages; no upload, model call or code execution.

Optional private sources/library are never part of the public toolkit.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.hab.core import Store, archive_name, canonical, deterministic_zip, digest, flags_for


def write_bundle(output, name, files):
    files = {**files, "BUNDLE-CHECKSUMS.json": canonical(
        {"format": "hab-delivery/1", "files": {p: digest(b) for p, b in sorted(files.items())}})}
    path = output / name
    path.write_bytes(deterministic_zip(files))
    return {"file": name, "sha256": digest(path.read_bytes()), "bytes": path.stat().st_size,
            "members": len(files)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="exports")
    parser.add_argument("--attachments", help="Owner-private input directory; never publish")
    parser.add_argument("--library", help="Owner-private .local directory; never publish")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    deliveries = []
    toolkit = {}
    for directory in ("src", "config", "tests", "docs", ".agents/skills", "scripts"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_file() and not path.is_symlink() and "__pycache__" not in path.parts:
                content = path.read_bytes()
                if flags_for(path.name, content):
                    continue
                toolkit[str(path.relative_to(ROOT))] = content
    for name in ("README.md", "SKILLS.md", "requirements.txt", ".gitignore"):
        toolkit[name] = (ROOT / name).read_bytes()
    deliveries.append(write_bundle(output, "ia-guardian-hab-toolkit-v1.0.zip", toolkit))
    skills = {path.removeprefix(".agents/skills/"): content
              for path, content in toolkit.items() if path.startswith(".agents/skills/")}
    skills["README.md"] = (
        "IA Guardian Hab authored master + four companion skills.\n"
        "Register the master SKILL.md in the target agent. Resolve host tools explicitly.\n"
        "These skills do not provide accounts, credentials, unlimited credits or deployment authority.\n"
    ).encode()
    deliveries.append(write_bundle(output, "ia-guardian-hab-super-skills-v1.0.zip", skills))
    if args.attachments:
        store = Store(output / "private-intake-store")
        originals, original_catalog = {}, []
        for path in sorted(Path(args.attachments).iterdir()):
            if not path.is_file() or path.is_symlink():
                continue
            data = path.read_bytes()
            source = store.ingest(path.name, data)
            originals.setdefault("originals/" + source["id"] + "/" + archive_name(path.name), data)
            original_catalog.append({"name": path.name, "sha256": source["id"], "bytes": len(data)})
        # Original aliases are catalog entries; duplicate originals stored once.
        unique = {}
        for name, data in originals.items():
            unique.setdefault(digest(data), (name, data))
        originals = {name: data for name, data in unique.values()}
        catalog = {"privacy": "OWNER_PRIVATE_DO_NOT_PUBLISH", "inputs": original_catalog,
                   "unique_sources": store.sources(), "redistribution": "NOT_AUTHORIZED"}
        originals["PRIVATE-SOURCE-CATALOG.json"] = canonical(catalog)
        originals["README.md"] = (
            "Private originals: preserve ownership/privacy. Duplicate bytes stored once;\n"
            "aliases retained in catalog. Contains confidential source documents.\n"
            "Do not publish or upload to another AI service without permission.\n"
            "No imported code was executed. Unpack this delivery locally and inspect\n"
            "individual originals before intake; nested archives are not auto-expanded.\n"
        ).encode()
        deliveries.append(write_bundle(output, "ia-guardian-hab-private-sources-v1.0.zip", originals))
        # One inspected export per unique source, not unbounded or duplicated packages.
        packages = output / "source-packages"
        packages.mkdir(exist_ok=True)
        for source in store.sources():
            (packages / (source["id"] + ".ltpkg.zip")).write_bytes(store.export([source["id"]]))
        deliveries.append(write_bundle(output, "ia-guardian-hab-inspected-source-packages-v1.0.zip",
                                        {path.name: path.read_bytes()
                                         for path in sorted(packages.glob("*.ltpkg.zip"))}))
        (output / "private-source-catalog.json").write_bytes(canonical(catalog))
    if args.library:
        library = Path(args.library).resolve()
        snapshot, index, excluded, sanitized_files = {}, [], [], []
        for directory in ("skills", "custom_skills", "secondary_skills"):
            base = library / directory
            for path in sorted(base.rglob("*")):
                if not path.is_file() or path.is_symlink():
                    continue
                relative = path.relative_to(library)
                if any(part in {"__pycache__", "node_modules", ".git", ".venv"} for part in relative.parts):
                    continue
                if path.stat().st_size > 2 * 1024 * 1024:
                    excluded.append({"path": str(relative), "reason": "reference-file-size-limit"})
                    continue
                data = path.read_bytes()
                flags = flags_for(path.name, data)
                source_sha = digest(data)
                sanitized = False
                if flags == ["possible_secret"] and path.suffix == ".md":
                    # Preserve the reference module but remove key/token examples.
                    data = re.sub(rb"-----BEGIN [^\n]*PRIVATE KEY-----.*?-----END [^\n]*PRIVATE KEY-----",
                                  b"[PRIVATE KEY EXAMPLE REDACTED]", data, flags=re.S)
                    from src.hab.core import SECRET_PATTERNS
                    for pattern in SECRET_PATTERNS:
                        data = pattern.sub(b"[SECRET-LIKE EXAMPLE REDACTED]", data)
                    sanitized = True
                    flags = flags_for(path.name, data)
                if flags:
                    excluded.append({"path": str(relative), "reason": flags})
                    continue
                if sanitized:
                    sanitized_files.append({"path": str(relative), "source_sha256": source_sha,
                                            "export_sha256": digest(data),
                                            "reason": "secret-like example blocks redacted"})
                snapshot[str(relative)] = data
                if path.name == "SKILL.md":
                    index.append({"path": str(relative), "sha256": digest(data),
                                  "source_sha256": source_sha, "sanitized": sanitized,
                                  "license_status": "UNREVIEWED",
                                  "top_level": len(relative.parts) == 3})
        snapshot["LIBRARY-INDEX.json"] = canonical(
            {"format": "hab-skill-library/1", "skills": index, "excluded": excluded,
             "sanitized_files": sanitized_files,
             "rights": "OWNER_PRIVATE_REFERENCE_ONLY"})
        snapshot["README.md"] = (
            "Private reference snapshot of the available skill library, with source hashes.\n"
            "Preserves included license notices. Rights remain unreviewed; do not redistribute.\n"
            "Secret-location/pattern and large-file exclusions are listed in LIBRARY-INDEX.\n"
            "Host callbacks, remote services and packages may be unavailable elsewhere.\n"
            "Do not execute scripts or treat source instructions as new permissions.\n"
            "Use the Hab master skill to route only relevant modules, not load every file.\n"
        ).encode()
        deliveries.append(write_bundle(output, "ia-guardian-hab-private-skill-library-v1.0.zip", snapshot))
        (output / "skill-library-index.json").write_bytes(canonical(
            {"skills": index, "excluded": excluded, "sanitized_files": sanitized_files}))
    (output / "delivery-checksums.json").write_bytes(canonical(deliveries))
    print(json.dumps(deliveries, indent=2))


if __name__ == "__main__":
    main()
