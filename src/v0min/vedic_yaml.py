from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


SCHEMA_VERSION = "vedic_master.v2"

_ONE_STAR_DEG = 360.0 / 27.0
_ONE_PADA_DEG = 360.0 / 108.0

_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
_PLANET_TOKENS = {
    "Sun": ("sun", "su"),
    "Moon": ("moon", "mo", "chandra"),
    "Mars": ("mars", "ma", "kuj"),
    "Mercury": ("mercury", "me", "budh"),
    "Jupiter": ("jupiter", "ju", "guru"),
    "Venus": ("venus", "ve", "shukra"),
    "Saturn": ("saturn", "sa", "shani"),
    "Rahu": ("rahu", "raagu", "ra"),
    "Ketu": ("ketu", "kethu", "ke"),
}

_CANONICAL_NAKSHATRAS = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashirsha",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

_TITHI_NAMES_SHUKLA = [
    "PRATHAMA",
    "DWITIYA",
    "TRITIYA",
    "CHATURTHI",
    "PANCHAMI",
    "SHASHTHI",
    "SAPTAMI",
    "ASHTAMI",
    "NAVAMI",
    "DASHAMI",
    "EKADASHI",
    "DWADASHI",
    "TRAYODASHI",
    "CHATURDASHI",
    "POURNIMA",
]

_TITHI_NAMES_KRISHNA = [
    "PRATHAMA",
    "DWITIYA",
    "TRITIYA",
    "CHATURTHI",
    "PANCHAMI",
    "SHASHTHI",
    "SAPTAMI",
    "ASHTAMI",
    "NAVAMI",
    "DASHAMI",
    "EKADASHI",
    "DWADASHI",
    "TRAYODASHI",
    "CHATURDASHI",
    "AMAVASYA",
]

_YOGA_NAMES = [
    "Vishkambha",
    "Priti",
    "Ayushman",
    "Saubhagya",
    "Shobhana",
    "Atiganda",
    "Sukarma",
    "Dhriti",
    "Shoola",
    "Ganda",
    "Vriddhi",
    "Dhruva",
    "Vyaghata",
    "Harshana",
    "Vajra",
    "Siddhi",
    "Vyatipata",
    "Variyana",
    "Parigha",
    "Shiva",
    "Siddha",
    "Sadhya",
    "Shubha",
    "Shukla",
    "Brahma",
    "Indra",
    "Vaidhriti",
]

_KARANA_PATTERN = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti"]
_CANONICAL_KARANAS = ["Kimstughna"] + _KARANA_PATTERN * 8 + ["Shakuni", "Chatushpada", "Naga"]


def normalize_graha_key_from_json(label: Optional[str]) -> Optional[str]:
    """Normalize PyJHora graha labels (e.g., 'Sun☉', 'Raagu☊') to canonical names."""
    if not label:
        return label
    letters = "".join(ch for ch in label if ch.isalpha()).lower()
    for canonical, tokens in _PLANET_TOKENS.items():
        if any(letters.startswith(tok) for tok in tokens):
            return canonical
    return label


def _normalize_sign(sign: Optional[str]) -> Optional[str]:
    if not sign:
        return None
    cleaned = re.sub(r"^[^A-Za-z]+", "", sign).strip()
    return cleaned or sign


def _hours_to_clock(hours: Optional[float]) -> Optional[str]:
    if hours is None:
        return None
    total_seconds = int(round((hours % 24) * 3600))
    h = total_seconds // 3600
    m = (total_seconds % 3600) // 60
    s = total_seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def _weekday_id(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return cleaned.upper() or None


def _canonicalize_id(label: Optional[str]) -> Optional[str]:
    if not label:
        return None
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", label).strip("_")
    return cleaned.upper() or None


def _nakshatra_from_degree(absolute_deg: Optional[float]) -> tuple[Optional[str], Optional[int]]:
    if absolute_deg is None:
        return None, None
    normalized = absolute_deg % 360.0
    index = int(normalized // _ONE_STAR_DEG)
    index = min(max(index, 0), len(_CANONICAL_NAKSHATRAS) - 1)
    remainder = normalized - index * _ONE_STAR_DEG
    pada = int(remainder // _ONE_PADA_DEG)
    return _CANONICAL_NAKSHATRAS[index], min(max(pada + 1, 1), 4)


def _canonical_tithi_id(index: Optional[int]) -> Optional[str]:
    if not index:
        return None
    idx = int(index)
    if idx < 1 or idx > 30:
        return None
    is_shukla = idx <= 15
    base_list = _TITHI_NAMES_SHUKLA if is_shukla else _TITHI_NAMES_KRISHNA
    base_name = base_list[(idx - 1) % 15]
    prefix = "SHUKLA" if is_shukla else "KRISHNA"
    return f"{prefix}_{base_name}"


def _canonical_nakshatra_id(index: Optional[int]) -> Optional[str]:
    if not index:
        return None
    idx = int(index)
    if idx < 1 or idx > len(_CANONICAL_NAKSHATRAS):
        return None
    return _canonicalize_id(_CANONICAL_NAKSHATRAS[idx - 1])


def _canonical_yoga_id(index: Optional[int]) -> Optional[str]:
    if not index:
        return None
    idx = int(index)
    if idx < 1 or idx > len(_YOGA_NAMES):
        return None
    return _canonicalize_id(_YOGA_NAMES[idx - 1])


def _canonical_karana_id(index: Optional[int]) -> Optional[str]:
    if not index:
        return None
    idx = int(index)
    if idx < 1 or idx > len(_CANONICAL_KARANAS):
        return None
    return _canonicalize_id(_CANONICAL_KARANAS[idx - 1])


def _wrap_panchanga(
    info: Optional[Dict[str, Any]],
    resolver,
    *,
    extra_keys: Optional[List[str]] = None,
) -> Optional[Dict[str, Any]]:
    if not info:
        return None
    block: Dict[str, Any] = {
        "id": resolver(info.get("index")),
        "local_name": info.get("name"),
        "index": info.get("index"),
    }
    if "pada" in info:
        block["pada"] = info.get("pada")
    if extra_keys:
        for key in extra_keys:
            if key in info:
                block[key] = info[key]
    return block


def _build_birth_block(birth_data: Dict[str, Any]) -> Dict[str, Any]:
    location = birth_data.get("location", {})
    return {
        "datetime_local": birth_data.get("datetime_local"),
        "datetime_utc": birth_data.get("datetime_utc"),
        "timezone": birth_data.get("timezone_name"),
        "utc_offset_hours": birth_data.get("utc_offset_hours"),
        "location": {
            "name": location.get("name"),
            "latitude_deg": location.get("lat"),
            "longitude_deg": location.get("lon"),
        },
    }


def _build_planet_entry(info: Dict[str, Any], asc_sign_index: Optional[int]) -> Dict[str, Any]:
    sign_index = info.get("sign_index")
    absolute_deg = info.get("absolute_deg")
    entry = {
        "sign": _normalize_sign(info.get("sign")),
        "degree": absolute_deg,
    }
    if sign_index is not None and asc_sign_index is not None:
        entry["house"] = ((sign_index - asc_sign_index) % 12) + 1
    else:
        entry["house"] = None
    nakshatra_name, pada = _nakshatra_from_degree(absolute_deg)
    entry["nakshatra"] = nakshatra_name
    entry["pada"] = pada
    return entry


def _normalize_house_occupancy(house_payload: Dict[str, List[str]]) -> Dict[int, List[str]]:
    normalized: Dict[int, List[str]] = {}
    for house_key, grahas in house_payload.items():
        try:
            house_number = int(house_key) + 1
        except (TypeError, ValueError):
            continue
        names = []
        for raw in grahas:
            canonical = normalize_graha_key_from_json(raw)
            if canonical:
                names.append(canonical)
        if names:
            normalized[house_number] = names
    return dict(sorted(normalized.items()))


def _build_chart_section(
    chart_payload: Dict[str, Any],
    asc_data: Dict[str, Any],
    *,
    include_house_data: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    asc_sign_index = asc_data.get("sign_index")
    asc_longitude = asc_data.get("absolute_deg")
    asc_nakshatra, asc_pada = _nakshatra_from_degree(asc_longitude)
    section: Dict[str, Any] = {
        "lagna": {
            "sign": _normalize_sign(asc_data.get("sign")),
            "degree": asc_longitude,
            "house": 1,
            "nakshatra": asc_nakshatra,
            "pada": asc_pada,
        },
        "planets": {},
    }
    planets = chart_payload.get("planets_detail") or chart_payload.get("planets") or {}
    for raw_name, info in planets.items():
        name = normalize_graha_key_from_json(raw_name)
        section["planets"][name] = _build_planet_entry(info, asc_sign_index)
    if include_house_data:
        normalized_houses = _normalize_house_occupancy(include_house_data)
        if normalized_houses:
            section["house_occupancy"] = normalized_houses
    return section


def _build_strength_block(strength_payload: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    shadbala_payload = strength_payload.get("shadbala")
    if shadbala_payload:
        shadbala: Dict[str, Any] = {}
        for raw_name, info in shadbala_payload.items():
            name = normalize_graha_key_from_json(raw_name)
            components = {
                "sthana": info.get("sthana"),
                "kaala": info.get("kaala"),
                "dig": info.get("dig"),
                "cheshta": info.get("cheshta"),
                "naisargika": info.get("naisargika"),
                "drik": info.get("drik"),
                "sum_shastiamsa": info.get("sum_shastiamsa"),
                "total_rupa": info.get("total_rupa"),
                "strength_ratio": info.get("strength_ratio"),
                "percent": info.get("percent"),
            }
            if info.get("note"):
                components["note"] = info.get("note")
            shadbala[name] = components
        if shadbala:
            result["shadbala"] = shadbala
    vargeeya_payload = strength_payload.get("dwadhasa_vargeeya_bala")
    if vargeeya_payload:
        vargeeya: Dict[str, Any] = {}
        for raw_name, value in vargeeya_payload.items():
            name = normalize_graha_key_from_json(raw_name)
            if name:
                vargeeya[name] = value
        if vargeeya:
            result["vargeeya"] = vargeeya
    ashtakavarga_payload = strength_payload.get("ashtakavarga")
    if ashtakavarga_payload:
        result["ashtakavarga"] = _build_ashtakavarga_block(ashtakavarga_payload)
    return result


def _build_ashtakavarga_block(ashtaka_payload: Dict[str, Any]) -> Dict[str, Any]:
    bav_payload = ashtaka_payload.get("binna_ashtakavarga", {})
    sav = ashtaka_payload.get("samudaya_ashtakavarga")
    bav: Dict[str, List[int]] = {}
    for raw_name, values in bav_payload.items():
        name = normalize_graha_key_from_json(raw_name)
        bav[name] = values
    return {"SAV": {"house_points": sav}, "BAV": bav}


def _build_panchanga_block(panchanga_payload: Dict[str, Any]) -> Dict[str, Any]:
    sunrise = panchanga_payload.get("sunrise", {})
    sunset = panchanga_payload.get("sunset", {})
    weekday_info = panchanga_payload.get("weekday", {})
    weekday = None
    if weekday_info:
        weekday = {
            "id": _weekday_id(weekday_info.get("name")),
            "local_name": weekday_info.get("name"),
            "index": weekday_info.get("index"),
        }
    tithi = _wrap_panchanga(
        panchanga_payload.get("tithi"),
        _canonical_tithi_id,
        extra_keys=["start_hour", "end_hour", "elapsed_percent"],
    )
    nakshatra = _wrap_panchanga(
        panchanga_payload.get("nakshatra"),
        _canonical_nakshatra_id,
        extra_keys=["start_hour", "end_hour", "elapsed_percent"],
    )
    yoga = _wrap_panchanga(
        panchanga_payload.get("yoga"),
        _canonical_yoga_id,
        extra_keys=["start_hour", "end_hour", "fraction"],
    )
    karana = _wrap_panchanga(
        panchanga_payload.get("karana"),
        _canonical_karana_id,
        extra_keys=["start_hour", "end_hour"],
    )
    return {
        "weekday": weekday,
        "tithi": tithi,
        "nakshatra": nakshatra,
        "yoga": yoga,
        "karana": karana,
        "sunrise": {
            "clock": sunrise.get("clock") or _hours_to_clock(sunrise.get("local_time_hours")),
            "local_time_hours": sunrise.get("local_time_hours"),
            "jd_local": sunrise.get("jd_local"),
        },
        "sunset": {
            "clock": sunset.get("clock") or _hours_to_clock(sunset.get("local_time_hours")),
            "local_time_hours": sunset.get("local_time_hours"),
            "jd_local": sunset.get("jd_local"),
        },
        "day_length_hours": panchanga_payload.get("day_length_hours"),
    }


def _build_vimshottari_block(
    timeline_payload: Optional[Dict[str, Any]],
    legacy_payload: Optional[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if not timeline_payload and not legacy_payload:
        return None

    md_entries = timeline_payload.get("md", []) if timeline_payload else []
    md_summary: List[Dict[str, Any]] = []
    for entry in md_entries:
        lord = entry.get("md_lord")
        start = entry.get("start_iso_local")
        end = entry.get("end_iso_local")
        if not lord or not start:
            continue
        md_summary.append(
            {
                "lord": lord,
                "start": start.split("T")[0],
                "end": end.split("T")[0] if isinstance(end, str) else None,
            }
        )

    timeline: List[Dict[str, Any]] = []
    if timeline_payload:
        for entry in timeline_payload.get("md_ad", []):
            md = entry.get("md_lord")
            ad = entry.get("ad_lord")
            start = entry.get("start_iso_local")
            if not md or not ad or not start:
                continue
            timeline.append(
                {
                    "md": md,
                    "ad": ad,
                    "start": start,
                }
            )

    if not md_summary and legacy_payload:
        legacy_sequence = legacy_payload.get("sequence", [])
        for row in legacy_sequence:
            raw_lord = row.get("mahadasha_lord")
            name = normalize_graha_key_from_json(raw_lord)
            start = row.get("start")
            if not name or not start:
                continue
            date_only = start.split(" ")[0]
            if not md_summary or md_summary[-1]["lord"] != name:
                if md_summary:
                    md_summary[-1]["end"] = date_only
                md_summary.append({"lord": name, "start": date_only, "end": None})
        if md_summary and md_summary[-1].get("end") is None:
            md_summary[-1]["end"] = None
        if not timeline:
            for row in legacy_sequence:
                md = normalize_graha_key_from_json(row.get("mahadasha_lord"))
                ad = normalize_graha_key_from_json(row.get("antardasha_lord"))
                start = row.get("start")
                if not md or not ad or not start:
                    continue
                timeline.append({"md": md, "ad": ad, "start": start.replace(" ", "T")})

    balance_dict = None
    if legacy_payload:
        balance = legacy_payload.get("balance_ymd", [])
        if len(balance) == 3:
            balance_dict = {"years": balance[0], "months": balance[1], "days": balance[2]}

    return {
        "balance_at_birth": balance_dict,
        "mahadashas": md_summary,
        "timeline": timeline,
    }


def _build_yoga_summary(yoga_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not yoga_payload:
        return None
    charts_payload = yoga_payload.get("by_chart", {})
    summary: Dict[str, List[Dict[str, str]]] = {}
    for chart_key in ("D1", "D9"):
        entries = charts_payload.get(chart_key)
        if not entries:
            continue
        summarized = []
        for item in entries:
            yoga_id = item.get("id")
            name = item.get("name")
            if not yoga_id or not name:
                continue
            summarized.append({"id": yoga_id, "name": name})
        if summarized:
            summary[chart_key] = summarized
    if not summary:
        return None
    return {
        "source": yoga_payload.get("engine", "PYJHORA"),
        "charts": summary,
    }


def build_vedic_master_from_full(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Transform a full_pyjhora payload into the vedic_master YAML structure."""

    meta = payload.get("meta", {})
    birth_data = payload.get("birth_data", {})
    person = birth_data.get("person")
    core_chart_source = payload.get("core_chart", {})
    result: Dict[str, Any] = {
        "meta": {
            "schema_version": SCHEMA_VERSION,
            "engine_version": meta.get("engine_version"),
            "source_jd_mode": meta.get("jd_mode"),
            "source_file_hint": f"{person}_full_pyjhora" if person else None,
            "person": person,
            "jd": {
                "mode": meta.get("jd_mode"),
                "jd_utc": meta.get("jd_utc"),
                "jd_local": meta.get("jd_local"),
            },
        },
        "birth": _build_birth_block(birth_data),
        "ayanamsa": {
            "mode": core_chart_source.get("ayanamsa_mode"),
            "value_deg": core_chart_source.get("ayanamsa_value_deg"),
        },
    }

    core_charts: Dict[str, Any] = {}
    if core_chart_source:
        core_charts["D1"] = _build_chart_section(
            core_chart_source,
            core_chart_source.get("lagna", {}),
            include_house_data=core_chart_source.get("house_occupancy"),
        )
    d9_payload = payload.get("vargas", {}).get("D9")
    if d9_payload:
        core_charts["D9"] = _build_chart_section(d9_payload, d9_payload.get("lagna", {}))
    d10_payload = payload.get("vargas", {}).get("D10")
    if d10_payload:
        core_charts["D10"] = _build_chart_section(d10_payload, d10_payload.get("lagna", {}))
    if core_charts:
        result["core_charts"] = core_charts

    strength_block = _build_strength_block(payload.get("strength", {}))
    if strength_block:
        result["strength"] = strength_block

    ashtaka_payload = payload.get("ashtakavarga")
    if ashtaka_payload:
        result["ashtakavarga"] = _build_ashtakavarga_block(ashtaka_payload)

    panchanga_payload = payload.get("panchanga_at_birth")
    if panchanga_payload:
        result["panchanga_at_birth"] = _build_panchanga_block(panchanga_payload)

    vim_full_payload = payload.get("vimshottari_full")
    dashas_payload = payload.get("dashas", {}).get("vimshottari")
    vim_block = _build_vimshottari_block(vim_full_payload, dashas_payload)
    if vim_block:
        result["vimshottari"] = vim_block

    yoga_summary = _build_yoga_summary(payload.get("yogas_pyjhora"))
    if yoga_summary:
        result["yogas"] = yoga_summary
    yogas_extended_payload = payload.get("yogas_extended")
    if yogas_extended_payload:
        result["yogas_extended"] = yogas_extended_payload

    planet_status_payload = payload.get("planet_status")
    if planet_status_payload:
        result["planet_status"] = planet_status_payload

    aspects_payload = payload.get("aspects")
    if aspects_payload:
        result["aspects"] = aspects_payload

    bhava_payload = payload.get("bhava_systems")
    if bhava_payload:
        result["bhava_systems"] = bhava_payload
    karaka_payload = payload.get("karakas")
    if karaka_payload:
        result["karakas"] = karaka_payload
    friendship_payload = payload.get("planet_friendships")
    if friendship_payload:
        result["planet_friendships"] = friendship_payload
    strength_trends_payload = payload.get("strength_trends")
    if strength_trends_payload:
        result["strength_trends"] = strength_trends_payload

    varshaphal_payload = payload.get("varshaphal")
    if varshaphal_payload:
        result["varshaphal"] = varshaphal_payload

    dosha_payload = payload.get("dosha")
    if dosha_payload:
        result["dosha"] = dosha_payload

    raja_payload = payload.get("raja_yoga")
    if raja_payload:
        result["raja_yoga"] = raja_payload

    predictions_payload = payload.get("predictions")
    if predictions_payload:
        result["predictions"] = predictions_payload

    extras_payload = payload.get("panchanga_extras")
    if extras_payload:
        result["panchanga_extras"] = extras_payload

    events_payload = payload.get("events")
    if events_payload:
        result["events"] = events_payload

    chakra_payload = payload.get("chakra")
    if chakra_payload:
        result["chakra"] = chakra_payload

    muhurta_payload = payload.get("muhurta")
    if muhurta_payload:
        result["muhurta"] = muhurta_payload

    prasna_payload = payload.get("prasna")
    if prasna_payload:
        result["prasna"] = prasna_payload

    return result


__all__ = ["SCHEMA_VERSION", "build_vedic_master_from_full", "normalize_graha_key_from_json"]
