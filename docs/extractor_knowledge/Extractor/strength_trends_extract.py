from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jhora import utils

STRENGTH_TRENDS_SCHEMA_VERSION = "strength_trends.v1"
ENGINE_NAME = "PYJHORA_STRENGTH_TRENDS"

_SIGN_NAMES = getattr(utils, "RAASI_LIST", [
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
])


@dataclass
class StrengthTrendsConfig:
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "StrengthTrendsConfig":
        if not data:
            return cls()
        return cls(enabled=bool(data.get("enabled", True)))


def compute_strength_trends_from_payload(
    full_payload: Dict[str, Any],
    config: Optional[StrengthTrendsConfig] = None,
) -> Dict[str, Any]:
    cfg = config or StrengthTrendsConfig()
    strength_block = full_payload.get("strength") or {}
    shadbala = strength_block.get("shadbala") or {}

    planet_ranking = _build_planet_ranking(shadbala)
    ashtakavarga = full_payload.get("ashtakavarga") or {}
    sign_ranking = _build_sign_ranking(ashtakavarga.get("samudaya_ashtakavarga"))

    meta_basis: List[str] = []
    if planet_ranking:
        meta_basis.append("shadbala")
    if sign_ranking:
        meta_basis.append("ashtakavarga")

    return {
        "schema_version": STRENGTH_TRENDS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "planet_ranking": planet_ranking,
        "sign_ranking": sign_ranking,
        "meta": {
            "basis": meta_basis,
            "planet_basis": "total_rupa",
            "sign_basis": "SAV",
            "chart_id": "D1",
        },
    }


def _build_planet_ranking(shadbala: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for planet, payload in shadbala.items():
        score = payload.get("total_rupa")
        if score is None:
            continue
        try:
            score_value = float(score)
        except (TypeError, ValueError):
            continue
        entries.append(
            {
                "planet": planet,
                "score": round(score_value, 6),
                "source": "shadbala_total_rupa",
            }
        )
    entries.sort(key=lambda item: item["score"], reverse=True)
    return entries


def _build_sign_ranking(sav: Optional[List[float]]) -> List[Dict[str, Any]]:
    if not sav:
        return []
    entries: List[Dict[str, Any]] = []
    for idx, value in enumerate(sav):
        try:
            score = float(value)
        except (TypeError, ValueError):
            continue
        sign_name = _SIGN_NAMES[idx % len(_SIGN_NAMES)]
        entries.append(
            {
                "sign": sign_name,
                "score": round(score, 6),
                "source": "ashtakavarga_sav",
            }
        )
    entries.sort(key=lambda item: item["score"], reverse=True)
    return entries


__all__ = [
    "StrengthTrendsConfig",
    "compute_strength_trends_from_payload",
    "STRENGTH_TRENDS_SCHEMA_VERSION",
]
