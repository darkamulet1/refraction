from __future__ import annotations

from collections import OrderedDict
from typing import Dict

from jhora import const
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min.core_time import BirthContext


# dhasavarga() yields bodies indexed 0..8 in this order.
PLANET_ORDER = [
    (0, "Sun"),
    (1, "Moon"),
    (2, "Mars"),
    (3, "Mercury"),
    (4, "Jupiter"),
    (5, "Venus"),
    (6, "Saturn"),
    (7, "Rahu"),
    (8, "Ketu"),
]


def _absolute_longitude(sign_index: float, longitude_in_sign: float) -> float:
    return (sign_index * 30.0 + longitude_in_sign) % 360.0


def compute_core_chart(
    bc: BirthContext,
    *,
    ayanamsa_mode: str | None = None,
    calculation_type: str = "drik",
) -> Dict[str, object]:
    """
    Run the legacy PyJHora rasi chart math for the supplied BirthContext.

    This keeps Swiss ephemeris configuration inside jhora.panchanga.drik /
    jhora.horoscope.chart.charts so v0min remains a thin coordination layer.
    """

    place_label = bc.location_name or "Birth Place"
    place = drik.Place(place_label, bc.latitude, bc.longitude, bc.utc_offset_hours)
    mode = (ayanamsa_mode or const._DEFAULT_AYANAMSA_MODE).upper()

    planet_positions = charts.rasi_chart(
        bc.jd_local,
        place,
        ayanamsa_mode=mode,
        calculation_type=calculation_type,
    )
    if not planet_positions or planet_positions[0][0] != const._ascendant_symbol:
        raise ValueError("Unexpected chart output: missing ascendant entry.")

    asc_sign, asc_long = planet_positions[0][1]
    lagna_longitude = _absolute_longitude(asc_sign, asc_long)

    position_lookup = {pid: data for pid, data in planet_positions[1:]}
    planets = OrderedDict()
    for pid, name in PLANET_ORDER:
        data = position_lookup.get(pid)
        if data is None:
            continue
        sign_index, longitude_in_sign = data
        planets[name] = _absolute_longitude(sign_index, longitude_in_sign)

    return {
        "ayanamsa_mode": mode,
        "lagna_longitude_deg": lagna_longitude,
        "planets": dict(planets),
    }


__all__ = ["compute_core_chart"]
