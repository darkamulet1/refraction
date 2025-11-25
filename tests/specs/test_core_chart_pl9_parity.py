from math import fabs

import pytest

from refraction_engine import run_core_chart
from refraction_engine.core_chart import _get_nakshatra_names

from ._utils import load_json

ARCSEC_TOLERANCE = 90.0
NAKSHATRA_SPAN_DEG = 360.0 / 27.0
NAKSHATRA_PADA_SPAN = NAKSHATRA_SPAN_DEG / 4.0
SIGN_NAMES = [
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
]
NAKSHATRA_NAMES = _get_nakshatra_names()

PL9_FIXTURES = {
    "arezoo": {
        "payload": "references/in/arezoo_birth.json",
        "positions": {
            "ASCENDANT": 30 + 39 / 60,
            "SUN": 180 + 7 + 38 / 60,
            "MOON": 300 + 25 + 16 / 60,
            "MARS": 150 + 24 + 29 / 60,
            "MERCURY": 180 + 19 + 46 / 60,
            "JUPITER": 150 + 12 + 21 / 60,
            "VENUS": 150 + 0 + 48 / 60,
            "SATURN": 90 + 3 + 14 / 60,
            "RAHU": 0 + 8 + 14 / 60,
            "KETU": 180 + 8 + 14 / 60,
        },
    },
    "arman": {
        "payload": "references/in/arman_birth.json",
        "positions": {
            "ASCENDANT": 150 + 6 + 32 / 60 + 31.39 / 3600,
            "SUN": 120 + 24 + 55 / 60 + 38.76 / 3600,
            "MOON": 120 + 24 + 12 / 60 + 53.86 / 3600,
            "MARS": 330 + 16 + 6 / 60 + 43.97 / 3600,
            "MERCURY": 150 + 21 + 3 / 60 + 20.14 / 3600,
            "JUPITER": 30 + 12 + 8 / 60 + 49.32 / 3600,
            "VENUS": 90 + 10 + 12 / 60 + 21.69 / 3600,
            "SATURN": 240 + 2 + 21 / 60 + 24.89 / 3600,
            "RAHU": 300 + 20 + 25 / 60 + 29.44 / 3600,
            "KETU": 120 + 20 + 25 / 60 + 29.44 / 3600,
        },
    },
}


def _delta_arcsec(engine: float, pl9: float) -> float:
    diff = fabs(engine - pl9)
    if diff > 180.0:
        diff = 360.0 - diff
    return diff * 3600.0


def _fetch_entry(frame, body_id: str):
    if body_id == "ASCENDANT":
        return frame["ascendant"]
    for planet in frame["planets"]:
        if planet["id"] == body_id:
            return planet
    raise AssertionError(f"{body_id} not present in core_chart output")


def _expected_meta(deg: float):
    deg = deg % 360.0
    sign_idx = int(deg // 30)
    sign = SIGN_NAMES[sign_idx]
    nak_idx = int(deg // NAKSHATRA_SPAN_DEG)
    nak = NAKSHATRA_NAMES[nak_idx % len(NAKSHATRA_NAMES)]
    pada = int(((deg % NAKSHATRA_SPAN_DEG) // NAKSHATRA_PADA_SPAN) + 1)
    return sign, nak, pada


@pytest.mark.parametrize("person_id", ["arezoo", "arman"])
def test_core_chart_pl9_parity(person_id: str):
    fixture = PL9_FIXTURES[person_id]
    payload = load_json(fixture["payload"])
    frame = run_core_chart(payload)["frames"][0]

    for body_id, pl9_deg in fixture["positions"].items():
        entry = _fetch_entry(frame, body_id)
        delta = _delta_arcsec(entry["longitude_deg"], pl9_deg)
        assert delta <= ARCSEC_TOLERANCE, f"{person_id}:{body_id} delta {delta:.2f} arcsec"
        expected_sign, expected_nak, expected_pada = _expected_meta(pl9_deg)
        assert entry["sign_name"] == expected_sign
        assert entry["nakshatra_name"] == expected_nak
        assert entry["nakshatra_pada"] == expected_pada
