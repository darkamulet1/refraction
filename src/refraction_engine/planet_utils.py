"""
Planet utilities for safe access to planet positions

This module provides safe helper functions for:
- Getting planet house numbers
- Getting planet rasi/degree values
- Converting planet names/indices
- Calculating house differences

Usage:
    from .planet_utils import get_planet_house, get_planet_rasi_degree
    
    mars_house = get_planet_house(positions, 'MARS')
    jupiter_rasi, jupiter_deg = get_planet_rasi_degree(positions, 'JUPITER')
"""

from typing import List, Tuple, Optional, Union, Dict
import logging

from .constants import PLANET_INDICES, PLANET_NAMES, PLANET_ALIASES
from .validators import validate_planet_positions

logger = logging.getLogger(__name__)


# =============================================================================
# PLANET LOOKUP UTILITIES
# =============================================================================

# =============================================================================
# PLANET LOOKUP UTILITIES
# =============================================================================


def create_planet_lookup(planets: List[Dict]) -> Dict[str, Dict]:
    """
    Create efficient planet lookup dictionary from planets list
    
    This is more efficient than iterating through the list repeatedly.
    
    Args:
        planets: List of planet dictionaries with "id" keys
    
    Returns:
        Dictionary mapping planet_id → planet dict
    
    Examples:
        >>> planets = [{"id": "SUN", "house": 1}, {"id": "MOON", "house": 5}]
        >>> lookup = create_planet_lookup(planets)
        >>> sun = lookup.get("SUN")
        >>> print(sun["house"])
        1
    """
    lookup = {}
    for planet in planets:
        planet_id = planet.get("id")
        if planet_id:
            # Normalize to uppercase
            planet_id_norm = planet_id.upper().strip()
            lookup[planet_id_norm] = planet
    return lookup


def get_planet_from_lookup(
    lookup: Dict[str, Dict],
    planet: Union[str, int]
) -> Optional[Dict]:
    """
    Get planet from lookup dictionary with normalization
    
    Args:
        lookup: Planet lookup dictionary from create_planet_lookup()
        planet: Planet name (str) or index (int)
    
    Returns:
        Planet dictionary or None if not found
    
    Examples:
        >>> lookup = create_planet_lookup(planets)
        >>> mars = get_planet_from_lookup(lookup, "mars")
        >>> mars = get_planet_from_lookup(lookup, 2)  # Also works
    """
    if isinstance(planet, str):
        planet_norm = normalize_planet_name(planet)
        return lookup.get(planet_norm)
    
    if isinstance(planet, int):
        planet_name = get_planet_name(planet)
        return lookup.get(planet_name)
    
    return None


def normalize_planet_name(planet: str) -> str:
    """
    Normalize planet name to canonical form
    
    Handles variations like:
    - "ragu" → "RAHU"
    - "kethu" → "KETU"
    - "Lagna" → "ASCENDANT"
    
    Args:
        planet: Planet name (case-insensitive)
    
    Returns:
        Normalized planet name
    
    Raises:
        ValueError: If planet name is not recognized
    
    Examples:
        >>> normalize_planet_name("mars")
        'MARS'
        >>> normalize_planet_name("RAGU")
        'RAHU'
    """
    if not isinstance(planet, str):
        raise ValueError(f"Planet must be string, got {type(planet).__name__}")
    
    # Convert to uppercase
    planet_upper = planet.upper().strip()
    
    # Check if it's already canonical
    if planet_upper in PLANET_NAMES:
        return planet_upper
    
    # Check aliases
    if planet_upper in PLANET_ALIASES:
        return PLANET_ALIASES[planet_upper]
    
    # Not found
    raise ValueError(f"Unknown planet: {planet}")


def get_planet_index(planet: Union[str, int]) -> int:
    """
    Get planet index from name or validate index
    
    Args:
        planet: Planet name (str) or index (int)
    
    Returns:
        Planet index (0-8)
    
    Raises:
        ValueError: If planet is invalid
    
    Examples:
        >>> get_planet_index('MARS')
        2
        >>> get_planet_index(2)
        2
    """
    if isinstance(planet, int):
        # Validate index
        if not (0 <= planet < len(PLANET_NAMES)):
            raise ValueError(
                f"Planet index out of range "
                f"(expected 0-{len(PLANET_NAMES)-1}, got {planet})"
            )
        return planet
    
    if isinstance(planet, str):
        # Normalize and lookup
        planet_norm = normalize_planet_name(planet)
        idx = PLANET_INDICES.get(planet_norm)
        
        if idx is None:
            raise ValueError(f"Unknown planet: {planet}")
        
        return idx
    
    raise ValueError(f"Planet must be str or int, got {type(planet).__name__}")


def get_planet_name(planet: Union[str, int]) -> str:
    """
    Get canonical planet name from index or name
    
    Args:
        planet: Planet name (str) or index (int)
    
    Returns:
        Canonical planet name
    
    Examples:
        >>> get_planet_name(0)
        'SUN'
        >>> get_planet_name('mars')
        'MARS'
        >>> get_planet_name('RAGU')
        'RAHU'
    """
    if isinstance(planet, str):
        return normalize_planet_name(planet)
    
    if isinstance(planet, int):
        if 0 <= planet < len(PLANET_NAMES):
            return PLANET_NAMES[planet]
        raise ValueError(f"Planet index out of range: {planet}")
    
    raise ValueError(f"Planet must be str or int, got {type(planet).__name__}")


# =============================================================================
# PLANET POSITION ACCESS
# =============================================================================

def get_planet_house(
    planet_positions: List,
    planet: Union[str, int],
    validate: bool = True
) -> int:
    """
    Get house number (0-11) for a specific planet with validation
    
    Args:
        planet_positions: PyJHora planet positions list
        planet: Planet name (str) or index (int)
        validate: Whether to validate structure first (default: True)
    
    Returns:
        House number (0-11, where 0 = first sign Aries)
    
    Raises:
        ValueError: If planet not found or invalid structure
    
    Examples:
        >>> positions = [(0, (6, 15.5), ...), ...]  # Sun in Libra
        >>> get_planet_house(positions, 'SUN')
        6
        >>> get_planet_house(positions, 0)  # Same, using index
        6
    """
    # Validate structure if requested
    if validate:
        validate_planet_positions(planet_positions, strict=False)
    
    # Get planet index
    idx = get_planet_index(planet)
    
    # Check if index is in range
    if idx >= len(planet_positions):
        planet_name = get_planet_name(planet)
        raise ValueError(
            f"Planet {planet_name} (index {idx}) not found in planet_positions "
            f"(length: {len(planet_positions)})"
        )
    
    # Extract rasi (house) from position
    try:
        pos = planet_positions[idx]
        rasi_deg = pos[1]
        rasi = rasi_deg[0]
        return rasi
    except (IndexError, TypeError) as e:
        planet_name = get_planet_name(planet)
        raise ValueError(
            f"Invalid structure for planet {planet_name} (index {idx}): {e}"
        )


def get_planet_rasi_degree(
    planet_positions: List,
    planet: Union[str, int],
    validate: bool = True
) -> Tuple[int, float]:
    """
    Get rasi (sign) and degree for a specific planet
    
    Args:
        planet_positions: PyJHora planet positions list
        planet: Planet name (str) or index (int)
        validate: Whether to validate structure first (default: True)
    
    Returns:
        Tuple of (rasi: int, degree: float)
        - rasi: 0-11 (Aries to Pisces)
        - degree: 0.0-30.0 within the sign
    
    Raises:
        ValueError: If planet not found or invalid structure
    
    Examples:
        >>> positions = [(0, (6, 15.5), ...), ...]
        >>> rasi, degree = get_planet_rasi_degree(positions, 'SUN')
        >>> print(f"Sun at {degree:.2f}° in sign {rasi}")
        Sun at 15.50° in sign 6
    """
    # Validate structure if requested
    if validate:
        validate_planet_positions(planet_positions, strict=False)
    
    # Get planet index
    idx = get_planet_index(planet)
    
    # Check if index is in range
    if idx >= len(planet_positions):
        planet_name = get_planet_name(planet)
        raise ValueError(
            f"Planet {planet_name} (index {idx}) not found in planet_positions"
        )
    
    # Extract rasi and degree
    try:
        pos = planet_positions[idx]
        rasi_deg = pos[1]
        rasi = rasi_deg[0]
        degree = rasi_deg[1]
        return rasi, degree
    except (IndexError, TypeError) as e:
        planet_name = get_planet_name(planet)
        raise ValueError(
            f"Invalid structure for planet {planet_name} (index {idx}): {e}"
        )


def get_planet_longitude(
    planet_positions: List,
    planet: Union[str, int],
    validate: bool = True
) -> float:
    """
    Get absolute longitude (0-360°) for a planet
    
    Args:
        planet_positions: PyJHora planet positions list
        planet: Planet name (str) or index (int)
        validate: Whether to validate structure first
    
    Returns:
        Longitude in degrees (0-360)
    
    Examples:
        >>> positions = [(0, (6, 15.5), ...), ...]  # Sun at Libra 15.5°
        >>> get_planet_longitude(positions, 'SUN')
        195.5  # (6 signs × 30° + 15.5°)
    """
    rasi, degree = get_planet_rasi_degree(planet_positions, planet, validate)
    return rasi * 30.0 + degree


def get_planet_nakshatra(
    planet_positions: List,
    planet: Union[str, int],
    validate: bool = True
) -> Tuple[int, int]:
    """
    Get nakshatra and pada for a planet
    
    Args:
        planet_positions: PyJHora planet positions list
        planet: Planet name (str) or index (int)
        validate: Whether to validate structure first
    
    Returns:
        Tuple of (nakshatra_index: int, pada: int)
        - nakshatra_index: 0-26 (Ashwini to Revati)
        - pada: 1-4 (quarter of nakshatra)
    
    Examples:
        >>> naks, pada = get_planet_nakshatra(positions, 'MOON')
        >>> print(f"Moon in nakshatra {naks}, pada {pada}")
    """
    # Get planet index
    idx = get_planet_index(planet)
    
    # Validate if requested
    if validate:
        validate_planet_positions(planet_positions, strict=False)
    
    # Check range
    if idx >= len(planet_positions):
        raise ValueError(f"Planet index {idx} out of range")
    
    # Extract nakshatra info (typically at index [2])
    try:
        pos = planet_positions[idx]
        if len(pos) > 2:
            naks_info = pos[2]
            if isinstance(naks_info, (list, tuple)) and len(naks_info) >= 2:
                return naks_info[0], naks_info[1]
    except (IndexError, TypeError):
        pass
    
    # If nakshatra not in position, calculate from longitude
    longitude = get_planet_longitude(planet_positions, planet, validate=False)
    nakshatra_index = int(longitude / (360.0 / 27))
    nakshatra_degree = (longitude % (360.0 / 27))
    pada = int(nakshatra_degree / ((360.0 / 27) / 4)) + 1
    
    return nakshatra_index, pada


# =============================================================================
# HOUSE CALCULATIONS
# =============================================================================

def calculate_house_from_ascendant(
    planet_rasi: int,
    ascendant_rasi: int
) -> int:
    """
    Calculate house number (1-12) from planet rasi and ascendant rasi
    
    Args:
        planet_rasi: Planet's sign index (0-11)
        ascendant_rasi: Ascendant sign index (0-11)
    
    Returns:
        House number (1-12)
    
    Examples:
        >>> calculate_house_from_ascendant(6, 0)  # Libra from Aries ascendant
        7  # 7th house
    """
    # Calculate difference (with wrap-around)
    house = ((planet_rasi - ascendant_rasi) % 12) + 1
    return house


def get_house_difference(house1: int, house2: int) -> int:
    """
    Calculate shortest distance between two houses
    
    Args:
        house1: First house (1-12)
        house2: Second house (1-12)
    
    Returns:
        Distance in houses (0-6)
    
    Examples:
        >>> get_house_difference(1, 4)  # 1st to 4th
        3
        >>> get_house_difference(1, 10)  # 1st to 10th
        3  # (can go either direction)
    """
    # Convert to 0-based
    h1 = house1 - 1
    h2 = house2 - 1
    
    # Calculate both directions
    forward = (h2 - h1) % 12
    backward = (h1 - h2) % 12
    
    # Return minimum
    return min(forward, backward)


def is_kendra_from_house(house1: int, house2: int) -> bool:
    """
    Check if house2 is in kendra (1, 4, 7, 10) from house1
    
    Args:
        house1: Reference house (1-12)
        house2: Target house (1-12)
    
    Returns:
        True if house2 is kendra from house1
    
    Examples:
        >>> is_kendra_from_house(1, 4)  # 4th from 1st
        True
        >>> is_kendra_from_house(1, 5)  # 5th from 1st
        False
    """
    diff = get_house_difference(house1, house2)
    return diff in [0, 3, 6, 9]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Planet lookup utilities
    'create_planet_lookup',
    'get_planet_from_lookup',
    
    # Planet name utilities
    'normalize_planet_name',
    'get_planet_index',
    'get_planet_name',
    
    # Position access
    'get_planet_house',
    'get_planet_rasi_degree',
    'get_planet_longitude',
    'get_planet_nakshatra',
    
    # House calculations
    'calculate_house_from_ascendant',
    'get_house_difference',
    'is_kendra_from_house',
]
