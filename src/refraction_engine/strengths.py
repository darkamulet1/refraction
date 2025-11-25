"""Strength (Shadbala) extractor for Refraction Engine V1."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict, List

from jhora import const, utils
from jhora.horoscope.chart import strength
from jhora.panchanga import drik

from .core_chart import _parse_core_chart_input
from .graha import graha_const_to_string

SHADBALA_PLANET_ORDER = [
    const._SUN,
    const._MOON,
    const._MARS,
    const._MERCURY,
    const._JUPITER,
    const._VENUS,
    const._SATURN,
]

STRONG_THRESHOLD = 1.0
WEAK_THRESHOLD = 0.75


def _birth_context(birth: Any, location: Any) -> Dict[str, Any]:
    dt = birth.aware_datetime
    date = drik.Date(dt.year, dt.month, dt.day)
    time_tuple = (dt.hour, dt.minute, dt.second + dt.microsecond / 1_000_000)
    jd = utils.julian_day_number(date, time_tuple)
    tz_offset = dt.utcoffset().total_seconds() / 3600 if dt.utcoffset() else 0.0
    place = drik.Place(
        location.place_name or "Refraction",
        location.lat,
        location.lon,
        tz_offset,
    )
    return {"jd": jd, "place": place}


def run_strengths(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Compute Shadbala strengths for classical planets."""
    normalized = _parse_core_chart_input(payload)
    birth = normalized["birth"]
    location = normalized["location"]
    config = normalized["config"]

    ctx = _birth_context(birth, location)
    ayanamsa_mode = config.ayanamsa_mode or const._DEFAULT_AYANAMSA_MODE
    ayanamsa_value = config.ayanamsa_value_deg
    zodiac_type = config.zodiac_type.upper()

    if zodiac_type == "SIDEREAL":
        drik.set_sideral_planets()
        drik.set_ayanamsa_mode(ayanamsa_mode, ayanamsa_value, jd=ctx["jd"])
    else:
        drik.set_tropical_planets()

    try:
        shad_components = strength.shad_bala(
            ctx["jd"],
            ctx["place"],
            ayanamsa_mode=ayanamsa_mode,
        )
    finally:
        if zodiac_type == "SIDEREAL":
            drik.reset_ayanamsa_mode()
    totals = shad_components[6]
    ratios = shad_components[8]

    planets_payload: List[Dict[str, Any]] = []
    strong_planets: List[str] = []
    weak_planets: List[str] = []

    for idx, planet_const in enumerate(SHADBALA_PLANET_ORDER):
        planet_id = graha_const_to_string(planet_const)
        if planet_id is None:
            continue
        total_value = float(totals[idx])
        ratio_value = float(ratios[idx])
        planets_payload.append(
            {
                "planet_id": planet_id,
                "total_shadbala": total_value,
                "strength_ratio": ratio_value,
            }
        )
        if ratio_value >= STRONG_THRESHOLD:
            strong_planets.append(planet_id)
        elif ratio_value <= WEAK_THRESHOLD:
            weak_planets.append(planet_id)

    person = normalized.get("person") or {}
    birth_dt = birth.aware_datetime
    person_payload = {
        "id": person.get("id"),
        "label": person.get("label"),
        "birth_date": birth_dt.date().isoformat(),
        "birth_time": birth_dt.time().replace(microsecond=0).isoformat(),
    }

    summary = {
        "strong_planets": strong_planets,
        "weak_planets": weak_planets,
    }

    meta = {
        "schema_version": "strengths_spec_v1",
        "timestamp_utc": datetime.now(dt_timezone.utc).isoformat(),
        "engine": {
            "name": "PyJHora",
            "version": getattr(const, "_APP_VERSION", None),
        },
        "extractor": "strengths",
    }

    config_echo = {
        "zodiac_type": config.zodiac_type,
        "ayanamsa_mode": config.ayanamsa_mode,
        "ayanamsa_value_deg": config.ayanamsa_value_deg,
        "house_system": config.house_system,
        "node_mode": config.node_mode,
        "include_bodies": config.include_bodies,
    }

    return {
        "meta": meta,
        "person": person_payload,
        "config_echo": config_echo,
        "frames": {
            "planets": planets_payload,
            "summary": summary,
        },
    }
