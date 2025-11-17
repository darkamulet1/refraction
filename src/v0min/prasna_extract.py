
from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional, Tuple

import pytz

from jhora import const, utils
from jhora.horoscope.chart import charts
from jhora.panchanga import drik

from v0min import payload_utils
from v0min.core_time import BirthContext, make_birth_context

PRASNA_SCHEMA_VERSION = "prasna.v1"
PLANET_NAMES = list(getattr(utils, "PLANET_NAMES", []))
if not PLANET_NAMES:
    PLANET_NAMES = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

RAASI_NAMES = list(getattr(utils, "RAASI_LIST", []))
if not RAASI_NAMES:
    RAASI_NAMES = [
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

NAKSHATRA_NAMES = list(getattr(utils, "NAKSHATRA_LIST", []))
if not NAKSHATRA_NAMES:
    NAKSHATRA_NAMES = [
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

KP_LEVELS = ["nakshatra", "sub", "pratyanttara", "sookshma", "praana", "deha"]
SCHEME_LIMITS = {
    "PRASNA_108": 108,
    "KP_249": 249,
    "NAADI_1800": 1800,
}


@dataclass
class PrasnaConfig:
    scheme: Literal["PRASNA_108", "KP_249", "NAADI_1800"] = "KP_249"
    seed_mode: Literal["manual", "time_seed", "random"] = "manual"
    manual_number: Optional[int] = None
    time_override: Optional[str] = None
    random_seed: Optional[int] = None
    kp_chain_max_depth: Optional[int] = None
    place_override: Optional[drik.Place] = None

    @classmethod
    def from_legacy(
        cls,
        mode: Optional[str],
        number: Optional[int],
        seed_source: str,
        dt_override: Optional[datetime],
        place_override: Optional[drik.Place],
        kp_chain_max_depth: Optional[int],
    ) -> "PrasnaConfig":
        scheme = (mode or "KP_249").upper()
        seed_mode = seed_source.lower() if seed_source else "manual"
        time_override = dt_override.isoformat() if dt_override else None
        return cls(
            scheme=scheme if scheme in SCHEME_LIMITS else "KP_249",
            seed_mode=seed_mode if seed_mode in {"manual", "time_seed", "random"} else "manual",
            manual_number=number,
            time_override=time_override,
            kp_chain_max_depth=kp_chain_max_depth,
            place_override=place_override,
        )

    def resolve_datetime(self, tz_name: str) -> datetime:
        tz = pytz.timezone(tz_name)
        if self.time_override:
            dt = datetime.fromisoformat(self.time_override)
        else:
            dt = datetime.now(tz)
        if dt.tzinfo is None:
            return tz.localize(dt)
        return dt.astimezone(tz)


@dataclass
class KPAdhipathiLevel:
    level: str
    lord: str
    lord_id: int
    nakshatra: Optional[str] = None
    start_deg: Optional[float] = None
    end_deg: Optional[float] = None


@dataclass
class KPAdhipathiChain:
    kp_number: int
    scheme: str
    levels: List[KPAdhipathiLevel]


@dataclass
class PrasnaChartSummary:
    method: str
    number: int
    seed_source: str
    lagna: Dict[str, object]
    planets: Dict[str, Dict[str, object]]
    raw_positions: List[Tuple[object, Tuple[int, float]]]


def _angle_to_dict(sign_index: int, deg_in_sign: float) -> Dict[str, object]:
    absolute_deg = round(sign_index * 30.0 + deg_in_sign, 6)
    return {
        "sign_index": sign_index,
        "sign": RAASI_NAMES[sign_index],
        "deg_in_sign": round(deg_in_sign, 6),
        "deg_dms": utils.to_dms(deg_in_sign, is_lat_long="plong"),
        "absolute_deg": absolute_deg,
    }


def _normalize_datetime(value: datetime | str, tz_name: str) -> datetime:
    tz = pytz.timezone(tz_name)
    if isinstance(value, str):
        dt = datetime.fromisoformat(value)
    else:
        dt = value
    if dt.tzinfo is None:
        return tz.localize(dt)
    return dt.astimezone(tz)


def _build_prasna_context_from_birth_payload(
    natal_payload: Dict[str, object],
    *,
    dt_override: Optional[datetime] = None,
    place_override: Optional[drik.Place] = None,
) -> Tuple[BirthContext, drik.Place]:
    birth_bc, birth_place = payload_utils.build_birth_context_from_payload(natal_payload)
    target_place = place_override or birth_place
    tz_name = birth_bc.tz_name
    if dt_override is None:
        dt_local = datetime.now(pytz.timezone(tz_name))
    else:
        dt_local = _normalize_datetime(dt_override, tz_name)
    bc = make_birth_context(
        dt_local.replace(tzinfo=None),
        target_place.latitude,
        target_place.longitude,
        tz_name=tz_name,
        location_name=target_place.Place,
    )
    place = drik.Place(target_place.Place, target_place.latitude, target_place.longitude, target_place.timezone)
    return bc, place


def _lagna_override_from_number(mode: str, number: int) -> Tuple[int, float]:
    if mode == "KP_249":
        details = const.prasna_kp_249_dict[number]
        sign = int(details[0])
        start_deg = float(details[2])
        end_deg = float(details[3])
        return sign, (start_deg + end_deg) / 2.0
    if mode == "PRASNA_108":
        zero_based = number - 1
        sign = zero_based // 9
        segment = zero_based % 9
        width = 30.0 / 9.0
        return sign, segment * width + width / 2.0
    if mode == "NAADI_1800":
        zero_based = number - 1
        sign = zero_based // 150
        remainder = zero_based % 150
        width = 30.0 / 150.0
        return sign, remainder * width + width / 2.0
    raise ValueError(f"Unsupported prasna mode: {mode}")


def _validate_number(mode: str, number: int) -> None:
    ranges = {
        "PRASNA_108": (1, 108),
        "KP_249": (1, 249),
        "NAADI_1800": (1, 1800),
    }
    lo, hi = ranges[mode]
    if not (lo <= number <= hi):
        raise ValueError(f"{mode} number must be in [{lo}, {hi}]")


def _compute_kp_adhipathi_chain(
    sign_index: int,
    deg_in_sign: float,
    scheme: str,
) -> KPAdhipathiChain:
    kp_info = charts._get_KP_lords_from_planet_longitude("KP_PRASNA", sign_index, deg_in_sign)
    values = list(kp_info.values())[0]
    kp_number = int(values[0])
    level_planets = values[1:]
    level_names = KP_LEVELS
    details = const.prasna_kp_249_dict.get(kp_number)
    nakshatra_index = int(details[1]) if details else None
    nakshatra_name = (
        NAKSHATRA_NAMES[nakshatra_index] if nakshatra_index is not None and 0 <= nakshatra_index < len(NAKSHATRA_NAMES) else None
    )
    start_deg = float(details[2]) if details else None
    end_deg = float(details[3]) if details else None
    levels: List[KPAdhipathiLevel] = []
    for idx, planet_id in enumerate(level_planets):
        level = level_names[idx]
        name = PLANET_NAMES[planet_id]
        level_entry = KPAdhipathiLevel(
            level=level,
            lord=name,
            lord_id=int(planet_id),
            nakshatra=nakshatra_name if idx == 0 else None,
            start_deg=start_deg if idx == 0 else None,
            end_deg=end_deg if idx == 0 else None,
        )
        levels.append(level_entry)
    return KPAdhipathiChain(kp_number=kp_number, scheme=scheme, levels=levels)


def _build_chart_summary(
    planet_positions: List[Tuple[object, Tuple[int, float]]],
    lagna_sign: int,
    lagna_deg: float,
) -> PrasnaChartSummary:
    adjusted = planet_positions.copy()
    adjusted[0] = (adjusted[0][0], (lagna_sign, lagna_deg))
    lagna_info = _angle_to_dict(lagna_sign, lagna_deg)
    planets: Dict[str, Dict[str, object]] = {}
    for planet_id, (sign_idx, deg) in adjusted[1:]:
        name = PLANET_NAMES[int(planet_id)]
        planets[name] = _angle_to_dict(int(sign_idx), float(deg))
    return PrasnaChartSummary(
        method="",
        number=0,
        seed_source="manual",
        lagna=lagna_info,
        planets=planets,
        raw_positions=adjusted,
    )


def compute_prasna_snapshot(
    natal_payload: Dict[str, object],
    *,
    mode: Optional[Literal["PRASNA_108", "KP_249", "NAADI_1800"]] = None,
    number: Optional[int] = None,
    seed_source: str = "manual",
    dt_override: Optional[datetime] = None,
    place_override: Optional[drik.Place] = None,
    kp_chain_max_depth: Optional[int] = None,
    config: Optional[PrasnaConfig] = None,
) -> Dict[str, object]:
    active_config = config or PrasnaConfig.from_legacy(
        mode,
        number,
        seed_source,
        dt_override,
        place_override,
        kp_chain_max_depth,
    )
    return _compute_prasna_snapshot_with_config(natal_payload, active_config)


def _compute_prasna_snapshot_with_config(
    natal_payload: Dict[str, object],
    config: PrasnaConfig,
) -> Dict[str, object]:
    scheme = config.scheme.upper()
    base_context, _ = payload_utils.build_birth_context_from_payload(natal_payload)
    dt_local = config.resolve_datetime(base_context.tz_name)
    bc, place = _build_prasna_context_from_birth_payload(
        natal_payload,
        dt_override=dt_local,
        place_override=config.place_override,
    )
    ayanamsa_mode = natal_payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI")
    planet_positions = charts.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)
    effective_number, seed_info = _resolve_seed(config, scheme, dt_local)
    lagna_sign, lagna_deg = _lagna_override_from_number(scheme, effective_number)
    chart_summary = _build_chart_summary(planet_positions, lagna_sign, lagna_deg)
    chart_summary.method = scheme
    chart_summary.number = effective_number
    chart_summary.seed_source = config.seed_mode
    kp_chain = _compute_kp_adhipathi_chain(lagna_sign, lagna_deg, scheme)
    place_dict = {
        "name": place.Place,
        "lat": place.latitude,
        "lon": place.longitude,
        "timezone": bc.tz_name,
    }
    dt_local_iso = _normalize_datetime(bc.dt_local, bc.tz_name).isoformat()
    kp_levels = kp_chain.levels
    if config.kp_chain_max_depth is not None:
        kp_levels = kp_levels[: int(config.kp_chain_max_depth)]
    kp_summary = {
        "kp_chain": [{"level": level.level, "ruler": level.lord} for level in kp_levels],
        "primary_ruler": kp_levels[0].lord if kp_levels else None,
        "kp_number": kp_chain.kp_number,
    }
    return {
        "schema_version": PRASNA_SCHEMA_VERSION,
        "mode": scheme,
        "number": effective_number,
        "seed_source": config.seed_mode,
        "datetime_local": dt_local_iso,
        "place": place_dict,
        "meta": {"seed_info": seed_info},
        "chart": {
            "method": chart_summary.method,
            "number": chart_summary.number,
            "seed_source": chart_summary.seed_source,
            "lagna": chart_summary.lagna,
            "planets": chart_summary.planets,
            "raw_positions": chart_summary.raw_positions,
        },
        "kp_adhipathi": {
            "kp_number": kp_chain.kp_number,
            "scheme": kp_chain.scheme,
            "levels": [
                {
                    "level": level.level,
                    "lord": level.lord,
                    "lord_id": level.lord_id,
                    "nakshatra": level.nakshatra,
                    "start_deg": level.start_deg,
                    "end_deg": level.end_deg,
                }
                for level in kp_chain.levels
            ],
        },
        "kp": kp_summary,
    }


def _resolve_seed(config: PrasnaConfig, scheme: str, dt_local: datetime) -> Tuple[int, Dict[str, object]]:
    limit = SCHEME_LIMITS.get(scheme, 249)
    mode = config.seed_mode if config.seed_mode in {"manual", "time_seed", "random"} else "manual"
    if mode == "manual":
        if config.manual_number is None:
            raise ValueError("manual_number must be provided for manual seed mode.")
        number = config.manual_number
        _validate_number(scheme, number)
        return number, {
            "mode": "manual",
            "scheme": scheme,
            "number": number,
            "value": str(number),
            "random_seed": None,
            "source": "user_input",
        }
    if mode == "time_seed":
        reference_dt = dt_local
        timestamp = int(reference_dt.timestamp())
        number = (abs(timestamp) % limit) + 1
        _validate_number(scheme, number)
        return number, {
            "mode": "time_seed",
            "scheme": scheme,
            "number": number,
            "value": config.time_override or reference_dt.isoformat(),
            "random_seed": None,
            "source": "system_time",
        }
    seed_used = config.random_seed
    if seed_used is None:
        seed_used = int(datetime.now(timezone.utc).timestamp() * 1000)
    rng = random.Random(seed_used)
    number = rng.randint(1, limit)
    _validate_number(scheme, number)
    return number, {
        "mode": "random",
        "scheme": scheme,
        "number": number,
        "value": str(number),
        "random_seed": seed_used,
        "source": "python_random",
    }


__all__ = [
    "compute_prasna_snapshot",
    "PrasnaConfig",
    "PRASNA_SCHEMA_VERSION",
]
