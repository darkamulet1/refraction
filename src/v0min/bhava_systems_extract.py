from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Union

from jhora import const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

BHAVA_SYSTEMS_SCHEMA_VERSION = "bhava_systems.v1"


@dataclass
class BhavaSystemsConfig:
    enabled: bool = True
    methods: Optional[List[Union[str, int]]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "BhavaSystemsConfig":
        if not data:
            return cls()
        return cls(
            enabled=bool(data.get("enabled", True)),
            methods=list(data.get("methods", []) or []),
        )


def compute_bhava_systems_from_payload(full_payload: Dict[str, Any], config: BhavaSystemsConfig) -> Dict[str, Any]:
    bc, place = build_birth_context_from_payload(full_payload)
    ayanamsa_mode = (full_payload.get("core_chart", {}) or {}).get("ayanamsa_mode", "LAHIRI")
    planet_positions = get_chart_positions(full_payload, "D1")
    if not planet_positions:
        planet_positions = charts.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)

    method_codes = _resolve_requested_methods(config.methods)
    systems: List[Dict[str, Any]] = []
    for code in method_codes:
        houses = _compute_houses_for_method(code, bc.jd_local, place, planet_positions)
        systems.append(
            {
                "method_code": str(code),
                "method": const.available_house_systems.get(code, str(code)),
                "houses": houses,
            }
        )

    return {
        "schema_version": BHAVA_SYSTEMS_SCHEMA_VERSION,
        "ayanamsa_mode": ayanamsa_mode,
        "methods": systems,
    }


def _resolve_requested_methods(methods: Iterable[Union[str, int, None]]) -> List[Any]:
    available = list(const.available_house_systems.keys())
    if not methods:
        return available
    resolved: List[Any] = []
    for token in methods:
        code = _resolve_single_method(token)
        if code is not None and code in const.available_house_systems:
            resolved.append(code)
    if not resolved:
        return available
    return resolved


def _resolve_single_method(token: Union[str, int, None]) -> Any:
    if token is None:
        return None
    if isinstance(token, int):
        return token
    token_str = str(token).strip()
    if not token_str:
        return None
    if token_str.isdigit():
        return int(token_str)
    # Match against codes
    for key in const.available_house_systems.keys():
        if isinstance(key, str) and key.upper() == token_str.upper():
            return key
        if str(key).upper() == token_str.upper():
            return key
        label = const.available_house_systems[key]
        if label.lower() == token_str.lower():
            return key
    return None


def _compute_houses_for_method(method_code: Any, jd: float, place: drik.Place, planet_positions: List) -> List[Dict[str, float]]:
    if method_code == 1:
        return _compute_equal_lagna_middle(planet_positions)
    if method_code == 2:
        return _compute_equal_lagna_start(planet_positions)
    if method_code == 3:
        return _compute_sripati(jd, place)
    if method_code == 4:
        return _compute_kp(jd, place)
    if method_code == 5:
        return _compute_rasi_houses(planet_positions)
    if method_code in const.western_house_systems:
        return _compute_western_system(jd, place, method_code)
    # Fallback to KP-style
    return _compute_kp(jd, place)


def _compute_equal_lagna_middle(planet_positions: List) -> List[Dict[str, float]]:
    asc_sign, asc_deg = planet_positions[0][1]
    asc_long = (asc_sign * 30.0 + asc_deg) % 360.0
    houses: List[Dict[str, float]] = []
    mid = asc_long
    for idx in range(12):
        start = _norm(mid - 15.0)
        end = _norm(mid + 15.0)
        houses.append(_house_entry(idx + 1, start, mid, end))
        mid = _norm(mid + 30.0)
    return houses


def _compute_equal_lagna_start(planet_positions: List) -> List[Dict[str, float]]:
    asc_sign, asc_deg = planet_positions[0][1]
    start = (asc_sign * 30.0 + asc_deg) % 360.0
    houses: List[Dict[str, float]] = []
    current_start = start
    for idx in range(12):
        mid = _norm(current_start + 15.0)
        end = _norm(current_start + 30.0)
        houses.append(_house_entry(idx + 1, current_start, mid, end))
        current_start = end
    return houses


def _compute_rasi_houses(planet_positions: List) -> List[Dict[str, float]]:
    asc_sign, asc_deg = planet_positions[0][1]
    houses: List[Dict[str, float]] = []
    for idx in range(12):
        sign = (asc_sign + idx) % 12
        start = sign * 30.0
        end = ((sign + 1) % 12) * 30.0
        mid = _norm(start + asc_deg)
        houses.append(_house_entry(idx + 1, start, mid, end))
    return houses


def _compute_sripati(jd: float, place: drik.Place) -> List[Dict[str, float]]:
    cusps = list(drik.bhaava_madhya_sripathi(jd, place))
    return _houses_from_cusps(cusps)


def _compute_kp(jd: float, place: drik.Place) -> List[Dict[str, float]]:
    cusps = list(drik.bhaava_madhya_kp(jd, place))
    return _houses_from_cusps(cusps)


def _compute_western_system(jd: float, place: drik.Place, code: str) -> List[Dict[str, float]]:
    cusps = list(drik.bhaava_madhya_swe(jd, place, house_code=code))
    return _houses_from_cusps(cusps)


def _houses_from_cusps(cusps: List[float]) -> List[Dict[str, float]]:
    if not cusps:
        return []
    normalized = [c % 360.0 for c in cusps]
    normalized.append(normalized[0] + 360.0)
    houses: List[Dict[str, float]] = []
    for idx in range(12):
        start = normalized[idx]
        end = normalized[idx + 1]
        mid = 0.5 * (start + end)
        houses.append(_house_entry(idx + 1, start, mid, end))
    return houses


def _house_entry(index: int, start: float, mid: float, end: float) -> Dict[str, float]:
    return {
        "house": index,
        "start_deg": _norm(start),
        "cusp_deg": _norm(mid),
        "end_deg": _norm(end),
    }


def _norm(value: float) -> float:
    return value % 360.0


__all__ = [
    "BhavaSystemsConfig",
    "BHAVA_SYSTEMS_SCHEMA_VERSION",
    "compute_bhava_systems_from_payload",
]
