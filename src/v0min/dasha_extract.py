from __future__ import annotations

import importlib
from dataclasses import asdict
from datetime import datetime
from typing import Dict, List, Optional

from jhora import const, utils
from jhora.panchanga import drik

from v0min.core_time import BirthContext, make_birth_context
from v0min.dasha_common import (
    DASHAS_SUPPORTED,
    ENGINE_BY_SYSTEM,
    PLANET_NAMES,
    DashaPeriod,
    DashaSystem,
    DashaTimeline,
)
from v0min.vimshottari_extract import build_vimshottari_timeline


SCHEMA_VERSION = "dasha.v1"
ENGINE_FALLBACK = "PYJHORA_DASHA"
SIDEREAL_YEAR = const.sidereal_year
LEVEL_ORDER = {"MD": 0, "AD": 1, "PD": 2, "SD": 3}
RAASI_NAMES = [
    "ARIES",
    "TAURUS",
    "GEMINI",
    "CANCER",
    "LEO",
    "VIRGO",
    "LIBRA",
    "SCORPIO",
    "SAGITTARIUS",
    "CAPRICORN",
    "AQUARIUS",
    "PISCES",
]
AUGMENTED_YEAR = const.average_gregorian_year


def _collect_levels(periods: List[DashaPeriod]) -> List[str]:
    unique_levels = {period.level for period in periods}
    return sorted(unique_levels, key=lambda lvl: LEVEL_ORDER.get(lvl, 99))


SYSTEM_CONFIG: Dict[DashaSystem, Dict[str, object]] = {
    "VIMSHOTTARI": {"adapter": "vimshottari", "system_type": "GRAHA"},
    "ASHTOTTARI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.ashtottari",
        "function": "get_ashtottari_dhasa_bhukthi",
        "input": "jd",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "DWADASOTTARI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.dwadasottari",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "DWISATPATHI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.dwisatpathi",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "SHODASOTTARI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.shodasottari",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "PANCHOTTARI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.panchottari",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "SHASTIHAYANI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.shastihayani",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "YOGINI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.graha.yogini",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "graha",
        "system_type": "GRAHA",
    },
    "KALACHAKRA": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.kalachakra",
        "function": "get_dhasa_bhukthi",
        "input": "dob_tob",
        "key_type": "rasi",
        "system_type": "RAASI",
    },
    "NARAYANA": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.narayana",
        "function": "narayana_dhasa_for_rasi_chart",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "PATTAYINI_VARSHIKA": {
        "adapter": "patyayini",
        "module": "jhora.horoscope.dhasa.annual.patyayini",
        "function": "patyayini_dhasa",
        "system_type": "ANNUAL",
        "kwargs": {"divisional_chart_factor": 1},
    },
    "BRAHMA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.brahma",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "CHAKRA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.chakra",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "CHARA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.chara",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "LAGNAMSAKA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.lagnamsaka",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "NAVAMSA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.navamsa",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "MANDOOKA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.mandooka",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "PARYAAYA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.paryaaya",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "PADHANADHAMSA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.padhanadhamsa",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "SANDHYA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.sandhya",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "STHIRA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.sthira",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "TARA_LAGNA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.tara_lagna",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "TRIKONA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.trikona",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "VARNADA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.varnada",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
    "YOGARDHA_RAASI": {
        "adapter": "generic",
        "module": "jhora.horoscope.dhasa.raasi.yogardha",
        "function": "get_dhasa_antardhasa",
        "input": "dob_tob",
        "key_type": "rasi",
        "kwargs": {"include_antardhasa": True},
        "system_type": "RAASI",
    },
}


def _jd_to_iso(jd: float) -> str:
    year, month, day, fractional_hours = utils.jd_to_gregorian(jd)
    total_seconds = int(round(fractional_hours * 3600))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{year:04d}-{month:02d}-{day:02d}T{hours:02d}:{minutes:02d}:{seconds:02d}"


def _place_from_context(bc: BirthContext) -> drik.Place:
    label = bc.location_name or "Birth Place"
    return drik.Place(label, bc.latitude, bc.longitude, bc.utc_offset_hours)


def _birth_context_from_snapshot(birth_snapshot: dict) -> BirthContext:
    birth = birth_snapshot["birth_data"]
    location = birth["location"]
    dt_local = datetime.fromisoformat(birth["datetime_local"])
    dt_naive = dt_local.replace(tzinfo=None)
    return make_birth_context(
        dt_naive,
        location["lat"],
        location["lon"],
        tz_name=birth["timezone_name"],
        location_name=location.get("name"),
    )


def _derive_dob_tob(birth_datetime: Optional[datetime], jd_local: float) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
    if birth_datetime is None:
        y, m, d, fractional_hours = utils.jd_to_gregorian(jd_local)
        total_seconds = int(round(fractional_hours * 3600))
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        dob = (y, m, d)
        tob = (hours, minutes, seconds)
        return dob, tob
    dt = birth_datetime
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return (dt.year, dt.month, dt.day), (dt.hour, dt.minute, dt.second)


def _normalize_label(value: object, key_type: str) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip().upper()
    index = int(value)
    if key_type == "rasi":
        return RAASI_NAMES[index % len(RAASI_NAMES)]
    return PLANET_NAMES[index % len(PLANET_NAMES)]


def _extract_duration_years(entry: List[object]) -> Optional[float]:
    if len(entry) >= 4 and isinstance(entry[-1], (int, float)):
        return float(entry[-1])
    return None


def _structure_entries(entries: List[list], key_type: str) -> List[dict]:
    structured: List[dict] = []
    for raw in entries:
        md_value = raw[0]
        ad_value = raw[1] if len(raw) > 1 and isinstance(raw[1], (int, float, str)) else None
        start_iso, start_jd = _parse_start_value(raw)
        duration_years = _extract_duration_years(raw)
        duration_days = duration_years * SIDEREAL_YEAR if duration_years is not None else None
        structured.append(
            {
                "md": _normalize_label(md_value, key_type),
                "ad": _normalize_label(ad_value, key_type),
                "start_jd": start_jd,
                "start_iso": start_iso,
                "duration_days": duration_days,
            }
        )
    for idx, entry in enumerate(structured):
        if idx + 1 < len(structured):
            entry["end_jd"] = structured[idx + 1]["start_jd"]
            entry["end_iso"] = structured[idx + 1]["start_iso"]
        elif entry["duration_days"]:
            end_jd = entry["start_jd"] + entry["duration_days"]
            entry["end_jd"] = end_jd
            entry["end_iso"] = _jd_to_iso(end_jd)
        else:
            entry["end_jd"] = None
            entry["end_iso"] = None
    return structured


def _parse_start_value(entry: List[object]) -> tuple[str, float]:
    for value in entry:
        if isinstance(value, str):
            stripped = value.strip()
            if stripped and any(sep in stripped for sep in ("-", "T", ":")):
                return _parse_start_string(stripped)
    for value in entry:
        if isinstance(value, (int, float)) and value > 10_000:
            return _parse_start_string(value)
    raise ValueError(f"Unable to identify start timestamp in dasha entry: {entry!r}")


def _parse_start_string(value: object) -> tuple[str, float]:
    if isinstance(value, (int, float)):
        return _jd_to_iso(float(value)), float(value)
    if isinstance(value, str):
        parts = value.strip().split()
        if len(parts) == 1:
            parts.append("00:00:00")
        dt = datetime.strptime(f"{parts[0]} {parts[1]}", "%Y-%m-%d %H:%M:%S")
        dob = (dt.year, dt.month, dt.day)
        tob = (dt.hour, dt.minute, dt.second)
        jd = utils.julian_day_number(dob, tob)
        return dt.isoformat(), jd
    raise TypeError(f"Unsupported start value: {value!r}")


def _md_periods_from_structured(system: str, structured: List[dict]) -> List[DashaPeriod]:
    md_nodes: List[dict] = []
    for entry in structured:
        if not md_nodes or md_nodes[-1]["lord"] != entry["md"]:
            md_nodes.append(
                {
                    "lord": entry["md"],
                    "start_jd": entry["start_jd"],
                    "start_iso": entry["start_iso"],
                    "entries": [],
                }
            )
        md_nodes[-1]["entries"].append(entry)
    for idx, node in enumerate(md_nodes):
        if idx + 1 < len(md_nodes):
            node["end_jd"] = md_nodes[idx + 1]["start_jd"]
            node["end_iso"] = md_nodes[idx + 1]["start_iso"]
        else:
            last_entry = node["entries"][-1]
            node["end_jd"] = last_entry["end_jd"]
            node["end_iso"] = last_entry["end_iso"]
    periods: List[DashaPeriod] = []
    for node in md_nodes:
        periods.append(
            DashaPeriod(
                level="MD",
                system=system,
                lord=node["lord"],
                sublord=None,
                start_jd=node["start_jd"],
                end_jd=node.get("end_jd"),
                start_iso=node["start_iso"],
                end_iso=node.get("end_iso"),
            )
        )
    return periods


def _ad_periods_from_structured(system: str, structured: List[dict]) -> List[DashaPeriod]:
    periods: List[DashaPeriod] = []
    for entry in structured:
        if entry["ad"] is None:
            continue
        periods.append(
            DashaPeriod(
                level="AD",
                system=system,
                lord=entry["ad"],
                sublord=entry["md"],
                start_jd=entry["start_jd"],
                end_jd=entry.get("end_jd"),
                start_iso=entry["start_iso"],
                end_iso=entry.get("end_iso"),
            )
        )
    return periods


def _flatten_periods(periods: List[DashaPeriod]) -> List[DashaPeriod]:
    return sorted(periods, key=lambda p: (p.start_jd, LEVEL_ORDER.get(p.level, 99)))


def _build_generic_timeline(system: str, entries: List[list], key_type: str, system_type: str) -> DashaTimeline:
    structured = _structure_entries(entries, key_type)
    md_periods = _md_periods_from_structured(system, structured)
    ad_periods = _ad_periods_from_structured(system, structured)
    periods = _flatten_periods(md_periods + ad_periods)
    levels = _collect_levels(periods)
    return DashaTimeline(
        schema_version=SCHEMA_VERSION,
        system=system,
        engine=ENGINE_BY_SYSTEM.get(system, ENGINE_FALLBACK),
        system_type=system_type,
        levels=levels,
        periods=periods,
    )


def _vimshottari_periods(system: str, vt) -> List[DashaPeriod]:
    periods: List[DashaPeriod] = []
    for item in vt.md:
        periods.append(
            DashaPeriod(
                level="MD",
                system=system,
                lord=item.md_lord,
                sublord=None,
                start_jd=item.start_jd_local,
                end_jd=item.end_jd_local,
                start_iso=item.start_iso_local,
                end_iso=item.end_iso_local,
            )
        )
    for item in vt.md_ad:
        periods.append(
            DashaPeriod(
                level="AD",
                system=system,
                lord=item.ad_lord,
                sublord=item.md_lord,
                start_jd=item.start_jd_local,
                end_jd=item.end_jd_local,
                start_iso=item.start_iso_local,
                end_iso=item.end_iso_local,
            )
        )
    for item in vt.md_ad_pd:
        periods.append(
            DashaPeriod(
                level="PD",
                system=system,
                lord=item.pd_lord,
                sublord=item.ad_lord,
                start_jd=item.start_jd_local,
                end_jd=item.end_jd_local,
                start_iso=item.start_iso_local,
                end_iso=item.end_iso_local,
            )
        )
    return _flatten_periods(periods)


def _build_patyayini_entries(jd_local: float, place: drik.Place, config: Dict[str, object]) -> List[list]:
    years_offset = int(config.get("years_offset", 1))
    kwargs = dict(config.get("kwargs", {}))
    module = importlib.import_module(config["module"])
    func = getattr(module, config["function"])
    jd_years = drik.next_solar_date(jd_local, place, years=years_offset)
    raw_entries = func(jd_years, place, **kwargs)
    duration_lookup = {item[0]: float(item[2]) for item in raw_entries}
    entries: List[list] = []
    for md_lord, bhukthi_rows, md_duration_days in raw_entries:
        bhukthi_rows = bhukthi_rows or []
        md_duration_days = float(md_duration_days)
        divisor = len(bhukthi_rows) or 1
        for ad_lord, start_str in bhukthi_rows:
            ad_duration_days = duration_lookup.get(ad_lord)
            if ad_duration_days is not None and AUGMENTED_YEAR:
                duration_days = (ad_duration_days / AUGMENTED_YEAR) * md_duration_days
            else:
                duration_days = md_duration_days / divisor
            duration_years = duration_days / SIDEREAL_YEAR if SIDEREAL_YEAR else None
            entries.append([md_lord, ad_lord, start_str, duration_years])
    return entries


def build_dasha_timeline(
    system: DashaSystem,
    jd_local: float,
    place: drik.Place,
    *,
    birth_datetime: Optional[datetime] = None,
) -> DashaTimeline:
    system = system.upper()
    config = SYSTEM_CONFIG.get(system)
    if not config:
        raise NotImplementedError(f"Dasha system '{system}' is not supported.")

    if config["adapter"] == "vimshottari":
        vt = build_vimshottari_timeline(jd_local, place)
        periods = _vimshottari_periods(system, vt)
        return DashaTimeline(
            schema_version=SCHEMA_VERSION,
            system=system,
            engine=ENGINE_BY_SYSTEM.get(system, ENGINE_FALLBACK),
            system_type="GRAHA",
            levels=_collect_levels(periods),
            periods=periods,
        )
    if config["adapter"] == "patyayini":
        entries = _build_patyayini_entries(jd_local, place, config)
        return _build_generic_timeline(
            system,
            entries,
            "graha",
            config.get("system_type", "ANNUAL"),
        )

    dob, tob = _derive_dob_tob(birth_datetime, jd_local)
    module = importlib.import_module(config["module"])
    func = getattr(module, config["function"])
    kwargs = dict(config.get("kwargs", {}))
    if config["input"] == "jd":
        entries = func(jd_local, place, **kwargs)
    elif config["input"] == "dob_tob":
        entries = func(dob, tob, place, **kwargs)
    else:
        raise ValueError(f"Unsupported input type for {system}")
    return _build_generic_timeline(
        system,
        entries,
        config.get("key_type", "graha"),
        config.get("system_type", "GRAHA"),
    )


def build_dasha_timeline_from_snapshot(birth_snapshot: dict, system: DashaSystem) -> DashaTimeline:
    bc = _birth_context_from_snapshot(birth_snapshot)
    place = _place_from_context(bc)
    return build_dasha_timeline(system, bc.jd_local, place, birth_datetime=bc.dt_local)


def build_all_dasha_timelines(
    birth_snapshot: dict,
    systems: Optional[List[DashaSystem]] = None,
) -> Dict[str, DashaTimeline]:
    bc = _birth_context_from_snapshot(birth_snapshot)
    place = _place_from_context(bc)
    resolved = systems or DASHAS_SUPPORTED
    return {
        system: build_dasha_timeline(system, bc.jd_local, place, birth_datetime=bc.dt_local)
        for system in resolved
    }


def build_dasha_full_payload(
    birth_snapshot: dict,
    systems: Optional[List[DashaSystem]] = None,
    reference_source: Optional[str] = None,
) -> dict:
    timelines = build_all_dasha_timelines(birth_snapshot, systems)
    return {
        "schema_version": "dasha.full.v1",
        "reference_source": reference_source or "",
        "person": birth_snapshot["birth_data"]["person"],
        "systems": {
            system: {
                "meta": {
                    "schema_version": timeline.schema_version,
                    "engine": timeline.engine,
                    "system": timeline.system,
                    "system_type": timeline.system_type,
                    "levels": timeline.levels,
                },
                "timeline": [asdict(period) for period in timeline.periods],
            }
            for system, timeline in timelines.items()
        },
    }


__all__ = [
    "build_dasha_timeline",
    "build_dasha_timeline_from_snapshot",
    "build_all_dasha_timelines",
    "build_dasha_full_payload",
]
