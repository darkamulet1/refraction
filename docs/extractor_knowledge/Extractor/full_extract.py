from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import tomllib

from v0min.core_space import compute_core_chart
from v0min.core_time import BirthContext
from v0min import yoga_extract
from v0min.planet_status import compute_planet_status_for_d1
from v0min.house_status_multivarga import compute_house_status_all_vargas
from v0min.vimshottari_extract import build_vimshottari_timeline
from v0min.dasha_extract import build_all_dasha_timelines
from v0min import panchanga_calendar_extract
from v0min.strength import compute_strength_all
from v0min.aspect_engine import compute_aspects_for_varga
from v0min.varshaphal_extract import (
    compute_varshaphal_snapshot,
    compute_varshaphal_subperiods,
)
from v0min.dosha_extract import compute_dosha_block
from v0min.raja_yoga_extract import compute_raja_yoga_block
from v0min.special_points_extract import compute_special_points_block
from v0min.prediction_extract import compute_predictions_block
from v0min.panchanga_extras_extract import compute_panchanga_extras_block
from v0min.muhurta_extract import MuhurtaConfig, compute_muhurta_windows
from v0min.prasna_extract import PrasnaConfig, compute_prasna_snapshot
from v0min.chakra_extract import ChakraConfig, compute_chakra_snapshot
from v0min.event_scan_extract import EventScanConfig, compute_events_snapshot
from v0min.bhava_systems_extract import (
    BhavaSystemsConfig,
    compute_bhava_systems_from_payload,
)
from v0min.yogas_extended_extract import YogasExtendedConfig, compute_yogas_extended_from_payload
from v0min.karakas_extract import KarakasConfig, compute_karakas_from_payload
from v0min.planet_friendships_extract import (
    PlanetFriendshipsConfig,
    compute_planet_friendships_from_payload,
)
from v0min.strength_trends_extract import (
    StrengthTrendsConfig,
    compute_strength_trends_from_payload,
)

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.horoscope.dhasa.graha import vimsottari
from jhora.panchanga import drik

DEFAULT_VARGA_FACTORS = {f"D{factor}": factor for factor in const.division_chart_factors}


def _load_engine_version() -> str:
    pyproject = Path(__file__).resolve().parents[2] / "pyproject.toml"
    try:
        data = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        return data.get("project", {}).get("version", "unknown")
    except Exception:
        return "unknown-local"


def _hours_to_clock(hours: float) -> str:
    total_seconds = (hours % 24) * 3600
    if total_seconds < 0:
        total_seconds += 24 * 3600
    total_seconds = round(total_seconds)
    h = int(total_seconds // 3600)
    m = int((total_seconds % 3600) // 60)
    s = int(total_seconds % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def _angle_to_dict(sign_idx: float, degrees_in_sign: float) -> Dict[str, float | str]:
    sign_index = int(sign_idx)
    absolute_deg = (sign_index * 30.0 + degrees_in_sign) % 360.0
    return {
        "sign_index": sign_index,
        "sign": utils.RAASI_LIST[sign_index],
        "deg_in_sign": round(degrees_in_sign, 6),
        "deg_dms": utils.to_dms(degrees_in_sign, is_lat_long="plong"),
        "absolute_deg": round(absolute_deg, 6),
    }


def _build_chart_snapshot(
    jd: float,
    place: drik.Place,
    ayanamsa_mode: str,
    factor: int = 1,
) -> Dict[str, Dict]:
    if factor == 1:
        positions = charts.rasi_chart(jd, place, ayanamsa_mode=ayanamsa_mode)
    else:
        positions = charts.divisional_chart(
            jd,
            place,
            ayanamsa_mode=ayanamsa_mode,
            divisional_chart_factor=factor,
        )
    lagna_info = _angle_to_dict(*positions[0][1])
    planet_details: Dict[str, Dict] = {}
    for planet_id, (sign_idx, deg_in_sign) in positions[1:]:
        name = utils.PLANET_NAMES[int(planet_id)]
        planet_details[name] = _angle_to_dict(sign_idx, deg_in_sign)
    return {"lagna": lagna_info, "planets": planet_details, "raw_positions": positions}


def _format_house_occupancy(planet_positions: List) -> Dict[str, List[str]]:
    house_map = {idx: [] for idx in range(12)}
    for entry in planet_positions[1:]:
        planet_id, (sign_idx, _) = entry
        house_map[int(sign_idx)].append(utils.PLANET_SHORT_NAMES[int(planet_id)])
    return {str(h): names for h, names in house_map.items()}


def _config_enabled(cfg: Any) -> bool:
    if isinstance(cfg, dict):
        return bool(cfg.get("enabled"))
    return bool(cfg)


def _compute_panchanga(jd_local: float, place: drik.Place) -> Dict[str, object]:
    _, _, _, birth_time_hours = utils.jd_to_gregorian(jd_local)
    vaara_idx = drik.vaara(jd_local)

    tithi_data = drik.tithi(jd_local, place)
    tithi_fraction = utils.get_fraction(tithi_data[1], tithi_data[2], birth_time_hours) * 100.0

    nak_data = drik.nakshatra(jd_local, place)
    nak_fraction = utils.get_fraction(nak_data[2], nak_data[3], birth_time_hours) * 100.0

    yoga_data = drik.yogam(jd_local, place)
    karana_data = drik.karana(jd_local, place)

    sunrise = drik.sunrise(jd_local, place)
    sunset = drik.sunset(jd_local, place)

    return {
        "weekday": {
            "index": vaara_idx,
            "name": utils.DAYS_LIST[vaara_idx],
        },
        "tithi": {
            "index": int(tithi_data[0]),
            "name": utils.TITHI_LIST[int(tithi_data[0]) - 1],
            "start_hour": tithi_data[1],
            "end_hour": tithi_data[2],
            "elapsed_percent": round(tithi_fraction, 3),
        },
        "nakshatra": {
            "index": int(nak_data[0]),
            "name": utils.NAKSHATRA_LIST[int(nak_data[0]) - 1],
            "pada": int(nak_data[1]),
            "start_hour": nak_data[2],
            "end_hour": nak_data[3],
            "elapsed_percent": round(nak_fraction, 3),
        },
        "yoga": {
            "index": int(yoga_data[0]),
            "name": utils.YOGAM_LIST[int(yoga_data[0]) - 1],
            "start_hour": yoga_data[1],
            "end_hour": yoga_data[2],
            "fraction": yoga_data[3],
        },
        "karana": {
            "index": int(karana_data[0]),
            "name": utils.KARANA_LIST[int(karana_data[0]) - 1],
            "start_hour": karana_data[1],
            "end_hour": karana_data[2],
        },
        "sunrise": {
            "local_time_hours": sunrise[0],
            "clock": _hours_to_clock(sunrise[0]),
            "jd_local": sunrise[2],
        },
        "sunset": {
            "local_time_hours": sunset[0],
            "clock": _hours_to_clock(sunset[0]),
            "jd_local": sunset[2],
        },
        "day_length_hours": drik.day_length(jd_local, place),
    }


def _format_vimshottari(jd_local: float, place: drik.Place) -> Dict[str, object]:
    vim_balance, rows = vimsottari.get_vimsottari_dhasa_bhukthi(
        jd_local,
        place,
        include_antardhasa=True,
    )
    formatted = [
        {
            "mahadasha_lord": utils.PLANET_NAMES[d],
            "antardasha_lord": utils.PLANET_NAMES[b],
            "start": ts,
        }
        for d, b, ts in rows
    ]
    return {"balance_ymd": vim_balance, "sequence": formatted}


def build_full_pyjhora_payload(
    bc: BirthContext,
    person: str,
    location_name: str,
    *,
    ayanamsa_mode: str = "LAHIRI",
    varga_factors: Optional[Dict[str, int]] = None,
    language: str = "en",
    panchanga_calendar_range: Optional[tuple[date, date]] = None,
    extraction_config: Optional[Dict[str, Any]] = None,
) -> Dict[str, object]:
    """Build the full PyJHora snapshot (schema-compatible with mehran_full_pyjhora.json)."""

    utils.set_language(language)
    ayanamsa_mode = (ayanamsa_mode or "LAHIRI").upper()
    place = drik.Place(location_name, bc.latitude, bc.longitude, bc.utc_offset_hours)
    engine_version = _load_engine_version()
    generated_at = datetime.now(timezone.utc).isoformat()

    core_chart_summary = compute_core_chart(bc, ayanamsa_mode=ayanamsa_mode)
    drik.set_ayanamsa_mode(ayanamsa_mode, jd=bc.jd_local)
    core_chart_summary["ayanamsa_value_deg"] = drik.get_ayanamsa_value(bc.jd_local)
    rasi_snapshot = _build_chart_snapshot(bc.jd_local, place, ayanamsa_mode)
    core_chart_summary["lagna"] = rasi_snapshot["lagna"]
    core_chart_summary["planets_detail"] = rasi_snapshot["planets"]
    core_chart_summary["house_occupancy"] = _format_house_occupancy(
        rasi_snapshot["raw_positions"]
    )

    panchanga = _compute_panchanga(bc.jd_local, place)

    vargas = {}
    factors = varga_factors or DEFAULT_VARGA_FACTORS
    for label, factor in factors.items():
        vargas[label] = _build_chart_snapshot(bc.jd_local, place, ayanamsa_mode, factor)

    base_context = {
        "birth_context": bc,
        "place": place,
        "ayanamsa_mode": ayanamsa_mode,
        "rasi_raw_positions": rasi_snapshot["raw_positions"],
        "location_name": location_name,
        "vargas": vargas,
    }

    planet_status_block: Dict[str, Any] = {}
    d1_varga = vargas.get("D1")
    if d1_varga:
        planet_status_block["D1"] = compute_planet_status_for_d1(d1_varga, vargas.get("D9"))

    config = extraction_config or {}
    strength_config = config.get("strength") or {}
    include_optional = strength_config.get("include_optional")
    if include_optional is None:
        include_optional = strength_config.get("include_extra")
    include_systems = strength_config.get("systems")
    strength_block = compute_strength_all(
        base_context,
        active_only=not include_optional,
        include=include_systems,
    )
    ashtaka = strength_block.get("ashtakavarga")

    dashas = _format_vimshottari(bc.jd_local, place)
    vim_timeline = build_vimshottari_timeline(bc.jd_local, place)
    yoga_block = yoga_extract.compute_yoga_block(bc, lang=language)

    payload = {
        "meta": {
            "engine_version": engine_version,
            "generated_at_utc": generated_at,
            "jd_mode": "LOCAL_WITH_DST",
            "jd_utc": bc.jd_utc,
            "jd_local": bc.jd_local,
        },
        "birth_data": {
            "person": person,
            "datetime_local": bc.dt_local.isoformat(),
            "datetime_utc": bc.dt_utc.isoformat(),
            "timezone_name": bc.tz_name,
            "utc_offset_hours": bc.utc_offset_hours,
            "location": {
                "name": location_name,
                "lat": bc.latitude,
                "lon": bc.longitude,
            },
        },
        "core_chart": core_chart_summary,
        "panchanga_at_birth": panchanga,
        "vargas": vargas,
        "ashtakavarga": ashtaka,
        "strength": strength_block,
        "dashas": {"vimshottari": dashas},
        "vimshottari_full": asdict(vim_timeline),
        "yogas_pyjhora": yoga_block,
    }
    dasha_cfg = config.get("dasha") or {}
    requested_systems = dasha_cfg.get("systems") or []
    if requested_systems:
        systems_normalized = [str(label).upper() for label in requested_systems]
        birth_snapshot = {"birth_data": payload["birth_data"]}
        timelines = build_all_dasha_timelines(birth_snapshot, systems=systems_normalized)
        payload["dashas"]["systems"] = {
            system: {
                "schema_version": timeline.schema_version,
                "engine": timeline.engine,
                "system_type": timeline.system_type,
                "levels": timeline.levels,
                "timeline": [
                    {
                        "level": period.level,
                        "lord": period.lord,
                        "sublord": period.sublord,
                        "start_jd": period.start_jd,
                        "end_jd": period.end_jd,
                        "start_iso": period.start_iso,
                        "end_iso": period.end_iso,
                    }
                    for period in timeline.periods
                ],
            }
            for system, timeline in timelines.items()
        }
    if planet_status_block:
        payload["planet_status"] = planet_status_block
    if payload.get("ashtakavarga") is None:
        from v0min.strength import ashtakavarga as ashtakavarga_module

        payload["ashtakavarga"] = ashtakavarga_module.compute(base_context).get("ashtakavarga")
    if panchanga_calendar_range:
        start, end = panchanga_calendar_range
        payload["panchanga_calendar"] = panchanga_calendar_extract.build_panchanga_calendar(
            bc,
            start,
            end,
        )
    if config.get("include_house_status"):
        payload["houses"] = compute_house_status_all_vargas(base_context)
    if config.get("include_aspects"):
        payload.setdefault("aspects", {})
        payload["aspects"]["D1"] = compute_aspects_for_varga(base_context, "D1")

    if _config_enabled(config.get("dosha")):
        payload["dosha"] = compute_dosha_block(payload, base_context)
    if _config_enabled(config.get("raja_yoga")):
        payload["raja_yoga"] = compute_raja_yoga_block(payload, base_context)
    sp_cfg = config.get("special_points") or {}
    if _config_enabled(sp_cfg):
        payload["special_points"] = compute_special_points_block(payload, base_context, config=sp_cfg)
    bhava_cfg = config.get("bhava_systems") or {}
    if _config_enabled(bhava_cfg):
        cfg_obj = BhavaSystemsConfig.from_dict(bhava_cfg)
        payload["bhava_systems"] = compute_bhava_systems_from_payload(payload, cfg_obj)
    karaka_cfg = config.get("karakas") or {}
    if _config_enabled(karaka_cfg):
        cfg_obj = KarakasConfig.from_dict(karaka_cfg)
        payload["karakas"] = compute_karakas_from_payload(payload, cfg_obj)
    friendship_cfg = config.get("planet_friendships") or {}
    if _config_enabled(friendship_cfg):
        cfg_obj = PlanetFriendshipsConfig.from_dict(friendship_cfg)
        payload["planet_friendships"] = compute_planet_friendships_from_payload(payload, cfg_obj)
    strength_trends_cfg = config.get("strength_trends") or {}
    if _config_enabled(strength_trends_cfg):
        cfg_obj = StrengthTrendsConfig.from_dict(strength_trends_cfg)
        payload["strength_trends"] = compute_strength_trends_from_payload(payload, cfg_obj)
    pred_cfg = config.get("predictions") or {}
    if _config_enabled(pred_cfg):
        pred_cfg_local = dict(pred_cfg)
        pred_cfg_local.setdefault("language", language)
        payload["predictions"] = compute_predictions_block(payload, pred_cfg_local)
    panchanga_cfg = config.get("panchanga_extras") or {}
    if _config_enabled(panchanga_cfg):
        payload["panchanga_extras"] = compute_panchanga_extras_block(payload, panchanga_cfg)
    muhurta_cfg = config.get("muhurta") or {}
    if _config_enabled(muhurta_cfg):
        mh_config = MuhurtaConfig.from_dict(muhurta_cfg)
        payload["muhurta"] = compute_muhurta_windows(payload, mh_config)
    events_cfg = config.get("events") or {}
    if _config_enabled(events_cfg):
        cfg_obj = EventScanConfig.from_dict(events_cfg)
        payload["events"] = compute_events_snapshot(payload, cfg_obj)
    chakra_cfg = config.get("chakra") or {}
    if _config_enabled(chakra_cfg):
        cfg_obj = ChakraConfig.from_dict(chakra_cfg)
        payload["chakra"] = compute_chakra_snapshot(payload, cfg_obj)
    prasna_cfg = config.get("prasna") or {}
    if _config_enabled(prasna_cfg):
        scheme = str(prasna_cfg.get("scheme") or prasna_cfg.get("mode") or "KP_249").upper()
        base_seed_mode = str(prasna_cfg.get("seed_mode") or prasna_cfg.get("seed_source") or "").lower()
        kp_depth = prasna_cfg.get("kp_chain_max_depth")
        base_time_override = prasna_cfg.get("time_override")
        base_random_seed = prasna_cfg.get("random_seed")
        entries = prasna_cfg.get("numbers")
        if not entries:
            entries = [None]
        snapshots: Dict[str, object] = {}
        resolved_numbers: List[int] = []
        for entry in entries:
            entry_cfg: Dict[str, object] = {}
            manual_number: Optional[int] = None
            if isinstance(entry, dict):
                entry_cfg = entry
                manual_number = entry_cfg.get("number")
            elif entry is not None:
                manual_number = int(entry)
            seed_mode = entry_cfg.get("seed_mode") or base_seed_mode
            time_override = entry_cfg.get("time_override", base_time_override)
            random_seed = entry_cfg.get("random_seed", base_random_seed)
            depth_override = entry_cfg.get("kp_chain_max_depth", kp_depth)
            resolved_mode = seed_mode or ("manual" if manual_number is not None else "time_seed")
            if resolved_mode == "manual" and manual_number is None:
                resolved_mode = "time_seed"
            config_obj = PrasnaConfig(
                scheme=scheme,
                seed_mode=resolved_mode,
                manual_number=manual_number,
                time_override=time_override,
                random_seed=random_seed,
                kp_chain_max_depth=depth_override,
            )
            snapshot = compute_prasna_snapshot(payload, config=config_obj)
            snapshots[str(snapshot["number"])] = snapshot
            resolved_numbers.append(snapshot["number"])
        payload["prasna"] = {
            "mode": scheme,
            "numbers": resolved_numbers,
            "seed_source": base_seed_mode or None,
            "snapshots": snapshots,
        }

    yogas_extended_cfg = config.get("yogas_extended") or {}
    if _config_enabled(yogas_extended_cfg):
        cfg_obj = YogasExtendedConfig.from_dict(yogas_extended_cfg)
        payload["yogas_extended"] = compute_yogas_extended_from_payload(payload, cfg_obj)

    varshaphal_cfg = config.get("varshaphal") or {}
    years = varshaphal_cfg.get("years") or []
    if years:
        varshaphal_payload: Dict[str, Any] = {}
        include_maasa = bool(varshaphal_cfg.get("include_maasa"))
        include_sixty_hour = bool(varshaphal_cfg.get("include_sixty_hour"))
        maasa_months = varshaphal_cfg.get("maasa_months")
        sixty_indices = varshaphal_cfg.get("sixty_indices")
        for year_value in years:
            year_int = int(year_value)
            snapshot = compute_varshaphal_snapshot(base_context, year_int)
            needs_maasa = include_maasa or bool(maasa_months)
            needs_sixty = include_sixty_hour or bool(sixty_indices)
            if needs_maasa or needs_sixty:
                snapshot["subperiods"] = compute_varshaphal_subperiods(
                    base_context,
                    year_int,
                    include_maasa=needs_maasa,
                    include_sixty_hour=needs_sixty,
                    maasa_months=maasa_months,
                    sixty_indices=sixty_indices,
                )
            varshaphal_payload[str(year_int)] = snapshot
        payload["varshaphal"] = varshaphal_payload

    return payload


def summarize_payload(payload: Dict[str, object], max_dasha_rows: int = 5) -> List[str]:
    """Return a list of human-readable summary lines for printing."""

    birth = payload["birth_data"]
    meta = payload["meta"]
    core_chart = payload["core_chart"]
    panchanga = payload["panchanga_at_birth"]
    dashas = payload["dashas"]["vimshottari"]

    lagna = core_chart["lagna"]
    tithi = panchanga["tithi"]
    nakshatra = panchanga["nakshatra"]

    lines = [
        f"Full PyJHora dump – {birth['person']}",
        "----------------------------------------",
        f"Local datetime: {birth['datetime_local']}",
        f"JD (local): {meta['jd_local']}",
        f"Lagna (D1): {lagna['sign']} {lagna['deg_dms']} ({core_chart['lagna_longitude_deg']:.6f}°)",
        f"Tithi: {tithi['name']} ({tithi['elapsed_percent']:.2f}% elapsed)",
        f"Nakshatra: {nakshatra['name']} pada {nakshatra['pada']} ({nakshatra['elapsed_percent']:.2f}% elapsed)",
        "First five Vimshottari entries:",
    ]

    for row in dashas["sequence"][:max_dasha_rows]:
        lines.append(f"  {row['start']} – {row['mahadasha_lord']} / {row['antardasha_lord']}")
    return lines


def save_payload(payload: Dict[str, object], path: Path) -> None:
    """Persist payload as pretty JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


__all__ = [
    "build_full_pyjhora_payload",
    "summarize_payload",
    "save_payload",
]
