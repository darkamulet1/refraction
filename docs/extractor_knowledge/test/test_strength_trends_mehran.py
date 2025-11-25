from __future__ import annotations

import json
from pathlib import Path

from v0min.strength_trends_extract import (
    StrengthTrendsConfig,
    compute_strength_trends_from_payload,
)


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_strength_trends_planet_ranking() -> None:
    payload = _load_payload()
    block = compute_strength_trends_from_payload(payload, StrengthTrendsConfig())
    planets = block["planet_ranking"]
    assert planets
    top_planets = [entry["planet"] for entry in planets[:3]]
    assert "Saturn" in top_planets
    signs = block["sign_ranking"]
    if signs:
        assert signs[0]["sign"]
