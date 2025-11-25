from __future__ import annotations

from typing import Any, Dict, List, Optional

from jhora.horoscope.chart import ashtakavarga, charts
from jhora import utils

from .common import resolve_context_components

_DEFAULT_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def _resolve_positions(context: Dict[str, Any]) -> List:
    raw_positions = context.get("rasi_raw_positions")
    if raw_positions:
        return raw_positions
    bc, place, ayanamsa_mode = resolve_context_components(context)
    return charts.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    planet_positions = _resolve_positions(context)
    house_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)
    bav, sav, _ = ashtakavarga.get_ashtaka_varga(house_planet_list)
    planet_names = getattr(utils, "PLANET_NAMES", _DEFAULT_PLANET_NAMES)
    bav_labels = [planet_names[i] for i in range(7)] + ["Lagna"]
    bav_map = {label: values for label, values in zip(bav_labels, bav)}
    return {
        "ashtakavarga": {
            "binna_ashtakavarga": bav_map,
            "samudaya_ashtakavarga": sav,
        }
    }
