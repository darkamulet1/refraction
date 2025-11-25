from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from jhora import const, utils
from jhora.panchanga import drik, vratha

from v0min import payload_utils

PANCHANGA_EXTRAS_SCHEMA_VERSION = "panchanga_extras.v1"
ENGINE_NAME = "PYJHORA_PANCHANGA_EXTRAS"

_PANCHA_PAKSHI_BIRDS = ["Vulture", "Owl", "Crow", "Cock", "Peacock"]
_PANCHA_PAKSHI_ACTIVITIES = ["Ruling", "Eating", "Walking", "Sleeping", "Dying"]
_PANCHA_PAKSHI_RELATIONS = ["Enemy", "Same", "Friend"]
_PANCHA_PAKSHI_EFFECTS = ["Very Bad", "Bad", "Average", "Good", "Very Good"]
_PANCHA_PAKSHI_STAR_BIRD_MAP = [
    (1, 5),
    (1, 5),
    (1, 5),
    (1, 5),
    (1, 5),
    (2, 4),
    (2, 4),
    (2, 4),
    (2, 4),
    (2, 4),
    (2, 4),
    (3, 3),
    (3, 3),
    (3, 3),
    (3, 3),
    (3, 3),
    (4, 2),
    (4, 2),
    (4, 2),
    (4, 2),
    (4, 2),
    (5, 1),
    (5, 1),
    (5, 1),
    (5, 1),
    (5, 1),
    (5, 1),
]
_VRATHA_TYPES = [
    "pradosham",
    "sankranti",
    "amavasya",
    "pournami",
    "ekadhashi",
    "sashti",
    "sankatahara_chathurthi",
    "vinayaka_chathurthi",
    "shivarathri",
    "srartha",
]


@dataclass
class PanchaPakshiRow:
    weekday_index: int
    paksha_index: int
    daynight_index: int
    nak_bird_index: int
    nak_activity_index: int
    sub_bird_index: int
    sub_activity_index: int
    duration_factor: float
    relation_index: Optional[int]
    effect_index: Optional[int]
    rating: Optional[int]


def _jd_to_iso_string(jd_value: float) -> str:
    year, month, day, fractional_hours = utils.jd_to_gregorian(jd_value)
    total_seconds = int(round(fractional_hours * 3600))
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}:{seconds:02d}"


def _load_pancha_pakshi_rows(bird_index: int, weekday_index: int, paksha_index: int) -> List[PanchaPakshiRow]:
    data_path = Path(const.ROOT_DIR) / "data" / "pancha_pakshi_db.csv"
    if not data_path.exists():
        return []
    rows: List[PanchaPakshiRow] = []
    with data_path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for entry in reader:
            try:
                if (
                    int(entry["nak_bird_index"]) != bird_index - 1
                    or int(entry["week_day_index"]) != weekday_index - 1
                    or int(entry["paksha_index"]) != paksha_index - 1
                ):
                    continue
                rows.append(
                    PanchaPakshiRow(
                        weekday_index=int(entry["week_day_index"]),
                        paksha_index=int(entry["paksha_index"]),
                        daynight_index=int(entry["daynight_index"]),
                        nak_bird_index=int(entry["nak_bird_index"]),
                        nak_activity_index=int(entry["nak_activity_index"]),
                        sub_bird_index=int(entry["sub_bird_index"]),
                        sub_activity_index=int(entry["sub_activity_index"]),
                        duration_factor=float(entry["duration_factor"]),
                        relation_index=int(entry["relation"]) if entry["relation"] else None,
                        effect_index=int(entry["effect"]) if entry["effect"] else None,
                        rating=int(entry["rating"]) if entry["rating"] else None,
                    )
                )
            except (KeyError, ValueError):
                continue
    return rows


def _pancha_pakshi_bird_index(jd_value: float, place) -> int:
    birth_star = drik.nakshatra(jd_value, place)[0]
    paksha_index = _get_paksha_index(jd_value, place)
    mapping = _PANCHA_PAKSHI_STAR_BIRD_MAP[birth_star - 1]
    return mapping[paksha_index - 1]


def _get_paksha_index(jd_value: float, place) -> int:
    tithi_value = drik.tithi(jd_value, place)[0]
    return 1 if tithi_value <= 15 else 2


def _build_pancha_pakshi_schedule(
    rows: List[PanchaPakshiRow],
    sunrise_jd: float,
    day_length: float,
    night_length: float,
) -> List[Dict[str, Any]]:
    schedule: List[Dict[str, Any]] = []
    pointer = sunrise_jd
    for idx in range(0, len(rows), 5):
        block = rows[idx : idx + 5]
        if not block:
            continue
        reference = block[0]
        base_hours = (day_length if reference.daynight_index == 0 else night_length) / 5.0
        base_days = base_hours / 24.0
        for entry in block:
            duration_days = base_days * entry.duration_factor
            end_point = pointer + duration_days
            schedule.append(
                {
                    "start": _jd_to_iso_string(pointer),
                    "end": _jd_to_iso_string(end_point),
                    "main_bird": _PANCHA_PAKSHI_BIRDS[entry.nak_bird_index],
                    "main_activity": _PANCHA_PAKSHI_ACTIVITIES[entry.nak_activity_index],
                    "sub_bird": _PANCHA_PAKSHI_BIRDS[entry.sub_bird_index],
                    "sub_activity": _PANCHA_PAKSHI_ACTIVITIES[entry.sub_activity_index],
                    "relation": _PANCHA_PAKSHI_RELATIONS[entry.relation_index] if entry.relation_index is not None else None,
                    "effect": _PANCHA_PAKSHI_EFFECTS[entry.effect_index] if entry.effect_index is not None else None,
                    "rating": entry.rating,
                    "start_jd": pointer,
                    "end_jd": end_point,
                }
            )
            pointer = end_point
    return schedule


def _find_birth_state(schedule: List[Dict[str, Any]], birth_jd: float) -> Optional[Dict[str, Any]]:
    for entry in schedule:
        if entry["start_jd"] <= birth_jd < entry["end_jd"]:
            return entry
    return None


def _float_hours_to_clock(value: float) -> str:
    total_seconds = int(round(value * 3600))
    hours = (total_seconds // 3600) % 24
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def _build_vratha_events(place, birth_date) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    start_date = drik.Date(birth_date.year, birth_date.month, birth_date.day)
    for vratha_key in _VRATHA_TYPES:
        try:
            rows = vratha.special_vratha_dates(place, start_date, start_date, vratha_type=vratha_key)
        except Exception:
            continue
        if not rows:
            continue
        for date_tuple, start_hours, end_hours, tag in rows:
            if tuple(date_tuple) != (birth_date.year, birth_date.month, birth_date.day):
                continue
            events.append(
                {
                    "id": vratha_key.upper(),
                    "name": tag,
                    "type": "VRATA",
                    "notes": f"{_float_hours_to_clock(start_hours)} - {_float_hours_to_clock(end_hours)}",
                }
            )
    return events


def compute_panchanga_extras_block(full_payload: Dict[str, Any], config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Build panchanga_extras.v1 from the supplied payload.
    """

    bc, place = payload_utils.build_birth_context_from_payload(full_payload)
    birth_date = bc.dt_local.date()
    dob = drik.Date(birth_date.year, birth_date.month, birth_date.day)
    tob = (
        bc.dt_local.hour,
        bc.dt_local.minute,
        bc.dt_local.second + bc.dt_local.microsecond / 1_000_000,
    )
    birth_jd = utils.julian_day_number((birth_date.year, birth_date.month, birth_date.day), tob)

    include_pancha_pakshi = config.get("include_pancha_pakshi", True) if config else True
    include_vratha = config.get("include_vratha_festivals", True) if config else True

    block: Dict[str, Any] = {
        "schema_version": PANCHANGA_EXTRAS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
    }

    if include_pancha_pakshi:
        jd_for_day = birth_jd
        sunrise_jd = drik.sunrise(jd_for_day, place)[-1]
        if birth_jd < sunrise_jd:
            jd_for_day -= 1
            sunrise_jd = drik.sunrise(jd_for_day, place)[-1]
        weekday_index = drik.vaara(jd_for_day) + 1
        paksha_index = _get_paksha_index(jd_for_day, place)
        bird_index = _pancha_pakshi_bird_index(jd_for_day, place)
        pp_rows = _load_pancha_pakshi_rows(bird_index, weekday_index, paksha_index)
        day_length = drik.day_length(jd_for_day, place)
        night_length = drik.night_length(jd_for_day, place)
        schedule = _build_pancha_pakshi_schedule(pp_rows, sunrise_jd, day_length, night_length)
        birth_state = _find_birth_state(schedule, birth_jd)
        block["pancha_pakshi"] = {
            "birth": {
                "bird": _PANCHA_PAKSHI_BIRDS[bird_index - 1],
                "state": birth_state["main_activity"] if birth_state else None,
                "strength_rank": birth_state.get("rating") if birth_state else None,
                "notes": birth_state.get("relation") if birth_state else None,
            },
            "day_schedule": [
                {
                    "start": entry["start"],
                    "end": entry["end"],
                    "main_bird": entry["main_bird"],
                    "main_activity": entry["main_activity"],
                    "sub_bird": entry["sub_bird"],
                    "sub_activity": entry["sub_activity"],
                    "relation": entry["relation"],
                    "effect": entry["effect"],
                }
                for entry in schedule
            ],
        }

    if include_vratha:
        events = _build_vratha_events(place, birth_date)
        block["vratha_and_festivals"] = {"birth_day": events}

    return block


__all__ = ["compute_panchanga_extras_block", "PANCHANGA_EXTRAS_SCHEMA_VERSION"]
