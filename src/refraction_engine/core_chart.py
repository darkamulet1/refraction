"""Input normalization and core chart payload generation for Refraction Engine V1."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone as dt_timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import pytz
import swisseph as swe
from jhora import const, utils
from jhora.panchanga import drik
from jhora.horoscope.chart import charts

from .graha import (
    GrahaID,
    GRAHA_ORDER,
    graha_id_to_name,
    graha_id_to_string,
    graha_string_to_id,
    degree_in_rasi,
    nakshatra_from_longitude,
    nakshatra_index_to_name,
    rasi_index_from_longitude,
    rasi_index_to_name,
)

CORE_SCHEMA_VERSION = "core_chart_spec_v1"
CORE_PRIMITIVES_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "pyjhora_knowledge"
    / "primitives"
    / "CorePrimitives.json"
)

DEFAULT_INCLUDE_BODIES = [graha_id_to_string(graha) for graha in GRAHA_ORDER]


@lru_cache(maxsize=1)
def _load_core_primitives() -> Dict[str, Any]:
    with CORE_PRIMITIVES_PATH.open() as f:
        return json.load(f)


@lru_cache(maxsize=32)
def _language_list(key: str) -> List[str]:
    primitives = _load_core_primitives()
    values = primitives.get("languages", {}).get("en", {}).get(key, [])
    return [str(item).upper() for item in values]


def _get_nakshatra_names() -> List[str]:
    return _language_list("NAKSHATRA_LIST")


def _get_tithi_names() -> List[str]:
    return _language_list("TITHI_LIST")


def _get_yoga_names() -> List[str]:
    return _language_list("YOGAM_LIST")


def _get_karana_names() -> List[str]:
    return _language_list("KARANA_LIST")


def _ayanamsa_lookup(name: Optional[str]) -> Optional[Dict[str, Any]]:
    if not name:
        return None
    primitives = _load_core_primitives()
    for entry in primitives.get("ayanamsa_modes", []):
        if entry["name"].upper() == name.upper() or entry["internal_constant"].upper() == name.upper():
            return entry
    raise ValueError(f"Unknown ayanamsa_mode '{name}'")


def _house_system_lookup(key: str) -> Dict[str, Any]:
    primitives = _load_core_primitives()
    for entry in primitives.get("house_systems", []):
        if entry["id"].upper() == str(key).upper() or entry["name"].upper() == str(key).upper():
            return entry
    raise ValueError(f"Unknown house_system '{key}'")


@dataclass
class CoreChartBirth:
    datetime_local: str
    timezone: str
    aware_datetime: datetime


@dataclass
class CoreChartLocation:
    lat: float
    lon: float
    place_name: Optional[str] = None


@dataclass
class CoreChartConfig:
    zodiac_type: str
    ayanamsa_mode: Optional[str]
    ayanamsa_value_deg: Optional[float]
    house_system: str
    node_mode: str
    include_bodies: List[str]


@dataclass
class RawBodyPosition:
    id: str
    longitude_deg: float
    speed_deg_per_day: Optional[float]
    retrograde: Optional[bool]


@dataclass
class RawHouseSegment:
    index: int
    start_deg: float
    cusp_deg: float
    end_deg: float
    sign_index: int


@dataclass
class RawD1Chart:
    jd: float
    jd_utc: float
    ascendant_longitude_deg: float
    house_segments: Sequence[RawHouseSegment]
    bodies: Sequence[RawBodyPosition]
    ayanamsa_deg: Optional[float]


def _datetime_with_timezone(value: str, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        parsed = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    if parsed.tzinfo is None:
        parsed = tz.localize(parsed)
    else:
        parsed = parsed.astimezone(tz)
    return parsed


def _normalize_angle(value: float) -> float:
    normalized = value % 360.0
    if normalized < 0:
        normalized += 360.0
    return normalized


def _sign_info(longitude: float) -> Tuple[int, str, float]:
    sign_index = rasi_index_from_longitude(longitude)
    sign_name = rasi_index_to_name(sign_index)
    return sign_index, sign_name, degree_in_rasi(longitude)


def _nakshatra_fields(longitude: float) -> Dict[str, Any]:
    nakshatra_index, pada, _ = nakshatra_from_longitude(longitude)
    names = _get_nakshatra_names()
    if 0 < nakshatra_index <= len(names):
        name = names[nakshatra_index - 1]
    else:
        name = nakshatra_index_to_name(nakshatra_index)
    return {
        "nakshatra_index": nakshatra_index,
        "nakshatra_name": name,
        "nakshatra_pada": pada,
    }


def _is_within_house(
    longitude: float, start: float, end: float
) -> bool:
    lon = _normalize_angle(longitude)
    start_norm = _normalize_angle(start)
    end_norm = _normalize_angle(end)
    if start_norm <= end_norm:
        return start_norm <= lon < end_norm
    return lon >= start_norm or lon < end_norm


def _house_index_for_longitude(
    longitude: float, segments: Sequence[RawHouseSegment]
) -> Optional[int]:
    for segment in segments:
        if _is_within_house(longitude, segment.start_deg, segment.end_deg):
            return segment.index
    return None


def _build_house_segments(house_data: Sequence[Any]) -> List[RawHouseSegment]:
    segments: List[RawHouseSegment] = []
    for idx, entry in enumerate(house_data, start=1):
        raw = entry[1]
        segments.append(
            RawHouseSegment(
                index=idx,
                start_deg=_normalize_angle(raw[0]),
                cusp_deg=_normalize_angle(raw[1]),
                end_deg=_normalize_angle(raw[2]),
                sign_index=((entry[0] % 12) + 1),
            )
        )
    return segments


def _parse_core_chart_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    birth = payload.get("birth")
    if not birth:
        raise ValueError("Missing 'birth' section in payload")
    datetime_local = birth.get("datetime_local")
    timezone = birth.get("timezone_name")
    if not datetime_local or not timezone:
        raise ValueError("birth.datetime_local and birth.timezone_name are required")
    aware_datetime = _datetime_with_timezone(datetime_local, timezone)

    location = birth.get("location")
    if not location:
        raise ValueError("Missing 'location' section in payload")
    try:
        lat = float(location["lat"])
        lon = float(location["lon"])
    except KeyError as exc:
        raise ValueError(f"Missing location coordinate: {exc}") from exc
    place_name = location.get("name")

    config = payload.get("config")
    if not config:
        raise ValueError("Missing 'config' section in payload")
    zodiac_type = config.get("zodiac_type")
    house_system = config.get("house_system")
    if not zodiac_type or not house_system:
        raise ValueError("'zodiac_type' and 'house_system' are required config values")

    ayanamsa_mode = config.get("ayanamsa_mode")
    if ayanamsa_mode:
        ayanamsa_mode = str(ayanamsa_mode).upper()
    if zodiac_type.upper() == "SIDEREAL" and not ayanamsa_mode:
        raise ValueError("ayanamsa_mode is required when zodiac_type is SIDEREAL")
    ayanamsa_value_deg = config.get("ayanamsa_value_deg")
    if ayanamsa_mode == "USER_DEFINED" and ayanamsa_value_deg is None:
        raise ValueError("ayanamsa_value_deg is required for USER_DEFINED ayanamsa_mode")

    node_mode = config.get("node_mode", "TRUE").upper()
    if node_mode not in {"TRUE", "MEAN"}:
        raise ValueError("node_mode must be 'TRUE' or 'MEAN'")

    include_bodies = config.get("include_bodies", DEFAULT_INCLUDE_BODIES)
    bodies: List[str]
    if isinstance(include_bodies, list):
        bodies = [str(item).upper() for item in include_bodies if item]
    else:
        raise ValueError("include_bodies must be a list of strings")
    if not bodies:
        bodies = DEFAULT_INCLUDE_BODIES

    return {
        "birth": CoreChartBirth(
            datetime_local=datetime_local,
            timezone=timezone,
            aware_datetime=aware_datetime,
        ),
        "location": CoreChartLocation(
            lat=lat, lon=lon, place_name=place_name
        ),
        "config": CoreChartConfig(
            zodiac_type=zodiac_type.upper(),
            ayanamsa_mode=ayanamsa_mode,
            ayanamsa_value_deg=ayanamsa_value_deg,
            house_system=house_system.upper(),
            node_mode=node_mode,
            include_bodies=bodies,
        ),
        "person": payload.get("person"),
    }


def _build_pyjhora_config(config: CoreChartConfig) -> Dict[str, Any]:
    ayanamsa_entry = _ayanamsa_lookup(config.ayanamsa_mode)
    house_entry = _house_system_lookup(config.house_system)
    house_method = house_entry.get("internal_constant") or house_entry["id"]
    if isinstance(house_method, str) and house_method.isdigit():
        house_method = int(house_method)
    return {
        "zodiac_type": config.zodiac_type,
        "ayanamsa": {
            "mode": ayanamsa_entry["name"] if ayanamsa_entry else config.ayanamsa_mode,
            "internal_constant": (
                ayanamsa_entry["internal_constant"] if ayanamsa_entry else None
            ),
            "value_deg": config.ayanamsa_value_deg,
        },
        "house_system": {
            "id": house_entry["id"],
            "name": house_entry["name"],
            "method": house_method,
        },
        "node_mode": config.node_mode,
        "include_bodies": config.include_bodies,
    }


def _compute_raw_d1_chart(
    birth: CoreChartBirth,
    location: CoreChartLocation,
    pyjhora_config: Dict[str, Any],
) -> RawD1Chart:
    dt = birth.aware_datetime
    date = drik.Date(dt.year, dt.month, dt.day)
    time_tuple = (dt.hour, dt.minute, dt.second + dt.microsecond / 1_000_000)
    jd = utils.julian_day_number(date, time_tuple)
    tz_offset = dt.utcoffset().total_seconds() / 3600 if dt.utcoffset() else 0.0
    place = drik.Place(
        location.place_name or "Refraction", location.lat, location.lon, tz_offset
    )

    zodiac_type = pyjhora_config["zodiac_type"]
    if zodiac_type == "SIDEREAL":
        drik.set_sideral_planets()
    else:
        drik.set_tropical_planets()

    ayanamsa_mode = (
        pyjhora_config["ayanamsa"]["internal_constant"]
        or pyjhora_config["ayanamsa"]["mode"]
        or const._DEFAULT_AYANAMSA_MODE
    )
    ayanamsa_value = pyjhora_config["ayanamsa"]["value_deg"]

    def _apply_ayanamsa() -> None:
        if zodiac_type == "SIDEREAL":
            drik.set_ayanamsa_mode(ayanamsa_mode, ayanamsa_value, jd=jd)

    _apply_ayanamsa()
    try:
        plan_speed = drik.planets_speed_info(jd, place)
        chart = charts.rasi_chart(
            jd,
            place,
            ayanamsa_mode=ayanamsa_mode,
            years=1,
            months=1,
            sixty_hours=1,
        )
        houses = charts.bhava_chart(
            jd,
            place,
            ayanamsa_mode=ayanamsa_mode,
            bhava_madhya_method=pyjhora_config["house_system"]["method"],
        )
        ayanamsa_deg = drik.get_ayanamsa_value(jd)
    finally:
        drik.reset_ayanamsa_mode()

    asc_entry = chart[0][1]
    asc_longitude = _normalize_angle(asc_entry[0] * 30 + asc_entry[1])
    planet_map = {entry[0]: entry[1] for entry in chart[1:]}

    def _true_rahu_longitude() -> float:
        jd_ut = jd - tz_offset / 24.0
        flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        longitudes, _ = swe.calc_ut(jd_ut, swe.TRUE_NODE, flags=flags)
        return _normalize_angle(longitudes[0])

    bodies: List[RawBodyPosition] = []
    for body in pyjhora_config["include_bodies"]:
        requested_id = str(body).upper()
        graha_enum = graha_string_to_id(requested_id)
        body_id = graha_id_to_string(graha_enum) if graha_enum else requested_id
        idx = int(graha_enum) if graha_enum is not None else None
        entry = planet_map.get(idx) if idx is not None else None
        longitude = None
        speed = None
        retro = None

        if body_id == "RAHU":
            longitude = _true_rahu_longitude()
        elif body_id == "KETU":
            longitude = _normalize_angle(_true_rahu_longitude() + 180.0)
        elif entry is not None:
            longitude = _normalize_angle(entry[0] * 30 + entry[1])
            if idx is not None:
                info = plan_speed.get(idx)
                if info:
                    speed = float(info[3])
                    retro = speed < 0

        if longitude is None:
            continue

        bodies.append(
            RawBodyPosition(
                id=body_id,
                longitude_deg=longitude,
                speed_deg_per_day=speed,
                retrograde=retro,
            )
        )

    house_segments = _build_house_segments(houses)
    jd_utc = jd - tz_offset / 24.0

    return RawD1Chart(
        jd=jd,
        jd_utc=jd_utc,
        ascendant_longitude_deg=asc_longitude,
        house_segments=house_segments,
        bodies=bodies,
        ayanamsa_deg=ayanamsa_deg,
    )


def _build_position_record(
    longitude: float,
    segments: Sequence[RawHouseSegment],
    body_id: Optional[str] = None,
    speed_deg_per_day: Optional[float] = None,
    retrograde: Optional[bool] = None,
) -> Dict[str, Any]:
    sign_index, sign_name, degree = _sign_info(longitude)
    base_record: Dict[str, Any] = {
        "longitude_deg": longitude,
        "degree_in_sign": degree,
        "sign_index": sign_index,
        "sign_name": sign_name,
        "house_index": _house_index_for_longitude(longitude, segments),
    }
    base_record.update(_nakshatra_fields(longitude))
    if body_id:
        base_record["id"] = body_id
        graha_enum = graha_string_to_id(body_id)
        base_record["name"] = (
            graha_id_to_name(graha_enum) if graha_enum else body_id.title()
        )
    if speed_deg_per_day is not None:
        base_record["speed_deg_per_day"] = speed_deg_per_day
    if retrograde is not None:
        base_record["retrograde"] = retrograde
    return base_record


def run_core_chart(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _parse_core_chart_input(payload)
    config = normalized["config"]
    pyjhora_config = _build_pyjhora_config(config)
    raw_chart = _compute_raw_d1_chart(
        birth=normalized["birth"],
        location=normalized["location"],
        pyjhora_config=pyjhora_config,
    )

    person = normalized.get("person", {}) or {}
    birth_dt = normalized["birth"].aware_datetime
    person_payload = {
        "name": person.get("name"),
        "birth_date": birth_dt.date().isoformat(),
        "birth_time": birth_dt.time().replace(microsecond=0).isoformat(),
        "timezone": normalized["birth"].timezone,
    }

    ascending_payload = _build_position_record(
        longitude=raw_chart.ascendant_longitude_deg,
        segments=raw_chart.house_segments,
    )

    planet_payloads = [
        _build_position_record(
            longitude=body.longitude_deg,
            segments=raw_chart.house_segments,
            body_id=body.id,
            speed_deg_per_day=body.speed_deg_per_day,
            retrograde=body.retrograde,
        )
        for body in raw_chart.bodies
    ]

    houses_payload = [
        {
            "index": segment.index,
            "start_deg": segment.start_deg,
            "end_deg": segment.end_deg,
            "cusp_deg": segment.cusp_deg,
            "sign_index": segment.sign_index,
            "sign_name": rasi_index_to_name(segment.sign_index),
        }
        for segment in raw_chart.house_segments
    ]

    frame = {
        "frame_id": "D1",
        "description": "Natal D1 chart",
        "jd": raw_chart.jd_utc,
        "place": {
            "latitude": normalized["location"].lat,
            "longitude": normalized["location"].lon,
            "place_name": normalized["location"].place_name,
        },
        "ascendant": ascending_payload,
        "planets": planet_payloads,
        "houses": houses_payload,
    }

    return {
        "meta": {
            "schema_version": CORE_SCHEMA_VERSION,
            "timestamp_utc": datetime.now(dt_timezone.utc).isoformat(),
            "ayanamsa_deg": raw_chart.ayanamsa_deg,
            "jd_utc": raw_chart.jd_utc,
        },
        "person": person_payload,
        "config_echo": {
            "zodiac_type": config.zodiac_type,
            "ayanamsa_mode": config.ayanamsa_mode,
            "ayanamsa_value_deg": config.ayanamsa_value_deg,
            "house_system": config.house_system,
            "node_mode": config.node_mode,
            "include_bodies": config.include_bodies,
        },
        "frames": [frame],
    }
