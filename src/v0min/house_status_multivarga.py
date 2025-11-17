from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Union

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min.core_time import BirthContext

HouseKey = Union[int, str]

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

HOUSE_SYSTEM_LABELS: Dict[HouseKey, str] = {
    1: "equal_mid",
    2: "equal_start",
    3: "sripati",
    4: "kp",
    5: "whole_sign",
    "P": "placidus",
    "K": "koch",
    "O": "porphyry",
    "R": "regiomontanus",
    "C": "campanus",
    "A": "equal_cusp",
    "V": "vehlow",
    "X": "axial",
    "H": "azimuthal",
    "T": "polich_page",
    "B": "alcabitus",
    "M": "morinus",
}

ALIAS_TO_KEY = {label: key for key, label in HOUSE_SYSTEM_LABELS.items()}

_SUPPORTED_ALL_VARGAS = {1, 2, 5}

_DEFAULT_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


def _resolve_place(context: Dict[str, Any]) -> drik.Place:
    place = context.get("place")
    if place is not None:
        return place
    bc = context.get("birth_context")
    if not isinstance(bc, BirthContext):
        raise ValueError("house_status context requires a BirthContext or explicit place.")
    label = bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def _normalize_systems(systems: Optional[Iterable[HouseKey]]) -> List[HouseKey]:
    if not systems:
        return list(HOUSE_SYSTEM_LABELS.keys())
    resolved: List[HouseKey] = []
    for key in systems:
        if key in HOUSE_SYSTEM_LABELS:
            resolved.append(key)
        elif key in ALIAS_TO_KEY:
            resolved.append(ALIAS_TO_KEY[key])
    return resolved


def compute_house_status_all_vargas(
    context: Dict[str, Any],
    systems: Optional[Iterable[HouseKey]] = None,
    include_unsupported: bool = False,
) -> Dict[str, Any]:
    """
    Build the house-state dictionary for every available varga chart.
    """

    bc = context.get("birth_context")
    if not isinstance(bc, BirthContext):
        raise ValueError("context must include a v0min.core_time.BirthContext under 'birth_context'")
    ayanamsa_mode = (context.get("ayanamsa_mode") or "LAHIRI").upper()
    place = _resolve_place(context)
    vargas = context.get("vargas") or {}
    systems_to_use = _normalize_systems(systems)

    results: Dict[str, Any] = {}
    for varga_code, chart in vargas.items():
        varga_result: Dict[str, Any] = {}
        for system_key in systems_to_use:
            label = HOUSE_SYSTEM_LABELS.get(system_key, str(system_key).lower())
            houses = compute_house_status_for_chart_and_system(
                chart,
                system_key,
                birth_context=bc,
                place=place,
                ayanamsa_mode=ayanamsa_mode,
                varga_code=varga_code,
            )
            if houses is None:
                if include_unsupported:
                    varga_result[label] = None
                continue
            varga_result[label] = houses
        if varga_result or include_unsupported:
            results[varga_code] = varga_result
    return results


def compute_house_status_for_chart_and_system(
    chart: Optional[Dict[str, Any]],
    house_system_key: HouseKey,
    *,
    birth_context: BirthContext,
    place: drik.Place,
    ayanamsa_mode: str,
    varga_code: str,
) -> Optional[Dict[str, Dict[str, Any]]]:
    """
    Compute house data for a specific chart/system combination.
    Returns None when the combination is unsupported.
    """

    if not chart:
        return None
    system_label = HOUSE_SYSTEM_LABELS.get(house_system_key)
    if system_label is None:
        return None

    lagna = chart.get("lagna") or {}
    sign_idx = lagna.get("sign_index")
    deg_in_sign = lagna.get("deg_in_sign")
    if sign_idx is None or deg_in_sign is None:
        return None

    if house_system_key in _SUPPORTED_ALL_VARGAS:
        houses = _compute_equal_house_system(int(sign_idx), float(deg_in_sign), house_system_key)
        return _spans_to_dict(houses, house_system_key, int(sign_idx), float(deg_in_sign))

    # Systems beyond equal/whole-sign are only exposed for the base D1 chart to avoid misleading results.
    if varga_code != "D1":
        return None

    try:
        bhava_chart = charts.bhava_chart(
            birth_context.jd_local,
            place,
            ayanamsa_mode=ayanamsa_mode,
            bhava_madhya_method=house_system_key,
        )
    except Exception:
        return None
    return _convert_engine_bhavas(bhava_chart)


def _compute_equal_house_system(sign_idx: int, deg_in_sign: float, key: HouseKey) -> List[tuple[float, float, float]]:
    asc_abs = (sign_idx * 30.0 + deg_in_sign) % 360.0
    spans: List[tuple[float, float, float]] = []
    for h in range(12):
        offset = h * 30.0
        if key == 1:  # Equal housing (lagna mid)
            mid = (asc_abs + offset) % 360.0
            start = (mid - 15.0) % 360.0
            end = (mid + 15.0) % 360.0
        elif key == 2:  # Equal housing (lagna start)
            start = (asc_abs + offset) % 360.0
            mid = (start + 15.0) % 360.0
            end = (start + 30.0) % 360.0
        else:  # Whole sign (each rasi is the house)
            base_sign = (sign_idx + h) % 12
            start = base_sign * 30.0
            mid = (start + deg_in_sign) % 360.0
            end = (start + 30.0) % 360.0
        spans.append((start, mid, end))
    return spans


def _spans_to_dict(
    spans: List[tuple[float, float, float]],
    system_key: HouseKey,
    asc_sign_idx: int,
    deg_in_sign: float,
) -> Dict[str, Dict[str, Any]]:
    houses: Dict[str, Dict[str, Any]] = {}
    for idx, (start, mid, end) in enumerate(spans, start=1):
        if system_key == 5:
            sign_index = (asc_sign_idx + idx - 1) % 12
        else:
            sign_index = int((mid % 360.0) // 30) % 12
        houses[str(idx)] = _make_house_entry(sign_index, start, mid, end)
    return houses


def _convert_engine_bhavas(bhava_chart: List[Any]) -> Dict[str, Dict[str, Any]]:
    houses: Dict[str, Dict[str, Any]] = {}
    for idx, entry in enumerate(bhava_chart, start=1):
        if not entry:
            continue
        sign_index = int(entry[0]) % 12
        start, mid, end = entry[1]
        houses[str(idx)] = _make_house_entry(sign_index, start, mid, end)
    return houses


def _make_house_entry(sign_idx: int, start: float, mid: float, end: float) -> Dict[str, Any]:
    start = start % 360.0
    mid = mid % 360.0
    end = end % 360.0
    lord_index = const._house_owners_list[sign_idx]
    names = getattr(utils, "PLANET_NAMES", _DEFAULT_PLANET_NAMES)
    if not names or len(names) <= int(lord_index):
        planet_name = _DEFAULT_PLANET_NAMES[int(lord_index)]
    else:
        planet_name = names[int(lord_index)]
    return {
        "sign": _CANONICAL_SIGNS[sign_idx],
        "sign_index": sign_idx,
        "lord": planet_name,
        "cusp_degree": round(mid, 6),
        "start_degree": round(start, 6),
        "end_degree": round(end, 6),
    }


__all__ = ["compute_house_status_all_vargas", "compute_house_status_for_chart_and_system"]
