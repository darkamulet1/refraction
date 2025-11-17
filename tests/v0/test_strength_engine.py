from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from v0min.core_time import make_birth_context
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


def test_strength_engine_default_systems() -> None:
    ctx = _context_from_snapshot(Path("references/out/mehran_full_pyjhora.json"))
    result = compute_strength_all(ctx)
    assert set(result.keys()) == {"shadbala", "dwadhasa_vargeeya_bala", "ashtakavarga"}


def test_strength_engine_include_optional() -> None:
    ctx = _context_from_snapshot(Path("references/out/mehran_full_pyjhora.json"))
    result = compute_strength_all(ctx, include=["harsha"])
    assert "harsha_bala" in result
    assert "Sun" in result["harsha_bala"]
