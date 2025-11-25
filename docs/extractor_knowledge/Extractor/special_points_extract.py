from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple

from jhora import const, utils
from jhora.horoscope.chart import arudhas, house, sphuta
from jhora.horoscope.chart import charts as charts_mod
from jhora.horoscope.chart import ashtakavarga as ashtakavarga_mod
from jhora.horoscope.transit import saham
from jhora.panchanga import drik

from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

SPECIAL_POINTS_SCHEMA_VERSION = "special_points.v1"
ENGINE_NAME = "PYJHORA_SPECIAL_POINTS"
GRAHA_DRISHTI_SCHEMA_VERSION = "graha_drishti_heatmap.v1"
PINDA_CHAKRA_SCHEMA_VERSION = "pinda_chakra.v1"
UPAGRAHA_SCHEMA_VERSION = "upagraha.v1"
SAHAMA_SCHEMA_VERSION = "sahama.v1"
STAR_METRICS_SCHEMA_VERSION = "star_metrics.v1"

_PLANET_FALLBACK = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_RAASI_FALLBACK = [
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

SPHUTA_REGISTRY = [
    ("tri_sphuta", "TRI_SPHUTA", "Tri Sphuta"),
    ("chatur_sphuta", "CHATUR_SPHUTA", "Chatur Sphuta"),
    ("pancha_sphuta", "PANCHA_SPHUTA", "Pancha Sphuta"),
    ("prana_sphuta", "PRANA_SPHUTA", "Prana Sphuta"),
    ("deha_sphuta", "DEHA_SPHUTA", "Deha Sphuta"),
    ("mrityu_sphuta", "MRITYU_SPHUTA", "Mrityu Sphuta"),
    ("tithi_sphuta", "TITHI_SPHUTA", "Tithi Sphuta"),
    ("yoga_sphuta", "YOGA_SPHUTA", "Yoga Sphuta"),
    ("rahu_tithi_sphuta", "RAHU_TITHI_SPHUTA", "Rahu Tithi Sphuta"),
    ("beeja_sphuta", "BEEJA_SPHUTA", "Beeja Sphuta"),
    ("kshetra_sphuta", "KSHETRA_SPHUTA", "Kshetra Sphuta"),
    ("yogi_sphuta", "YOGI_SPHUTA", "Yogi Sphuta"),
    ("avayogi_sphuta", "AVAYOGI_SPHUTA", "Avayogi Sphuta"),
]


def compute_special_points_block(
    full_payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]] = None,
    *,
    config: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build the special_points.v1 block by wrapping PyJHora's Arudha and Sphuta engines.
    """

    cfg = config or {}
    include_arudhas = cfg.get("include_arudhas", True)
    include_sphutas = cfg.get("include_sphutas", True)
    include_special_charts = cfg.get("include_special_charts", False)
    include_graha_drishti = cfg.get("include_graha_drishti", True)
    include_pinda = cfg.get("include_pinda", True)
    include_upagrahas = cfg.get("include_upagrahas", True)
    include_sahamas = cfg.get("include_sahamas", True)
    include_star_metrics = cfg.get("include_star_metrics", True)
    drishti_systems = cfg.get("drishti_systems") or ["parashari", "jaimini"]

    bc, place, ayanamsa_mode = _resolve_context(full_payload, base_context)
    planet_positions = _resolve_planet_positions(full_payload, base_context, bc, place, ayanamsa_mode)
    if planet_positions is None:
        raise ValueError("Unable to resolve D1 chart positions for special points extraction.")

    result: Dict[str, Any] = {
        "schema_version": SPECIAL_POINTS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
    }
    lagna_sign = int(planet_positions[0][1][0])
    dob, tob = _build_birth_datetime(bc)
    night_time_birth = _is_night_birth(bc, place)

    if include_arudhas:
        result["arudhas"] = _compute_arudha_block(planet_positions)
    if include_sphutas:
        result["sphutas"] = _compute_sphuta_block(bc, place, ayanamsa_mode, planet_positions, dob, tob)
    house_to_planet_list: Optional[List[str]] = None
    if include_graha_drishti or include_pinda:
        house_to_planet_list = utils.get_house_planet_list_from_planet_positions(planet_positions)

    if include_graha_drishti and house_to_planet_list:
        drishti_block = _compute_graha_drishti_block(
            house_to_planet_list,
            lagna_sign,
            planet_positions,
            drishti_systems,
        )
        if drishti_block:
            result["graha_drishti_heatmap"] = drishti_block
    if include_pinda and house_to_planet_list:
        pinda_block = _compute_pinda_chakra_block(house_to_planet_list)
        if pinda_block:
            result["pinda_chakra"] = pinda_block
    if include_upagrahas:
        upagraha_block = _compute_upagraha_block(
            place,
            ayanamsa_mode,
            planet_positions,
            lagna_sign,
            dob,
            tob,
        )
        if upagraha_block:
            result["upagraha"] = upagraha_block
    if include_sahamas:
        saham_block = _compute_sahama_block(planet_positions, lagna_sign, night_time_birth)
        if saham_block:
            result["sahamas"] = saham_block
    if include_star_metrics:
        star_metrics = _compute_star_metrics_block(dob, tob, place, planet_positions, lagna_sign)
        if star_metrics:
            result["star_metrics"] = star_metrics

    if include_special_charts:
        special = _compute_special_charts_block(bc, place, ayanamsa_mode)
        if special:
            result["special_charts"] = special

    return result


def _resolve_context(
    payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]],
) -> Tuple[Any, drik.Place, str]:
    if base_context:
        bc = base_context["birth_context"]
        place = base_context.get("place")
        if place is None:
            place = drik.Place(bc.location_name or "Birth Place", bc.latitude, bc.longitude, bc.utc_offset_hours)
        ayanamsa = base_context.get("ayanamsa_mode") or payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI")
        return bc, place, ayanamsa
    bc, place = build_birth_context_from_payload(payload)
    ayanamsa = payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI")
    return bc, place, ayanamsa


def _resolve_planet_positions(
    payload: Dict[str, Any],
    base_context: Optional[Dict[str, Any]],
    bc,
    place,
    ayanamsa_mode: str,
):
    if base_context and base_context.get("rasi_raw_positions"):
        return base_context["rasi_raw_positions"]
    positions = get_chart_positions(payload, "D1")
    if positions:
        return positions
    return charts_mod.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)


def _compute_arudha_block(planet_positions: List) -> Dict[str, Any]:
    lagna_sign = planet_positions[0][1][0]
    arudha_section: Dict[str, Any] = {}
    arudha_section["lagna_arudhas"] = _format_bhava_arudhas(
        arudhas.bhava_arudhas_from_planet_positions(planet_positions),
        lagna_sign,
        prefix="A",
    )
    arudha_section["graha_arudhas"] = _format_graha_arudhas(
        arudhas.graha_arudhas_from_planet_positions(planet_positions),
        lagna_sign,
    )
    arudha_section["special_arudhas"] = _format_special_arudhas(planet_positions, lagna_sign)
    return arudha_section


def _format_bhava_arudhas(values: Iterable[int], lagna_sign: int, prefix: str) -> Dict[str, Any]:
    entries: Dict[str, Any] = {}
    names = ["L"] + [str(i) for i in range(2, 13)]
    for idx, sign in enumerate(values):
        name = prefix + names[idx] if idx < len(names) else f"{prefix}{idx+1}"
        entries[name] = _angle_from_sign(sign, lagna_sign, placeholder=True)
    return entries


def _format_graha_arudhas(values: Iterable[int], lagna_sign: int) -> Dict[str, Any]:
    entries: Dict[str, Any] = {}
    planet_names = _get_planet_names()
    name_map = ["Lagna"] + planet_names[: len(values) - 1]
    for idx, sign in enumerate(values):
        name = name_map[idx] if idx < len(name_map) else f"Planet_{idx}"
        entries[name] = _angle_from_sign(sign, lagna_sign, placeholder=True)
    return entries


def _format_special_arudhas(planet_positions: List, lagna_sign: int) -> Dict[str, Any]:
    entries: Dict[str, Any] = {}
    surya_list = arudhas.bhava_arudhas_from_planet_positions(planet_positions, arudha_base=1)
    chandra_list = arudhas.bhava_arudhas_from_planet_positions(planet_positions, arudha_base=2)
    if surya_list:
        entries["Surya_Arudha"] = _angle_from_sign(surya_list[0], lagna_sign, placeholder=True)
    if chandra_list:
        entries["Chandra_Arudha"] = _angle_from_sign(chandra_list[0], lagna_sign, placeholder=True)
    return entries


def _compute_sphuta_block(
    bc,
    place,
    ayanamsa_mode: str,
    planet_positions: List,
    dob=None,
    tob=None,
) -> Dict[str, Any]:
    if dob is None or tob is None:
        dob, tob = _build_birth_datetime(bc)
    lagna_sign = planet_positions[0][1][0]
    points: List[Dict[str, Any]] = []
    for func_name, point_id, label in SPHUTA_REGISTRY:
        fn = getattr(sphuta, func_name, None)
        if fn is None:
            continue
        try:
            sign_deg = fn(
                dob,
                tob,
                place,
                ayanamsa_mode=ayanamsa_mode,
                divisional_chart_factor=1,
                chart_method=1,
            )
        except Exception:
            continue
        if not isinstance(sign_deg, (list, tuple)) or len(sign_deg) < 2:
            continue
        sign_index = int(sign_deg[0]) % 12
        degree_in_sign = float(sign_deg[1])
        points.append(
            {
                "id": point_id,
                "name": label,
                "longitude_deg": sign_index * 30.0 + degree_in_sign,
                "sign_index": sign_index,
                "sign": _get_sign_name(sign_index),
                "degree_in_sign": degree_in_sign,
                "house": house.get_relative_house_of_planet(lagna_sign, sign_index),
                "planets_involved": [],
                "notes": None,
            }
        )
    return {"points": points}


def _compute_special_charts_block(bc, place, ayanamsa_mode: str) -> Dict[str, Any]:
    dob = drik.Date(bc.dt_local.year, bc.dt_local.month, bc.dt_local.day)
    tob = (
        bc.dt_local.hour,
        bc.dt_local.minute,
        bc.dt_local.second + bc.dt_local.microsecond / 1_000_000,
    )
    try:
        sign_deg = charts_mod.varnada_lagna(dob, tob, place, ayanamsa_mode=ayanamsa_mode)
    except Exception:
        return {}
    sign_index = int(sign_deg[0]) % 12
    degree_in_sign = float(sign_deg[1])
    entry = _angle_from_sign(sign_index, lagna_sign=None, placeholder=False, degree=degree_in_sign)
    return {"special_lagnas": {"Varnada_Lagna": entry}}


def _angle_from_sign(
    sign_index: int,
    lagna_sign: Optional[int] = None,
    placeholder: bool = True,
    degree: float = 0.0,
) -> Dict[str, Any]:
    sign_index = int(sign_index) % 12
    deg_in_sign = degree if not placeholder else 0.0
    entry = {
        "sign_index": sign_index,
        "sign": _get_sign_name(sign_index),
        "degree_in_sign": deg_in_sign,
        "longitude_deg": sign_index * 30.0 + deg_in_sign,
    }
    if lagna_sign is not None:
        entry["house"] = house.get_relative_house_of_planet(lagna_sign, sign_index)
    return entry


def _get_planet_names() -> List[str]:
    names = getattr(utils, "PLANET_NAMES", None)
    if not names:
        names = list(_PLANET_FALLBACK)
    return names


def _get_sign_name(sign_index: int) -> str:
    names = getattr(utils, "RAASI_LIST", None)
    if not names:
        names = _RAASI_FALLBACK
    return names[sign_index % 12]


def _build_birth_datetime(bc):
    dob = drik.Date(bc.dt_local.year, bc.dt_local.month, bc.dt_local.day)
    seconds = bc.dt_local.second + bc.dt_local.microsecond / 1_000_000
    tob = (
        bc.dt_local.hour,
        bc.dt_local.minute,
        seconds,
    )
    return dob, tob


def _is_night_birth(bc, place: drik.Place) -> bool:
    fraction_hours = (
        bc.dt_local.hour + bc.dt_local.minute / 60.0 + bc.dt_local.second / 3600.0 + bc.dt_local.microsecond / 3_600_000_000.0
    )
    sunrise_str = drik.sunrise(bc.jd_local, place)[1]
    sunset_str = drik.sunset(bc.jd_local, place)[1]
    sunrise_components = utils.from_dms_str_to_dms(sunrise_str)
    sunset_components = utils.from_dms_str_to_dms(sunset_str)
    sunrise_hours = sunrise_components[0] + sunrise_components[1] / 60.0 + sunrise_components[2] / 3600.0
    sunset_hours = sunset_components[0] + sunset_components[1] / 60.0 + sunset_components[2] / 3600.0
    return fraction_hours < sunrise_hours or fraction_hours > sunset_hours


_SOLAR_UPAGRAHAS = [
    ("dhuma", "Dhuma"),
    ("vyatipaata", "Vyatipata"),
    ("parivesha", "Parivesha"),
    ("indrachaapa", "Indrachapa"),
]

_PLANETARY_UPAGRAHAS = [
    ("kaala", "Kaala", drik.kaala_longitude),
    ("mrityu", "Mrityu", drik.mrityu_longitude),
    ("yama_ghantaka", "Yamagandaka", drik.yama_ghantaka_longitude),
    ("gulika", "Gulika", drik.gulika_longitude),
    ("maandi", "Mandi", drik.maandi_longitude),
]


def _compute_upagraha_block(
    place: drik.Place,
    ayanamsa_mode: str,
    planet_positions: List,
    lagna_sign: int,
    dob,
    tob,
) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    planet_map = {body: coords for body, coords in planet_positions}
    # Solar upagrahas rely on Sun's longitude
    sun_coords = planet_map.get(0)
    if sun_coords:
        sun_longitude = sun_coords[0] * 30.0 + sun_coords[1]
        for key, label in _SOLAR_UPAGRAHAS:
            try:
                sign_deg = drik.solar_upagraha_longitudes(sun_longitude, key)
            except Exception:
                sign_deg = None
            entries.append(_format_upagraha_entry(key, label, sign_deg, lagna_sign, source="SOLAR"))
    else:
        for key, label in _SOLAR_UPAGRAHAS:
            entries.append(_format_upagraha_entry(key, label, None, lagna_sign, source="SOLAR"))

    for key, label, fn in _PLANETARY_UPAGRAHAS:
        try:
            sign_deg = fn(dob, tob, place, ayanamsa_mode=ayanamsa_mode, divisional_chart_factor=1)
        except TypeError:
            sign_deg = fn(dob, tob, place)
        except Exception:
            sign_deg = None
        entries.append(_format_upagraha_entry(key, label, sign_deg, lagna_sign, source="PLANETARY"))

    return {"schema_version": UPAGRAHA_SCHEMA_VERSION, "entries": entries}


def _format_upagraha_entry(
    key: str,
    label: str,
    sign_deg: Optional[Iterable[float]],
    lagna_sign: int,
    *,
    source: str,
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "id": f"UPAGRAHA_{key.upper()}",
        "name": label,
        "source": source,
        "is_malefic": True,
    }
    if not sign_deg:
        entry.update(
            {
                "sign_index": None,
                "sign": None,
                "degree_in_sign": None,
                "longitude_deg": None,
                "house": None,
            }
        )
        return entry
    sign_index = int(sign_deg[0]) % 12
    degree_in_sign = float(sign_deg[1])
    longitude_deg = sign_index * 30.0 + degree_in_sign
    entry.update(
        {
            "sign_index": sign_index,
            "sign": _get_sign_name(sign_index),
            "degree_in_sign": round(degree_in_sign, 6),
            "longitude_deg": round(longitude_deg, 6),
            "house": house.get_relative_house_of_planet(lagna_sign, sign_index),
        }
    )
    return entry


def _compute_sahama_block(planet_positions: List, lagna_sign: int, night_time_birth: bool) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    for saham_name in getattr(const, "_saham_list", []):
        func_name = f"{saham_name}_saham"
        fn = getattr(saham, func_name, None)
        entry: Dict[str, Any] = {
            "id": f"SAHAMA_{saham_name.upper()}",
            "name": saham_name.replace("_", " ").title(),
        }
        value: Optional[float] = None
        if fn is not None:
            try:
                value = fn(planet_positions, night_time_birth=night_time_birth)
            except TypeError:
                value = fn(planet_positions)
            except Exception:
                value = None
        if value is None:
            entry.update(
                {
                    "sign_index": None,
                    "sign": None,
                    "degree_in_sign": None,
                    "longitude_deg": None,
                    "house": None,
                }
            )
        else:
            sign_index = int(value // 30) % 12
            degree_in_sign = value % 30.0
            entry.update(
                {
                    "sign_index": sign_index,
                    "sign": _get_sign_name(sign_index),
                    "degree_in_sign": round(degree_in_sign, 6),
                    "longitude_deg": round(value, 6),
                    "house": house.get_relative_house_of_planet(lagna_sign, sign_index),
                }
            )
        entries.append(entry)
    return {"schema_version": SAHAMA_SCHEMA_VERSION, "entries": entries}


def _compute_star_metrics_block(
    dob,
    tob,
    place: drik.Place,
    planet_positions: List,
    lagna_sign: int,
) -> Dict[str, Any]:
    mrityu_entries: List[Dict[str, Any]] = []
    planet_map = {body: coords for body, coords in planet_positions}
    raw_mrityu = charts_mod.planets_in_mrityu_bhaga(dob, tob, place, planet_positions)
    for planet_key, sign_index, diff in raw_mrityu:
        coords = _resolve_body_coords(planet_key, planet_map, dob, tob, place)
        if coords is None:
            continue
        sign_idx = int(coords[0]) % 12
        degree_in_sign = float(coords[1])
        longitude_deg = sign_idx * 30.0 + degree_in_sign
        mrityu_entries.append(
            {
                "planet": _resolve_planet_label(planet_key),
                "sign_index": sign_idx,
                "sign": _get_sign_name(sign_idx),
                "degree_in_sign": round(degree_in_sign, 6),
                "longitude_deg": round(longitude_deg, 6),
                "house": house.get_relative_house_of_planet(lagna_sign, sign_idx),
                "offset_deg": round(float(diff), 6),
            }
        )

    push_navamsa, push_bhaga = charts_mod.planets_in_pushkara_navamsa_bhaga(planet_positions)
    push_entries: List[Dict[str, Any]] = []
    for planet_id in push_navamsa:
        entry = _format_pushkara_entry(planet_id, "NAVAMSA", planet_map, lagna_sign)
        if entry:
            push_entries.append(entry)
    for planet_id in push_bhaga:
        entry = _format_pushkara_entry(planet_id, "BHAGA", planet_map, lagna_sign)
        if entry:
            push_entries.append(entry)

    supported = []
    if mrityu_entries:
        supported.append("mrityu_bhaga")
    if push_entries:
        supported.append("pushkara")

    return {
        "schema_version": STAR_METRICS_SCHEMA_VERSION,
        "mrityu_bhaga": mrityu_entries,
        "pushkara_points": push_entries,
        "meta": {
            "supported_metrics": supported or ["mrityu_bhaga", "pushkara"],
        },
    }


def _format_pushkara_entry(planet_id, point_type: str, planet_map: Dict[Any, Tuple[int, float]], lagna_sign: int):
    coords = planet_map.get(planet_id)
    if coords is None:
        return None
    sign_idx = int(coords[0]) % 12
    degree_in_sign = float(coords[1])
    longitude_deg = sign_idx * 30.0 + degree_in_sign
    return {
        "planet": _get_planet_name_by_id(planet_id),
        "type": point_type,
        "sign_index": sign_idx,
        "sign": _get_sign_name(sign_idx),
        "degree_in_sign": round(degree_in_sign, 6),
        "longitude_deg": round(longitude_deg, 6),
        "house": house.get_relative_house_of_planet(lagna_sign, sign_idx),
    }


def _resolve_body_coords(
    key,
    planet_map: Dict[Any, Tuple[int, float]],
    dob,
    tob,
    place: drik.Place,
):
    if isinstance(key, str):
        if key.upper() == "MD":
            try:
                return drik.maandi_longitude(dob, tob, place)
            except Exception:
                return None
        if key == const._ascendant_symbol:
            return planet_map.get(const._ascendant_symbol)
        return planet_map.get(key)
    return planet_map.get(key)


def _resolve_planet_label(key) -> str:
    if isinstance(key, str):
        if key.upper() == "MD":
            return "Mandi"
        if key == const._ascendant_symbol:
            return "Lagna"
        return key
    return _get_planet_name_by_id(int(key))


def _compute_graha_drishti_block(
    house_to_planet_list: List[str],
    lagna_sign: int,
    planet_positions: List,
    systems: Iterable[str],
) -> Dict[str, Any]:
    planet_sign_map = utils.get_planet_house_dictionary_from_planet_positions(planet_positions)
    planet_names = list(_PLANET_FALLBACK)
    block: Dict[str, Any] = {}
    for system in systems:
        key = str(system).lower()
        if key == "parashari":
            payload = _build_drishti_payload(
                system="parashari",
                house_to_planet_list=house_to_planet_list,
                lagna_sign=lagna_sign,
                planet_sign_map=planet_sign_map,
                planet_names=planet_names,
                resolver=house.graha_drishti_from_chart,
                type_resolver=_parashari_aspect_type,
            )
        elif key == "jaimini":
            payload = _build_drishti_payload(
                system="jaimini",
                house_to_planet_list=house_to_planet_list,
                lagna_sign=lagna_sign,
                planet_sign_map=planet_sign_map,
                planet_names=planet_names,
                resolver=house.raasi_drishti_from_chart,
                type_resolver=_jaimini_aspect_type,
            )
        else:
            continue
        if payload:
            block[key] = payload
    return block


def _build_drishti_payload(
    *,
    system: str,
    house_to_planet_list: List[str],
    lagna_sign: int,
    planet_sign_map: Dict[Any, Any],
    planet_names: List[str],
    resolver,
    type_resolver,
) -> Optional[Dict[str, Any]]:
    try:
        arp, ahp, _ = resolver(house_to_planet_list)
    except Exception:
        return None
    houses = list(range(1, 13))
    planet_to_house_entries: List[Dict[str, Any]] = []
    planet_to_planet_entries: List[Dict[str, Any]] = []
    planets_id_map = {name: idx for idx, name in enumerate(planet_names)}
    for planet_idx, name in enumerate(planet_names):
        target_signs = arp.get(planet_idx, [])
        target_houses = ahp.get(planet_idx, [])
        aspects: List[Dict[str, Any]] = []
        targets: List[Dict[str, Any]] = []
        source_sign = planet_sign_map.get(planet_idx)
        for aspect_idx, sign_index in enumerate(target_signs):
            house_number = (
                target_houses[aspect_idx]
                if aspect_idx < len(target_houses)
                else house.get_relative_house_of_planet(lagna_sign, sign_index)
            )
            aspect_type = type_resolver(source_sign, sign_index, planet_idx)
            aspect_payload = {
                "target_house": int(house_number),
                "target_sign_index": int(sign_index),
                "target_sign": _get_sign_name(sign_index),
                "type": aspect_type,
                "strength": 1.0,
            }
            aspects.append(aspect_payload)
            for target_planet in _extract_house_planets(house_to_planet_list[sign_index]):
                targets.append(
                    {
                        "planet": _get_planet_name_by_id(target_planet),
                        "planet_id": target_planet,
                        "target_house": int(house_number),
                        "target_sign_index": int(sign_index),
                        "target_sign": _get_sign_name(sign_index),
                        "type": aspect_type,
                        "strength": 1.0,
                    }
                )
        planet_to_house_entries.append(
            {
                "source": name,
                "source_sign_index": source_sign if source_sign is not None else None,
                "source_sign": _get_sign_name(source_sign) if isinstance(source_sign, int) else None,
                "aspects": aspects,
            }
        )
        planet_to_planet_entries.append({"source": name, "targets": targets})
    return {
        "schema_version": GRAHA_DRISHTI_SCHEMA_VERSION,
        "system": system,
        "planets": planet_names,
        "planets_id_map": planets_id_map,
        "houses": houses,
        "matrix": {
            "planet_to_house": planet_to_house_entries,
            "planet_to_planet": planet_to_planet_entries,
        },
    }


def _parashari_aspect_type(source_sign: Optional[int], target_sign: int, _: int) -> str:
    if source_sign is None:
        return "PARASHARI"
    delta = (target_sign - source_sign) % 12 + 1
    mapping = {
        4: "FOURTH",
        5: "FIFTH",
        7: "SEVENTH",
        8: "EIGHTH",
        9: "NINTH",
        10: "TENTH",
    }
    return mapping.get(delta, f"HOUSE_{delta}")


def _jaimini_aspect_type(_: Optional[int], __: int, ___: int) -> str:
    return "RAASI_DRISHTI"


def _extract_house_planets(entry: str) -> List[int]:
    if not entry:
        return []
    tokens = [token.strip() for token in entry.split("/") if token.strip()]
    result: List[int] = []
    asc_symbol = str(const._ascendant_symbol).upper()
    for token in tokens:
        if token.upper() == asc_symbol:
            continue
        try:
            result.append(int(token))
        except ValueError:
            continue
    return result


def _get_planet_name_by_id(planet_id: int) -> str:
    if 0 <= planet_id < len(_PLANET_FALLBACK):
        return _PLANET_FALLBACK[planet_id]
    names = getattr(utils, "PLANET_NAMES", None)
    if names and 0 <= planet_id < len(names):
        return names[planet_id]
    return f"Planet_{planet_id}"


def _compute_pinda_chakra_block(house_to_planet_list: List[str]) -> Dict[str, Any]:
    try:
        bav, _, _ = ashtakavarga_mod.get_ashtaka_varga(house_to_planet_list)
        raasi_pindas, graha_pindas, sodhya_pindas = ashtakavarga_mod.sodhaya_pindas(bav, house_to_planet_list)
    except Exception:
        return {}
    planet_names = _get_planet_names()[:7]
    values: List[Dict[str, float | str]] = []
    for idx, name in enumerate(planet_names):
        values.append(
            {
                "planet": name,
                "raasi_pinda": float(raasi_pindas[idx]),
                "graha_pinda": float(graha_pindas[idx]),
                "sodhya_pinda": float(sodhya_pindas[idx]),
            }
        )
    return {
        "D1": {
            "schema_version": PINDA_CHAKRA_SCHEMA_VERSION,
            "chart_id": "D1",
            "planets": planet_names,
            "values": values,
            "meta": {
                "source": "PYJHORA_ASHTAKAVARGA",
                "notes": "Derived from ashtakavarga.sodhaya_pindas for D1.",
            },
        }
    }


__all__ = ["compute_special_points_block", "SPECIAL_POINTS_SCHEMA_VERSION"]
