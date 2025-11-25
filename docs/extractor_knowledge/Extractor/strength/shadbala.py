from __future__ import annotations

from typing import Any, Dict

from jhora import const
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
    ayanamsa_mode = (context.get("ayanamsa_mode") or const._DEFAULT_AYANAMSA_MODE).upper()
    place = _resolve_place(context)

    (
        sthana,
        kaala,
        dig,
        cheshta,
        naisargika,
        drik_bala,
        sb_sum,
        sb_rupa,
        sb_ratio,
    ) = strength.shad_bala(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)

    payload: Dict[str, Any] = {}
    for idx, name in enumerate(_PLANET_NAMES):
        payload[name] = {
            "sthana": sthana[idx],
            "kaala": kaala[idx],
            "dig": dig[idx],
            "cheshta": cheshta[idx],
            "naisargika": naisargika[idx],
            "drik": drik_bala[idx],
            "sum_shastiamsa": sb_sum[idx],
            "total_rupa": sb_rupa[idx],
            "strength_ratio": sb_ratio[idx],
            "percent": round(sb_ratio[idx] * 100.0, 2),
        }

    for node in _NODE_NAMES:
        payload[node] = {
            "sthana": None,
            "kaala": None,
            "dig": None,
            "cheshta": None,
            "naisargika": None,
            "drik": None,
            "sum_shastiamsa": None,
            "total_rupa": None,
            "strength_ratio": None,
            "percent": None,
            "note": "Shadbala is not defined for nodes in PyJHora.",
        }

    return {"shadbala": payload}
