"""Dashas extractors for Refraction Engine V1."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple

from jhora import const, utils
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.panchanga import drik

from .core_chart import _load_core_primitives, _parse_core_chart_input

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
    return {
        "jd": jd,
        "place": place,
        "tzinfo": dt_timezone.utc,
    }


def _jd_to_iso(jd: float, tzinfo: dt_timezone) -> str:
    year, month, day, hours = utils.jd_to_gregorian(jd)
    whole_hours = int(hours)
    minutes_total = (hours - whole_hours) * 60
    whole_minutes = int(minutes_total)
    seconds_total = (minutes_total - whole_minutes) * 60
    whole_seconds = int(seconds_total)
    microseconds = int(round((seconds_total - whole_seconds) * 1_000_000))
    dt = datetime(
        year,
        month,
        day,
        whole_hours,
        whole_minutes,
        whole_seconds,
        microseconds,
        tzinfo=tzinfo,
    )
    return dt.isoformat()


def _normalize_planet_label(label: str) -> str:
    stripped = "".join(ch for ch in label if ch.isalpha()).upper()
    for suffix in ("DHASA", "BHUKTHI"):
        if stripped.endswith(suffix):
            stripped = stripped[: -len(suffix)]
            break
    return {
        "RAAGU": "RAHU",
        "KETHU": "KETU",
        "RAHU": "RAHU",
        "KETU": "KETU",
    }.get(stripped, stripped)


@lru_cache(maxsize=1)
def _dhasa_index_to_id() -> Dict[int, str]:
    primitives = _load_core_primitives()
    english = primitives.get("languages", {}).get("en", {})
    names = english.get("DHASA_LIST", [])
    mapping: Dict[int, str] = {}
    for idx, label in enumerate(names):
        mapping[idx] = _normalize_planet_label(label)
    if not mapping:
        fallback = [
            "SUN",
            "MOON",
            "MARS",
            "MERCURY",
            "JUPITER",
            "VENUS",
            "SATURN",
            "RAHU",
            "KETU",
        ]
        mapping = {idx: name for idx, name in enumerate(fallback)}
    return mapping


def _build_periods(
    dashas: Dict[int, float],
    reference_jd: float,
    tzinfo: dt_timezone,
) -> Tuple[List[Dict[str, Any]], Optional[str]]:
    items = list(dashas.items())
    if not items:
        return [], None

    index_map = _dhasa_index_to_id()

    periods: List[Dict[str, Any]] = []
    for idx, (planet_const, start_jd) in enumerate(items):
        planet_id = index_map.get(planet_const)
        if not planet_id:
            continue
        if idx + 1 < len(items):
            end_jd = items[idx + 1][1]
        else:
            duration_years = const.vimsottari_dict.get(planet_const, 0.0)
            end_jd = start_jd + duration_years * const.sidereal_year
        end_jd = max(end_jd, start_jd)
        duration_years = float(const.vimsottari_dict.get(planet_const, 0.0))
        periods.append(
            {
                "order_index": idx,
                "planet_id": planet_id,
                "start": _jd_to_iso(start_jd, tzinfo),
                "end": _jd_to_iso(end_jd, tzinfo),
                "duration_years": duration_years,
                "is_current": start_jd <= reference_jd < end_jd,
            }
        )

    current = next((period["planet_id"] for period in periods if period["is_current"]), None)
    return periods, current


def run_dashas_vimshottari(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _parse_core_chart_input(payload)
    birth = normalized["birth"]
    location = normalized["location"]
    config = normalized["config"]

    context = _birth_context(birth, location)
    dashas = vimsottari.vimsottari_mahadasa(context["jd"], context["place"])
    periods, current_mahadasha = _build_periods(dashas, context["jd"], context["tzinfo"])

    person = normalized.get("person") or {}
    birth_dt = birth.aware_datetime
    person_payload = {
        "id": person.get("id"),
        "label": person.get("label"),
        "name": person.get("label") or person.get("name"),
        "birth_date": birth_dt.date().isoformat(),
        "birth_time": birth_dt.time().replace(microsecond=0).isoformat(),
        "timezone": birth.timezone,
    }

    config_echo = {
        "zodiac_type": config.zodiac_type,
        "ayanamsa_mode": config.ayanamsa_mode,
        "ayanamsa_value_deg": config.ayanamsa_value_deg,
        "house_system": config.house_system,
        "node_mode": config.node_mode,
    }

    frame = {
        "frame_id": "VIMSOTTARI_MAHADASHA",
        "description": "Chronological Vimshottari Mahadasha periods",
        "levels": [
            {
                "level": "MAHADASHA",
                "periods": periods,
            }
        ],
    }

    meta = {
        "schema_version": "dashas_vimshottari_spec_v1",
        "timestamp_utc": datetime.now(dt_timezone.utc).isoformat(),
        "engine": {
            "name": "PyJHora",
            "version": getattr(const, "_APP_VERSION", None),
        },
        "current_mahadasha": current_mahadasha,
    }

    return {
        "meta": meta,
        "person": person_payload,
        "config_echo": config_echo,
        "frames": [frame],
    }
