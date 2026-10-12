"""Offline revision comparison. Never fetch, merge, delete, sign or deploy."""
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCHEMA = "hab-revisions/1"
MAX_BYTES = 256 * 1024
MAX_SOURCES = 200
STATES = {"OBSERVED", "EMPTY", "UNAVAILABLE", "BLOCKED"}


def _time(value):
    if not isinstance(value, str):
        raise ValueError("An explicit timezone-aware observation timestamp is required")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError("Invalid observation timestamp") from error
    if parsed.tzinfo is None:
        raise ValueError("Observation timestamp must include a timezone")
    return parsed.astimezone(timezone.utc)


def read_snapshot(path):
    with Path(path).open("rb") as stream:
        payload = stream.read(MAX_BYTES + 1)
    if len(payload) > MAX_BYTES:
        raise ValueError("Revision snapshot exceeds the size limit")
    return json.loads(payload.decode("utf-8-sig"))


def _sources(snapshot):
    if not isinstance(snapshot, dict) or snapshot.get("schema") != SCHEMA:
        raise ValueError("Unsupported revision snapshot schema")
    observed = _time(snapshot.get("observed_at"))
    entries = snapshot.get("sources")
    if not isinstance(entries, list) or len(entries) > MAX_SOURCES:
        raise ValueError("A bounded source list is required")
    result = {}
    for source in entries:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object")
        identity = source.get("id")
        if (not isinstance(identity, str) or not identity.strip() or identity != identity.strip()
                or len(identity) > 512 or re.search(r"[\x00-\x1f\x7f]", identity)):
            raise ValueError("Invalid source identity")
        if identity in result:
            raise ValueError("Duplicate source identity")
        state = source.get("status")
        if not isinstance(state, str) or state not in STATES:
            raise ValueError("Unknown source status")
        revision = source.get("revision")
        if state == "OBSERVED" and (
                not isinstance(revision, str)
                or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", revision)):
            raise ValueError("An observed source requires a complete revision hash")
        if state != "OBSERVED" and revision is not None:
            raise ValueError("Unavailable or empty sources cannot assert an observed revision")
        result[identity] = {**source, "observed": _time(
            source.get("observed_at", observed.isoformat()))}
    return result


def compare_revisions(previous, current, *, now=None, max_age_hours=24):
    if (isinstance(max_age_hours, bool) or not isinstance(max_age_hours, (int, float))
            or not 0 < max_age_hours <= 8760):
        raise ValueError("Observation age limit must be positive and bounded")
    clock = _time(now) if now is not None else datetime.now(timezone.utc)
    before, after = _sources(previous), _sources(current)
    changes = []
    for identity in sorted(set(before) | set(after)):
        old, new = before.get(identity), after.get(identity)
        reason = None
        if new is None:
            state, reason = "UNAVAILABLE", "Missing from current inventory; NOT a deletion"
        elif new["status"] != "OBSERVED":
            state, reason = "BLOCKED", new["status"]
        elif new["observed"] > clock + timedelta(minutes=5):
            state, reason = "BLOCKED", "FUTURE_OBSERVATION"
        elif clock - new["observed"] > timedelta(hours=max_age_hours):
            state, reason = "BLOCKED", "STALE_OBSERVATION"
        elif old is None or old["status"] != "OBSERVED":
            state = "NEW"
        elif old["revision"] == new["revision"]:
            state = "UNCHANGED"
        else:
            state = "CHANGED"
        changes.append({"id": identity, "state": state, "reason": reason,
                        "previous_revision": old.get("revision") if old else None,
                        "current_revision": new.get("revision") if new else None,
                        "review_required": state != "UNCHANGED"})
    return {"schema": "hab-revision-comparison/1", "checked_at": clock.isoformat(),
            "changes": changes,
            "counts": {state: sum(row["state"] == state for row in changes)
                       for state in ("NEW", "UNCHANGED", "CHANGED", "UNAVAILABLE", "BLOCKED")},
            "automatic_actions_enabled": False, "financial_actions_enabled": False,
            "boundary": "Metadata comparison only; no ancestry, code, tests or deployment certification"}
