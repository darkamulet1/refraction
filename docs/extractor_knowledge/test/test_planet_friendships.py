from __future__ import annotations

import json
from pathlib import Path

from v0min.planet_friendships_extract import (
    PlanetFriendshipsConfig,
    compute_planet_friendships_from_payload,
)


def _load_payload() -> dict:
    return json.loads(Path("references/out/mehran_full_pyjhora.json").read_text(encoding="utf-8"))


def test_planet_friendships_structure() -> None:
    payload = _load_payload()
    block = compute_planet_friendships_from_payload(payload, PlanetFriendshipsConfig())
    assert block["schema_version"] == "planet_friendships.v1"
    entries = block["entries"]
    assert len(entries) == 9
    for entry in entries[:7]:
        assert entry["natural_friends"]
        assert entry["natural_enemies"] or entry["temporary_enemies"]
        net = entry["net_result"]
        assert "friends" in net and "enemies" in net
        assert net["friends"] or net["enemies"]
