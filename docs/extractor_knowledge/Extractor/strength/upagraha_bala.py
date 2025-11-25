from __future__ import annotations

from typing import Any, Dict, List

from jhora import utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from .common import resolve_context_components, resolve_drik_date

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_PERSONAL_UPAGRAHAS = {
    "Kaala": drik.kaala_longitude,
    "Mrityu": drik.mrityu_longitude,
    "ArthaPraharaka": drik.artha_praharaka_longitude,
    "YamaGhantaka": drik.yama_ghantaka_longitude,
    "Gulika": drik.gulika_longitude,
    "Maandi": drik.maandi_longitude,
}
_SOLAR_UPAGRAHAS = ["dhuma", "vyatipaata", "parivesha", "indrachaapa", "upaketu"]
_DEFAULT_SIGN_NAMES = [
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
_SIGN_NAMES = getattr(utils, "RAASI_LIST", _DEFAULT_SIGN_NAMES)


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    bc, place, ayanamsa_mode = resolve_context_components(context)
    dob_date, tob = resolve_drik_date(context)
    positions = context.get("rasi_raw_positions")
    if not positions:
        positions = charts.rasi_chart(
            bc.jd_local,
            place,
            ayanamsa_mode=ayanamsa_mode,
        )

    planet_map = _planet_positions(positions)
    catalog = _build_upagraha_catalog(
        positions,
        dob_date,
        tob,
        place,
        ayanamsa_mode,
    )

    payload: Dict[str, Any] = {}
    for planet_idx, (sign_idx, degrees_in_sign) in planet_map.items():
        name = _PLANET_NAMES[planet_idx]
        planet_abs = sign_idx * 30.0 + degrees_in_sign
        matches = []
        for entry in catalog:
            if entry["sign_index"] != sign_idx:
                continue
            orb = abs(round(entry["absolute_deg"] - planet_abs, 4))
            matches.append(
                {
                    "name": entry["name"],
                    "orb_deg": orb,
                    "sign": entry["sign"],
                    "degree_in_sign": entry["degree_in_sign"],
                }
            )
        payload[name] = {
            "matches": matches,
            "summary": [m["name"] for m in matches],
        }

    payload["_catalog"] = catalog
    return {"upagraha_bala": payload}


def _planet_positions(positions: List) -> Dict[int, tuple]:
    planet_map: Dict[int, tuple] = {}
    for entry in positions[1 : len(_PLANET_NAMES) + 1]:
        planet_idx, (sign_idx, degrees_in_sign) = entry
        planet_map[int(planet_idx)] = (int(sign_idx), float(degrees_in_sign))
    return planet_map


def _build_upagraha_catalog(
    positions: List,
    dob_date: drik.Date,
    tob: tuple,
    place: drik.Place,
    ayanamsa_mode: str,
) -> List[Dict[str, Any]]:
    catalog: List[Dict[str, Any]] = []

    for name, func in _PERSONAL_UPAGRAHAS.items():
        sign_idx, degrees = func(
            dob_date,
            tob,
            place,
            ayanamsa_mode=ayanamsa_mode,
            divisional_chart_factor=1,
        )
        catalog.append(
            _format_entry(
                name,
                int(sign_idx),
                float(degrees),
            )
        )

    for key in _SOLAR_UPAGRAHAS:
        sign_idx, degrees = charts.solar_upagraha_longitudes(
            positions,
            key,
            divisional_chart_factor=1,
        )
        catalog.append(
            _format_entry(
                key.title(),
                int(sign_idx),
                float(degrees),
            )
        )

    return catalog


def _format_entry(name: str, sign_idx: int, degrees: float) -> Dict[str, Any]:
    absolute = sign_idx * 30.0 + degrees
    return {
        "name": name,
        "sign_index": sign_idx,
        "sign": _SIGN_NAMES[sign_idx],
        "degree_in_sign": round(degrees, 4),
        "absolute_deg": round(absolute, 4),
    }
