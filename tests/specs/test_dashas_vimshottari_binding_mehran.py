from datetime import datetime

from refraction_engine import run_dashas_vimshottari

from ._utils import load_json

EXPECTED_ORDER = [
    "JUPITER",
    "SATURN",
    "MERCURY",
    "KETU",
    "VENUS",
    "SUN",
    "MOON",
    "MARS",
    "RAHU",
]


def _extract_periods(result: dict):
    frames = result.get("frames")
    assert isinstance(frames, list) and frames, "dashas payload must include frames"
    levels = frames[0].get("levels")
    assert isinstance(levels, list) and levels, "dashas payload missing levels"
    periods = levels[0].get("periods")
    assert isinstance(periods, list) and len(periods) == 9, "Vimshottari should emit 9 periods"
    return periods


def test_dashas_vimshottari_mehran_golden():
    payload = load_json("references/in/mehran_birth.json")
    result = run_dashas_vimshottari(payload)

    periods = _extract_periods(result)
    ids = [period["planet_id"] for period in periods]
    assert ids == EXPECTED_ORDER, f"Unexpected Mahadasha order: {ids}"

    currents = [period for period in periods if period.get("is_current")]
    assert len(currents) == 1, "Exactly one Mahadasha should be marked current"
    assert currents[0]["planet_id"] == "JUPITER", "Mehran's birth falls within Jupiter Mahadasha"

    starts = [datetime.fromisoformat(period["start"]) for period in periods]
    assert starts == sorted(starts), "Mahadasha periods should be chronologically ordered"

    for idx, period in enumerate(periods):
        assert period["order_index"] == idx, f"order_index mismatch for {period}"
        assert period["duration_years"] > 0, f"duration_years must be positive for {period}"
