from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from jhora import utils
from jhora.horoscope.chart import charts, strength
from jhora.panchanga import drik

from .common import resolve_context_components

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    bc, place, ayanamsa_mode = resolve_context_components(context)
    jd = bc.jd_local
    bala_values = strength._yuddha_bala(jd, place)
    battles = _build_battles(bc.jd_local, place, ayanamsa_mode, bala_values)
    return {"graha_yuddha": battles}


def _build_battles(
    jd: float,
    place: drik.Place,
    ayanamsa_mode: str,
    bala_values: Tuple[float, ...],
) -> Dict[str, Any]:
    winner_idx = next((idx for idx, val in enumerate(bala_values) if val > 0), None)
    loser_idx = next((idx for idx, val in enumerate(bala_values) if val < 0), None)
    if winner_idx is None or loser_idx is None:
        return {}

    longitudes = _planet_longitudes(jd, place, ayanamsa_mode)
    degree_diff = round(abs(longitudes[winner_idx] - longitudes[loser_idx]), 4)
    winner = _PLANET_NAMES[winner_idx]
    loser = _PLANET_NAMES[loser_idx]
    key = f"{winner}_vs_{loser}"

    return {
        key: {
            "winner": winner,
            "loser": loser,
            "winner_score": round(bala_values[winner_idx], 4),
            "loser_score": round(bala_values[loser_idx], 4),
            "degree_diff": degree_diff,
            "notes": f"{winner} wins the planetary war against {loser}.",
        }
    }


def _planet_longitudes(
    jd: float,
    place: drik.Place,
    ayanamsa_mode: str,
) -> Dict[int, float]:
    positions = charts.rasi_chart(jd, place, ayanamsa_mode=ayanamsa_mode)
    longs: Dict[int, float] = {}
    for entry in positions[1 : len(_PLANET_NAMES) + 1]:
        planet_idx, (sign_idx, degrees_in_sign) = entry
        longs[int(planet_idx)] = sign_idx * 30.0 + degrees_in_sign
    return longs
