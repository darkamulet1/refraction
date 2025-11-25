"""High-level pipeline that bundles all core extractors."""

from __future__ import annotations

from datetime import datetime, timezone as dt_timezone
from typing import Any, Dict

from .core_chart import _parse_core_chart_input
from .core_chart import run_core_chart
from .dashas import run_dashas_vimshottari
from .panchanga import run_panchanga
from .strengths import run_strengths
from .yogas import run_yogas


def _build_person_payload(normalized: Dict[str, Any]) -> Dict[str, Any]:
    person = normalized.get("person") or {}
    birth_dt = normalized["birth"].aware_datetime
    return {
        "id": person.get("id"),
        "label": person.get("label"),
        "birth_date": birth_dt.date().isoformat(),
        "birth_time": birth_dt.time().replace(microsecond=0).isoformat(),
        "timezone": normalized["birth"].timezone,
    }


def _build_config_echo(normalized: Dict[str, Any]) -> Dict[str, Any]:
    config = normalized["config"]
    return {
        "zodiac_type": config.zodiac_type,
        "ayanamsa_mode": config.ayanamsa_mode,
        "ayanamsa_value_deg": config.ayanamsa_value_deg,
        "house_system": config.house_system,
        "node_mode": config.node_mode,
        "include_bodies": config.include_bodies,
    }


def run_refraction_core(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Run all core extractors and bundle their outputs."""
    normalized = _parse_core_chart_input(payload)

    bundle = {
        "meta": {
            "schema_version": "refraction_core_bundle_spec_v1",
            "timestamp_utc": datetime.now(dt_timezone.utc).isoformat(),
        },
        "person": _build_person_payload(normalized),
        "config_echo": _build_config_echo(normalized),
        "frames": {
        "core_chart": run_core_chart(payload),
        "panchanga": run_panchanga(payload),
        "dashas_vimshottari": run_dashas_vimshottari(payload),
        "strengths": run_strengths(payload),
        "yogas": run_yogas(payload),
        },
    }

    return bundle
