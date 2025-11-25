from __future__ import annotations

from typing import Any, Dict, Tuple

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from .common import resolve_context_components, resolve_dob_tob

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_RULE_LABELS = (
    "harsha_house",
    "dignity_or_own",
    "gender_house",
    "gender_daylight",
)


def _is_daytime(
    dob_tuple: Tuple[int, int, int],
    tob_tuple: Tuple[int, int, float],
    place: drik.Place,
) -> Tuple[bool, float, float]:
    jd = utils.julian_day_number(dob_tuple, tob_tuple)
    sunrise = drik.sunrise(jd, place)[0]
    sunset = drik.sunset(jd, place)[0]
    fh = utils.from_dms(tob_tuple[0], tob_tuple[1], tob_tuple[2])
    is_day = sunrise <= fh <= sunset
    return is_day, sunrise, sunset


def compute(context: Dict[str, Any]) -> Dict[str, Any]:
    bc, place, ayanamsa_mode = resolve_context_components(context)
    dob_tuple, tob_tuple = resolve_dob_tob(context)
    is_daytime, sunrise, sunset = _is_daytime(dob_tuple, tob_tuple, place)
    jd = utils.julian_day_number(dob_tuple, tob_tuple)
    planet_positions = charts.divisional_chart(
        jd,
        place,
        ayanamsa_mode=ayanamsa_mode,
        divisional_chart_factor=1,
    )
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    asc_house = p_to_h[const._ascendant_symbol]

    payload: Dict[str, Any] = {}
    for planet_idx, name in enumerate(_PLANET_NAMES):
        h_p = p_to_h.get(planet_idx)
        if h_p is None:
            continue
        house_from_lagna = (h_p - asc_house) % 12
        rule_scores = {
            "harsha_house": 5.0
            if const.harsha_bala_houses[planet_idx] == house_from_lagna
            else 0.0,
            "dignity_or_own": 5.0
            if const.house_strengths_of_planets[planet_idx][h_p] > const._FRIEND
            or h_p in const.house_lords_dict[planet_idx]
            else 0.0,
            "gender_house": _gender_house_score(planet_idx, house_from_lagna),
            "gender_daylight": _gender_daylight_score(planet_idx, is_daytime),
        }
        total = round(sum(rule_scores.values()), 2)
        payload[name] = {
            "total": total,
            "max": 20.0,
            "components": rule_scores,
            "house_index": int(h_p),
            "house_from_lagna": int(house_from_lagna + 1),
        }

    payload["_meta"] = {
        "sunrise_hours": round(sunrise, 4),
        "sunset_hours": round(sunset, 4),
        "is_daytime": is_daytime,
        "jd": bc.jd_local,
    }
    return {"harsha_bala": payload}


def _gender_house_score(planet_idx: int, house_from_lagna: int) -> float:
    if planet_idx in const.feminine_planets:
        return (
            5.0 if house_from_lagna in const.harsha_bala_feminine_houses else 0.0
        )
    if planet_idx in const.masculine_planets:
        return (
            5.0 if house_from_lagna in const.harsha_bala_masculine_houses else 0.0
        )
    return 0.0


def _gender_daylight_score(planet_idx: int, is_daytime: bool) -> float:
    if is_daytime and planet_idx in const.masculine_planets:
        return 5.0
    if not is_daytime and planet_idx in const.feminine_planets:
        return 5.0
    return 0.0
