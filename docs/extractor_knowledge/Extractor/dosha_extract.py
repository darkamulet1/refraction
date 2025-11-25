from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import dosha as dosha_mod, house
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min.core_time import BirthContext
from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

DOSHA_SCHEMA_VERSION = "dosha.v1"
ENGINE_NAME = "PYJHORA_DOSHA"

_PLANET_FALLBACK = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_NATURAL_MALEFICS = getattr(const, "natural_malefics", [2, 3, 4, 5, 6, 7, 8])


def _ensure_language(lang: str) -> None:
    try:
        utils.set_language(lang)
    except Exception:
        pass
    if not hasattr(utils, "PLANET_NAMES"):
        utils.PLANET_NAMES = list(_PLANET_FALLBACK)


def compute_dosha_block(
    full_payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]] = None,
    *,
    language: str = "en",
) -> Dict[str, Any]:
    """
    Build the dosha.v1 JSON block using PyJHora's dosha module.
    """

    _ensure_language(language)
    bc, place = _resolve_context(full_payload, base_context)
    planet_positions = _resolve_planet_positions(full_payload, base_context, bc, place)
    if not planet_positions:
        raise ValueError("Unable to resolve D1 planet positions for dosha extraction.")

    lagna_house = planet_positions[0][1][0]
    house_list = utils.get_house_planet_list_from_planet_positions(planet_positions)

    builders = [
        _compute_kala_sarpa,
        _compute_manglik,
        _compute_pitru,
        _compute_guru_chandala,
        _compute_ganda_moola,
        _compute_kalathra,
        _compute_ghata,
        _compute_shrapit,
    ]

    by_chart: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    counts_by_category: Dict[str, int] = defaultdict(int)
    severe_ids: List[str] = []

    for builder in builders:
        entry = builder(planet_positions, lagna_house, house_list, bc, place)
        if entry is None:
            continue
        chart_id = entry.get("chart_id", "D1")
        by_chart[chart_id].append(entry)
        if entry.get("is_present"):
            cat = entry.get("category")
            if cat:
                counts_by_category[cat] += 1
            if entry.get("severity") == "SEVERE":
                severe_ids.append(entry["id"])

    # Ensure deterministic ordering
    for entries in by_chart.values():
        entries.sort(key=lambda item: item.get("id", ""))

    summary = {
        "has_severe": bool(severe_ids),
        "severe_ids": severe_ids,
        "counts_by_category": counts_by_category,
    }

    return {
        "schema_version": DOSHA_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "by_chart": dict(by_chart),
        "summary": summary,
    }


def _resolve_context(
    payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]],
) -> tuple[BirthContext, drik.Place]:
    if base_context:
        bc: BirthContext = base_context["birth_context"]
        place = base_context.get("place")
        if place is None:
            place = drik.Place(bc.location_name or "Birth Place", bc.latitude, bc.longitude, bc.utc_offset_hours)
        return bc, place
    return build_birth_context_from_payload(payload)


def _resolve_planet_positions(
    payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]],
    bc: BirthContext,
    place: drik.Place,
):
    if base_context and base_context.get("rasi_raw_positions"):
        return base_context["rasi_raw_positions"]
    positions = get_chart_positions(payload, "D1")
    if positions:
        return positions
    return charts.rasi_chart(bc.jd_local, place, ayanamsa_mode=(payload.get("core_chart", {}).get("ayanamsa_mode") or "LAHIRI"))


def _planet_name(idx: Any) -> str:
    if idx == const._ascendant_symbol or idx == "L":
        return "Lagna"
    names = getattr(utils, "PLANET_NAMES", _PLANET_FALLBACK)
    try:
        return names[idx]
    except Exception:
        if isinstance(idx, str):
            return idx
        return _PLANET_FALLBACK[idx] if isinstance(idx, int) and idx < len(_PLANET_FALLBACK) else str(idx)


def _chart_entry(
    *,
    id: str,
    name: str,
    category: str,
    is_present: bool,
    severity: str,
    subtype: Optional[str] = None,
    planets: Optional[Iterable[str]] = None,
    houses: Optional[Iterable[int]] = None,
    notes: Optional[str] = None,
    chart_id: str = "D1",
) -> Dict[str, Any]:
    return {
        "id": id,
        "name": name,
        "category": category,
        "subtype": subtype,
        "is_present": bool(is_present),
        "severity": severity,
        "chart_id": chart_id,
        "planets": list(planets or []),
        "houses": list(houses or []),
        "notes": notes,
    }


def _compute_kala_sarpa(planet_positions, lagna_house, house_list, bc, place):
    present = bool(dosha_mod.kala_sarpa(house_list))
    return _chart_entry(
        id="KALA_SARPA",
        name="Kala Sarpa Dosha",
        category="SERPENT",
        is_present=present,
        severity="SEVERE" if present else "NONE",
        planets=["Rahu", "Ketu"],
        houses=[],
    )


def _compute_manglik(planet_positions, lagna_house, house_list, bc, place):
    result = dosha_mod.manglik(planet_positions)
    present = bool(result[0])
    has_exception = bool(result[1]) if len(result) > 1 else False
    exception_indices = result[2] if len(result) > 2 else []
    severity = "SEVERE" if present and not has_exception else ("MODERATE" if present else "NONE")
    subtype = "REDUCED" if present and has_exception else None
    mars_house = house.get_relative_house_of_planet(lagna_house, planet_positions[3][1][0])
    notes = None
    if exception_indices:
        notes = f"exceptions={exception_indices}"
    return _chart_entry(
        id="MANGALIK",
        name="Manglik Dosha",
        category="MANGALIK",
        is_present=present,
        severity=severity,
        subtype=subtype,
        planets=["Mars"],
        houses=[mars_house],
        notes=notes,
    )


def _compute_pitru(planet_positions, lagna_house, house_list, bc, place):
    present, triggers = dosha_mod.pitru_dosha(planet_positions)
    notes = f"conditions={triggers}" if triggers else None
    return _chart_entry(
        id="PITRU",
        name="Pitru Dosha",
        category="ANCESTRAL",
        is_present=bool(present),
        severity="SEVERE" if present else "NONE",
        planets=["Sun", "Moon", "Rahu", "Ketu"],
        houses=[2, 4, 5, 9, 12],
        notes=notes,
    )


def _compute_guru_chandala(planet_positions, lagna_house, house_list, bc, place):
    present, jupiter_strong = dosha_mod.guru_chandala_dosha(planet_positions)
    jupiter_house = planet_positions[5][1][0]
    rahu_house = planet_positions[8][1][0]
    ketu_house = planet_positions[9][1][0]
    node = None
    if jupiter_house == rahu_house:
        node = "Rahu"
    elif jupiter_house == ketu_house:
        node = "Ketu"
    planets = ["Jupiter"]
    if node:
        planets.append(node)
    subtype = "JUPITER_STRONG" if present and jupiter_strong else None
    notes = f"node={node}" if node else None
    return _chart_entry(
        id="GURU_CHANDALA",
        name="Guru Chandala Dosha",
        category="SPIRITUAL",
        is_present=bool(present),
        severity="SEVERE" if present else "NONE",
        subtype=subtype,
        planets=planets,
        houses=[house.get_relative_house_of_planet(lagna_house, jupiter_house)],
        notes=notes,
    )


def _compute_ganda_moola(planet_positions, lagna_house, house_list, bc, place):
    moon_star = drik.nakshatra(bc.jd_local, place)[0]
    if isinstance(moon_star, (list, tuple)):
        moon_star = moon_star[0]
    star_index = int(moon_star)
    present = star_index in getattr(const, "ganda_moola_stars", [])
    notes = f"nakshatra_index={star_index}"
    return _chart_entry(
        id="GANDA_MOOLA",
        name="Ganda Moola Dosha",
        category="ANCESTRAL",
        is_present=bool(present),
        severity="MODERATE" if present else "NONE",
        planets=["Moon"],
        houses=[],
        notes=notes,
    )


def _compute_kalathra(planet_positions, lagna_house, house_list, bc, place):
    present = bool(dosha_mod.kalathra(planet_positions))
    planets = [_planet_name(p) for p in _NATURAL_MALEFICS]
    return _chart_entry(
        id="KALATHRA",
        name="Kalathra Dosha",
        category="MARRIAGE",
        is_present=present,
        severity="SEVERE" if present else "NONE",
        planets=planets,
        houses=[1, 2, 4, 7, 8, 12],
    )


def _compute_ghata(planet_positions, lagna_house, house_list, bc, place):
    present = bool(dosha_mod.ghata(planet_positions))
    mars_house = house.get_relative_house_of_planet(lagna_house, planet_positions[3][1][0])
    saturn_house = house.get_relative_house_of_planet(lagna_house, planet_positions[7][1][0])
    return _chart_entry(
        id="GHATA",
        name="Ghata Dosha",
        category="CONJUNCTION",
        is_present=present,
        severity="SEVERE" if present else "NONE",
        planets=["Mars", "Saturn"],
        houses=sorted({mars_house, saturn_house}),
    )


def _compute_shrapit(planet_positions, lagna_house, house_list, bc, place):
    present = bool(dosha_mod.shrapit(planet_positions))
    saturn_house = house.get_relative_house_of_planet(lagna_house, planet_positions[7][1][0])
    rahu_house = house.get_relative_house_of_planet(lagna_house, planet_positions[8][1][0])
    return _chart_entry(
        id="SHRAPIT",
        name="Shrapit Dosha",
        category="CONJUNCTION",
        is_present=present,
        severity="SEVERE" if present else "NONE",
        planets=["Saturn", "Rahu"],
        houses=sorted({saturn_house, rahu_house}),
    )


__all__ = ["compute_dosha_block", "DOSHA_SCHEMA_VERSION"]
