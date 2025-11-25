from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Dict

import pytz
import swisseph as swe

from jhora import utils
from jhora.panchanga import drik

from v0min.core_time import BirthContext


def _hours_to_clock(hours: float) -> str:
    total_seconds = int(round(hours * 3600))
    h = (total_seconds // 3600) % 24
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _build_place(bc: BirthContext, tz_offset_hours: float) -> drik.Place:
    label = bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, tz_offset_hours)


def _trikalam_block(jd_local: float, place: drik.Place, option: str) -> Dict[str, str]:
    srise = drik.sunrise(jd_local, place)[0]
    day_dur = drik.day_length(jd_local, place)
    weekday = drik.vaara(jd_local)
    offsets = {
        "raahu": [0.875, 0.125, 0.75, 0.5, 0.625, 0.375, 0.25],
        "gulika": [0.75, 0.625, 0.5, 0.375, 0.25, 0.125, 0.0],
        "yamaganda": [0.5, 0.375, 0.25, 0.125, 0.0, 0.75, 0.625],
    }
    key = option.lower()
    start_val = srise + day_dur * offsets[key][weekday]
    end_val = start_val + 0.125 * day_dur
    return {
        "start_local": _hours_to_clock(start_val),
        "end_local": _hours_to_clock(end_val),
    }


def _build_day_entry(jd_local: float, place: drik.Place) -> Dict[str, object]:
    tz_hours = place[3]
    vaara_idx = drik.vaara(jd_local)

    tithi_data = drik.tithi(jd_local, place)
    nak_data = drik.nakshatra(jd_local, place)
    yoga_data = drik.yogam(jd_local, place)
    karana_data = drik.karana(jd_local, place)

    sunrise = drik.sunrise(jd_local, place)
    sunset = drik.sunset(jd_local, place)

    rahu = _trikalam_block(jd_local, place, "raahu")
    yamaganda = _trikalam_block(jd_local, place, "yamaganda")
    gulika = _trikalam_block(jd_local, place, "gulika")

    return {
        "reference_jd_local": jd_local,
        "weekday": {
            "id": vaara_idx,
            "local_name": utils.DAYS_LIST[vaara_idx],
        },
        "tithi": {
            "id": int(tithi_data[0]),
            "local_name": utils.TITHI_LIST[int(tithi_data[0]) - 1],
        },
        "nakshatra": {
            "id": int(nak_data[0]),
            "local_name": utils.NAKSHATRA_LIST[int(nak_data[0]) - 1],
        },
        "yoga": {
            "id": int(yoga_data[0]),
            "local_name": utils.YOGAM_LIST[int(yoga_data[0]) - 1],
        },
        "karana": {
            "id": int(karana_data[0]),
            "local_name": utils.KARANA_LIST[int(karana_data[0]) - 1],
        },
        "sunrise": {
            "local_time": _hours_to_clock(sunrise[0]),
            "jd_local": sunrise[2],
            "jd_utc": sunrise[2] - tz_hours / 24.0,
        },
        "sunset": {
            "local_time": _hours_to_clock(sunset[0]),
            "jd_local": sunset[2],
            "jd_utc": sunset[2] - tz_hours / 24.0,
        },
        "rahukalam": [rahu],
        "yamaganda": [yamaganda],
        "gulika": [gulika],
    }


def build_panchanga_calendar(
    bc: BirthContext,
    start_date: date,
    end_date: date,
) -> Dict[str, object]:
    """
    Build a day-wise Panchanga calendar for the supplied date range.
    """

    tz = pytz.timezone(bc.tz_name)
    current = start_date
    days: Dict[str, Dict[str, object]] = {}
    while current <= end_date:
        dt_local = tz.localize(datetime(current.year, current.month, current.day, 5, 30, 0))
        local_hour = (
            dt_local.hour
            + dt_local.minute / 60.0
            + dt_local.second / 3600.0
            + dt_local.microsecond / 3_600_000_000
        )
        jd_local = swe.julday(dt_local.year, dt_local.month, dt_local.day, local_hour)
        offset_hours = dt_local.utcoffset().total_seconds() / 3600.0
        place = _build_place(bc, offset_hours)
        entry = _build_day_entry(jd_local, place)
        days[current.isoformat()] = entry
        current += timedelta(days=1)

    return {
        "engine": "PYJHORA_PANCHANGA_CALENDAR",
        "place": {
            "name": bc.location_name or "Birth Place",
            "latitude_deg": bc.latitude,
            "longitude_deg": bc.longitude,
            "timezone": bc.tz_name,
        },
        "range": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
        },
        "days": days,
    }


__all__ = ["build_panchanga_calendar"]
