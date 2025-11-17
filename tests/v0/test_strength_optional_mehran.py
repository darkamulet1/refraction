from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload
from v0min.strength import compute_strength_all


def _context_from_snapshot(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    birth = payload["birth_data"]
    location = birth["location"]
    dt_local = datetime.fromisoformat(birth["datetime_local"])
    bc = make_birth_context(
        dt_local.replace(tzinfo=None),
        location["lat"],
        location["lon"],
        tz_name=birth["timezone_name"],
        location_name=location.get("name"),
    )
    return {
        "birth_context": bc,
        "ayanamsa_mode": payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI"),
        "rasi_raw_positions": payload.get("vargas", {}).get("D1", {}).get("raw_positions"),
    }


def test_optional_strength_modules_present_with_flag() -> None:
    ctx = _context_from_snapshot(Path("references/out/mehran_full_pyjhora.json"))
    block = compute_strength_all(ctx, active_only=False)
    for key in ("harsha_bala", "avastha_bala", "graha_yuddha", "tatkalika_bala", "upagraha_bala"):
        assert key in block
    assert "Sun" in block["harsha_bala"]
    assert "state" in block["avastha_bala"]["Moon"]
    assert "components" in block["tatkalika_bala"]["Sun"]
    assert "_catalog" in block["upagraha_bala"]


def test_strength_block_respects_include_optional_flag() -> None:
    bc = make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )
    baseline = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")
    assert "harsha_bala" not in baseline["strength"]

    enriched = build_full_pyjhora_payload(
        bc,
        person="Mehran",
        location_name="Tehran",
        extraction_config={"strength": {"include_optional": True}},
    )
    assert "harsha_bala" in enriched["strength"]
