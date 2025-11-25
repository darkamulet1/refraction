"""Yogas extractor based on PyJHora outputs - Refactored with defensive utilities."""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .core_chart import run_core_chart
from .constants import (
    KENDRA_HOUSES,
    PANCHA_MAHAPURUSHA_DEFINITIONS,
    ALL_WEALTH_SIGNS,
    STRENGTH_POINTS,
    MALEFIC_PENALTY,
)
from .planet_utils import create_planet_lookup, get_planet_from_lookup
from .validators import validate_planet_positions_safe

logger = logging.getLogger(__name__)


def run_yogas(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Produce the yogas payload aligned to yogas_spec_v1.
    
    Enhanced with defensive validation and efficient planet lookups.
    """
    # Get core chart
    core_chart = run_core_chart(payload)
    
    # Select and validate primary frame
    frame = _select_primary_frame(core_chart)
    planets = frame.get("planets", [])
    houses = frame.get("houses", [])
    
    # Optional: Validate planet structure (can be disabled for performance)
    valid, error = validate_planet_positions_safe(planets)
    if not valid:
        logger.warning(f"Planet structure validation warning: {error}")
    
    # Create efficient planet lookup dictionary (O(1) access instead of O(n))
    planet_lookup = create_planet_lookup(planets)
    
    # Detect yogas using lookup
    yogas: List[Dict[str, Any]] = []
    for detector in [
        _detect_gaja_kesari(planet_lookup),
        _detect_kala_sarpa(planet_lookup, planets, houses),
        _detect_kemadruma(planet_lookup),
        _detect_raja_yogas(planet_lookup),
        _detect_budhaditya(planet_lookup),
        _detect_chandra_mangala(planet_lookup),
        _detect_adhi_yoga(planet_lookup),
    ]:
        if detector:
            yogas.append(detector)
    
    # Detect multi-result yogas
    yogas.extend(_detect_pancha_mahapurusha(planet_lookup))
    yogas.extend(_detect_dhana_yogas(planet_lookup))
    
    # Create summary
    summary = _create_summary(yogas)
    
    return {
        "meta": {
            "schema_version": "yogas_spec_v1",
            "timestamp_utc": datetime.utcnow().isoformat() + "Z",
            "jd_utc": frame.get("jd") or core_chart["meta"].get("jd_utc"),
            "ayanamsa_deg": core_chart["meta"].get("ayanamsa_deg"),
        },
        "person": core_chart.get("person", {}),
        "config_echo": core_chart.get("config_echo", {}),
        "frames": {"yogas": yogas, "summary": summary},
    }


def _select_primary_frame(core_chart: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select primary natal frame from core chart.
    
    Enhanced with validation and better error messages.
    """
    frames = core_chart.get("frames")
    
    # Handle list format
    if isinstance(frames, list):
        if not frames:
            raise ValueError("Core chart frames list is empty")
        return frames[0]
    
    # Handle nested dict format
    if isinstance(frames, dict):
        nested = frames.get("frames")
        if isinstance(nested, list):
            if not nested:
                raise ValueError("Core chart nested frames list is empty")
            return nested[0]
    
    raise ValueError(
        f"Core chart frames structure is invalid: "
        f"expected list or dict with 'frames', got {type(frames).__name__}"
    )


def _get_planet(lookup: Dict[str, Dict], planet_id: str) -> Optional[Dict[str, Any]]:
    """
    Get planet from lookup dictionary.
    
    This is now O(1) instead of O(n) compared to old implementation.
    """
    return get_planet_from_lookup(lookup, planet_id)


def _in_kendra(house_a: Optional[int], house_b: Optional[int]) -> bool:
    """Check if two houses are in kendra (angular) relationship."""
    if house_a is None or house_b is None:
        return False
    diff = abs(house_a - house_b) % 12
    diff = diff if diff <= 6 else 12 - diff
    return diff in {0, 3}


# =============================================================================
# YOGA DETECTION FUNCTIONS
# =============================================================================


def _detect_gaja_kesari(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Gaja Kesari Yoga (Jupiter in kendra from Moon)."""
    jupiter = _get_planet(lookup, "JUPITER")
    moon = _get_planet(lookup, "MOON")
    
    if not jupiter or not moon:
        return None
    
    if _in_kendra(jupiter.get("house_index"), moon.get("house_index")):
        return {
            "id": "GAJA_KESARI",
            "name": "Gaja Kesari Yoga",
            "category": "WEALTH",
            "tier": 1,
            "planets": ["JUPITER", "MOON"],
            "description": "Jupiter in kendra from Moon",
            "strength": "STRONG",
            "active": True,
            "formation_details": {
                "jupiter_house": jupiter.get("house_index"),
                "moon_house": moon.get("house_index"),
                "angle": "kendra",
            },
        }
    return None


def _detect_pancha_mahapurusha(lookup: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Detect Pancha Mahapurusha Yogas (5 great person yogas)."""
    yogas: List[Dict[str, Any]] = []
    
    for planet_id, yoga_id, own_set, exalt_set in PANCHA_MAHAPURUSHA_DEFINITIONS:
        planet = _get_planet(lookup, planet_id)
        if not planet:
            continue
        
        house = planet.get("house_index")
        sign = planet.get("sign_name")
        
        # Must be in kendra (angular house)
        if house not in KENDRA_HOUSES or not sign:
            continue
        
        # Check dignity
        strength = "MODERATE"
        dignity = "own"
        
        if sign in exalt_set:
            strength = "STRONG"
            dignity = "exaltation"
        elif sign in own_set:
            strength = "MODERATE"
            dignity = "own"
        else:
            # Not in own or exalted sign
            continue
        
        yogas.append({
            "id": yoga_id,
            "name": planet_id.replace("_", " ").title(),
            "category": "PANCHA_MAHAPURUSHA",
            "tier": 1,
            "planet": planet_id,
            "description": f"{planet_id} in kendra with dignity",
            "strength": strength,
            "active": True,
            "formation_details": {
                "planet_sign": sign,
                "planet_house": house,
                "dignity": dignity,
            },
        })
    
    return yogas


def _detect_kala_sarpa(
    lookup: Dict[str, Dict],
    planets: List[Dict[str, Any]],
    houses: List[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    """Detect Kala Sarpa Dosha (all planets hemmed between Rahu-Ketu axis)."""
    rahu = _get_planet(lookup, "RAHU")
    if not rahu:
        return None
    
    rahu_long = rahu.get("longitude_deg")
    if rahu_long is None:
        return None
    
    # Ketu is always 180° opposite Rahu
    ketu_long = (rahu_long + 180) % 360
    
    # Get house indices
    rahu_house = _house_index_for_longitude(rahu_long, houses)
    ketu_house = _house_index_for_longitude(ketu_long, houses)
    
    # Check if all planets (except Rahu) are between the axis
    for planet in planets:
        if planet.get("id") == "RAHU":
            continue
        if not _is_between_axis(planet.get("longitude_deg"), rahu_long, ketu_long):
            return None
    
    return {
        "id": "KALA_SARPA",
        "name": "Kala Sarpa Dosha",
        "category": "DOSHA",
        "tier": 1,
        "planets": ["RAHU", "KETU"],
        "description": "All planets hemmed between Rahu-Ketu axis",
        "strength": "STRONG",
        "active": True,
        "malefic": True,
        "formation_details": {
            "type": "Anant",
            "rahu_house": rahu_house,
            "ketu_house": ketu_house,
        },
    }


def _detect_kemadruma(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Kemadruma Yoga (Moon isolated without planets in 2nd/12th)."""
    moon = _get_planet(lookup, "MOON")
    if not moon:
        return None
    
    moon_house = moon.get("house_index")
    if moon_house is None:
        return None
    
    # Calculate 2nd and 12th houses from Moon
    second = ((moon_house - 1 + 1) % 12) + 1
    twelfth = ((moon_house - 1 + 11) % 12) + 1
    
    # Get occupied houses (excluding Moon, Rahu, Ketu)
    occupied = set()
    for planet_id in ["SUN", "MARS", "MERCURY", "JUPITER", "VENUS", "SATURN"]:
        planet = _get_planet(lookup, planet_id)
        if planet:
            house = planet.get("house_index")
            if house is not None:
                occupied.add(house)
    
    # If 2nd and 12th are both empty, Kemadruma exists
    if second not in occupied and twelfth not in occupied:
        return {
            "id": "KEMADRUMA",
            "name": "Kemadruma Yoga",
            "category": "DOSHA",
            "tier": 1,
            "planet": "MOON",
            "description": "Moon isolated with no planets in 2nd/12th",
            "strength": "STRONG",
            "active": True,
            "malefic": True,
            "formation_details": {"moon_house": moon_house},
        }
    
    return None


def _detect_dhana_yogas(lookup: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Detect Dhana (wealth) yogas."""
    results: List[Dict[str, Any]] = []
    
    for planet_id, category in [("VENUS", "WEALTH"), ("JUPITER", "WEALTH")]:
        planet = _get_planet(lookup, planet_id)
        if not planet:
            continue
        
        sign = planet.get("sign_name")
        
        # Check if in favorable sign for wealth
        if sign in ALL_WEALTH_SIGNS:
            results.append({
                "id": f"DHANA_{planet_id}",
                "name": f"Dhana Yoga ({planet_id})",
                "category": category,
                "tier": 2,
                "planet": planet_id,
                "description": f"{planet_id} in benefic dignity",
                "strength": "MODERATE",
                "active": True,
                "formation_details": {
                    "planet_sign": sign,
                    "planet_house": planet.get("house_index"),
                },
            })
    
    return results


def _detect_raja_yogas(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Raja Yoga (Jupiter in angular house)."""
    jupiter = _get_planet(lookup, "JUPITER")
    if not jupiter:
        return None
    
    house = jupiter.get("house_index")
    
    if house in KENDRA_HOUSES:
        return {
            "id": "RAJA_JUPITER",
            "name": "Raja Yoga (Jupiter)",
            "category": "RAJA",
            "tier": 2,
            "planet": "JUPITER",
            "description": "Jupiter in angular house",
            "strength": "MODERATE",
            "active": True,
            "formation_details": {"planet_house": house},
        }
    
    return None


def _detect_budhaditya(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Budhaditya Yoga (Sun-Mercury conjunction)."""
    sun = _get_planet(lookup, "SUN")
    mercury = _get_planet(lookup, "MERCURY")
    
    if not sun or not mercury:
        return None
    
    if sun.get("sign_name") == mercury.get("sign_name"):
        return {
            "id": "BUDHADITYA",
            "name": "Budhaditya Yoga",
            "category": "SPECIAL",
            "tier": 3,
            "planets": ["SUN", "MERCURY"],
            "description": "Sun-Mercury conjunction",
            "strength": "MODERATE",
            "active": True,
            "formation_details": {"sign": sun.get("sign_name")},
        }
    
    return None


def _detect_chandra_mangala(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Chandra Mangala Yoga (Moon-Mars conjunction)."""
    moon = _get_planet(lookup, "MOON")
    mars = _get_planet(lookup, "MARS")
    
    if not moon or not mars:
        return None
    
    if moon.get("sign_name") == mars.get("sign_name"):
        return {
            "id": "CHANDRA_MANGALA",
            "name": "Chandra Mangala Yoga",
            "category": "WEALTH",
            "tier": 3,
            "planets": ["MOON", "MARS"],
            "description": "Moon-Mars conjunction",
            "strength": "MODERATE",
            "active": True,
            "formation_details": {"sign": moon.get("sign_name")},
        }
    
    return None


def _detect_adhi_yoga(lookup: Dict[str, Dict]) -> Optional[Dict[str, Any]]:
    """Detect Adhi Yoga (benefics in 6th, 7th, 8th from Moon)."""
    moon = _get_planet(lookup, "MOON")
    if not moon:
        return None
    
    moon_house = moon.get("house_index")
    if moon_house is None:
        return None
    
    benefics = ["MERCURY", "JUPITER", "VENUS"]
    distant = 0
    
    for planet_id in benefics:
        planet = _get_planet(lookup, planet_id)
        if not planet:
            continue
        if _is_benefic_in_six_seven_eight(moon_house, planet.get("house_index")):
            distant += 1
    
    if distant >= 2:
        return {
            "id": "ADHI",
            "name": "Adhi Yoga",
            "category": "SPECIAL",
            "tier": 4,
            "description": "Benefics around Moon",
            "strength": "MODERATE" if distant == 2 else "STRONG",
            "active": True,
            "formation_details": {"benefics": distant},
        }
    
    return None


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _is_benefic_in_six_seven_eight(moon_house: int, planet_house: Optional[int]) -> bool:
    """Check if planet is in 6th, 7th, or 8th house from Moon."""
    if planet_house is None:
        return False
    
    second_house = ((moon_house - 1 + 5) % 12) + 1
    third_house = ((moon_house - 1 + 6) % 12) + 1
    fourth_house = ((moon_house - 1 + 7) % 12) + 1
    
    return planet_house in {second_house, third_house, fourth_house}


def _house_index_for_longitude(
    longitude: Optional[float],
    houses: List[Dict[str, Any]]
) -> Optional[int]:
    """Calculate house index for a given longitude."""
    if longitude is None or not houses:
        return None
    
    lon = longitude % 360
    
    for house in houses:
        start = house.get("start_deg", 0) % 360
        end = house.get("end_deg", 0) % 360
        
        if start < end:
            if start <= lon < end:
                return house.get("index")
        else:
            # Wrap-around case
            if lon >= start or lon < end:
                return house.get("index")
    
    return None


def _is_between_axis(value: Optional[float], start: float, end: float) -> bool:
    """Check if a longitude value is between two axis points."""
    if value is None:
        return False
    
    value = value % 360
    start = start % 360
    end = end % 360
    
    if start <= end:
        return start <= value <= end
    
    # Wrap-around case
    return value >= start or value <= end


def _create_summary(yogas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create summary statistics from detected yogas."""
    total = len(yogas)
    active = sum(1 for y in yogas if y.get("active"))
    
    by_category: Dict[str, int] = {}
    by_tier: Dict[str, int] = {}
    malefic = 0
    strength_score = 0
    
    for yoga in yogas:
        # Count by category
        category = yoga.get("category")
        if category:
            by_category[category] = by_category.get(category, 0) + 1
        
        # Count by tier
        tier = str(yoga.get("tier", 0))
        by_tier[tier] = by_tier.get(tier, 0) + 1
        
        # Calculate strength score
        strength_score += STRENGTH_POINTS.get(yoga.get("strength"), 0)
        
        # Count malefics and apply penalty
        if yoga.get("malefic"):
            malefic += 1
            strength_score -= MALEFIC_PENALTY
    
    return {
        "total_yogas": total,
        "active_yogas": active,
        "by_category": by_category,
        "by_tier": by_tier,
        "strength_score": max(0, strength_score),
        "malefic_count": malefic,
    }
