from __future__ import annotations

import json
from pathlib import Path

from v0min.matching_extract import compute_ashtakoota_matching


def _load_payload(name: str) -> dict:
    return json.loads(Path(f"references/out/{name}").read_text(encoding="utf-8"))


def test_matching_structure() -> None:
    payload_one = _load_payload("mehran_full_pyjhora.json")
    payload_two = _load_payload("afra_full_pyjhora.json")

    result = compute_ashtakoota_matching(payload_one, payload_two)
    assert result["meta"]["engine"] == "PYJHORA_MATCHING"
    components = result["ashtakoota"]["components"]
    expected_keys = {
        "varna",
        "vashya",
        "tara",
        "yoni",
        "graha_maitri",
        "gana",
        "bhakoota",
        "nadi",
    }
    assert set(components.keys()) == expected_keys
    assert result["ashtakoota"]["score"] == result["total"]["score"]
    assert result["dosha_flags"]["nadi_dosha"] in (True, False)
    assert "naalu_porutham" in result
    assert "filters" in result
