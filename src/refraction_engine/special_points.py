"""Special Points extractor for Refraction Engine V1."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Tuple

import pytz
from jhora import utils
from jhora.panchanga import drik

from .graha import (
    rasi_index_from_longitude,
    rasi_index_to_name,
    nakshatra_from_longitude,
    nakshatra_index_to_name,
)


def _lagna_longitude(spec_lagna: Tuple[int, float]) -> float:
    rasi_idx, deg = spec_lagna
    if rasi_idx and deg is not None:
        return ((rasi_idx - 1) * 30 + deg) % 360
    return 0.0


def _format_lagna(lagna_id: str, lagna_name: str, spec_lagna: Tuple[int, float]) -> Dict[str, Any]:
    longitude = _lagna_longitude(spec_lagna)
    sign_idx = rasi_index_from_longitude(longitude)
    nak_idx, nak_pada, _ = nakshatra_from_longitude(longitude)
    return {
        "id": lagna_id,
        "name": lagna_name,
        "longitude_deg": round(longitude, 2),
        "degree_in_sign": round(longitude % 30, 2),
        "sign_index": sign_idx,
        "sign_name": rasi_index_to_name(sign_idx),
        "nakshatra_index": nak_idx,
        "nakshatra_name": nakshatra_index_to_name(nak_idx),
        "nakshatra_pada": nak_pada,
    }


def _read_birth(payload: Dict[str, Any]) -> Tuple[datetime, Dict[str, Any]]:
    birth = payload["birth"]
    dt = datetime.fromisoformat(birth["datetime_local"])
    tz = pytz.timezone(birth["timezone_name"])
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)
    return dt, birth


def run_special_points(payload: Dict[str, Any]) -> Dict[str, Any]:
    config = payload.get("config", {})
    person = payload.get("person", {})

    dt, birth = _read_birth(payload)
    date = drik.Date(dt.year, dt.month, dt.day)
    time_tuple = (dt.hour, dt.minute, dt.second + dt.microsecond / 1_000_000)
    jd = utils.julian_day_number(date, time_tuple)
    offset = dt.utcoffset().total_seconds() / 3600 if dt.utcoffset() else 0.0
    place = drik.Place(
        birth["location"].get("name", "Refraction"),
        birth["location"]["lat"],
        birth["location"]["lon"],
        offset,
    )

    ayanamsa_mode = config.get("ayanamsa_mode", "LAHIRI")
    drik.set_ayanamsa_mode(ayanamsa_mode)
    ayanamsa_deg = drik.get_ayanamsa_value(jd)

    special_bodies = [
        (drik.bhava_lagna, "BHAVA_LAGNA", "Bhava Lagna"),
        (drik.hora_lagna, "HORA_LAGNA", "Hora Lagna"),
        (drik.ghati_lagna, "GHATI_LAGNA", "Ghati Lagna"),
        (drik.sree_lagna, "SREE_LAGNA", "Sree Lagna"),
    ]

    special_lagnas = [
        _format_lagna(lagna_id, name, func(jd, place, ayanamsa_mode=ayanamsa_mode))
        for func, lagna_id, name in special_bodies
    ]

    drik.reset_ayanamsa_mode()
    reference_iso = dt.astimezone(pytz.utc).isoformat()

    return {
        "meta": {
            "schema_version": "special_points_spec_v1",
            "timestamp_utc": reference_iso,
            "jd_utc": jd,
            "ayanamsa_deg": ayanamsa_deg,
        },
        "person": {
            "id": person.get("id"),
            "label": person.get("label"),
            "birth_date": dt.strftime("%Y-%m-%d"),
            "birth_time": dt.strftime("%H:%M:%S"),
            "timezone": birth["timezone_name"],
        },
        "config_echo": {
            "zodiac_type": config.get("zodiac_type"),
            "ayanamsa_mode": ayanamsa_mode,
            "house_system": config.get("house_system"),
        },
        "frames": {
            "special_lagnas": special_lagnas,
        },
    }
