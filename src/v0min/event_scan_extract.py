from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from typing import Dict, List, Optional, Sequence, Tuple

import pytz
import swisseph as swe

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min import payload_utils

DEFAULT_EVENT_TYPES = [
    "SIGN_ENTRY",
    "RETROGRADE",
    "CONJUNCTION",
    "ECLIPSE",
    "SANKRANTI",
    "HOUSE_ENTRY",
    "RETROGRADE_SEGMENT",
]
DEFAULT_PLANETS = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]

PLANET_NAME_LIST = list(getattr(utils, "PLANET_NAMES", []))
if not PLANET_NAME_LIST:
    PLANET_NAME_LIST = DEFAULT_PLANETS
PLANET_NAME_TO_ID = {name.upper(): idx for idx, name in enumerate(PLANET_NAME_LIST)}
SIGN_NAMES = list(getattr(utils, "RAASI_LIST", []))
if not SIGN_NAMES:
    SIGN_NAMES = [
        "Aries",
        "Taurus",
        "Gemini",
        "Cancer",
        "Leo",
        "Virgo",
        "Libra",
        "Scorpio",
        "Sagittarius",
        "Capricorn",
        "Aquarius",
        "Pisces",
    ]


@dataclass
class EventScanConfig:
    start_datetime: str
    end_datetime: str
    place_override: Optional[Dict[str, object]] = None
    systems: Optional[List[str]] = None
    event_types: Optional[List[str]] = None
    planets: Optional[List[str]] = None
    max_events: int = 500
    include_house_entries: bool = False
    include_vakra_segments: bool = False
    vakra_planets: Optional[List[str]] = None

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "EventScanConfig":
        return EventScanConfig(
            start_datetime=str(data["start_datetime"]),
            end_datetime=str(data["end_datetime"]),
            place_override=data.get("place_override"),
            systems=data.get("systems"),
            event_types=data.get("event_types"),
            planets=data.get("planets"),
            max_events=int(data.get("max_events", 500)),
            include_house_entries=bool(data.get("include_house_entries", False)),
            include_vakra_segments=bool(data.get("include_vakra_segments", False)),
            vakra_planets=data.get("vakra_planets"),
        )


def compute_events_snapshot(
    birth_payload: Dict[str, object],
    config: EventScanConfig,
) -> Dict[str, object]:
    birth_ctx, base_place = payload_utils.build_birth_context_from_payload(birth_payload)
    place, tz_name = _resolve_place_override(base_place, birth_ctx.tz_name, config.place_override)
    jd_start = _iso_to_jd(config.start_datetime, tz_name)
    jd_end = _iso_to_jd(config.end_datetime, tz_name)
    event_types = [evt.upper() for evt in (config.event_types or DEFAULT_EVENT_TYPES)]
    ayanamsa_mode = birth_payload.get("core_chart", {}).get("ayanamsa_mode", const._DEFAULT_AYANAMSA_MODE)

    if jd_end <= jd_start:
        raise ValueError("end_datetime must be after start_datetime")

    events: List[Dict[str, object]] = []
    remaining = config.max_events

    include_sign_entries = "SIGN_ENTRY" in event_types
    include_sankranti = "SANKRANTI" in event_types
    include_retro = any(evt in {"RETROGRADE", "RETROGRADE_START", "RETROGRADE_END"} for evt in event_types)
    include_conjunction = "CONJUNCTION" in event_types
    include_eclipse = any(evt in {"ECLIPSE", "SOLAR_ECLIPSE", "LUNAR_ECLIPSE"} for evt in event_types)
    include_house_entries = config.include_house_entries and "HOUSE_ENTRY" in event_types
    include_vakra_segments = config.include_vakra_segments and ("RETROGRADE_SEGMENT" in event_types)

    systems = [sys.upper() for sys in (config.systems or ["D1"])]
    planet_ids = _resolve_planet_ids(config.planets)

    snapshot_place = {
        "name": place.Place,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "tz_offset_hours": place.timezone,
        "tz_name": tz_name,
    }

    if (include_sign_entries or include_sankranti) and remaining > 0:
        events.extend(
            _scan_sign_entries(
                jd_start,
                jd_end,
                place,
                tz_name,
                systems,
                planet_ids,
                remaining,
                include_sign_entries,
                include_sankranti,
            )
        )
        remaining = config.max_events - len(events)

    if include_retro and remaining > 0:
        events.extend(
            _scan_retrograde_events(
                jd_start,
                jd_end,
                place,
                tz_name,
                planet_ids,
                remaining,
                event_types,
            )
        )
        remaining = config.max_events - len(events)

    if include_conjunction and remaining > 0:
        events.extend(
            _scan_conjunctions(
                jd_start,
                jd_end,
                place,
                tz_name,
                planet_ids,
                remaining,
            )
        )
        remaining = config.max_events - len(events)

    if include_eclipse and remaining > 0:
        events.extend(
            _scan_eclipses(
                jd_start,
                jd_end,
                place,
                tz_name,
                remaining,
                event_types,
            )
        )
        remaining = config.max_events - len(events)

    if include_house_entries and remaining > 0:
        events.extend(
            _scan_house_entries(
                jd_start,
                jd_end,
                place,
                tz_name,
                planet_ids,
                remaining,
                ayanamsa_mode,
            )
        )
        remaining = config.max_events - len(events)

    if include_vakra_segments and remaining > 0:
        events.extend(
            _scan_vakra_segments(
                jd_start,
                jd_end,
                place,
                tz_name,
                config.vakra_planets or config.planets,
                remaining,
            )
        )

    events.sort(key=lambda ev: ev["jd_utc"])
    if len(events) > config.max_events:
        events = events[: config.max_events]

    return {
        "schema_version": "events.v1",
        "start_datetime_local": config.start_datetime,
        "end_datetime_local": config.end_datetime,
        "ayanamsa": birth_payload.get("core_chart", {}).get("ayanamsa_mode"),
        "place": snapshot_place,
        "events": events,
        "meta": {
            "systems": systems,
            "event_types": event_types,
            "max_events": config.max_events,
        },
    }


def _scan_sign_entries(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    systems: Sequence[str],
    planet_ids: Sequence[int],
    max_events: int,
    include_sign_entries: bool,
    include_sankranti: bool,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for system in systems:
        factor = _system_to_factor(system)
        if factor is None:
            continue
        for planet_id in planet_ids:
            jd_cursor = jd_start
            while jd_cursor < jd_end and len(results) < max_events:
                entry = _next_divisional_entry(jd_cursor, place, planet_id, factor)
                if not entry:
                    break
                entry_jd, longitude = entry
                if entry_jd <= jd_cursor + 1e-7:
                    jd_cursor += 0.01
                    continue
                if entry_jd > jd_end:
                    break
                event_record = _build_sign_event(
                    entry_jd,
                    longitude,
                    planet_id,
                    system,
                    place,
                    tz_name,
                )
                if include_sign_entries:
                    results.append(event_record)
                if include_sankranti and planet_id == 0 and system == "D1":
                    sankranti_event = dict(event_record)
                    sankranti_event["type"] = "SANKRANTI"
                    results.append(sankranti_event)
                jd_cursor = entry_jd + 1e-4
                if len(results) >= max_events:
                    break
    return results


def _scan_retrograde_events(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    planet_ids: Sequence[int],
    max_events: int,
    requested_types: Sequence[str],
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    allowed_planets = [pid for pid in planet_ids if pid in {2, 3, 4, 5, 6}]
    if not allowed_planets:
        return results
    current_date = _jd_to_date(jd_start)
    for planet_id in allowed_planets:
        date_cursor = current_date
        while len(results) < max_events:
            ret = drik.next_planet_retrograde_change_date(planet_id, date_cursor, place)
            if not ret:
                break
            event_jd, direction = ret
            if event_jd > jd_end:
                break
            event_type = "RETROGRADE_START" if direction == -1 else "RETROGRADE_END"
            if "RETROGRADE" in requested_types or event_type in requested_types:
                results.append(
                    _build_event_record(
                        event_type,
                        place,
                        tz_name,
                        event_jd,
                        planet=PLANET_NAME_LIST[planet_id],
                    )
                )
            date_cursor = _jd_to_date(event_jd + 1)
            if event_jd + 1 > jd_end:
                break
    return results


def _scan_conjunctions(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    planet_ids: Sequence[int],
    max_events: int,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    if not planet_ids:
        return results
    if len(planet_ids) == 1:
        pairs = [(0, planet_ids[0])]
    else:
        pairs = list(combinations(planet_ids[: min(5, len(planet_ids))], 2))
    for p1, p2 in pairs:
        jd_cursor = jd_start
        while len(results) < max_events and jd_cursor < jd_end:
            try:
                ret = drik.next_conjunction_of_planet_pair(jd_cursor, place, p1, p2, direction=1)
            except Exception:
                break
            if not ret:
                break
            event_jd = ret[0]
            if event_jd > jd_end:
                break
            results.append(
                _build_event_record(
                    "CONJUNCTION",
                    place,
                    tz_name,
                    event_jd,
                    planet=PLANET_NAME_LIST[p1],
                    planet2=PLANET_NAME_LIST[p2],
                )
            )
            jd_cursor = event_jd + 1
    return results


def _scan_eclipses(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    max_events: int,
    event_types: Sequence[str],
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    include_solar = "ECLIPSE" in event_types or "SOLAR_ECLIPSE" in event_types
    include_lunar = "ECLIPSE" in event_types or "LUNAR_ECLIPSE" in event_types
    jd_cursor = jd_start
    if include_solar:
        while jd_cursor < jd_end and len(results) < max_events:
            ret = drik.next_solar_eclipse(jd_cursor, place)
            if not ret:
                break
            retflag, tret, attrs = ret
            if retflag == -1:
                break
            event_jd = tret[0]
            if event_jd > jd_end:
                break
            results.append(
                _build_event_record(
                    "ECLIPSE",
                    place,
                    tz_name,
                    event_jd,
                    subtype="SOLAR",
                    extra={"magnitude": attrs[0] if attrs else None},
                )
            )
            jd_cursor = event_jd + 5
    if include_lunar:
        jd_cursor = jd_start
        while jd_cursor < jd_end and len(results) < max_events:
            ret = drik.next_lunar_eclipse(jd_cursor, place)
            if not ret:
                break
            retflag, tret, attrs = ret
            if retflag == -1:
                break
            event_jd = tret[0]
            if event_jd > jd_end:
                break
                results.append(
                    _build_event_record(
                        "ECLIPSE",
                        place,
                        tz_name,
                        event_jd,
                        subtype="LUNAR",
                        extra={"magnitude": attrs[0] if attrs else None},
                    )
                )
                jd_cursor = event_jd + 5
    return results


def _collect_sign_entry_times(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    planet_id: int,
    max_entries: int,
) -> List[float]:
    events: List[float] = []
    jd_cursor = jd_start
    checks = 0
    while jd_cursor < jd_end and len(events) < max_entries and checks < max_entries * 4:
        entry = _next_divisional_entry(jd_cursor, place, planet_id, 1)
        if not entry:
            break
        entry_jd = entry[0]
        if entry_jd <= jd_cursor + 1e-7:
            jd_cursor += 0.01
            checks += 1
            continue
        if entry_jd > jd_end:
            break
        events.append(entry_jd)
        jd_cursor = entry_jd + 1e-4
        checks += 1
    return events


def _collect_asc_entry_times(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    max_entries: int,
) -> List[float]:
    events: List[float] = []
    jd_cursor = jd_start
    checks = 0
    while jd_cursor < jd_end and len(events) < max_entries and checks < max_entries * 10:
        try:
            ret = drik.next_ascendant_entry_date(jd_cursor, place)
        except Exception:
            break
        if not ret:
            break
        entry_jd = ret[0]
        if entry_jd <= jd_cursor + 1e-7:
            jd_cursor += 1.0 / 24.0
            checks += 1
            continue
        if entry_jd > jd_end:
            break
        events.append(entry_jd)
        jd_cursor = entry_jd + 1e-4
        checks += 1
    return events


def _house_info_at(
    jd_utc: float,
    place: drik.Place,
    ayanamsa_mode: str,
    planet_id: int,
) -> Optional[Dict[str, int]]:
    chart = _chart_for_jd(jd_utc, place, ayanamsa_mode)
    if not chart:
        return None
    lagna_sign = chart[0][1][0]
    sign_idx = None
    for pid, (sign_value, _) in chart[1:]:
        if pid == planet_id:
            sign_idx = sign_value
            break
    if sign_idx is None:
        return None
    house_number = ((sign_idx - lagna_sign) % 12) + 1
    return {"house": house_number, "sign_index": sign_idx, "lagna_index": lagna_sign}


def _chart_for_jd(jd_utc: float, place: drik.Place, ayanamsa_mode: str):
    local_jd = jd_utc + place.timezone / 24.0
    try:
        return charts.rasi_chart(local_jd, place, ayanamsa_mode=ayanamsa_mode)
    except Exception:
        return None


def _scan_house_entries(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    planet_ids: Sequence[int],
    max_events: int,
    ayanamsa_mode: str,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    for planet_id in planet_ids:
        if isinstance(planet_id, str):
            continue
        planet_entries = _collect_sign_entry_times(jd_start, jd_end, place, planet_id, max_events * 2)
        combined = sorted(planet_entries)
        prev_info = _house_info_at(jd_start, place, ayanamsa_mode, planet_id)
        if not prev_info:
            continue
        prev_house = prev_info["house"]
        prev_sign = prev_info["sign_index"]
        for entry_jd in combined:
            if entry_jd <= jd_start:
                continue
            info = _house_info_at(entry_jd + 1e-6, place, ayanamsa_mode, planet_id)
            if not info:
                continue
            new_house = info["house"]
            if new_house != prev_house:
                results.append(
                    _build_event_record(
                        "HOUSE_ENTRY",
                        place,
                        tz_name,
                        entry_jd,
                        planet=PLANET_NAME_LIST[planet_id],
                        from_house=prev_house,
                        to_house=new_house,
                        from_sign=SIGN_NAMES[prev_sign],
                        to_sign=SIGN_NAMES[info["sign_index"]],
                    )
                )
                prev_house = new_house
                prev_sign = info["sign_index"]
                if len(results) >= max_events:
                    return results
    return results


def _collect_retrograde_changes(
    planet_id: int,
    jd_start: float,
    jd_end: float,
    place: drik.Place,
) -> List[Tuple[float, int]]:
    events: List[Tuple[float, int]] = []
    date_cursor = _jd_to_date(jd_start)
    safety = 0
    while safety < 200:
        ret = drik.next_planet_retrograde_change_date(planet_id, date_cursor, place)
        if not ret:
            break
        event_jd, new_state = ret
        if event_jd > jd_end + 1:
            break
        events.append((event_jd, new_state))
        date_cursor = _jd_to_date(event_jd + 1)
        safety += 1
    return events


def _motion_direction(planet_id: int, jd_utc: float) -> int:
    delta = 1.0 / (24.0 * 60.0)
    pl = drik.planet_list[planet_id]
    lon1 = drik.sidereal_longitude(jd_utc, pl)
    lon2 = drik.sidereal_longitude(jd_utc + delta, pl)
    diff = (lon2 - lon1 + 540.0) % 360.0 - 180.0
    return -1 if diff < 0 else 1


def _scan_vakra_segments(
    jd_start: float,
    jd_end: float,
    place: drik.Place,
    tz_name: str,
    planet_names: Optional[Sequence[str]],
    max_events: int,
) -> List[Dict[str, object]]:
    results: List[Dict[str, object]] = []
    candidate_ids = _resolve_planet_ids(planet_names) if planet_names else [2, 3, 4, 5, 6]
    planet_ids = [pid for pid in candidate_ids if pid in {2, 3, 4, 5, 6}]
    for planet_id in planet_ids:
        if len(results) >= max_events:
            break
        current_state = _motion_direction(planet_id, jd_start - 1e-4)
        segment_start = jd_start if current_state == -1 else None
        start_kind = None
        changes = _collect_retrograde_changes(planet_id, jd_start, jd_end, place)
        for change_jd, new_state in changes:
            if change_jd < jd_start:
                current_state = new_state
                continue
            if segment_start is not None and current_state == -1:
                end_jd = min(change_jd, jd_end)
                results.append(
                    _build_vakra_segment_record(
                        place,
                        tz_name,
                        PLANET_NAME_LIST[planet_id],
                        segment_start,
                        end_jd,
                        start_kind=start_kind,
                        end_kind="STATIONARY_DIRECT",
                        start_stationary_jd=segment_start if start_kind else None,
                        end_stationary_jd=change_jd,
                    )
                )
                if len(results) >= max_events:
                    break
                segment_start = None
                start_kind = None
            if new_state == -1 and change_jd < jd_end:
                segment_start = max(change_jd, jd_start)
                start_kind = "STATIONARY_RETROGRADE"
            current_state = new_state
        if len(results) >= max_events:
            break
        if segment_start is not None and current_state == -1:
            results.append(
                _build_vakra_segment_record(
                    place,
                    tz_name,
                    PLANET_NAME_LIST[planet_id],
                    segment_start,
                    jd_end,
                    start_kind=start_kind,
                    end_kind=None,
                    start_stationary_jd=segment_start if start_kind else None,
                    end_stationary_jd=None,
                )
            )
    return results


def _build_sign_event(
    jd_utc: float,
    longitude_deg: float,
    planet_id: int,
    system: str,
    place: drik.Place,
    tz_name: str,
) -> Dict[str, object]:
    to_sign_idx = int(longitude_deg // 30) % 12
    from_sign_idx = (to_sign_idx - 1) % 12
    return _build_event_record(
        "SIGN_ENTRY",
        place,
        tz_name,
        jd_utc,
        planet=PLANET_NAME_LIST[planet_id],
        subtype=system,
        from_sign=SIGN_NAMES[from_sign_idx],
        to_sign=SIGN_NAMES[to_sign_idx],
    )


def _build_event_record(
    event_type: str,
    place: drik.Place,
    tz_name: str,
    jd_utc: float,
    planet: Optional[str] = None,
    planet2: Optional[str] = None,
    subtype: Optional[str] = None,
    extra: Optional[Dict[str, object]] = None,
    from_sign: Optional[str] = None,
    to_sign: Optional[str] = None,
    from_house: Optional[int] = None,
    to_house: Optional[int] = None,
) -> Dict[str, object]:
    iso = _jd_to_iso(jd_utc, tz_name)
    record: Dict[str, object] = {
        "type": event_type,
        "datetime_local": iso,
        "jd_utc": jd_utc,
        "place": _place_payload(place),
        "source": "PYJHORA_EVENT",
    }
    if planet:
        record["planet"] = planet
    if planet2:
        record["planet2"] = planet2
    if subtype:
        record["subtype"] = subtype
    if from_sign:
        record["from_sign"] = from_sign
    if to_sign:
        record["to_sign"] = to_sign
    if from_house is not None:
        record["from_house"] = from_house
    if to_house is not None:
        record["to_house"] = to_house
    if extra:
        record["extra"] = extra
    return record


def _build_vakra_segment_record(
    place: drik.Place,
    tz_name: str,
    planet: str,
    jd_start: float,
    jd_end: float,
    start_kind: Optional[str] = None,
    end_kind: Optional[str] = None,
    start_stationary_jd: Optional[float] = None,
    end_stationary_jd: Optional[float] = None,
) -> Dict[str, object]:
    record: Dict[str, object] = {
        "type": "RETROGRADE_SEGMENT",
        "planet": planet,
        "jd_start": jd_start,
        "jd_end": jd_end,
        "jd_utc": jd_start,
        "datetime_local_start": _jd_to_iso(jd_start, tz_name),
        "datetime_local_end": _jd_to_iso(jd_end, tz_name),
        "place": _place_payload(place),
        "source": "PYJHORA_EVENT",
    }
    points: List[Dict[str, object]] = []
    if start_kind and start_stationary_jd is not None:
        points.append(
            {
                "jd": start_stationary_jd,
                "datetime_local": _jd_to_iso(start_stationary_jd, tz_name),
                "kind": start_kind,
            }
        )
    if end_kind and end_stationary_jd is not None:
        points.append(
            {
                "jd": end_stationary_jd,
                "datetime_local": _jd_to_iso(end_stationary_jd, tz_name),
                "kind": end_kind,
            }
        )
    if points:
        record["stationary_points"] = points
    return record


def _place_payload(place: drik.Place) -> Dict[str, object]:
    return {
        "name": place.Place,
        "latitude": place.latitude,
        "longitude": place.longitude,
        "tz_offset_hours": place.timezone,
    }


def _next_divisional_entry(
    jd: float,
    place: drik.Place,
    planet_id: int,
    factor: int,
) -> Optional[Tuple[float, float]]:
    try:
        if factor == 1:
            return drik.next_planet_entry_date(planet_id, jd, place)
        return charts.next_planet_entry_date_divisional_chart(
            jd,
            place,
            planet=planet_id,
            divisional_chart_factor=factor,
        )
    except Exception:
        return None


def _resolve_planet_ids(planets: Optional[Sequence[str]]) -> List[int]:
    if not planets:
        return [PLANET_NAME_TO_ID.get(name.upper(), idx) for idx, name in enumerate(PLANET_NAME_LIST)]
    resolved = []
    for name in planets:
        idx = PLANET_NAME_TO_ID.get(name.upper())
        if idx is not None:
            resolved.append(idx)
    return resolved


def _system_to_factor(system: str) -> Optional[int]:
    if system == "D1":
        return 1
    if system.startswith("D") and system[1:].isdigit():
        return int(system[1:])
    return None


def _resolve_place_override(
    base_place: drik.Place,
    base_tz_name: str,
    override: Optional[Dict[str, object]],
) -> Tuple[drik.Place, str]:
    if not override:
        return base_place, base_tz_name
    name = override.get("name", base_place.Place)
    lat = float(override.get("lat", base_place.latitude))
    lon = float(override.get("lon", base_place.longitude))
    tz_offset = float(override.get("tz_offset_hours", base_place.timezone))
    tz_name = override.get("tz_name", base_tz_name)
    return drik.Place(name, lat, lon, tz_offset), str(tz_name)


def _iso_to_jd(value: str, tz_name: str) -> float:
    dt = datetime.fromisoformat(value)
    tz = pytz.timezone(tz_name)
    if dt.tzinfo is None:
        dt = tz.localize(dt)
    else:
        dt = dt.astimezone(tz)
    dt_utc = dt.astimezone(pytz.UTC)
    hour = (
        dt_utc.hour
        + dt_utc.minute / 60.0
        + dt_utc.second / 3600.0
        + dt_utc.microsecond / 3_600_000_000.0
    )
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour)


def _jd_to_iso(jd: float, tz_name: str) -> str:
    dt_utc = _jd_to_datetime(jd, pytz.UTC)
    tz = pytz.timezone(tz_name)
    return dt_utc.astimezone(tz).isoformat()


def _jd_to_datetime(jd: float, tz) -> datetime:
    year, month, day, fh = utils.jd_to_gregorian(jd)
    hour = int(fh)
    minute = int((fh - hour) * 60)
    second_float = (fh - hour - minute / 60.0) * 3600.0
    second = int(second_float)
    microsecond = int((second_float - second) * 1_000_000)
    dt = datetime(year, month, day, hour, minute, second, microsecond, tzinfo=pytz.UTC)
    if tz is pytz.UTC:
        return dt
    return dt.astimezone(tz)


def _jd_to_date(jd: float) -> drik.Date:
    year, month, day, _ = utils.jd_to_gregorian(jd)
    return drik.Date(year, month, day)


__all__ = ["compute_events_snapshot", "EventScanConfig"]
