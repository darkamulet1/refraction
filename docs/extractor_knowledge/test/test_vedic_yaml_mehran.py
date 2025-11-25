from __future__ import annotations

import json
from pathlib import Path

from v0min.vedic_yaml import build_vedic_master_from_full, SCHEMA_VERSION


def test_vedic_yaml_mehran_structure() -> None:
    src = Path("references/out/mehran_full_pyjhora.json")
    payload = json.loads(src.read_text(encoding="utf-8"))

    vedic = build_vedic_master_from_full(payload)

    assert vedic["meta"]["schema_version"] == SCHEMA_VERSION
    assert vedic["meta"]["person"] == "Mehran"
    assert vedic["meta"]["jd"]["jd_utc"] == payload["meta"]["jd_utc"]

    ayanamsa_val = vedic["ayanamsa"]["value_deg"]
    assert ayanamsa_val is not None
    assert 20.0 < ayanamsa_val < 25.0

    assert vedic["birth"]["datetime_utc"] == payload["birth_data"]["datetime_utc"]
    assert vedic["birth"]["utc_offset_hours"] == payload["birth_data"]["utc_offset_hours"]

    d1 = vedic["core_charts"]["D1"]
    assert d1["lagna"]["sign"]
    assert "Sun" in d1["planets"]
    assert d1["lagna"]["nakshatra"]
    assert d1["lagna"]["pada"] in (1, 2, 3, 4)
    assert d1["planets"]["Moon"]["nakshatra"]
    assert d1["planets"]["Moon"]["pada"] in (1, 2, 3, 4)
    assert "house_occupancy" in d1

    d9 = vedic["core_charts"]["D9"]
    assert d9["lagna"]["nakshatra"]
    assert d9["planets"]["Moon"]["nakshatra"]
    assert "D10" in vedic["core_charts"]

    sun_strength = vedic["strength"]["shadbala"]["Sun"]
    assert sun_strength["sthana"] is not None and sun_strength["sthana"] > 0

    panchanga = vedic["panchanga_at_birth"]
    assert panchanga["tithi"]["local_name"] == "Thiruthiyai"
    assert panchanga["tithi"]["id"].startswith("SHUKLA_") or panchanga["tithi"]["id"].startswith(
        "KRISHNA_"
    )
    assert panchanga["nakshatra"]["id"] == "PUNARVASU"
    assert panchanga["nakshatra"]["local_name"] == "Punarpoosam"
    assert panchanga["nakshatra"]["pada"] in (1, 2, 3, 4)
    assert panchanga["karana"]["id"] is not None
    assert 0 <= panchanga["tithi"]["elapsed_percent"] <= 100

    timeline = vedic["vimshottari"]["timeline"]
    assert timeline
    assert {"md", "ad", "start"}.issubset(timeline[0].keys())

    yogas = vedic.get("yogas")
    assert yogas is not None
    assert yogas["source"] == "PYJHORA_YOGA"
    yoga_charts = yogas.get("charts", {})
    assert "D1" in yoga_charts and len(yoga_charts["D1"]) > 0
    assert all("id" in item and "name" in item for item in yoga_charts["D1"])

    planet_status = vedic.get("planet_status")
    assert planet_status is not None
    assert planet_status["D1"]["Sun"]["dignity"]
