from __future__ import annotations

from typing import Any, Dict

from jhora.horoscope.chart import strength

from .common import resolve_context_components

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    bc, place, ayanamsa_mode = resolve_context_components(context)
    jd = bc.jd_local

    totals = strength._kaala_bala(jd, place, ayanamsa_mode=ayanamsa_mode)
    component_arrays = {
        "nathonnatha": strength._nathonnath_bala(jd, place),
        "paksha": strength._paksha_bala(jd, place, ayanamsa_mode=ayanamsa_mode),
        "tribhaga": strength._tribhaga_bala(jd, place),
        "abdadhipathi": strength._abdadhipathi(jd, place),
        "masadhipathi": strength._masadhipathi(jd, place),
        "vaaradhipathi": strength._vaaradhipathi(jd, place),
        "hora": strength._hora_bala(jd, place),
        "ayana": strength._ayana_bala(jd, place),
        "yuddha": strength._yuddha_bala(jd, place),
    }

    payload: Dict[str, Any] = {}
    for idx, name in enumerate(_PLANET_NAMES):
        payload[name] = {
            "total": round(totals[idx], 2),
            "components": {
                key: round(values[idx], 2) for key, values in component_arrays.items()
            },
        }

    payload["_meta"] = {
        "ayanamsa_mode": ayanamsa_mode,
    }
    return {"tatkalika_bala": payload}
