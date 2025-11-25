from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import house

_DEFAULT_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_CANONICAL_SIGNS = [
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


def compute_aspects_for_varga(
    context: Dict[str, Any],
    varga_code: str = "D1",
    include: Iterable[str] = ("graha", "rashi"),
) -> Dict[str, Any]:
    """Return graha/rashi drishti blocks for the requested varga."""

    include = tuple(include or ())
    results: Dict[str, Any] = {}

    if varga_code != "D1":
        if "graha" in include:
            results["graha_drishti"] = {}
        if "rashi" in include:
            results["rashi_drishti"] = {}
        return results

    if "graha" in include:
        results["graha_drishti"] = _build_graha_drishti_block(context) or {}
    if "rashi" in include:
        results["rashi_drishti"] = _build_rashi_drishti_block() or {}
    return results


def _build_graha_drishti_block(context: Dict[str, Any]) -> Optional[Dict[str, List[Dict[str, Any]]]]:
    raw_positions = _get_d1_positions(context)
    if not raw_positions:
        return None

    house_to_planet = utils.get_house_planet_list_from_planet_positions(raw_positions)
    planet_to_house = utils.get_planet_house_dictionary_from_planet_positions(raw_positions)
    _, _, app = house.graha_drishti_from_chart(house_to_planet)
    planet_names = getattr(utils, "PLANET_NAMES", _DEFAULT_PLANET_NAMES)

    graha_block: Dict[str, List[Dict[str, Any]]] = {}
    for source_idx, targets in app.items():
        if source_idx >= len(planet_names):
            continue
        source_name = planet_names[source_idx]
        entries: List[Dict[str, Any]] = []
        source_house = planet_to_house.get(source_idx)
        if source_house is None:
            continue
        for target_idx in sorted(set(targets)):
            if target_idx >= len(planet_names):
                continue
            target_house = planet_to_house.get(target_idx)
            if target_house is None:
                continue
            distance = ((target_house - source_house) % 12) + 1
            strength = 1.0
            entries.append(
                {
                    "target": planet_names[target_idx],
                    "house_distance": distance,
                    "strength": strength,
                }
            )
        entries.sort(key=lambda item: (item["target"], item["house_distance"]))
        graha_block[source_name] = entries

    return graha_block


def _build_rashi_drishti_block() -> Dict[str, List[str]]:
    try:
        rashi_map = house._get_raasi_drishti()  # type: ignore[attr-defined]
    except AttributeError:
        rashi_map = _fallback_rashi_drishti()

    block: Dict[str, List[str]] = {}
    for sign_idx, targets in rashi_map.items():
        sign_name = _CANONICAL_SIGNS[int(sign_idx) % 12]
        block[sign_name] = [_CANONICAL_SIGNS[int(t) % 12] for t in targets]
    return block


def _fallback_rashi_drishti() -> Dict[int, List[int]]:
    mapping: Dict[int, List[int]] = {}
    for sign in const.movable_signs:
        mapping[sign] = [fs for fs in const.fixed_signs if fs != (sign + 1) % 12 and fs != (sign - 1) % 12]
    for sign in const.fixed_signs:
        mapping[sign] = [ms for ms in const.movable_signs if ms != (sign + 1) % 12 and ms != (sign - 1) % 12]
    for sign in const.dual_signs:
        mapping[sign] = [du for du in const.dual_signs if du != sign]
    return mapping


def _get_d1_positions(context: Dict[str, Any]) -> Optional[List]:
    vargas = context.get("vargas") or {}
    d1 = vargas.get("D1")
    if not d1:
        return None
    return d1.get("raw_positions")
