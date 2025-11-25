"""
Refraction Engine V1 - Central Graha/Rasi/Nakshatra Mappings
=============================================================

Single source of truth for all astrological entity mappings.
All extractors MUST import from this module instead of maintaining separate mappings.

Design Philosophy:
- Type-safe enums for compile-time checks
- Bidirectional mappings (ID ? name, index ? name)
- PyJHora compatibility layer
- JSON-loadable for CorePrimitives.json validation
"""

from enum import IntEnum
from typing import Dict, Optional, List, Tuple, Any
import json
import re
from pathlib import Path

from jhora import const

CORE_PRIMITIVES_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "pyjhora_knowledge"
    / "primitives"
    / "CorePrimitives.json"
)

_PLANET_TUPLE_PATTERN = re.compile(r"\(?\s*(-?\d+)\s*,\s*(-?\d+)\s*\)?")

# ============================================================================
# SECTION 1: GRAHA (PLANETS)
# ============================================================================

class GrahaID(IntEnum):
    SUN = 0
    MOON = 1
    MARS = 2
    MERCURY = 3
    JUPITER = 4
    VENUS = 5
    SATURN = 6
    RAHU = 7
    KETU = 8

GRAHA_STRING_IDS: Dict[GrahaID, str] = {
    GrahaID.SUN: "SUN",
    GrahaID.MOON: "MOON",
    GrahaID.MARS: "MARS",
    GrahaID.MERCURY: "MERCURY",
    GrahaID.JUPITER: "JUPITER",
    GrahaID.VENUS: "VENUS",
    GrahaID.SATURN: "SATURN",
    GrahaID.RAHU: "RAHU",
    GrahaID.KETU: "KETU",
}

GRAHA_NAMES: Dict[GrahaID, str] = {
    GrahaID.SUN: "Sun",
    GrahaID.MOON: "Moon",
    GrahaID.MARS: "Mars",
    GrahaID.MERCURY: "Mercury",
    GrahaID.JUPITER: "Jupiter",
    GrahaID.VENUS: "Venus",
    GrahaID.SATURN: "Saturn",
    GrahaID.RAHU: "Rahu",
    GrahaID.KETU: "Ketu",
}

CONST_TO_GRAHA_ID: Dict[int, GrahaID] = {
    const._SUN: GrahaID.SUN,
    const._MOON: GrahaID.MOON,
    const._MARS: GrahaID.MARS,
    const._MERCURY: GrahaID.MERCURY,
    const._JUPITER: GrahaID.JUPITER,
    const._VENUS: GrahaID.VENUS,
    const._SATURN: GrahaID.SATURN,
    const._RAHU: GrahaID.RAHU,
    const._KETU: GrahaID.KETU,
}

GRAHA_ORDER: List[GrahaID] = [
    GrahaID.SUN,
    GrahaID.MOON,
    GrahaID.MERCURY,
    GrahaID.VENUS,
    GrahaID.MARS,
    GrahaID.JUPITER,
    GrahaID.SATURN,
    GrahaID.RAHU,
    GrahaID.KETU,
]

_GRAHA_STRING_TO_ID: Dict[str, GrahaID] = {v: k for k, v in GRAHA_STRING_IDS.items()}
_GRAHA_NAME_TO_ID: Dict[str, GrahaID] = {v: k for k, v in GRAHA_NAMES.items()}


def graha_id_to_string(graha_id: GrahaID) -> str:
    return GRAHA_STRING_IDS[graha_id]


def graha_id_to_name(graha_id: GrahaID) -> str:
    return GRAHA_NAMES[graha_id]


def graha_string_to_id(graha_string: str) -> Optional[GrahaID]:
    return _GRAHA_STRING_TO_ID.get(graha_string.upper())


def graha_name_to_id(graha_name: str) -> Optional[GrahaID]:
    return _GRAHA_NAME_TO_ID.get(graha_name)


def graha_const_to_id(graha_const: int) -> Optional[GrahaID]:
    return CONST_TO_GRAHA_ID.get(graha_const)


def graha_const_to_string(graha_const: int) -> Optional[str]:
    graha = graha_const_to_id(graha_const)
    return graha_id_to_string(graha) if graha is not None else None

# ============================================================================
# SECTION 2: RASI (SIGNS)
# ============================================================================

class RasiID(IntEnum):
    ARIES = 1
    TAURUS = 2
    GEMINI = 3
    CANCER = 4
    LEO = 5
    VIRGO = 6
    LIBRA = 7
    SCORPIO = 8
    SAGITTARIUS = 9
    CAPRICORN = 10
    AQUARIUS = 11
    PISCES = 12

RASI_NAMES: Dict[RasiID, str] = {
    RasiID.ARIES: "ARIES",
    RasiID.TAURUS: "TAURUS",
    RasiID.GEMINI: "GEMINI",
    RasiID.CANCER: "CANCER",
    RasiID.LEO: "LEO",
    RasiID.VIRGO: "VIRGO",
    RasiID.LIBRA: "LIBRA",
    RasiID.SCORPIO: "SCORPIO",
    RasiID.SAGITTARIUS: "SAGITTARIUS",
    RasiID.CAPRICORN: "CAPRICORN",
    RasiID.AQUARIUS: "AQUARIUS",
    RasiID.PISCES: "PISCES",
}

_RASI_NAME_TO_ID: Dict[str, RasiID] = {v: k for k, v in RASI_NAMES.items()}


def rasi_index_to_name(rasi_index: int) -> str:
    return RASI_NAMES[RasiID(rasi_index)]


def rasi_name_to_index(rasi_name: str) -> Optional[int]:
    rasi_id = _RASI_NAME_TO_ID.get(rasi_name.upper())
    return int(rasi_id) if rasi_id else None


def rasi_index_from_longitude(longitude_deg: float) -> int:
    return int(longitude_deg // 30) + 1


def degree_in_rasi(longitude_deg: float) -> float:
    return longitude_deg % 30.0

# ============================================================================
# SECTION 3: NAKSHATRA
# ============================================================================

class NakshatraID(IntEnum):
    ASHWINI = 1
    BHARANI = 2
    KARTHIGAI = 3
    ROHINI = 4
    MRIGASIRA = 5
    THIRUVATHIRAI = 6
    PUNARPOOSAM = 7
    POOSAM = 8
    AYILYAM = 9
    MAGAM = 10
    POORAM = 11
    UTHIRAM = 12
    HASTHAM = 13
    CHITHIRAI = 14
    SWAATHI = 15
    VISAKAM = 16
    ANUSHAM = 17
    KETTAI = 18
    MOOLAM = 19
    POORAADAM = 20
    UTHIRAADAM = 21
    THIRUVONAM = 22
    AVITTAM = 23
    SADAYAM = 24
    POORATTATHI = 25
    UTHIRATTATHI = 26
    REVATHI = 27

_NAKSHATRA_NAME_LIST = [
    "ASHWINI",
    "BHARANI",
    "KARTHIGAI",
    "ROHINI",
    "MRIGASIRA",
    "THIRUVATHIRAI",
    "PUNARPOOSAM",
    "POOSAM",
    "AYILYAM",
    "MAGAM",
    "POORAM",
    "UTHIRAM",
    "HASTHAM",
    "CHITHIRAI",
    "SWAATHI",
    "VISAKAM",
    "ANUSHAM",
    "KETTAI",
    "MOOLAM",
    "POORAADAM",
    "UTHIRAADAM",
    "THIRUVONAM",
    "AVITTAM",
    "SADAYAM",
    "POORATTATHI",
    "UTHIRATTATHI",
    "REVATHI",
]

NAKSHATRA_NAMES: Dict[NakshatraID, str] = {
    nakshatra: _NAKSHATRA_NAME_LIST[index]
    for index, nakshatra in enumerate(NakshatraID)
}

_NAKSHATRA_NAME_TO_ID: Dict[str, NakshatraID] = {
    name: nakshatra for nakshatra, name in NAKSHATRA_NAMES.items()
}

NAKSHATRA_LORDS: Dict[NakshatraID, str] = {
    NakshatraID.ASHWINI: "Ketu",
    NakshatraID.BHARANI: "Venus",
    NakshatraID.KARTHIGAI: "Sun",
    NakshatraID.ROHINI: "Moon",
    NakshatraID.MRIGASIRA: "Mars",
    NakshatraID.THIRUVATHIRAI: "Rahu",
    NakshatraID.PUNARPOOSAM: "Jupiter",
    NakshatraID.POOSAM: "Saturn",
    NakshatraID.AYILYAM: "Mercury",
    NakshatraID.MAGAM: "Ketu",
    NakshatraID.POORAM: "Venus",
    NakshatraID.UTHIRAM: "Sun",
    NakshatraID.HASTHAM: "Moon",
    NakshatraID.CHITHIRAI: "Mars",
    NakshatraID.SWAATHI: "Rahu",
    NakshatraID.VISAKAM: "Jupiter",
    NakshatraID.ANUSHAM: "Saturn",
    NakshatraID.KETTAI: "Mercury",
    NakshatraID.MOOLAM: "Ketu",
    NakshatraID.POORAADAM: "Venus",
    NakshatraID.UTHIRAADAM: "Sun",
    NakshatraID.THIRUVONAM: "Moon",
    NakshatraID.AVITTAM: "Mars",
    NakshatraID.SADAYAM: "Rahu",
    NakshatraID.POORATTATHI: "Jupiter",
    NakshatraID.UTHIRATTATHI: "Saturn",
    NakshatraID.REVATHI: "Mercury",
}


def nakshatra_index_to_name(nakshatra_index: int) -> str:
    return NAKSHATRA_NAMES[NakshatraID(nakshatra_index)]


def nakshatra_name_to_index(nakshatra_name: str) -> Optional[int]:
    nak_id = _NAKSHATRA_NAME_TO_ID.get(nakshatra_name.upper())
    return int(nak_id) if nak_id else None


_NAKSHATRA_DIVISION = 360.0 / 27

def nakshatra_from_longitude(longitude_deg: float) -> Tuple[int, int, float]:
    normalized_longitude = longitude_deg % 360.0
    nakshatra_index = int(normalized_longitude // _NAKSHATRA_DIVISION) + 1
    nakshatra_index = min(max(nakshatra_index, 1), 27)
    start_deg = (nakshatra_index - 1) * _NAKSHATRA_DIVISION
    span_deg = normalized_longitude - start_deg
    span_deg = max(span_deg, 0.0)
    pada_span = _NAKSHATRA_DIVISION / 4
    pada = int(span_deg // pada_span) + 1
    pada = min(max(pada, 1), 4)
    return nakshatra_index, pada, span_deg


def nakshatra_lord(nakshatra_index: int) -> str:
    return NAKSHATRA_LORDS[NakshatraID(nakshatra_index)]

# ============================================================================
# SECTION 4: VAARA (WEEKDAY)
# ============================================================================

class VaaraID(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

VAARA_NAMES: Dict[VaaraID, str] = {
    VaaraID.SUNDAY: "SUNDAY",
    VaaraID.MONDAY: "MONDAY",
    VaaraID.TUESDAY: "TUESDAY",
    VaaraID.WEDNESDAY: "WEDNESDAY",
    VaaraID.THURSDAY: "THURSDAY",
    VaaraID.FRIDAY: "FRIDAY",
    VaaraID.SATURDAY: "SATURDAY",
}


def vaara_index_to_name(vaara_index: int) -> str:
    return VAARA_NAMES[VaaraID(vaara_index)]

# ============================================================================ 
# VALIDATION
# ============================================================================


def _parse_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _normalize_planet_entry(entry: Any) -> Optional[Dict[str, int]]:
    if isinstance(entry, dict):
        if "const" in entry and "value" in entry:
            return {"const": int(entry["const"]), "value": int(entry["value"])}
        if len(entry) >= 2:
            items = list(entry.values())
            return {"const": int(items[0]), "value": int(items[1])}
    if isinstance(entry, (list, tuple)) and len(entry) >= 2:
        return {"const": int(entry[0]), "value": int(entry[1])}
    if isinstance(entry, str):
        match = _PLANET_TUPLE_PATTERN.match(entry)
        if match:
            return {"const": int(match.group(1)), "value": int(match.group(2))}
    return None

def validate_against_core_primitives(core_primitives_path: Optional[Path] = None) -> Dict[str, bool]:
    if core_primitives_path is None:
        core_primitives_path = CORE_PRIMITIVES_PATH
    if not core_primitives_path.exists():
        return {"error": "CorePrimitives.json not found"}
    try:
        with open(core_primitives_path, "r", encoding="utf-8") as f:
            core_prims = json.load(f)
    except Exception as exc:
        return {"error": f"Failed to load CorePrimitives.json: {exc}"}
    results = {}
    try:
        if isinstance(core_prims, dict):
            english = core_prims.get("languages", {}).get("en", {})
            planet_names = english.get("PLANET_NAMES", [])
            rasi_names = english.get("RAASI_LIST", [])
            nakshatra_names = english.get("NAKSHATRA_LIST", [])
            normalized_planets = [entry for entry in (_normalize_planet_entry(item) for item in planet_names) if entry]
            normalized_rasis = [num for num in (_parse_int(item) for item in rasi_names) if num is not None]
            results["grahas"] = len(normalized_planets) >= len(GRAHA_ORDER)
            results["rasis"] = len(normalized_rasis) >= len(RasiID)
            if nakshatra_names:
                results["nakshatras"] = len(nakshatra_names) >= len(NakshatraID)
    except Exception as exc:
        return {"error": f"Validation failed: {exc}"}
    if not results:
        return {"error": "CorePrimitives structure unsupported"}
    return results

__all__ = [
    "GrahaID",
    "GRAHA_STRING_IDS",
    "GRAHA_NAMES",
    "GRAHA_ORDER",
    "graha_id_to_string",
    "graha_id_to_name",
    "graha_string_to_id",
    "graha_name_to_id",
    "CONST_TO_GRAHA_ID",
    "graha_const_to_id",
    "graha_const_to_string",
    "RasiID",
    "RASI_NAMES",
    "rasi_index_to_name",
    "rasi_name_to_index",
    "rasi_index_from_longitude",
    "degree_in_rasi",
    "NakshatraID",
    "NAKSHATRA_NAMES",
    "NAKSHATRA_LORDS",
    "nakshatra_index_to_name",
    "nakshatra_name_to_index",
    "nakshatra_from_longitude",
    "nakshatra_lord",
    "VaaraID",
    "VAARA_NAMES",
    "vaara_index_to_name",
    "validate_against_core_primitives",
]
