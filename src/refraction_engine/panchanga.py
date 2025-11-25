"""Panchanga extractor implementation for Refraction Engine V1."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone as dt_timezone
from typing import Any, Dict, List, Optional, Sequence, Tuple

from jhora import const, utils
from jhora.panchanga import drik

from .core_chart import (
    _build_pyjhora_config,
    _get_karana_names,
    _get_tithi_names,
    _get_yoga_names,
    _language_list,
    _normalize_angle,
    _parse_core_chart_input,
)
from .graha import (
    graha_const_to_string,
    nakshatra_from_longitude,
    nakshatra_index_to_name,
)


def _hours_to_local_iso(base_dt: datetime, hours: float) -> str:
    total_seconds = hours * 3600.0
    seconds = int(total_seconds)
    microseconds = int(round((total_seconds - seconds) * 1_000_000))
    delta = timedelta(seconds=seconds, microseconds=microseconds)
    midnight = base_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight + delta).isoformat()


def _tuple_to_local_iso(base_dt: datetime, time_value: Sequence[float] | str) -> str:
    if isinstance(time_value, str):
        hours, minutes, seconds = utils.from_dms_str_to_dms(time_value)
    else:
        hours, minutes, seconds = time_value[:3]
    delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    midnight = base_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    return (midnight + delta).isoformat()


def _align_interval(start: float, end: float, current: float) -> Tuple[float, float]:
    while start > current:
        start -= 24
        end -= 24
    while end <= current:
        start += 24
        end += 24
    return start, end


def _prepare_drik(pyjhora_config: Dict[str, Any], jd: float) -> Optional[float]:
    zodiac_type = pyjhora_config["zodiac_type"]
    if zodiac_type == "SIDEREAL":
        drik.set_sideral_planets()
        ayanamsa_mode = (
            pyjhora_config["ayanamsa"]["internal_constant"]
            or pyjhora_config["ayanamsa"]["mode"]
            or const._DEFAULT_AYANAMSA_MODE
        )
        ayanamsa_value = pyjhora_config["ayanamsa"]["value_deg"]
        drik.set_ayanamsa_mode(ayanamsa_mode, ayanamsa_value, jd=jd)
        return drik.get_ayanamsa_value(jd)
    drik.set_tropical_planets()
    return drik.get_ayanamsa_value(jd)


def _build_time_interval_windows(
    base_dt: datetime,
    windows: List[Sequence[float]],
    tags: List[str],
) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    for time_pair, tag in zip(windows, tags):
        if len(time_pair) < 2:
            continue
        start = _tuple_to_local_iso(base_dt, time_pair[0])
        end = _tuple_to_local_iso(base_dt, time_pair[1])
        result.append({"start": start, "end": end, "tag": tag})
    return result


def _build_inauspicious_windows(
    base_dt: datetime, jd: float, place: drik.Place
) -> List[Dict[str, str]]:
    windows: List[Sequence[float]] = []
    labels: List[str] = []
    for fn, label in [
        (drik.raahu_kaalam, "RAHU_KALAM"),
        (drik.yamaganda_kaalam, "YAMAGANDA"),
        (drik.gulikai_kaalam, "GULIKAI"),
    ]:
        window = fn(jd, place)
        if len(window) >= 2:
            windows.append(window)
            labels.append(label)
    return _build_time_interval_windows(base_dt, windows, labels)


def _build_auspicious_windows(
    base_dt: datetime, jd: float, place: drik.Place
) -> List[Dict[str, str]]:
    window = drik.abhijit_muhurta(jd, place)
    if len(window) >= 2:
        return _build_time_interval_windows(base_dt, [window], ["ABHIJIT"])
    return []


def _compute_remaining_percentage(
    tithi_result: Sequence[float], current_hours: float
) -> float:
    if len(tithi_result) < 3:
        return 0.0
    start = tithi_result[1]
    end = tithi_result[2]
    start, end = _align_interval(start, end, current_hours)
    duration = end - start
    if duration <= 0:
        return 0.0
    remaining = max(0.0, min(1.0, (end - current_hours) / duration))
    return remaining


def _compute_hora_lord(birth_dt: datetime, sunrise_hours: float) -> str:
    hora_sequence = ["SUN", "VENUS", "MERCURY", "MOON", "SATURN", "JUPITER", "MARS"]
    weekday_lord = {
        0: "MOON",
        1: "MARS",
        2: "MERCURY",
        3: "JUPITER",
        4: "VENUS",
        5: "SATURN",
        6: "SUN",
    }
    current_hours = (
        birth_dt.hour
        + birth_dt.minute / 60.0
        + birth_dt.second / 3600.0
        + birth_dt.microsecond / 3_600_000_000
    )
    diff = current_hours - sunrise_hours
    if diff < 0:
        diff += 24
    start_idx = hora_sequence.index(weekday_lord[birth_dt.weekday()])
    hora_idx = int(diff) % len(hora_sequence)
    return hora_sequence[(start_idx + hora_idx) % len(hora_sequence)]


def run_panchanga(payload: Dict[str, Any]) -> Dict[str, Any]:
    normalized = _parse_core_chart_input(payload)
    config = normalized["config"]
    pyjhora_config = _build_pyjhora_config(config)
    birth = normalized["birth"]
    location = normalized["location"]
    dt = birth.aware_datetime
    date = drik.Date(dt.year, dt.month, dt.day)
    time_tuple = (dt.hour, dt.minute, dt.second + dt.microsecond / 1_000_000)
    jd = utils.julian_day_number(date, time_tuple)
    tz_offset = dt.utcoffset().total_seconds() / 3600 if dt.utcoffset() else 0.0
    place = drik.Place(
        location.place_name or "Refraction", location.lat, location.lon, tz_offset
    )

    ayanamsa_deg = _prepare_drik(pyjhora_config, jd)
    try:
        sunrise_info = drik.sunrise(jd, place)
        sunset_info = drik.sunset(jd, place)
        tithi_result = drik.tithi(jd, place)
        yoga_result = drik.yogam(jd, place)
        karana_result = drik.karana(jd, place)
        moon_longitude = drik.lunar_longitude(jd)
    finally:
        drik.reset_ayanamsa_mode()

    tithi_index = int(tithi_result[0]) if tithi_result else 0
    tithi_names = _get_tithi_names()
    tithi_name = (
        tithi_names[tithi_index - 1]
        if 1 <= tithi_index <= len(tithi_names)
        else f"TITHI_{tithi_index}"
    )
    current_hours = (
        dt.hour + dt.minute / 60.0 + dt.second / 3600.0 + dt.microsecond / 3_600_000_000
    )
    remaining_percentage = _compute_remaining_percentage(tithi_result, current_hours)
    paksha = "SHUKLA" if 1 <= tithi_index <= 15 else "KRISHNA"

    yoga_index = int(yoga_result[0]) if yoga_result else 0
    yoga_names = _get_yoga_names()
    yoga_name = (
        yoga_names[yoga_index - 1]
        if 1 <= yoga_index <= len(yoga_names)
        else f"YOGA_{yoga_index}"
    )

    karana_index = int(karana_result[0]) if karana_result else 0
    karana_names = _get_karana_names()
    karana_name = (
        karana_names[karana_index - 1]
        if 1 <= karana_index <= len(karana_names)
        else f"KARANA_{karana_index}"
    )

    nakshatra_index, nakshatra_pada, span_deg = nakshatra_from_longitude(moon_longitude)
    nakshatra_name = nakshatra_index_to_name(nakshatra_index)
    lord_const = const.nakshatra_lords[nakshatra_index - 1] if 1 <= nakshatra_index <= 27 else None
    nakshatra_lord = (
        graha_const_to_string(lord_const) if lord_const is not None else None
    )

    reference_iso = dt.astimezone(dt_timezone.utc).isoformat()
    sunrise_iso = _hours_to_local_iso(dt, sunrise_info[0])
    sunset_iso = _hours_to_local_iso(dt, sunset_info[0])

    windows_base = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    auspicious = _build_auspicious_windows(windows_base, jd, place)
    inauspicious = _build_inauspicious_windows(windows_base, jd, place)

    hora_lord = _compute_hora_lord(dt, sunrise_info[0])
    vaara_index = (dt.weekday() + 1) % 7
    vaara_names = _language_list("DAYS_LIST")
    vaara_name = (
        vaara_names[vaara_index] if 0 <= vaara_index < len(vaara_names) else str(vaara_index)
    )

    return {
        "meta": {
            "schema_version": "panchanga_spec_v1",
            "timestamp_utc": datetime.now(dt_timezone.utc).isoformat(),
            "ayanamsa_deg": ayanamsa_deg,
            "jd_utc": jd - tz_offset / 24.0,
        },
        "panchanga": {
            "reference": {
                "datetime_utc": reference_iso,
                "timezone": birth.timezone,
                "location": {
                    "latitude": location.lat,
                    "longitude": location.lon,
                },
            },
            "vaara": {"index": vaara_index, "name": vaara_name},
            "tithi": {
                "index": tithi_index,
                "name": tithi_name,
                "paksha": paksha,
                "remaining_percentage": remaining_percentage,
            },
            "nakshatra": {
                "index": nakshatra_index,
                "name": nakshatra_name,
                "pada": nakshatra_pada,
                "lord": nakshatra_lord,
                "span_deg": span_deg,
            },
            "yoga": {"index": yoga_index, "name": yoga_name},
            "karana": {"index": karana_index, "name": karana_name},
            "hora_lord": hora_lord,
            "sunrise": sunrise_iso,
            "sunset": sunset_iso,
            "auspicious_windows": auspicious,
            "inauspicious_windows": inauspicious,
        },
    }
