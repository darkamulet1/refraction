"""Transit snapshot extractor for Refraction Engine V1."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import pytz

from .core_chart import (
    CoreChartBirth,
    CoreChartConfig,
    CoreChartLocation,
    _build_pyjhora_config,
    _compute_raw_d1_chart,
    _build_position_record,
)
from .graha import GRAHA_ORDER, graha_id_to_string


@dataclass
class TransitReference:
    datetime_local: str
    timezone: str
    aware_datetime: datetime


def _parse_transit_input(payload: Dict[str, Any]) -> Dict[str, Any]:
    reference = payload.get("reference")
    if not reference:
        raise ValueError("Missing 'reference' section for transit payload")
    datetime_local = reference.get("datetime_local")
    timezone = reference.get("timezone_name") or reference.get("timezone")
    if not datetime_local or not timezone:
        raise ValueError("reference.datetime_local and reference.timezone_name are required")
    try:
        aware_dt = datetime.fromisoformat(datetime_local)
    except ValueError:
        aware_dt = datetime.strptime(datetime_local, "%Y-%m-%dT%H:%M:%S")
    tz = pytz.timezone(timezone)
    if aware_dt.tzinfo is None:
        aware_dt = tz.localize(aware_dt)
    else:
        aware_dt = aware_dt.astimezone(tz)

    location = reference.get("location")
    if not location:
        raise ValueError("Missing reference.location")
    try:
        lat = float(location["latitude"])
        lon = float(location["longitude"])
    except KeyError as exc:
        raise ValueError(f"Missing location coordinate: {exc}") from exc
    place_name = location.get("place_name")

    config = payload.get("config")
    if not config:
        raise ValueError("Missing 'config' section")
    zodiac_type = config.get("zodiac_type")
    house_system = config.get("house_system")
    if not zodiac_type or not house_system:
        raise ValueError("zodiac_type and house_system are required")
    include_bodies = config.get(
        "include_bodies", [graha_id_to_string(graha) for graha in GRAHA_ORDER]
    )
    bodies = [str(item).upper() for item in include_bodies if item]

    return {
        "reference": TransitReference(
            datetime_local=datetime_local, timezone=timezone, aware_datetime=aware_dt
        ),
        "location": CoreChartLocation(lat=lat, lon=lon, place_name=place_name),
        "config": CoreChartConfig(
            zodiac_type=zodiac_type.upper(),
            ayanamsa_mode=config.get("ayanamsa_mode"),
            ayanamsa_value_deg=config.get("ayanamsa_value_deg"),
            house_system=house_system.upper(),
            node_mode=config.get("node_mode", "TRUE").upper(),
            include_bodies=bodies or [graha_id_to_string(g) for g in GRAHA_ORDER],
        ),
        "person": payload.get("person"),
    }


def run_transit(payload: Dict[str, Any]) -> Dict[str, Any]:
    parsed = _parse_transit_input(payload)
    config = parsed["config"]
    pyjhora_config = _build_pyjhora_config(config)
    raw_chart = _compute_raw_d1_chart(
        birth=CoreChartBirth(
            datetime_local=parsed["reference"].datetime_local,
            timezone=parsed["reference"].timezone,
            aware_datetime=parsed["reference"].aware_datetime,
        ),
        location=parsed["location"],
        pyjhora_config=pyjhora_config,
    )

    reference_utc = parsed["reference"].aware_datetime.astimezone(pytz.utc)
    reference_iso = reference_utc.isoformat()
    frame = {
        "frame_id": "TRANSIT",
        "description": "Transit snapshot",
        "reference": {
            "datetime_utc": reference_iso,
            "timezone": parsed["reference"].timezone,
            "location": {
                "latitude": parsed["location"].lat,
                "longitude": parsed["location"].lon,
                "place_name": parsed["location"].place_name,
            },
        },
        "ascendant": _build_position_record(
            longitude=raw_chart.ascendant_longitude_deg,
            segments=raw_chart.house_segments,
            body_id=None,
        ),
        "planets": [
            _build_position_record(
                longitude=body.longitude_deg,
                segments=raw_chart.house_segments,
                body_id=body.id,
                speed_deg_per_day=body.speed_deg_per_day,
                retrograde=body.retrograde,
            )
            for body in raw_chart.bodies
        ],
    }

    person = parsed.get("person") or {}
    birth_dt = parsed["reference"].aware_datetime
    reference_utc = parsed["reference"].aware_datetime.astimezone(pytz.utc)
    return {
        "meta": {
            "schema_version": "transit_spec_v1",
            "timestamp_utc": reference_utc.isoformat(),
            "engine": {"name": "PyJHora", "version": "1.0.0"},
        },
        "person": {
            "id": person.get("id"),
            "label": person.get("label"),
        },
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
