from refraction_engine import run_core_chart

from ._utils import load_json


def _extract_frame(result: dict):
    frames = result.get("frames")
    assert isinstance(frames, list) and frames, "core_chart result must include at least one frame"
    return frames[0]


def _find_planet(planets, planet_id: str) -> dict:
    for planet in planets:
        if planet.get("id") == planet_id:
            return planet
    raise AssertionError(f"Planet {planet_id} not found in core_chart payload")


def test_core_chart_mehran_basic():
    payload = load_json("references/in/mehran_birth.json")
    result = run_core_chart(payload)

    frame = _extract_frame(result)
    asc = frame.get("ascendant") or {}
    planets = frame.get("planets") or []

    # Expected values derived from refraction_engine/PyJHora output (2025-11-24)
    asc_sign_index = asc.get("sign_index")
    assert asc_sign_index == 8, f"Expected ascendant sign index 8 (Scorpio), got {asc_sign_index}"

    moon = _find_planet(planets, "MOON")
    sun = _find_planet(planets, "SUN")

    moon_sign_index = moon.get("sign_index")
    assert moon_sign_index == 3, f"Expected Moon sign index 3 (Gemini), got {moon_sign_index}"

    sun_nakshatra_index = sun.get("nakshatra_index")
    assert (
        sun_nakshatra_index == 4
    ), f"Expected Sun nakshatra index 4 (Rohini), got {sun_nakshatra_index}"
