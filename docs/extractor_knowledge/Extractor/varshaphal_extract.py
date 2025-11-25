from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.annual import mudda
from jhora.horoscope.dhasa.raasi import narayana as narayana_raasi
from jhora.horoscope.transit import saham, tajaka
from jhora.panchanga import drik

from v0min.core_time import BirthContext

_PLANET_NAMES = list(getattr(utils, "PLANET_NAMES", []))
_SIGN_NAMES = list(getattr(utils, "RAASI_LIST", []))
if not _PLANET_NAMES:
    _PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
if not _SIGN_NAMES:
    _SIGN_NAMES = [
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

_OPTIONAL_KEYS = {"sahams", "dashas", "tajaka_aspects"}


def compute_varshaphal_snapshot(
    context: Dict[str, Any],
    year: int,
    include: Optional[Iterable[str]] = None,
) -> Dict[str, Any]:
    """
    Build a JSON-friendly snapshot of the annual Varshaphal/Tajaka chart.
    """

    bc, place, years_from_dob = _prepare_base_context(context, year)
    ayanamsa_mode = (context.get("ayanamsa_mode") or "LAHIRI").upper()

    include_set = _OPTIONAL_KEYS if include is None else {item.lower() for item in include}

    # Annual chart + return timing
    chart_positions, _ = tajaka.varsha_pravesh(
        bc.jd_local,
        place,
        divisional_chart_factor=1,
        years=years_from_dob,
    )
    return_jd = drik.next_solar_date(bc.jd_local, place, years=years_from_dob)
    ret_year, ret_month, ret_day, fh = utils.jd_to_gregorian(return_jd)
    time_str = utils.to_dms(fh, as_string=True)
    return_datetime_local = f"{ret_year:04d}-{ret_month:02d}-{ret_day:02d}T{time_str}"
    night_time_birth = _is_night_time(return_jd, fh, place)

    chart_block = _build_chart_block(chart_positions)
    muntha_block = _build_muntha_block(chart_positions, chart_block, years_from_dob)
    varshesh_block = _build_varshesh_block(bc.jd_local, place, years_from_dob, ayanamsa_mode)

    snapshot: Dict[str, Any] = {
        "schema_version": "varshaphal.v1",
        "year": year,
        "years_from_birth": years_from_dob,
        "return_datetime_local": return_datetime_local,
        "return_jd_local": return_jd,
        "ayanamsa_mode": ayanamsa_mode,
        "chart": chart_block,
        "varshesh": varshesh_block,
        "muntha": muntha_block,
    }

    if "sahams" in include_set:
        snapshot["sahams"] = _compute_sahams(chart_positions, night_time_birth)
    if "dashas" in include_set:
        snapshot["dashas"] = _compute_dashas(context, years_from_dob)
    if "tajaka_aspects" in include_set:
        snapshot["tajaka_aspects"] = _compute_tajaka_aspects(chart_positions)

    return snapshot


def compute_maasa_snapshots(
    context: Dict[str, Any],
    year: int,
    months: Optional[Iterable[int]] = None,
) -> List[Dict[str, Any]]:
    bc, place, years_from_dob = _prepare_base_context(context, year)
    month_list = list(months) if months is not None else list(range(1, 13))
    snapshots: List[Dict[str, Any]] = []
    for month_value in month_list:
        month_idx = int(month_value)
        if month_idx < 1 or month_idx > 12:
            continue
        chart_positions, ((y, m, d), time_str) = tajaka.maasa_pravesh(
            bc.jd_local,
            place,
            divisional_chart_factor=1,
            years=years_from_dob,
            months=month_idx,
        )
        chart_block = _build_chart_block(chart_positions)
        return_datetime_local = f"{y:04d}-{m:02d}-{d:02d}T{time_str}"
        snapshots.append(
            {
                "schema_version": "varshaphal.maasa.v1",
                "year": year,
                "month_index": month_idx,
                "return_datetime_local": return_datetime_local,
                "chart": chart_block,
            }
        )
    return snapshots


def compute_sixty_hour_snapshots(
    context: Dict[str, Any],
    year: int,
    indices: Optional[Iterable[int]] = None,
) -> List[Dict[str, Any]]:
    bc, place, years_from_dob = _prepare_base_context(context, year)
    index_list = list(indices) if indices is not None else list(range(0, 6))
    snapshots: List[Dict[str, Any]] = []
    for index_value in index_list:
        idx = int(index_value)
        if idx < 0:
            continue
        sixty_hour_count = idx + 1
        chart_positions, ((y, m, d), time_str) = tajaka.sixty_hour_chart(
            bc.jd_local,
            place,
            divisional_chart_factor=1,
            years=years_from_dob,
            months=1,
            sixty_hour_count=sixty_hour_count,
        )
        chart_block = _build_chart_block(chart_positions)
        return_datetime_local = f"{y:04d}-{m:02d}-{d:02d}T{time_str}"
        snapshots.append(
            {
                "schema_version": "varshaphal.sixty_hour.v1",
                "year": year,
                "index": idx,
                "return_datetime_local": return_datetime_local,
                "chart": chart_block,
            }
        )
    return snapshots


def compute_varshaphal_subperiods(
    context: Dict[str, Any],
    year: int,
    *,
    include_maasa: bool = True,
    include_sixty_hour: bool = False,
    maasa_months: Optional[Iterable[int]] = None,
    sixty_indices: Optional[Iterable[int]] = None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    if include_maasa:
        payload["maasa"] = compute_maasa_snapshots(context, year, months=maasa_months)
    if include_sixty_hour:
        payload["sixty_hour"] = compute_sixty_hour_snapshots(context, year, indices=sixty_indices)
    return payload


def _resolve_place(context: Dict[str, Any]) -> drik.Place:
    place = context.get("place")
    if place is not None:
        return place
    bc: BirthContext = context["birth_context"]
    label = context.get("location_name") or bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def _build_chart_block(chart_positions: List) -> Dict[str, Any]:
    lagna_sign_idx, lagna_deg = chart_positions[0][1]
    lagna_info = _angle_to_dict(lagna_sign_idx, lagna_deg)
    planets: Dict[str, Any] = {}
    for planet_id, (sign_idx, deg_in_sign) in chart_positions[1:]:
        if not isinstance(planet_id, int):
            continue
        if planet_id >= len(_PLANET_NAMES):
            continue
        planets[_PLANET_NAMES[planet_id]] = _angle_to_dict(sign_idx, deg_in_sign)
    return {
        "raw_positions": chart_positions,
        "lagna": lagna_info,
        "planets": planets,
    }


def _angle_to_dict(sign_idx: float, degrees_in_sign: float) -> Dict[str, Any]:
    sign_index = int(sign_idx) % 12
    absolute = (sign_index * 30.0 + degrees_in_sign) % 360.0
    return {
        "sign_index": sign_index,
        "sign": _SIGN_NAMES[sign_index],
        "degree_in_sign": round(degrees_in_sign, 6),
        "absolute_deg": round(absolute, 6),
    }


def _build_muntha_block(chart_positions: List, chart_block: Dict[str, Any], years_from_dob: int) -> Dict[str, Any]:
    p_to_h = utils.get_planet_house_dictionary_from_planet_positions(chart_positions)
    asc_house_idx = p_to_h[const._ascendant_symbol]
    muntha_idx = tajaka.muntha_house(asc_house_idx, years_from_dob) % 12
    lagna_sign_index = chart_block["lagna"]["sign_index"]
    muntha_sign_index = (lagna_sign_index + muntha_idx) % 12
    return {
        "house_index": muntha_idx,
        "house_number": muntha_idx + 1,
        "sign_index": muntha_sign_index,
        "sign": _SIGN_NAMES[muntha_sign_index],
    }


def _build_varshesh_block(
    jd_at_dob: float,
    place: drik.Place,
    years_from_dob: int,
    ayanamsa_mode: str,
) -> Dict[str, Any]:
    planet_idx = _safe_lord_of_year(jd_at_dob, place, years_from_dob, ayanamsa_mode)
    planet_name = _PLANET_NAMES[planet_idx] if planet_idx < len(_PLANET_NAMES) else str(planet_idx)
    return {
        "planet_id": planet_idx,
        "planet": planet_name,
    }


def _compute_sahams(chart_positions: List, night_time_birth: bool) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for saham_name in getattr(const, "_saham_list", []):
        func_name = f"{saham_name}_saham"
        fn = getattr(saham, func_name, None)
        if fn is None:
            continue
        try:
            value = fn(chart_positions, night_time_birth=night_time_birth)
        except TypeError:
            value = fn(chart_positions)
        sign_index = int(value // 30) % 12
        deg_in_sign = value % 30.0
        results.append(
            {
                "name": saham_name,
                "longitude_deg": round(value, 6),
                "sign_index": sign_index,
                "sign": _SIGN_NAMES[sign_index],
                "degree_in_sign": round(deg_in_sign, 6),
            }
        )
    return results


def _compute_dashas(context: Dict[str, Any], years_from_dob: int) -> Dict[str, Any]:
    bc: BirthContext = context["birth_context"]
    place = _resolve_place(context)
    ayanamsa_mode = (context.get("ayanamsa_mode") or "LAHIRI").upper()
    dob = drik.Date(bc.dt_local.year, bc.dt_local.month, bc.dt_local.day)
    seconds = bc.dt_local.second + bc.dt_local.microsecond / 1_000_000
    tob = (bc.dt_local.hour, bc.dt_local.minute, seconds)

    varsha_vimsottari = mudda.varsha_vimsottari_dhasa_bhukthi(
        bc.jd_local,
        place,
        years_from_dob,
        divisional_chart_factor=1,
    )
    varsha_vimsottari_block = [
        {
            "mahadasha_lord_id": md,
            "mahadasha_lord": _PLANET_NAMES[md] if md < len(_PLANET_NAMES) else str(md),
            "antardasha_lord_id": ad,
            "antardasha_lord": _PLANET_NAMES[ad] if ad < len(_PLANET_NAMES) else str(ad),
            "start": start,
            "duration_days": duration,
        }
        for md, ad, start, duration in varsha_vimsottari
    ]

    varsha_narayana = narayana_raasi.varsha_narayana_dhasa_bhukthi(
        dob,
        tob,
        place,
        years=years_from_dob,
        divisional_chart_factor=1,
        include_antardhasa=True,
    )
    varsha_narayana_block = [
        {
            "rasi_id": rasi_id,
            "rasi": _SIGN_NAMES[rasi_id % 12],
            "subrasi_id": sub_id,
            "subrasi": _SIGN_NAMES[sub_id % 12],
            "start": start,
            "duration_days": duration,
        }
        for rasi_id, sub_id, start, duration in varsha_narayana
    ]

    return {
        "varsha_vimsottari": varsha_vimsottari_block,
        "varsha_narayana": varsha_narayana_block,
        "ayanamsa_mode": ayanamsa_mode,
    }


def _compute_tajaka_aspects(chart_positions: List) -> Dict[str, Any]:
    house_planets = utils.get_house_planet_list_from_planet_positions(chart_positions)
    benefic: Dict[str, Any] = {}
    malefic: Dict[str, Any] = {}
    for planet_id in range(0, min(7, len(_PLANET_NAMES))):
        bah, _ = tajaka.benefic_aspects_of_the_planet(house_planets, planet_id)
        mah, _ = tajaka.malefic_aspects_of_the_planet(house_planets, planet_id)
        benefic[_PLANET_NAMES[planet_id]] = _format_house_entries(bah)
        malefic[_PLANET_NAMES[planet_id]] = _format_house_entries(mah)

    ithasala = []
    for p1 in range(0, 7):
        for p2 in range(p1 + 1, 7):
            match, ithasala_type = tajaka.both_planets_within_their_deeptamsa(chart_positions, p1, p2)
            if not match:
                continue
            ithasala.append(
                {
                    "planet1": _PLANET_NAMES[p1],
                    "planet2": _PLANET_NAMES[p2],
                    "ithasala_type": _ithasala_label(ithasala_type),
                }
            )
    return {
        "benefic_aspects": benefic,
        "malefic_aspects": malefic,
        "ithasala": ithasala,
    }


def _format_house_entries(indices: Iterable[int]) -> List[Dict[str, Any]]:
    entries: List[Dict[str, Any]] = []
    for idx in indices or []:
        house_idx = int(idx) % 12
        entries.append(
            {
                "house_index": house_idx,
                "house_number": house_idx + 1,
                "sign": _SIGN_NAMES[house_idx],
            }
        )
    return entries


def _ithasala_label(ithasala_type: Optional[int]) -> Optional[str]:
    return {
        1: "VARTHAMANA",
        2: "POORNA",
        3: "BHAVISHYA",
    }.get(ithasala_type)


def _is_night_time(jd_local: float, fh: float, place: drik.Place) -> bool:
    sunrise_str = drik.sunrise(jd_local, place)[1]
    sunset_str = drik.sunset(jd_local, place)[1]
    sunrise_components = utils.from_dms_str_to_dms(sunrise_str)
    sunset_components = utils.from_dms_str_to_dms(sunset_str)
    sunrise_hours = sunrise_components[0] + sunrise_components[1] / 60.0 + sunrise_components[2] / 3600.0
    sunset_hours = sunset_components[0] + sunset_components[1] / 60.0 + sunset_components[2] / 3600.0
    return fh < sunrise_hours or fh > sunset_hours


def _prepare_base_context(context: Dict[str, Any], year: int) -> tuple[BirthContext, drik.Place, int]:
    bc: BirthContext = context["birth_context"]
    years_from_dob = year - bc.dt_local.year
    if years_from_dob < 0:
        raise ValueError(f"Target year {year} is before birth year {bc.dt_local.year}.")
    place = _resolve_place(context)
    return bc, place, years_from_dob


def _safe_lord_of_year(
    jd_at_dob: float,
    place: drik.Place,
    years_from_dob: int,
    ayanamsa_mode: str,
) -> int:
    try:
        return tajaka.lord_of_the_year(jd_at_dob, place, years_from_dob)
    except KeyError:
        return _fallback_lord_of_year(jd_at_dob, place, years_from_dob, ayanamsa_mode)


def _fallback_lord_of_year(
    jd_at_dob: float,
    place: drik.Place,
    years_from_dob: int,
    ayanamsa_mode: str,
) -> int:
    natal_chart = charts.divisional_chart(
        jd_at_dob,
        place,
        ayanamsa_mode=ayanamsa_mode,
        divisional_chart_factor=1,
    )
    natal_p_to_h = utils.get_planet_house_dictionary_from_planet_positions(natal_chart)
    natal_lagna_house = natal_p_to_h[const._ascendant_symbol]
    jd_at_years = drik.next_solar_date(jd_at_dob, place, years=years_from_dob)
    tob_hours = utils.jd_to_gregorian(jd_at_years)[3]
    night_time_birth = _is_night_time(jd_at_years, tob_hours, place)
    annual_chart = charts.divisional_chart(
        jd_at_years,
        place,
        ayanamsa_mode=ayanamsa_mode,
        divisional_chart_factor=1,
    )
    candidates = tajaka._get_lord_candidates(annual_chart, years_from_dob, natal_lagna_house, night_time_birth)
    filtered = [candidate for candidate in candidates if isinstance(candidate, int) and 0 <= candidate < 7]
    candidates_to_use = filtered or [candidate for candidate in candidates if isinstance(candidate, int)] or [0]
    return tajaka._get_the_lord_of_tajaka_chart(jd_at_years, place, candidates_to_use)


__all__ = [
    "compute_varshaphal_snapshot",
    "compute_maasa_snapshots",
    "compute_sixty_hour_snapshots",
    "compute_varshaphal_subperiods",
]
