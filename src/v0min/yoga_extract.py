from __future__ import annotations

from typing import Dict, List

from jhora.horoscope.chart import yoga as yoga_mod
from jhora.panchanga import drik

from v0min.core_time import BirthContext


def _build_place(bc: BirthContext) -> drik.Place:
    label = bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def _normalize_catalog(raw_catalog: Dict[str, List[str]]) -> Dict[str, Dict[str, str]]:
    catalog: Dict[str, Dict[str, str]] = {}
    for key, values in (raw_catalog or {}).items():
        name = values[0] if len(values) > 0 else key.replace("_", " ").title()
        description = values[1] if len(values) > 1 else ""
        benefit = values[2] if len(values) > 2 else ""
        catalog[key] = {
            "id": key.upper(),
            "name": name,
            "description": description,
            "benefit": benefit,
        }
    return catalog


def compute_yoga_block(bc: BirthContext, lang: str = "en") -> Dict[str, object]:
    """
    Compute the PyJHora yogas for the supplied birth context.
    """

    place = _build_place(bc)
    raw_catalog = yoga_mod.get_yoga_resources(language=lang)
    catalog = _normalize_catalog(raw_catalog)
    yoga_map, _, _ = yoga_mod.get_yoga_details_for_all_charts(
        bc.jd_local,
        place,
        language=lang,
    )

    by_chart: Dict[str, List[Dict[str, str]]] = {}
    for yoga_key, detail in (yoga_map or {}).items():
        if not detail:
            continue
        chart_id = detail[0]
        meta = catalog.get(yoga_key, {})
        normalized_id = meta.get("id") or yoga_key.upper()
        name = meta.get("name") or (detail[1] if len(detail) > 1 else yoga_key)
        description = meta.get("description") or (detail[2] if len(detail) > 2 else "")
        benefit = meta.get("benefit") or (detail[3] if len(detail) > 3 else "")
        chart_key = chart_id if chart_id.upper().startswith("D") else f"D{chart_id}"
        by_chart.setdefault(chart_key, []).append(
            {
                "id": normalized_id,
                "name": name,
                "description": description,
                "benefit": benefit,
            }
        )

    for entries in by_chart.values():
        entries.sort(key=lambda item: (item.get("id") or "", item.get("name") or ""))

    return {
        "engine": "PYJHORA_YOGA",
        "lang": lang,
        "by_chart": by_chart,
    }


__all__ = ["compute_yoga_block"]
