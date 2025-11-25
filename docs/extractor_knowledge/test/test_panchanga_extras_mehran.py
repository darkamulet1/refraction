from __future__ import annotations

import json
from pathlib import Path

from v0min.panchanga_extras_extract import compute_panchanga_extras_block

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_panchanga_extras_structure() -> None:
    payload = compute_panchanga_extras_block(_load_payload())
    assert payload["schema_version"] == "panchanga_extras.v1"
    assert payload["engine"] == "PYJHORA_PANCHANGA_EXTRAS"
    pancha_pakshi = payload.get("pancha_pakshi")
    assert pancha_pakshi is not None
    assert "birth" in pancha_pakshi
    assert "bird" in pancha_pakshi["birth"]
    vratha = payload.get("vratha_and_festivals")
    assert vratha is not None
    assert isinstance(vratha["birth_day"], list)
