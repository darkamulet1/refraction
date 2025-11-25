from refraction_engine import run_strengths

from ._utils import load_json

PLANET_SEQUENCE = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]


def _as_dict(planets):
    return {entry["planet_id"]: entry for entry in planets}


def test_strengths_mehran_binding():
    payload = load_json("references/in/mehran_birth.json")
    result = run_strengths(payload)

    frames = result.get("frames") or {}
    planets = frames.get("planets") or []
    summary = frames.get("summary") or {}

    ids = [planet["planet_id"] for planet in planets]
    assert ids == PLANET_SEQUENCE, "Unexpected planet ordering"

    expected_strong = set(PLANET_SEQUENCE)
    assert set(summary.get("strong_planets", [])) == expected_strong
    assert summary.get("weak_planets") == []

    for planet in planets:
        assert planet["total_shadbala"] > 0
        assert planet["strength_ratio"] >= 1.0
