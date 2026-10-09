"""Verify every delivery and per-source package without executing/extracting code."""
import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.hab.core import digest, safe_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    root = Path(args.directory)
    deliveries = json.loads((root / "delivery-checksums.json").read_text())
    verified = 0
    for delivery in deliveries:
        payload = (root / delivery["file"]).read_bytes()
        assert digest(payload) == delivery["sha256"]
        with zipfile.ZipFile(io.BytesIO(payload)) as archive:
            assert archive.testzip() is None
            names = archive.namelist()
            assert len(names) == len(set(names))
            for name in names:
                safe_name(name)
            checks = json.loads(archive.read("BUNDLE-CHECKSUMS.json"))["files"]
            assert set(checks) == set(names) - {"BUNDLE-CHECKSUMS.json"}
            for name, sha in checks.items():
                assert digest(archive.read(name)) == sha
        verified += 1
    packages = list((root / "source-packages").glob("*.zip"))
    for path in packages:
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            manifest = json.loads(archive.read("MANIFEST.ltpkg.json"))
            for name, sha in manifest["files"].items():
                assert digest(archive.read(name)) == sha
    toolkit = root / "ia-guardian-hab-toolkit-v1.0.zip"
    with zipfile.ZipFile(toolkit) as archive:
        assert "tests/test_hab.py" in archive.namelist()
        assert not any("profile.md" in name or "AI-OPERATOR-AGENT-PROFILE" in name
                       or name.startswith("attached_assets/") for name in archive.namelist())
    print(json.dumps({"delivery_archives_verified": verified,
                      "source_packages_verified": len(packages),
                      "all_manifest_checksums": "passed",
                      "private_source_separation": "passed"}))


if __name__ == "__main__":
    main()
