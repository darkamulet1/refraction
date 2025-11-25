from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

import pytz

from jhora import utils

from v0min.core_space import compute_core_chart
from v0min.core_time import BirthContext, make_birth_context


PLANET_ORDER = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


@dataclass
class TransitGrahaOverlay:
    name: str
    natal_longitude_deg: float
    natal_sign_index: int
    natal_house_index: int
    transit_longitude_deg: float
    transit_sign_index: int
    transit_house_from_natal_lagna: int
    aspects_to_natal: List[Dict[str, object]] = field(default_factory=list)


@dataclass
class TransitHighLevelFlags:
    sade_sati_phase: Optional[str] = None
    saturn_house_from_moon: Optional[int] = None
    saturn_house_from_lagna: Optional[int] = None
    jupiter_house_from_lagna: Optional[int] = None
    rahu_house_from_lagna: Optional[int] = None
    ketu_house_from_lagna: Optional[int] = None


@dataclass
class TransitSnapshot:
    schema_version: str
    engine_version: Optional[str]
    generated_at_utc: str
    reference_person: str
    reference_source_file: str
    natal_jd_local: float
    natal_datetime_local: str
    transit_datetime_local: str
    transit_jd_local: float
    transit_jd_utc: float
    location: Dict[str, object]
    natal_lagna_longitude_deg: float
    natal_moon_longitude_deg: float
    transit_lagna_longitude_deg: float
    grahas: List[TransitGrahaOverlay]
    flags: TransitHighLevelFlags


def _split_longitude(longitude_deg: float) -> tuple[int, float]:
    sign_idx = int(longitude_deg // 30.0) % 12
    return sign_idx, longitude_deg % 30.0


def _house_from_lagna(target_sign: int, lagna_sign: int) -> int:
    return ((target_sign - lagna_sign) % 12) + 1


def _normalize_local_datetime(dt: datetime | str, tz_name: str) -> datetime:
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    tz = pytz.timezone(tz_name)
    if dt.tzinfo is None:
        return tz.localize(dt)
    return dt.astimezone(tz)


def _compute_aspects(transit_long: float, natal_positions: Dict[str, float], name: str) -> List[Dict[str, object]]:
    orb = 3.0
    special_aspects = {
        "Mars": [90.0, 180.0, 270.0],
        "Jupiter": [120.0, 180.0, 240.0],
        "Saturn": [60.0, 180.0, 300.0],
        "Rahu": [60.0, 180.0, 300.0],
        "Ketu": [60.0, 180.0, 300.0],
    }
    default_aspects = [180.0]
    aspects: List[Dict[str, object]] = []
    aspect_angles = special_aspects.get(name, default_aspects)
    for target, natal_long in natal_positions.items():
        angle = (transit_long - natal_long) % 360.0
        for exact in aspect_angles:
            diff = abs(angle - exact)
            diff = min(diff, 360.0 - diff)
            if diff <= orb:
                aspects.append(
                    {
                        "target": target,
                        "type": f"ASPECT_{int(exact)}",
                        "orb_deg": round(diff, 3),
                    }
                )
    return aspects


def _compute_flags(
    natal_moon_sign_idx: int,
    natal_lagna_sign_idx: int,
    transit_sign_lookup: Dict[str, int],
) -> TransitHighLevelFlags:
    flags = TransitHighLevelFlags()
    saturn_sign = transit_sign_lookup.get("Saturn")
    jupiter_sign = transit_sign_lookup.get("Jupiter")
    rahu_sign = transit_sign_lookup.get("Rahu")
    ketu_sign = transit_sign_lookup.get("Ketu")

    if saturn_sign is not None:
        flags.saturn_house_from_lagna = _house_from_lagna(saturn_sign, natal_lagna_sign_idx)
        flags.saturn_house_from_moon = _house_from_lagna(saturn_sign, natal_moon_sign_idx)
        offset = flags.saturn_house_from_moon
        if offset in (12, 1, 2):
            flags.sade_sati_phase = "DURING"
        elif offset in (3, 4):
            flags.sade_sati_phase = "AFTER"
        elif offset == 11:
            flags.sade_sati_phase = "BEFORE"

    if jupiter_sign is not None:
        flags.jupiter_house_from_lagna = _house_from_lagna(jupiter_sign, natal_lagna_sign_idx)

    if rahu_sign is not None:
        flags.rahu_house_from_lagna = _house_from_lagna(rahu_sign, natal_lagna_sign_idx)

    if ketu_sign is not None:
        flags.ketu_house_from_lagna = _house_from_lagna(ketu_sign, natal_lagna_sign_idx)

    return flags


def build_transit_snapshot(
    natal_payload: Dict[str, object],
    transit_datetime_local: datetime | str,
    tz_name: Optional[str] = None,
) -> TransitSnapshot:
    birth_meta = natal_payload["meta"]
    birth_data = natal_payload["birth_data"]
    core_chart = natal_payload["core_chart"]
    person = birth_data["person"]
    location = birth_data["location"]
    tz = tz_name or birth_data["timezone_name"]

    natal_lagna_deg = core_chart["lagna_longitude_deg"]
    natal_lagna_sign, _ = _split_longitude(natal_lagna_deg)
    natal_moon_deg = core_chart["planets"]["Moon"]
    natal_moon_sign, _ = _split_longitude(natal_moon_deg)

    natal_planets_detail = core_chart["planets_detail"]
    natal_house_map = {
        name: data.get("sign_index", 0)
        for name, data in natal_planets_detail.items()
    }
    natal_abs_positions = core_chart["planets"]

    natal_place_label = location.get("name")
    lat = location["lat"]
    lon = location["lon"]
    dt_local = _normalize_local_datetime(transit_datetime_local, tz)
    bc_transit = make_birth_context(
        dt_local.replace(tzinfo=None),
        lat,
        lon,
        tz_name=tz,
        location_name=natal_place_label,
    )
    transit_chart = compute_core_chart(bc_transit, ayanamsa_mode=core_chart.get("ayanamsa_mode"))
    transit_planets = transit_chart["planets"]
    transit_sign_lookup = {name: _split_longitude(value)[0] for name, value in transit_planets.items()}

    grahas: List[TransitGrahaOverlay] = []
    for name in PLANET_ORDER:
        natal_long = core_chart["planets"][name]
        natal_sign_idx, _ = _split_longitude(natal_long)
        natal_house_idx = ((natal_sign_idx - natal_lagna_sign) % 12) + 1

        transit_long = transit_planets[name]
        transit_sign_idx, _ = _split_longitude(transit_long)
        house_from_lagna = ((transit_sign_idx - natal_lagna_sign) % 12) + 1

        aspects = _compute_aspects(transit_long, natal_abs_positions, name)

        grahas.append(
            TransitGrahaOverlay(
                name=name,
                natal_longitude_deg=natal_long,
                natal_sign_index=natal_sign_idx,
                natal_house_index=natal_house_idx,
                transit_longitude_deg=transit_long,
                transit_sign_index=transit_sign_idx,
                transit_house_from_natal_lagna=house_from_lagna,
                aspects_to_natal=aspects,
            )
        )

    flags = _compute_flags(natal_moon_sign, natal_lagna_sign, transit_sign_lookup)

    snapshot = TransitSnapshot(
        schema_version="transit.v1",
        engine_version=birth_meta.get("engine_version"),
        generated_at_utc=datetime.utcnow().isoformat(),
        reference_person=person,
        reference_source_file="",
        natal_jd_local=birth_meta["jd_local"],
        natal_datetime_local=birth_data["datetime_local"],
        transit_datetime_local=dt_local.isoformat(),
        transit_jd_local=bc_transit.jd_local,
        transit_jd_utc=bc_transit.jd_utc,
        location={
            "name": natal_place_label,
            "latitude_deg": lat,
            "longitude_deg": lon,
            "timezone": tz,
        },
        natal_lagna_longitude_deg=natal_lagna_deg,
        natal_moon_longitude_deg=natal_moon_deg,
        transit_lagna_longitude_deg=transit_chart["lagna_longitude_deg"],
        grahas=grahas,
        flags=flags,
    )
    return snapshot


def build_transit_payload(
    natal_payload: Dict[str, object],
    transit_datetime_local: datetime | str,
    tz_name: Optional[str] = None,
) -> Dict[str, object]:
    snapshot = build_transit_snapshot(natal_payload, transit_datetime_local, tz_name)
    return asdict(snapshot)


__all__ = [
    "TransitGrahaOverlay",
    "TransitHighLevelFlags",
    "TransitSnapshot",
    "build_transit_snapshot",
    "build_transit_payload",
]
