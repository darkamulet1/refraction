from __future__ import annotations

import json
from pathlib import Path

from v0min.event_scan_extract import EventScanConfig, compute_events_snapshot

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_events_snapshot_basic() -> None:
    payload = _load_payload()
    cfg = EventScanConfig(
        start_datetime="2025-01-01T00:00:00+03:30",
        end_datetime="2026-01-01T00:00:00+03:30",
        event_types=["HOUSE_ENTRY", "RETROGRADE_SEGMENT"],
        planets=["Saturn"],
        systems=["D1"],
        max_events=200,
        include_house_entries=True,
        include_vakra_segments=True,
    )
    snapshot = compute_events_snapshot(payload, cfg)
    assert snapshot["schema_version"] == "events.v1"
    events = snapshot["events"]
    assert events, "Expected at least one event in the snapshot"
    types = {event["type"] for event in events}
    assert "HOUSE_ENTRY" in types
    assert "RETROGRADE_SEGMENT" in types
