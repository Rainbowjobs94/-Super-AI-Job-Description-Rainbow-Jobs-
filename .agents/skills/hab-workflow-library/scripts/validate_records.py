"""Structure-only validator for proposed Hab JSON record formats, not a gateway."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

EXTENSIONS = {".habflow", ".ltresearch", ".ltsource", ".ltclaim", ".ltproto", ".ltrole"}
MAX_BYTES = 65536
SECRET_FIELDS = {"privatekey", "apikey", "mnemonic", "seedphrase", "accesstoken",
                 "decryptionkey", "password", "cookie", "authorization"}


def validate_bytes(data, extension):
    if extension not in EXTENSIONS or not isinstance(data, bytes) or len(data) > MAX_BYTES:
        raise ValueError("Unsupported format or byte limit")

    def reject_constant(_):
        raise ValueError("Non-JSON numeric constant")

    def reject_duplicate_keys(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("Duplicate JSON field")
            obj[key] = value
        return obj

    try:
        record = json.loads(data.decode("utf-8"), parse_constant=reject_constant,
                            object_pairs_hook=reject_duplicate_keys)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValueError("Malformed UTF-8 JSON") from None
    if not isinstance(record, dict) or set(record) != {"schema_version", "id", "payload"}:
        raise ValueError("Envelope fields do not match")
    if record["schema_version"] != "1":
        raise ValueError("Unsupported schema version")
    if not isinstance(record["id"], str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,80}", record["id"]):
        raise ValueError("Opaque ID required")
    if not isinstance(record["payload"], dict):
        raise ValueError("Object payload required")
    stack = [(record, 0)]
    while stack:
        value, depth = stack.pop()
        if depth > 32:
            raise ValueError("Nesting limit exceeded")
        if isinstance(value, dict):
            for key, child in value.items():
                if re.sub(r"[^a-z0-9]", "", key.lower()) in SECRET_FIELDS:
                    raise ValueError("Credential field rejected")
                stack.append((child, depth + 1))
        elif isinstance(value, list):
            stack.extend((child, depth + 1) for child in value)
        elif isinstance(value, float) and not math.isfinite(value):
            raise ValueError("Nonfinite numeric value")
    return {"status": "STRUCTURE_VALID_ONLY", "extension": extension,
            "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
            "signature_verified": False, "ownership_verified": False,
            "authorization_granted": False, "value_or_settlement_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", help="One explicit local file; no directory scan")
    args = parser.parse_args()
    path = Path(args.file)
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
            raise ValueError("Nonregular or oversized input")
        # Trusted local filesystem utility, not a multi-tenant secure-file gateway.
        data = path.read_bytes()
        result = validate_bytes(data, path.suffix)
    except (OSError, ValueError):
        print(json.dumps({"status": "INVALID", "detail": "Format/structure/size/credential checks failed"}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
