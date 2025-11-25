from __future__ import annotations

from typing import Any, Dict, List, Tuple

from jhora import utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from .common import resolve_context_components, resolve_dob_tob

_PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
_PLANET_DAY_PREF = {
    "Sun": "day",
    "Moon": "night",
    "Mars": "day",
    "Mercury": "neutral",
    "Jupiter": "day",
    "Venus": "night",
    "Saturn": "night",
}
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
    dob_tuple, tob_tuple = resolve_dob_tob(context)
    is_daytime = _is_daytime(dob_tuple, tob_tuple, place)

    positions = context.get("rasi_raw_positions")
    if not positions:
        positions = charts.rasi_chart(
            bc.jd_local,
            place,
            ayanamsa_mode=ayanamsa_mode,
        )

    payload: Dict[str, Any] = {}
    for entry in positions[1 : len(_PLANET_NAMES) + 1]:
        planet_idx, (sign_idx, degrees_in_sign) = entry
        name = _PLANET_NAMES[int(planet_idx)]
        state, score, note = _classify_state(
            name,
            int(sign_idx),
            degrees_in_sign,
            is_daytime,
        )
        payload[name] = {
            "state": state,
            "raw_score": score,
            "sign": _SIGN_NAMES[int(sign_idx)],
            "sign_index": int(sign_idx),
            "degree_in_sign": round(degrees_in_sign, 4),
            "note": note,
        }

    payload["_meta"] = {"is_daytime": is_daytime}
    return {"avastha_bala": payload}


def _is_daytime(
    dob_tuple: Tuple[int, int, int],
    tob_tuple: Tuple[int, int, float],
    place: drik.Place,
) -> bool:
    jd = utils.julian_day_number(dob_tuple, tob_tuple)
    sunrise = drik.sunrise(jd, place)[0]
    sunset = drik.sunset(jd, place)[0]
    fh = utils.from_dms(tob_tuple[0], tob_tuple[1], tob_tuple[2])
    return sunrise <= fh <= sunset


def _classify_state(
    name: str,
    sign_idx: int,
    degrees_in_sign: float,
    is_daytime: bool,
) -> Tuple[str, float, str]:
    preference = _PLANET_DAY_PREF.get(name, "neutral")
    sign_context = "day" if sign_idx % 2 == 0 else "night"
    time_context = "day" if is_daytime else "night"

    if preference == "neutral":
        return (
            "balanced",
            5.0,
            f"{name} is neutral for shayanadi avasthas and adopts the {sign_context} sign qualities.",
        )

    matches_sign = (preference == "day" and sign_context == "day") or (
        preference == "night" and sign_context == "night"
    )
    matches_time = (preference == "day" and is_daytime) or (
        preference == "night" and not is_daytime
    )

    if matches_sign and matches_time:
        return (
            "awake",
            12.5,
            f"{name} thrives in a {sign_context} sign during the {time_context} portion of the day.",
        )
    if not matches_sign and not matches_time:
        return (
            "sleeping",
            -10.0,
            f"{name} is dormant (sign={sign_context}, time={time_context}).",
        )
    return (
        "restless",
        0.0,
        f"{name} experiences mixed avastha cues (sign={sign_context}, time={time_context}).",
    )
