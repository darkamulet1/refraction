from __future__ import annotations

import json
from pathlib import Path


def test_planet_status_structure_mehran() -> None:
    payload = json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))
    status = payload.get("planet_status", {}).get("D1")
    assert status is not None

    expected_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    assert set(status.keys()) == set(expected_planets)

    assert status["Mercury"]["retrograde"] is True
    assert status["Jupiter"]["retrograde"] is True
    assert status["Venus"]["retrograde"] is True
    assert status["Sun"]["retrograde"] is False

    assert status["Rahu"]["combust"] is False
    assert status["Ketu"]["combust"] is False

    assert status["Rahu"]["sandhi"] is True
    assert isinstance(status["Sun"]["sandhi"], bool)

    assert all(not status[planet]["vargottama"] for planet in expected_planets)
    assert status["Sun"]["dignity"] in {"EXALTED", "DEBILITATED", "MOOLATRIKONA", "OWN_SIGN", "NEUTRAL", "FRIENDLY", "ENEMY"}
