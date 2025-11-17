from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from jhora import const, utils
from jhora.horoscope.chart import charts as charts_mod, house

from v0min.payload_utils import build_birth_context_from_payload, get_chart_positions

PLANET_FRIENDSHIPS_SCHEMA_VERSION = "planet_friendships.v1"
ENGINE_NAME = "PYJHORA_FRIENDSHIPS"

_PLANET_FALLBACK = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]


@dataclass
class PlanetFriendshipsConfig:
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "PlanetFriendshipsConfig":
        if not data:
            return cls()
        return cls(enabled=bool(data.get("enabled", True)))


def compute_planet_friendships_from_payload(
    full_payload: Dict[str, Any],
    config: Optional[PlanetFriendshipsConfig] = None,
) -> Dict[str, Any]:
    bc, place = build_birth_context_from_payload(full_payload)
    ayanamsa_mode = (full_payload.get("core_chart", {}) or {}).get("ayanamsa_mode", "LAHIRI")

    planet_positions = get_chart_positions(full_payload, "D1")
    if not planet_positions:
        planet_positions = charts_mod.rasi_chart(bc.jd_local, place, ayanamsa_mode=ayanamsa_mode)

    h_to_p = utils.get_house_planet_list_from_planet_positions(planet_positions)
    natural_friends = house.natural_friends_of_planets()
    natural_enemies = house.natural_enemies_of_planets()
    natural_neutral = house.natural_neutral_of_planets()
    temp_friends = house._get_temporary_friends_of_planets(h_to_p)  # type: ignore[attr-defined]
    temp_enemies = house._get_temporary_enemies_of_planets(h_to_p)  # type: ignore[attr-defined]

    planet_names = _get_planet_names()
    entries: List[Dict[str, Any]] = []
    for planet_id in range(9):
        natural_friend_names = _indexes_to_names(natural_friends[planet_id], planet_names)
        natural_enemy_names = _indexes_to_names(natural_enemies[planet_id], planet_names)
        temp_friend_names = _indexes_to_names(temp_friends.get(planet_id, []), planet_names)
        temp_enemy_names = _indexes_to_names(temp_enemies.get(planet_id, []), planet_names)
        net_result = _build_net_relation(
            planet_id,
            natural_friends[planet_id],
            natural_enemies[planet_id],
            temp_friends.get(planet_id, []),
            temp_enemies.get(planet_id, []),
            natural_neutral[planet_id],
            planet_names,
        )
        entries.append(
            {
                "planet": planet_names[planet_id],
                "natural_friends": natural_friend_names,
                "natural_enemies": natural_enemy_names,
                "temporary_friends": temp_friend_names,
                "temporary_enemies": temp_enemy_names,
                "net_result": net_result,
            }
        )

    return {
        "schema_version": PLANET_FRIENDSHIPS_SCHEMA_VERSION,
        "engine": ENGINE_NAME,
        "entries": entries,
    }


def _build_net_relation(
    planet_id: int,
    natural_friends: List[int],
    natural_enemies: List[int],
    temporary_friends: List[int],
    temporary_enemies: List[int],
    natural_neutral: List[int],
    planet_names: List[str],
) -> Dict[str, List[str]]:
    scores: Dict[int, int] = {}
    for target in range(9):
        if target == planet_id:
            continue
        score = 0
        if target in natural_friends:
            score += 1
        if target in natural_enemies:
            score -= 1
        if target in temporary_friends:
            score += 1
        if target in temporary_enemies:
            score -= 1
        # Neutral counts as slight friend bias
        if target in natural_neutral:
            score += 0
        if score != 0:
            scores[target] = score
    friends = [planet_names[idx] for idx, value in scores.items() if value > 0]
    enemies = [planet_names[idx] for idx, value in scores.items() if value < 0]
    return {"friends": sorted(set(friends)), "enemies": sorted(set(enemies))}


def _indexes_to_names(indexes: List[int], planet_names: List[str]) -> List[str]:
    names = []
    for idx in indexes:
        if 0 <= idx < len(planet_names):
            names.append(planet_names[idx])
    return names


def _get_planet_names() -> List[str]:
    names = getattr(utils, "PLANET_NAMES", None)
    if not names:
        names = list(_PLANET_FALLBACK)
    return names


__all__ = [
    "PLANET_FRIENDSHIPS_SCHEMA_VERSION",
    "PlanetFriendshipsConfig",
    "compute_planet_friendships_from_payload",
]
