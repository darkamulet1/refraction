from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_events_cli_smoke(tmp_path: Path) -> None:
    out_path = tmp_path / "events.json"
    cmd = [
        sys.executable,
        "scripts/events_cli.py",
        "--birth-json",
        "references/out/mehran_full_pyjhora.json",
        "--start",
        "2025-01-01T00:00:00+03:30",
        "--end",
        "2026-01-01T00:00:00+03:30",
        "--event-types",
        "HOUSE_ENTRY,RETROGRADE_SEGMENT",
        "--planets",
        "Saturn",
        "--include-house-entries",
        "--include-vakra-segments",
        "--max-events",
        "200",
        "--out",
        str(out_path),
    ]
    subprocess.check_call(cmd, cwd=Path(__file__).resolve().parents[2])
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "events.v1"
    event_types = {event["type"] for event in data["events"]}
    assert "HOUSE_ENTRY" in event_types
    assert "RETROGRADE_SEGMENT" in event_types
