from __future__ import annotations

import contextlib
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import dosha as dosha_mod
from jhora.horoscope.chart import house
from jhora.horoscope.chart import yoga as yoga_mod
from jhora.horoscope.chart import charts

from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

YOGAS_EXTENDED_SCHEMA_VERSION = "yogas_extended.v1"
ENGINE_NAME = "PYJHORA_YOGAS_EXTENDED"

_PLANET_FALLBACK = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


@dataclass
class YogasExtendedConfig:
    enabled: bool = True
    charts: List[str] = field(default_factory=lambda: ["D1"])
    language: str = "en"
    include_kaala_sarpa_variants: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "YogasExtendedConfig":
        if not data:
            return cls()
        charts_value = data.get("charts")
        if isinstance(charts_value, str):
            charts_list = [charts_value]
        elif isinstance(charts_value, Iterable):
            charts_list = [str(item) for item in charts_value]
        else:
            charts_list = ["D1"]
        charts_list = [entry for entry in charts_list if entry]
        return cls(
            enabled=bool(data.get("enabled", True)),
            charts=charts_list or ["D1"],
            language=str(data.get("language") or "en"),
            include_kaala_sarpa_variants=bool(data.get("include_kaala_sarpa_variants", True)),
        )


def compute_yogas_extended_from_payload(
    full_payload: Dict[str, Any],
    config: YogasExtendedConfig,
) -> Dict[str, Any]:
    """
    Build the yogas_extended.v1 JSON payload from a *_full_pyjhora.json snapshot.
    """

    bc, place = build_birth_context_from_payload(full_payload)
    language = config.language or getattr(const, "_DEFAULT_LANGUAGE", "en")
    entries: List[Dict[str, Any]] = []

    with _temporary_language(language):
        catalog = _load_yoga_catalog(language)
        for chart_id in _normalized_chart_ids(config.charts):
            factor = _chart_factor_from_id(chart_id)
            if factor is None:
                continue
            try:
                yoga_map, _, _ = yoga_mod.get_yoga_details_for_all_charts(
                    bc.jd_local,
                    place,
                    language=language,
                    divisional_chart_factor=factor,
                )
            except Exception:
                continue
            entries.extend(_normalize_yoga_entries(yoga_map, catalog, chart_id))

        if config.include_kaala_sarpa_variants:
            ks_entry = _build_kaala_sarpa_entry(full_payload, bc, place, language)
            if ks_entry:
                entries.append(ks_entry)

    entries.sort(key=lambda item: (item.get("family", ""), item.get("id", "")))

    return {
        "schema_version": YOGAS_EXTENDED_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "language": language,
        "entries": entries,
    }


def _load_yoga_catalog(language: str) -> Dict[str, Dict[str, str]]:
    try:
        raw_catalog = yoga_mod.get_yoga_resources(language=language)
    except Exception:
        raw_catalog = {}
    catalog: Dict[str, Dict[str, str]] = {}
    for key, values in (raw_catalog or {}).items():
        name = values[0] if len(values) > 0 else key.replace("_", " ").title()
        description = values[1] if len(values) > 1 else ""
        benefit = values[2] if len(values) > 2 else ""
        normalized_id = key.upper()
        catalog[key] = {
            "id": normalized_id,
            "name": name,
            "description": description,
            "benefit": benefit,
        }
    return catalog


def _normalize_yoga_entries(
    yoga_map: Optional[Dict[str, List[str]]],
    catalog: Dict[str, Dict[str, str]],
    fallback_chart_id: str,
) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    if not yoga_map:
        return entries
    for yoga_key, details in yoga_map.items():
        if not details:
            continue
        chart_field = details[0] if len(details) > 0 else fallback_chart_id
        chart_id = _canonical_chart_id(chart_field, fallback_chart_id)
        meta = catalog.get(yoga_key, {})
        normalized_id = meta.get("id") or yoga_key.upper()
        label = meta.get("name") or (details[1] if len(details) > 1 else normalized_id.title())
        description = meta.get("description") or (details[2] if len(details) > 2 else "")
        benefit = meta.get("benefit") or (details[3] if len(details) > 3 else "")
        family = _derive_family(yoga_key)
        entries.append(
            {
                "id": normalized_id,
                "family": family,
                "label": label,
                "chart": chart_id,
                "planets": [],
                "houses": [],
                "present": True,
                "description": description,
                "benefits": benefit,
                "severity": "info",
                "source": "PYJHORA_YOGA_MODULE",
            }
        )
    return entries


def _derive_family(key: str) -> str:
    token = key.lower()
    if token.endswith("_yoga"):
        token = token[: -len("_yoga")]
    return token


def _canonical_chart_id(raw: Any, fallback: str) -> str:
    if isinstance(raw, str):
        token = raw.strip().upper()
        if token.startswith("D") and token[1:].isdigit():
            return token
        if token.isdigit():
            return f"D{token}"
    if isinstance(raw, (int, float)):
        value = int(raw)
        if value > 0:
            return f"D{value}"
    return fallback


def _normalized_chart_ids(charts: Iterable[str]) -> List[str]:
    normalized: List[str] = []
    seen: set[str] = set()
    for entry in charts:
        token = str(entry or "").strip().upper()
        if not token:
            continue
        if not token.startswith("D") and token.isdigit():
            token = f"D{token}"
        if not token.startswith("D"):
            continue
        if token in seen:
            continue
        seen.add(token)
        normalized.append(token)
    return normalized or ["D1"]


def _chart_factor_from_id(chart_id: str) -> Optional[int]:
    token = (chart_id or "").strip().upper()
    if not token.startswith("D"):
        return None
    try:
        value = int(token[1:])
        return value if value > 0 else None
    except ValueError:
        return None


def _build_kaala_sarpa_entry(full_payload: Dict[str, Any], bc, place, language: str) -> Optional[Dict[str, Any]]:
    positions = get_chart_positions(full_payload, "D1")
    if not positions:
        try:
            positions = charts.rasi_chart(bc.jd_local, place)
        except Exception:
            positions = None
    if not positions:
        return None
    house_list = utils.get_house_planet_list_from_planet_positions(positions)
    if not dosha_mod.kala_sarpa(house_list):
        return None
    lagna_sign = int(positions[0][1][0])
    rahu_sign = int(positions[8][1][0])
    ketu_sign = int(positions[9][1][0])
    rahu_house = house.get_relative_house_of_planet(lagna_sign, rahu_sign)
    ketu_house = house.get_relative_house_of_planet(lagna_sign, ketu_sign)
    messages = _load_kala_sarpa_messages(language)
    label, description = _extract_kala_sarpa_label(messages, rahu_house)
    return {
        "id": f"KAALA_SARPA_VARIANT_{rahu_house:02d}",
        "family": "kaala_sarpa",
        "label": label,
        "chart": "D1",
        "planets": _get_planet_names(),
        "houses": _houses_between(rahu_house, ketu_house),
        "present": True,
        "description": description,
        "benefits": None,
        "severity": "high",
        "source": "PYJHORA_DOSHA_MODULE",
    }


def _houses_between(start: int, end: int) -> List[int]:
    houses: List[int] = []
    current = start
    for _ in range(12):
        houses.append(current)
        if current == end:
            break
        current = current % 12 + 1
    return houses


def _load_kala_sarpa_messages(language: str) -> List[str]:
    try:
        dosha_msgs = dosha_mod.get_dosha_resources(language=language)
    except Exception:
        dosha_msgs = {}
    return dosha_msgs.get("kala_sarpa", [])


def _extract_kala_sarpa_label(messages: List[str], house_index: int) -> tuple[str, str]:
    if not messages:
        return ("Kaala Sarpa Variant", "")
    idx = min(max(house_index, 0), len(messages) - 1)
    raw_text = messages[idx]
    if "-" in raw_text:
        title, desc = raw_text.split("-", 1)
        return title.strip(), desc.strip()
    return raw_text.strip(), ""


def _get_planet_names() -> List[str]:
    names = getattr(utils, "PLANET_NAMES", None)
    if names and len(names) >= len(_PLANET_FALLBACK):
        return list(names[: len(_PLANET_FALLBACK)])
    return list(_PLANET_FALLBACK)


@contextlib.contextmanager
def _temporary_language(language: str):
    current = getattr(const, "_DEFAULT_LANGUAGE", "en")
    target = language or current
    if target == current:
        yield
        return
    try:
        utils.set_language(target)
    except Exception:
        yield
        return
    try:
        yield
    finally:
        utils.set_language(current)


__all__ = [
    "YOGAS_EXTENDED_SCHEMA_VERSION",
    "YogasExtendedConfig",
    "compute_yogas_extended_from_payload",
]
