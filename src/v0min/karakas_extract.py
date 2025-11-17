from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import house, charts as charts_mod

from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

KARAKAS_SCHEMA_VERSION = "karakas.v1"
ENGINE_NAME = "PYJHORA_KARAKAS"

_PLANET_FALLBACK = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

_STHIRA_KARAKAS = [
    ("Atma", "Sun"),
    ("Mana", "Moon"),
    ("Bhratri", "Mars"),
    ("Vach", "Mercury"),
    ("Putra", "Jupiter"),
    ("Dara", "Venus"),
    ("Jeeva", "Saturn"),
]

_ROLE_ABBREVIATIONS = {
    "atma_karaka": "AK",
    "amatya_karaka": "AmK",
    "bhratri_karaka": "BK",
    "maitri_karaka": "MK",
    "pitri_karaka": "PiK",
    "putra_karaka": "PK",
    "jnaati_karaka": "GK",
    "data_karaka": "DK",
}


@dataclass
class KarakasConfig:
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "KarakasConfig":
        if not data:
            return cls()
        return cls(enabled=bool(data.get("enabled", True)))


def compute_karakas_from_payload(full_payload: Dict[str, Any], config: Optional[KarakasConfig] = None) -> Dict[str, Any]:
    bc, place = build_birth_context_from_payload(full_payload)
    ayanamsa_mode = (full_payload.get("core_chart", {}) or {}).get("ayanamsa_mode", "LAHIRI")

    planet_positions = get_chart_positions(full_payload, "D1")
    if not planet_positions:
        planet_positions = charts_mod.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)

    planet_names = _get_planet_names()
    chara_entries: List[Dict[str, str]] = []
    chara_planets = house.chara_karakas(planet_positions)
    for idx, planet_idx in enumerate(chara_planets):
        role_id = const.chara_karaka_names[idx] if idx < len(const.chara_karaka_names) else f"karaka_{idx+1}"
        chara_entries.append(
            {
                "role": _abbreviate_role(role_id),
                "planet": _resolve_planet_name(planet_idx, planet_names),
            }
        )

    sthira_entries = [
        {
            "role": role,
            "planet": planet,
        }
        for role, planet in _STHIRA_KARAKAS
    ]

    return {
        "schema_version": KARAKAS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "chara": chara_entries,
        "sthira": sthira_entries,
        "meta": {
            "ayanamsa_mode": ayanamsa_mode,
            "source": "PYJHORA_HOUSE",
        },
    }


def _get_planet_names() -> List[str]:
    names = getattr(utils, "PLANET_NAMES", None)
    if not names:
        names = list(_PLANET_FALLBACK)
    return names


def _resolve_planet_name(planet_idx: int, planet_names: List[str]) -> str:
    if 0 <= planet_idx < len(_PLANET_FALLBACK):
        return _PLANET_FALLBACK[planet_idx]
    if 0 <= planet_idx < len(planet_names):
        return planet_names[planet_idx]
    return str(planet_idx)


def _abbreviate_role(role_id: str) -> str:
    if role_id in _ROLE_ABBREVIATIONS:
        return _ROLE_ABBREVIATIONS[role_id]
    parts = [segment for segment in role_id.split("_") if segment]
    if not parts:
        return role_id.upper()
    return "".join(part[0].upper() for part in parts)


__all__ = ["KarakasConfig", "compute_karakas_from_payload", "KARAKAS_SCHEMA_VERSION"]
