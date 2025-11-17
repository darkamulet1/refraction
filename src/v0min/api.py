from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Union

import pytz

from jhora import utils

from .chakra_extract import ChakraConfig, compute_chakra_snapshot
from .dosha_extract import compute_dosha_block
from .event_scan_extract import EventScanConfig, compute_events_snapshot
from .payload_utils import build_birth_context_from_payload
from .raja_yoga_extract import compute_raja_yoga_block
from .strength_trends_extract import StrengthTrendsConfig, compute_strength_trends_from_payload
from .vedic_yaml import build_vedic_master_from_full

_SOURCE_PAYLOADS: Dict[int, Dict[str, Any]] = {}


def _load_birth_payload(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _register_source_payload(container: Dict[str, Any], payload: Dict[str, Any]) -> None:
    """
    Keep an internal mapping between the Vedic YAML dict and its originating full PyJHora payload.

    The mapping is internal-only so exported YAML files are not bloated by duplicated JSON data.
    """

    _SOURCE_PAYLOADS[id(container)] = payload


def _get_full_payload(container: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resolve a canonical *_full_pyjhora payload from either the raw dict or a registered YAML mapping.
    """

    if "birth_data" in container and "core_chart" in container:
        return container
    payload = _SOURCE_PAYLOADS.get(id(container))
    if payload is None:
        raise ValueError(
            "Unable to resolve the originating full_pyjhora payload. "
            "Provide the raw payload or build the YAML via build_full_yaml_from_birth_json first."
        )
    return payload


def _attach_source_meta(target: Dict[str, Any], key: str, meta: Dict[str, Any]) -> None:
    meta_block = target.setdefault("meta", {})
    sources = meta_block.setdefault("sources", {})
    sources[key] = meta


def _append_warning(target: Dict[str, Any], warning: str) -> None:
    warnings = target.setdefault("meta", {}).setdefault("warnings", [])
    if warning not in warnings:
        warnings.append(warning)


def build_core_yaml_from_birth_json(path: str) -> Dict[str, Any]:
    """
    Build the base vedic_master payload from a *_full_pyjhora.json snapshot without extra enrichment.
    """

    birth_path = Path(path)
    payload = _load_birth_payload(birth_path)
    vedic_payload = build_vedic_master_from_full(payload)
    meta = vedic_payload.setdefault("meta", {})
    meta["source_birth_json"] = str(birth_path)
    _attach_source_meta(
        vedic_payload,
        "core",
        {
            "engine": "v0min.vedic_yaml",
            "schema_version": vedic_payload["meta"].get("schema_version"),
        },
    )
    _register_source_payload(vedic_payload, payload)
    return vedic_payload


def enrich_with_chakras(core_yaml: Dict[str, Any]) -> Dict[str, Any]:
    if "chakra" in core_yaml:
        return core_yaml
    payload = _get_full_payload(core_yaml)
    try:
        chakra_block = compute_chakra_snapshot(payload, ChakraConfig())
    except Exception:
        _append_warning(core_yaml, "chakra_generation_failed")
        return core_yaml
    core_yaml["chakra"] = chakra_block
    _attach_source_meta(
        core_yaml,
        "chakras",
        {
            "engine": "v0min.chakra_extract",
            "schema_version": chakra_block.get("schema_version"),
        },
    )
    return core_yaml


def enrich_with_strength_trends(core_yaml: Dict[str, Any]) -> Dict[str, Any]:
    if "strength_trends" in core_yaml:
        return core_yaml
    payload = _get_full_payload(core_yaml)
    try:
        block = compute_strength_trends_from_payload(payload, StrengthTrendsConfig())
    except Exception:
        _append_warning(core_yaml, "strength_trends_generation_failed")
        return core_yaml
    core_yaml["strength_trends"] = block
    meta = block.get("meta", {})
    _attach_source_meta(
        core_yaml,
        "strength_trends",
        {
            "engine": "v0min.strength_trends_extract",
            "planet_basis": meta.get("planet_basis"),
            "sign_basis": meta.get("sign_basis"),
            "chart_id": meta.get("chart_id"),
        },
    )
    return core_yaml


def build_full_yaml_from_birth_json(path: str) -> Dict[str, Any]:
    """
    Build a vedic_master payload and enrich it with chakra + strength trend data.
    """

    core = build_core_yaml_from_birth_json(path)
    core = enrich_with_chakras(core)
    core = enrich_with_strength_trends(core)
    return core


def compute_chakras(full_yaml: Dict[str, Any]) -> Dict[str, Any]:
    return full_yaml.get("chakra", {})


def compute_strength_trends(full_yaml: Dict[str, Any]) -> Dict[str, Any]:
    return full_yaml.get("strength_trends", {})


def compute_dosha(full_yaml: Dict[str, Any]) -> Dict[str, Any]:
    payload = _get_full_payload(full_yaml)
    return compute_dosha_block(payload)


def compute_raja_yogas(full_yaml: Dict[str, Any]) -> Dict[str, Any]:
    payload = _get_full_payload(full_yaml)
    return compute_raja_yoga_block(payload)


def _jd_to_iso_local(jd: float, tz_name: str) -> str:
    year, month, day, fractional_hour = utils.jd_to_gregorian(jd)
    hour = int(fractional_hour)
    minute_float = (fractional_hour - hour) * 60.0
    minute = int(minute_float)
    second_float = (minute_float - minute) * 60.0
    second = int(second_float)
    microsecond = int(round((second_float - second) * 1_000_000))
    dt_utc = datetime(year, month, day, hour, minute, second, microsecond, tzinfo=pytz.UTC)
    tz = pytz.timezone(tz_name)
    return dt_utc.astimezone(tz).isoformat()


def compute_events(
    full_yaml: Dict[str, Any],
    start: Union[str, float],
    end: Union[str, float],
    *,
    event_types: Optional[Sequence[str]] = None,
    planets: Optional[Sequence[str]] = None,
    systems: Optional[Sequence[str]] = None,
    max_events: int = 500,
    include_house_entries: bool = False,
    include_vakra_segments: bool = False,
    vakra_planets: Optional[Sequence[str]] = None,
) -> Dict[str, Any]:
    payload = _get_full_payload(full_yaml)
    birth_ctx, _ = build_birth_context_from_payload(payload)
    if isinstance(start, (int, float)):
        start_iso = _jd_to_iso_local(float(start), birth_ctx.tz_name)
    else:
        start_iso = start
    if isinstance(end, (int, float)):
        end_iso = _jd_to_iso_local(float(end), birth_ctx.tz_name)
    else:
        end_iso = end
    cfg = EventScanConfig(
        start_datetime=start_iso,
        end_datetime=end_iso,
        event_types=list(event_types) if event_types else None,
        planets=list(planets) if planets else None,
        systems=list(systems) if systems else None,
        max_events=max_events,
        include_house_entries=include_house_entries,
        include_vakra_segments=include_vakra_segments,
        vakra_planets=list(vakra_planets) if vakra_planets else None,
    )
    snapshot = compute_events_snapshot(payload, cfg)
    _attach_source_meta(
        full_yaml,
        "events",
        {
            "engine": "v0min.event_scan_extract",
            "event_types": cfg.event_types or None,
            "systems": cfg.systems or None,
        },
    )
    return snapshot


__all__ = [
    "build_core_yaml_from_birth_json",
    "build_full_yaml_from_birth_json",
    "compute_chakras",
    "compute_dosha",
    "compute_events",
    "compute_raja_yogas",
    "compute_strength_trends",
    "enrich_with_chakras",
    "enrich_with_strength_trends",
]
