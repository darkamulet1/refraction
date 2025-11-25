from __future__ import annotations

from typing import Any, Dict

from jhora.horoscope.chart import strength
from jhora.panchanga import drik

from v0min.core_time import BirthContext

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_NODE_NAMES = ["Rahu", "Ketu"]


def _resolve_place(context: Dict[str, Any]) -> drik.Place:
    place = context.get("place")
    if place is not None:
        return place
    bc: BirthContext = context["birth_context"]
    label = context.get("location_name") or bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    bc: BirthContext = context["birth_context"]
    place = _resolve_place(context)
    dvb_raw = strength.dwadhasa_vargeeya_bala(bc.jd_local, place)

    dvb_map: Dict[str, Any] = {}
    for idx, name in enumerate(_PLANET_NAMES):
        dvb_map[name] = dvb_raw.get(idx, 0)
    for node in _NODE_NAMES:
        dvb_map[node] = None

    return {"dwadhasa_vargeeya_bala": dvb_map}
