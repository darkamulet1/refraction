from __future__ import annotations

import json
from pathlib import Path

from v0min.prediction_extract import compute_predictions_block

REF_PATH = Path("references/out/mehran_full_pyjhora.json")


def _load_payload() -> dict:
    return json.loads(REF_PATH.read_text(encoding="utf-8"))


def test_predictions_structure() -> None:
    payload = compute_predictions_block(_load_payload())
    assert payload["schema_version"] == "predictions.v1"
    assert payload["engine"] == "PYJHORA_PREDICTIONS"
    general = payload.get("general")
    assert general is not None
    assert isinstance(general["sections"], list)
    if general["sections"]:
        section = general["sections"][0]
        assert "id" in section
        assert isinstance(section["paragraphs"], list)
    naadi = payload.get("naadi_marriage")
    assert naadi is not None
    assert "enabled" in naadi
    longevity = payload.get("longevity")
    assert longevity is not None
    assert "summary" in longevity
