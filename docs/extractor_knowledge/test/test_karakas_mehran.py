from __future__ import annotations

import json
from pathlib import Path

from v0min.karakas_extract import KarakasConfig, compute_karakas_from_payload


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_karakas_mehran() -> None:
    payload = _load_payload()
    block = compute_karakas_from_payload(payload, KarakasConfig())
    assert block["schema_version"] == "karakas.v1"
    chara = block["chara"]
    expected_pairs = {
        "AK": "Rahu",
        "AmK": "Jupiter",
        "BK": "Saturn",
        "MK": "Sun",
        "PiK": "Moon",
        "PK": "Venus",
        "GK": "Mercury",
        "DK": "Mars",
    }
    roles = {entry["role"]: entry["planet"] for entry in chara}
    for role, planet in expected_pairs.items():
        actual = roles.get(role)
        assert actual is not None
        normalized = "".join(ch for ch in actual if ch.isalpha()).lower()
        assert planet.lower().replace(" ", "") in normalized
    sthira = block["sthira"]
    assert len(sthira) >= 7
    assert sthira[0]["role"] == "Atma"
