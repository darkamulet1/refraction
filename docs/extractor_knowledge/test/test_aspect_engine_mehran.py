from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from v0min.aspect_engine import compute_aspects_for_varga
from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload
from v0min.vedic_yaml import build_vedic_master_from_full


def _load_context() -> tuple[dict, dict]:
    payload = json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))
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
    context = {
        "birth_context": bc,
        "place": None,
        "ayanamsa_mode": payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI"),
        "vargas": payload.get("vargas", {}),
        "rasi_raw_positions": payload.get("vargas", {}).get("D1", {}).get("raw_positions"),
    }
    return payload, context


def test_aspect_engine_structure() -> None:
    _, context = _load_context()
    aspects = compute_aspects_for_varga(context, "D1", include=("graha", "rashi"))
    assert "graha_drishti" in aspects
    assert "rashi_drishti" in aspects

    graha_block = aspects["graha_drishti"]
    for planet in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        assert planet in graha_block
    mars_aspects = graha_block["Mars"]
    assert isinstance(mars_aspects, list)
    assert mars_aspects == sorted(mars_aspects, key=lambda a: (a["target"], a["house_distance"]))
    assert all({"target", "house_distance", "strength"} <= set(entry.keys()) for entry in mars_aspects)

    rashi_block = aspects["rashi_drishti"]
    assert "Aries" in rashi_block
    assert isinstance(rashi_block["Aries"], list)
    assert all(isinstance(sign, str) for sign in rashi_block["Aries"])


def test_aspects_optional_in_payload() -> None:
    payload, _ = _load_context()
    birth = payload["birth_data"]
    location = birth["location"]
    dt_local = datetime.fromisoformat(birth["datetime_local"]).replace(tzinfo=None)
    bc = make_birth_context(
        dt_local,
        location["lat"],
        location["lon"],
        tz_name=birth["timezone_name"],
        location_name=location.get("name"),
    )

    minimal = build_full_pyjhora_payload(
        bc,
        person=birth["person"],
        location_name=location.get("name") or birth["person"],
    )
    assert "aspects" not in minimal

    enriched = build_full_pyjhora_payload(
        bc,
        person=birth["person"],
        location_name=location.get("name") or birth["person"],
        extraction_config={"include_aspects": True},
    )
    assert "aspects" in enriched
    assert "D1" in enriched["aspects"]
    assert "graha_drishti" in enriched["aspects"]["D1"]

    yaml_data = build_vedic_master_from_full(enriched)
    assert "aspects" in yaml_data
