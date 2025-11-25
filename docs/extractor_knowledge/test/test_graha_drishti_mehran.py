from __future__ import annotations

import json
from pathlib import Path

from v0min.special_points_extract import compute_special_points_block


def _load_payload() -> dict:
    payload_path = Path("references/out/mehran_full_pyjhora.json")
    return json.loads(payload_path.read_text(encoding="utf-8"))


def test_graha_drishti_heatmap_structure() -> None:
    payload = _load_payload()
    cfg = {
        "enabled": True,
        "include_arudhas": False,
        "include_sphutas": False,
        "include_special_charts": False,
        "include_graha_drishti": True,
        "include_pinda": False,
        "drishti_systems": ["parashari", "jaimini"],
    }
    block = compute_special_points_block(payload, config=cfg)
    heatmap = block["graha_drishti_heatmap"]
    assert "parashari" in heatmap
    parashari = heatmap["parashari"]
    assert parashari["schema_version"] == "graha_drishti_heatmap.v1"
    assert len(parashari["planets"]) == 9
    mars_entry = next(entry for entry in parashari["matrix"]["planet_to_house"] if entry["source"] == "Mars")
    mars_types = {aspect["type"] for aspect in mars_entry["aspects"]}
    assert {"FOURTH", "SEVENTH", "EIGHTH"} == mars_types
    sun_entry = next(entry for entry in parashari["matrix"]["planet_to_house"] if entry["source"] == "Sun")
    assert {aspect["type"] for aspect in sun_entry["aspects"]} == {"SEVENTH"}
    jupiter_targets = next(
        entry for entry in parashari["matrix"]["planet_to_planet"] if entry["source"] == "Jupiter"
    )
    assert jupiter_targets["targets"], "Expected Jupiter to cast graha drishti on at least one body."
    assert "jaimini" in heatmap
    assert heatmap["jaimini"]["system"] == "jaimini"
