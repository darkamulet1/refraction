from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from jhora.panchanga import drik

from v0min.core_time import make_birth_context
from v0min.house_status_multivarga import compute_house_status_all_vargas


def _load_context(full_path: Path) -> dict:
    payload = json.loads(full_path.read_text(encoding="utf-8"))
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
    place = drik.Place(
        location.get("name") or birth.get("person", "Birth Place"),
        bc.latitude,
        bc.longitude,
        bc.utc_offset_hours,
    )
    return {
        "payload": payload,
        "context": {
            "birth_context": bc,
            "place": place,
            "ayanamsa_mode": payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI"),
            "vargas": payload.get("vargas", {}),
        },
    }


def test_house_status_whole_sign_scopes() -> None:
    paths = _load_context(Path("references/out/mehran_full_pyjhora.json"))
    ctx = paths["context"]

    houses = compute_house_status_all_vargas(
        ctx,
        systems=["whole_sign", "sripati"],
        include_unsupported=False,
    )
    assert "D1" in houses and "whole_sign" in houses["D1"]
    d1_whole = houses["D1"]["whole_sign"]
    assert len(d1_whole) == 12
    assert d1_whole["1"]["sign"] == "Scorpio"
    assert d1_whole["1"]["lord"].startswith("Mars")

    assert "D9" in houses and "whole_sign" in houses["D9"]
    d9_whole = houses["D9"]["whole_sign"]
    assert d9_whole["1"]["sign"] == "Aquarius"
    assert d9_whole["1"]["lord"].startswith("Saturn")

    assert "sripati" in houses["D1"]
    assert "sripati" not in houses["D9"]


def test_house_status_include_unsupported() -> None:
    paths = _load_context(Path("references/out/mehran_full_pyjhora.json"))
    ctx = paths["context"]

    houses = compute_house_status_all_vargas(
        ctx,
        systems=["sripati"],
        include_unsupported=True,
    )
    assert houses["D1"]["sripati"] is not None
    assert "sripati" in houses["D9"]
    assert houses["D9"]["sripati"] is None
