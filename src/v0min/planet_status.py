from __future__ import annotations

from typing import Any, Dict, Optional

from jhora.horoscope.chart import charts

PLANET_ID_TO_NAME = {
    0: "Sun",
    1: "Moon",
    2: "Mars",
    3: "Mercury",
    4: "Jupiter",
    5: "Venus",
    6: "Saturn",
    7: "Rahu",
    8: "Ketu",
}

SANDHI_THRESHOLD_DEG = 1.0

DIGNITY_RULES = {
    "Sun": {
        "exalt": 0,
        "debilitation": 6,
        "moolatrikona": 4,
        "own": [4],
    },
    "Moon": {
        "exalt": 1,
        "debilitation": 7,
        "moolatrikona": 1,
        "own": [3],
    },
    "Mars": {
        "exalt": 9,
        "debilitation": 3,
        "moolatrikona": 0,
        "own": [0, 7],
    },
    "Mercury": {
        "exalt": 5,
        "debilitation": 11,
        "moolatrikona": 5,
        "own": [2, 5],
    },
    "Jupiter": {
        "exalt": 3,
        "debilitation": 9,
        "moolatrikona": 8,
        "own": [8, 11],
    },
    "Venus": {
        "exalt": 11,
        "debilitation": 5,
        "moolatrikona": 6,
        "own": [1, 6],
    },
    "Saturn": {
        "exalt": 6,
        "debilitation": 0,
        "moolatrikona": 10,
        "own": [9, 10],
    },
}


def _parse_positions(raw_positions: Optional[list]) -> Dict[int, tuple[int, float]]:
    mapping: Dict[int, tuple[int, float]] = {}
    if not raw_positions:
        return mapping
    for entry in raw_positions:
        pid, coord = entry
        if isinstance(pid, str):
            continue
        sign_idx, deg_in_sign = coord
        mapping[int(pid)] = (int(sign_idx), float(deg_in_sign))
    return mapping


def _is_sandhi(deg_in_sign: float) -> bool:
    return deg_in_sign < SANDHI_THRESHOLD_DEG or (30.0 - deg_in_sign) < SANDHI_THRESHOLD_DEG


def _determine_dignity(planet_name: str, sign_idx: int) -> str:
    if planet_name in ("Rahu", "Ketu"):
        return "NEUTRAL"
    rules = DIGNITY_RULES.get(planet_name)
    if not rules:
        return "NEUTRAL"
    if sign_idx == rules.get("exalt"):
        return "EXALTED"
    if sign_idx == rules.get("debilitation"):
        return "DEBILITATED"
    if sign_idx == rules.get("moolatrikona"):
        return "MOOLATRIKONA"
    if sign_idx in rules.get("own", []):
        return "OWN_SIGN"
    return "NEUTRAL"


def compute_planet_status_for_d1(
    d1_snapshot: Dict[str, Any],
    d9_snapshot: Optional[Dict[str, Any]] = None,
) -> Dict[str, Dict[str, Any]]:
    """
    Compute retrograde/combust/dignity/vargottama/sandhi flags for D1 planets.
    """

    if not d1_snapshot:
        return {}
    raw_positions = d1_snapshot.get("raw_positions")
    if not raw_positions:
        return {}

    d1_positions = _parse_positions(raw_positions)
    d9_positions = _parse_positions(d9_snapshot.get("raw_positions") if d9_snapshot else None)

    retrograde_ids = set(charts.planets_in_retrograde(raw_positions))
    combust_ids = set(charts.planets_in_combustion(raw_positions))

    status: Dict[str, Dict[str, Any]] = {}
    for pid, name in PLANET_ID_TO_NAME.items():
        coord = d1_positions.get(pid)
        if not coord:
            continue
        sign_idx, deg_in_sign = coord
        vargottama = False
        if pid in d9_positions:
            vargottama = d9_positions[pid][0] == sign_idx

        planet_status = {
            "retrograde": pid in retrograde_ids,
            "combust": pid in combust_ids,
            "dignity": _determine_dignity(name, sign_idx),
            "vargottama": bool(vargottama),
            "sandhi": _is_sandhi(deg_in_sign),
        }

        if name in ("Rahu", "Ketu"):
            planet_status["retrograde"] = False
            planet_status["combust"] = False

        status[name] = planet_status

    return status


__all__ = ["compute_planet_status_for_d1"]
