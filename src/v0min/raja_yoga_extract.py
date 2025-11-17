from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from jhora import utils
from jhora.horoscope.chart import raja_yoga
from jhora.panchanga import drik

from v0min.payload_utils import build_birth_context_from_payload

RAJA_YOGA_SCHEMA_VERSION = "raja_yoga.v1"
ENGINE_NAME = "PYJHORA_RAJA_YOGA"

_PLANET_FALLBACK = {
    "sun": "Sun",
    "moon": "Moon",
    "mars": "Mars",
    "mercury": "Mercury",
    "jupiter": "Jupiter",
    "venus": "Venus",
    "saturn": "Saturn",
    "rahu": "Rahu",
    "ragu": "Rahu",
    "raagu": "Rahu",
    "ketu": "Ketu",
    "lagna": "Lagna",
}

_TYPE_MAP = {
    "vipareetha_raja_yoga": "VIPARITA",
    "dharma_karmadhipati_raja_yoga": "RAJA",
    "neecha_bhanga_raja_yoga": "CANCELLATION",
}

_HOUSES_BY_ID = {
    "dharma_karmadhipati_raja_yoga": [9, 10],
    "vipareetha_raja_yoga": [6, 8, 12],
}


def _ensure_language(lang: str) -> None:
    try:
        utils.set_language(lang)
    except Exception:
        pass


def compute_raja_yoga_block(
    full_payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]] = None,
    *,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Build the raja_yoga.v1 JSON block using PyJHora's Raja Yoga module.
    """

    _ensure_language(language)
    if base_context and "birth_context" in base_context:
        bc = base_context["birth_context"]
        place = base_context.get("place")
        if place is None:
            from jhora.panchanga import drik

            place = drik.Place(bc.location_name or "Birth Place", bc.latitude, bc.longitude, bc.utc_offset_hours)
    else:
        bc, place = build_birth_context_from_payload(full_payload)

    results, _, _ = raja_yoga.get_raja_yoga_details_for_all_charts(bc.jd_local, place, language=language)
    by_chart: Dict[str, List[Dict[str, Any]]] = {}
    for yoga_key, details in results.items():
        entry = _normalize_yoga_entry(yoga_key, details)
        chart_id = entry["chart_id"]
        by_chart.setdefault(chart_id, []).append(entry)

    for entries in by_chart.values():
        entries.sort(key=lambda item: item.get("id", ""))

    return {
        "schema_version": RAJA_YOGA_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "by_chart": by_chart,
    }


def _normalize_yoga_entry(yoga_key: str, detail: List[str]) -> Dict[str, Any]:
    info_line = detail[0] if detail else ""
    chart_id, pair_info = _parse_chart_info(info_line)
    planets = _extract_planets(pair_info)
    entry_id = yoga_key.upper()
    return {
        "id": entry_id,
        "name": detail[1] if len(detail) > 1 else entry_id,
        "type": _TYPE_MAP.get(yoga_key, "OTHER"),
        "chart_id": chart_id,
        "is_present": True,
        "strength": "STRONG",
        "planets": planets,
        "houses": _HOUSES_BY_ID.get(yoga_key, []),
        "notes": pair_info.strip() or None,
        "description": detail[2] if len(detail) > 2 else None,
        "benefits": detail[3] if len(detail) > 3 else None,
    }


def _parse_chart_info(info_line: str) -> tuple[str, str]:
    if "-" in info_line:
        chart_part, rest = info_line.split("-", 1)
        chart_id = chart_part.strip()
        return chart_id, rest.strip()
    return "D1", info_line.strip()


def _extract_planets(pair_info: str) -> List[str]:
    matches = re.findall(r"\[([^\]]+)\]", pair_info)
    names: List[str] = []
    seen = set()
    for match in matches:
        for raw in match.split("-"):
            normalized = _normalize_planet_label(raw)
            if normalized and normalized not in seen:
                names.append(normalized)
                seen.add(normalized)
    return names


def _normalize_planet_label(label: str) -> Optional[str]:
    cleaned = "".join(ch for ch in label if ch.isalpha())
    cleaned_lower = cleaned.lower()
    if not cleaned_lower:
        return None
    return _PLANET_FALLBACK.get(cleaned_lower, cleaned.title())


__all__ = ["compute_raja_yoga_block", "RAJA_YOGA_SCHEMA_VERSION"]
