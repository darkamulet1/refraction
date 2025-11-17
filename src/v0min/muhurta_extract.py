from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import pytz

from jhora import const, utils

from v0min import payload_utils
from v0min.core_space import compute_core_chart
from v0min.core_time import BirthContext, make_birth_context
from v0min.panchanga_calendar_extract import build_panchanga_calendar


PANCHANGA_KEYS = ("rahukalam", "yamaganda", "gulika")
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFICS = {"Saturn", "Mars", "Rahu", "Ketu", "Sun"}


DEFAULT_RULE_WEIGHTS = {
    "RAHUKALAM": -80.0,
    "YAMAKANDA": -60.0,
    "GULIKA": -50.0,
    "FAVORABLE_TITHI": 15.0,
    "UNFAVORABLE_TITHI": -20.0,
    "BENEFIC_LAGNA": 20.0,
    "MALEFIC_LAGNA": -25.0,
    "BENEFIC_ANGLES": 12.0,
    "MALEFIC_ANGLES": -18.0,
    "TRAVEL_HOUSES_BENEFIC": 12.0,
    "TRAVEL_HOUSES_MALEFIC": -14.0,
}

ACTIVITY_PROFILES = {
    "CLASS_START": {
        "favorable_tithis": {2, 3, 5, 6, 10, 11},
        "avoid_tithis": {4, 8, 12, 14, 29, 30},
        "use_angle_rules": True,
        "use_travel_rules": False,
    },
    "PROJECT_LAUNCH": {
        "favorable_tithis": {2, 3, 5, 6, 10, 11, 16},
        "avoid_tithis": {4, 8, 12, 14, 29, 30},
        "use_angle_rules": True,
        "use_travel_rules": False,
    },
    "TRAVEL": {
        "favorable_tithis": {3, 5, 7, 9, 15, 17},
        "avoid_tithis": {1, 4, 8, 12, 29, 30},
        "use_angle_rules": False,
        "use_travel_rules": True,
    },
    "GENERIC": {
        "favorable_tithis": {2, 3, 5, 7, 10, 11, 13},
        "avoid_tithis": {4, 8, 12, 29, 30},
        "use_angle_rules": True,
        "use_travel_rules": False,
    },
}


@dataclass
class MuhurtaWindow:
    start_iso: str
    end_iso: str
    score: float
    tier: str
    reasons: List[str] = field(default_factory=list)


@dataclass
class MuhurtaConfig:
    activity_type: str
    start_date: str
    end_date: str
    step_minutes: int = 30
    max_windows: Optional[int] = 50
    weights: Optional[Dict[str, float]] = None

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "MuhurtaConfig":
        return MuhurtaConfig(
            activity_type=str(data.get("activity_type", "CLASS_START")),
            start_date=str(data["start_date"]),
            end_date=str(data["end_date"]),
            step_minutes=int(data.get("step_minutes", 30)),
            max_windows=data.get("max_windows"),
            weights=data.get("weights"),
        )


class MuhurtaScorer:
    def __init__(self, config: MuhurtaConfig, base_context: BirthContext, ayanamsa_mode: str):
        self.config = config
        self.weights = dict(DEFAULT_RULE_WEIGHTS)
        if config.weights:
            self.weights.update(config.weights)
        activity_key = config.activity_type.upper()
        self.profile = ACTIVITY_PROFILES.get(activity_key, ACTIVITY_PROFILES["GENERIC"])
        self.base_context = base_context
        self.ayanamsa_mode = ayanamsa_mode
        self.tz = pytz.timezone(base_context.tz_name)

    def score_window(
        self,
        window_start: datetime,
        window_end: datetime,
        day_entry: Dict[str, object],
    ) -> Tuple[float, List[str]]:
        reasons: List[str] = []
        score = 0.0
        tithi_id = int(day_entry.get("tithi", {}).get("id", 0))
        if tithi_id in self.profile["favorable_tithis"]:
            score += self.weights["FAVORABLE_TITHI"]
            reasons.append("FAVORABLE_TITHI")
        if tithi_id in self.profile["avoid_tithis"]:
            score += self.weights["UNFAVORABLE_TITHI"]
            reasons.append("UNFAVORABLE_TITHI")
        for key in PANCHANGA_KEYS:
            if self._window_overlaps_interval(window_start, window_end, day_entry.get(key, []), self.tz):
                weight_key = key.upper()
                score += self.weights.get(weight_key, 0.0)
                reasons.append(weight_key)
        transit_chart = self._compute_transit_chart(window_start)
        lagna_sign_idx = int(transit_chart["lagna_longitude_deg"] // 30.0) % 12
        houses = self._build_house_map(transit_chart["planets"], lagna_sign_idx)
        if self.profile["use_angle_rules"]:
            score += self._score_angle_rules(houses, reasons)
        if self.profile["use_travel_rules"]:
            score += self._score_travel_rules(houses, reasons)
        return score, reasons

    def _score_angle_rules(self, houses: Dict[int, List[str]], reasons: List[str]) -> float:
        delta = 0.0
        lagna_benefics = [p for p in houses.get(1, []) if p in BENEFICS]
        lagna_malefics = [p for p in houses.get(1, []) if p in MALEFICS]
        angular_benefics = [p for house in (1, 10) for p in houses.get(house, []) if p in BENEFICS]
        angular_malefics = [p for house in (1, 10) for p in houses.get(house, []) if p in MALEFICS]
        if lagna_benefics:
            delta += self.weights["BENEFIC_LAGNA"]
            reasons.append("BENEFIC_LAGNA")
        if lagna_malefics:
            delta += self.weights["MALEFIC_LAGNA"]
            reasons.append("MALEFIC_LAGNA")
        if angular_benefics:
            delta += self.weights["BENEFIC_ANGLES"]
            reasons.append("BENEFIC_ANGLES")
        if angular_malefics:
            delta += self.weights["MALEFIC_ANGLES"]
            reasons.append("MALEFIC_ANGLES")
        return delta

    def _score_travel_rules(self, houses: Dict[int, List[str]], reasons: List[str]) -> float:
        delta = 0.0
        travel_houses = (3, 9, 12)
        benefics = [p for house in travel_houses for p in houses.get(house, []) if p in BENEFICS]
        malefics = [p for house in travel_houses for p in houses.get(house, []) if p in MALEFICS]
        if benefics:
            delta += self.weights["TRAVEL_HOUSES_BENEFIC"]
            reasons.append("TRAVEL_HOUSES_BENEFIC")
        if malefics:
            delta += self.weights["TRAVEL_HOUSES_MALEFIC"]
            reasons.append("TRAVEL_HOUSES_MALEFIC")
        return delta

    def _compute_transit_chart(self, dt_local: datetime) -> Dict[str, object]:
        tz = pytz.timezone(self.base_context.tz_name)
        localized = dt_local.astimezone(tz)
        naive = localized.replace(tzinfo=None)
        context = make_birth_context(
            naive,
            self.base_context.latitude,
            self.base_context.longitude,
            tz_name=self.base_context.tz_name,
            location_name=self.base_context.location_name,
        )
        return compute_core_chart(context, ayanamsa_mode=self.ayanamsa_mode)

    @staticmethod
    def _build_house_map(planets: Dict[str, float], lagna_sign_idx: int) -> Dict[int, List[str]]:
        houses: Dict[int, List[str]] = {}
        for name, longitude in planets.items():
            sign_idx = int(longitude // 30.0) % 12
            house = ((sign_idx - lagna_sign_idx) % 12) + 1
            houses.setdefault(house, []).append(name)
        return houses

    @staticmethod
    @staticmethod
    def _window_overlaps_interval(
        start: datetime,
        end: datetime,
        blocks: List[Dict[str, object]],
        tz,
    ) -> bool:
        if not blocks:
            return False
        for block in blocks:
            block_start = MuhurtaScorer._combine_datetime(start.date(), block.get("start_local"), tz)
            block_end = MuhurtaScorer._combine_datetime(start.date(), block.get("end_local"), tz)
            if block_start and block_end and end > block_start and start < block_end:
                return True
        return False

    @staticmethod
    def _combine_datetime(day: date, time_str: Optional[str], tzinfo) -> Optional[datetime]:
        if not time_str:
            return None
        try:
            hours, minutes, seconds = [int(part) for part in time_str.split(":")]
        except ValueError:
            return None
        dt = datetime(day.year, day.month, day.day, hours, minutes, seconds)
        if tzinfo:
            return tzinfo.localize(dt)
        return dt


def _tier_for_score(score: float) -> str:
    if score <= -30:
        return "AVOID"
    if score < 10:
        return "NEUTRAL"
    if score < 40:
        return "GOOD"
    return "EXCELLENT"


def compute_muhurta_windows(natal_payload: Dict[str, object], config: MuhurtaConfig) -> Dict[str, object]:
    previous_language = _get_current_language()
    utils.set_language("en")
    try:
        bc, place = payload_utils.build_birth_context_from_payload(natal_payload)
        ayanamsa_mode = natal_payload.get("core_chart", {}).get("ayanamsa_mode", "LAHIRI")
        tz = pytz.timezone(bc.tz_name)
        start_date = datetime.strptime(config.start_date, "%Y-%m-%d").date()
        end_date = datetime.strptime(config.end_date, "%Y-%m-%d").date()
        calendar = build_panchanga_calendar(bc, start_date, end_date)
        day_map = calendar.get("days", {})
        start_dt = tz.localize(datetime.combine(start_date, datetime.min.time()))
        end_dt = tz.localize(datetime.combine(end_date + timedelta(days=1), datetime.min.time()))
        step = timedelta(minutes=config.step_minutes)
        scorer = MuhurtaScorer(config, bc, ayanamsa_mode)
        windows: List[MuhurtaWindow] = []
        current = start_dt
        while current < end_dt:
            next_dt = min(current + step, end_dt)
            day_entry = day_map.get(current.date().isoformat())
            if day_entry:
                score, reasons = scorer.score_window(current, next_dt, day_entry)
                tier = _tier_for_score(score)
                windows.append(
                    MuhurtaWindow(
                        start_iso=current.isoformat(),
                        end_iso=next_dt.isoformat(),
                        score=round(score, 2),
                        tier=tier,
                        reasons=reasons,
                    )
                )
            current = next_dt
        windows.sort(key=lambda w: (-w.score, w.start_iso))
        if config.max_windows is not None:
            windows = windows[: int(config.max_windows)]
        return {
            "schema_version": "muhurta.v1",
            "activity_type": config.activity_type,
            "range": {
                "start_date": config.start_date,
                "end_date": config.end_date,
            },
            "step_minutes": config.step_minutes,
            "windows": [window.__dict__ for window in windows],
        }
    finally:
        if previous_language:
            utils.set_language(previous_language)


def _get_current_language() -> str:
    if hasattr(utils, "language"):
        lang = getattr(utils, "language")
        if isinstance(lang, str) and lang:
            return lang
    return getattr(const, "_DEFAULT_LANGUAGE", "en")


__all__ = [
    "MuhurtaConfig",
    "MuhurtaWindow",
    "compute_muhurta_windows",
]
