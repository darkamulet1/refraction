from refraction_engine import run_strengths

from ._utils import load_json

PLANET_SEQUENCE = ["SUN", "MOON", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]


def _as_dict(planets):
    return {entry["planet_id"]: entry for entry in planets}


def test_strengths_athena_binding():
    payload = load_json("references/in/athena_birth.json")
    result = run_strengths(payload)

    frames = result.get("frames") or {}
    planets = frames.get("planets") or []
    summary = frames.get("summary") or {}

    ids = [planet["planet_id"] for planet in planets]
    assert ids == PLANET_SEQUENCE, "Unexpected planet ordering"

    expected_strong = {"SUN", "MOON", "MARS", "JUPITER", "VENUS", "SATURN"}
    assert set(summary.get("strong_planets", [])) == expected_strong
    assert summary.get("weak_planets") == []

    planet_map = _as_dict(planets)
    assert planet_map["MERCURY"]["strength_ratio"] < 1.0
    for planet_id in expected_strong:
        assert planet_map[planet_id]["strength_ratio"] >= 1.0
