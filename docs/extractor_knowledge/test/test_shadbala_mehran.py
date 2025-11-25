from __future__ import annotations

from datetime import datetime

from v0min.core_time import make_birth_context
from v0min.full_extract import build_full_pyjhora_payload


def test_shadbala_mehran_basic() -> None:
    bc = make_birth_context(
        datetime(1997, 6, 7, 20, 28, 36),
        35.6892,
        51.3890,
        tz_name="Asia/Tehran",
        location_name="Tehran",
    )
    payload = build_full_pyjhora_payload(bc, person="Mehran", location_name="Tehran")

    assert "strength" in payload
    assert "shadbala" in payload["strength"]

    shadbala = payload["strength"]["shadbala"]
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    for planet in planets:
        assert planet in shadbala
        entry = shadbala[planet]
        if planet in {"Rahu", "Ketu"}:
            assert entry["total_rupa"] is None
            continue
        assert entry["total_rupa"] >= 0
        assert entry["percent"] >= 0
