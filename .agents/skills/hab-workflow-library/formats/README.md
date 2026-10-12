# Proposed JSON-backed file formats

These are actual sample files and a structure-only validator, not registered
media types, installed OS file associations, financial instruments or proofs.
They preserve the difference between source claims and verified outcomes.

| Extension | Meaning |
| --- | --- |
| .habflow | Advisory workflow record |
| .ltresearch | Research/evidence brief |
| .ltsource | Source/provenance manifest |
| .ltclaim | Claim and evidence status |
| .ltproto | Unverified protocol snapshot |
| .ltrole | Proposed role/access record |

All share schema_version, opaque id and object payload. JSON Schema is in
record-envelope.schema.json. Maximum size 64 KiB, depth 32; UTF-8 only.
The Python validator checks envelope/limits and selected credential field
names. It is not a complete data-loss prevention scanner or general JSON Schema
engine. Use a trusted local filesystem; it is not a multi-tenant file gateway.

Standalone module: `python scripts/validate_records.py formats/sample.habflow`.
Project tree: use the same relative paths inside this module's folder.
Tests: `python scripts/test_records.py`.

Valid structure gives no authorization, verified signature, ownership, novelty,
legal compliance, token backing, price or settlement. Keep private contents out
of public exports. No parser executes payloads or interprets approvals.
