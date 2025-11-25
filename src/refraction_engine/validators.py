"""
Validation utilities for Refraction Engine

This module provides defensive validation functions for:
- planet_positions structure
- Chart IDs
- Language parameters
- House numbers
- Degrees and signs

Usage:
    from .validators import validate_planet_positions, normalize_chart_id
    
    validate_planet_positions(positions)  # Raises ValueError if invalid
    chart_id = normalize_chart_id(raw_id)  # Always returns valid "DXX" format
"""

from typing import Any, List, Tuple, Optional
import logging

from .constants import (
    PLANET_NAMES,
    MIN_SIGN_INDEX,
    MAX_SIGN_INDEX,
    MIN_DEGREE,
    MAX_DEGREE,
    MIN_HOUSE_NUMBER,
    MAX_HOUSE_NUMBER,
    MIN_PLANETS,
    ALLOWED_LANGUAGES,
    DEFAULT_LANGUAGE,
)

logger = logging.getLogger(__name__)


# =============================================================================
# PLANET POSITIONS VALIDATION
# =============================================================================

def validate_planet_positions(planet_positions: List, strict: bool = True) -> bool:
    """
    Validate planet_positions structure from PyJHora
    
    Expected format:
        [
            (planet_id, (rasi, degree), nakshatra_info, retrograde),
            ...
        ]
    
    Args:
        planet_positions: List of planet position tuples
        strict: If True, enforces exactly 9 planets; if False, allows more
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If structure is invalid with detailed error message
    
    Examples:
        >>> positions = [(0, (0, 15.5), (1, 0), False), ...]  # 9 planets
        >>> validate_planet_positions(positions)
        True
    """
    # Check for None or empty
    if planet_positions is None:
        raise ValueError("planet_positions is None")
    
    if not planet_positions:
        raise ValueError("planet_positions is empty")
    
    # Check minimum length
    if len(planet_positions) < MIN_PLANETS:
        raise ValueError(
            f"Expected at least {MIN_PLANETS} planets, got {len(planet_positions)}"
        )
    
    # If strict mode, check for exactly 9 planets
    if strict and len(planet_positions) != MIN_PLANETS:
        raise ValueError(
            f"Expected exactly {MIN_PLANETS} planets in strict mode, "
            f"got {len(planet_positions)}"
        )
    
    # Validate each planet's structure
    for i, pos in enumerate(planet_positions):
        planet_name = PLANET_NAMES[i] if i < len(PLANET_NAMES) else f"Planet{i}"
        
        # Check if tuple/list
        if not isinstance(pos, (list, tuple)):
            raise ValueError(
                f"{planet_name} (index {i}): position is not a tuple/list, "
                f"got {type(pos).__name__}"
            )
        
        # Check length (should have at least 2 elements)
        if len(pos) < 2:
            raise ValueError(
                f"{planet_name} (index {i}): position too short "
                f"(expected ≥2 elements, got {len(pos)})"
            )
        
        # Validate (rasi, degree) tuple at index [1]
        rasi_deg = pos[1]
        if not isinstance(rasi_deg, (list, tuple)):
            raise ValueError(
                f"{planet_name} (index {i}): rasi/degree is not a tuple/list, "
                f"got {type(rasi_deg).__name__}"
            )
        
        if len(rasi_deg) < 2:
            raise ValueError(
                f"{planet_name} (index {i}): rasi/degree tuple too short "
                f"(expected 2 elements, got {len(rasi_deg)})"
            )
        
        # Validate rasi (sign index 0-11)
        rasi = rasi_deg[0]
        if not isinstance(rasi, int):
            raise ValueError(
                f"{planet_name} (index {i}): rasi is not an integer, "
                f"got {type(rasi).__name__} = {rasi}"
            )
        
        if not (MIN_SIGN_INDEX <= rasi <= MAX_SIGN_INDEX):
            raise ValueError(
                f"{planet_name} (index {i}): rasi out of range "
                f"(expected {MIN_SIGN_INDEX}-{MAX_SIGN_INDEX}, got {rasi})"
            )
        
        # Validate degree (0-30)
        degree = rasi_deg[1]
        if not isinstance(degree, (int, float)):
            raise ValueError(
                f"{planet_name} (index {i}): degree is not numeric, "
                f"got {type(degree).__name__} = {degree}"
            )
        
        if not (MIN_DEGREE <= degree < MAX_DEGREE):
            raise ValueError(
                f"{planet_name} (index {i}): degree out of range "
                f"(expected {MIN_DEGREE}-{MAX_DEGREE}, got {degree:.4f})"
            )
    
    return True


def validate_planet_positions_safe(planet_positions: List) -> Tuple[bool, Optional[str]]:
    """
    Safe version of validate_planet_positions that returns success/error
    instead of raising exceptions
    
    Args:
        planet_positions: List of planet position tuples
    
    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    
    Examples:
        >>> valid, error = validate_planet_positions_safe(positions)
        >>> if not valid:
        ...     print(f"Validation failed: {error}")
    """
    try:
        validate_planet_positions(planet_positions, strict=False)
        return True, None
    except ValueError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {e}"


# =============================================================================
# CHART ID NORMALIZATION
# =============================================================================

def normalize_chart_id(chart_id: Any, default: str = "D1") -> str:
    """
    Safely normalize chart ID to DXX format
    
    Handles various input types:
    - None → default
    - Integer (1, 9) → "D1", "D9"
    - String ("D9", "9", "d9") → "D9"
    - Other types → converted to string
    
    Args:
        chart_id: Chart identifier (could be int, str, None, etc.)
        default: Default value if chart_id is None (default: "D1")
    
    Returns:
        Normalized chart ID like "D1", "D9", "D60", etc.
    
    Examples:
        >>> normalize_chart_id(None)
        'D1'
        >>> normalize_chart_id(9)
        'D9'
        >>> normalize_chart_id("D9")
        'D9'
        >>> normalize_chart_id("navamsa")
        'DNAVAMSA'
    """
    if chart_id is None:
        return default
    
    # Convert to string and clean
    chart_str = str(chart_id).upper().strip()
    
    # Already has "D" prefix
    if chart_str.startswith("D"):
        return chart_str
    
    # Add "D" prefix
    return f"D{chart_str}"


# =============================================================================
# LANGUAGE VALIDATION
# =============================================================================

def sanitize_language(lang: Any, default: str = DEFAULT_LANGUAGE) -> str:
    """
    Validate and sanitize language parameter
    
    Args:
        lang: Language code (e.g., "en", "ta", "hi")
        default: Default language if invalid (default: "en")
    
    Returns:
        Valid language code from ALLOWED_LANGUAGES
    
    Examples:
        >>> sanitize_language("en")
        'en'
        >>> sanitize_language("EN")
        'en'
        >>> sanitize_language("invalid")
        'en'
        >>> sanitize_language(None)
        'en'
    """
    if lang is None or not isinstance(lang, str):
        logger.debug(f"Invalid language type: {type(lang)}, using default: {default}")
        return default
    
    # Normalize to lowercase
    lang = lang.lower().strip()
    
    # Check if valid
    if lang in ALLOWED_LANGUAGES:
        return lang
    
    logger.debug(f"Unsupported language: {lang}, using default: {default}")
    return default


# =============================================================================
# HOUSE NUMBER VALIDATION
# =============================================================================

def validate_house_number(house: int, allow_zero: bool = False) -> bool:
    """
    Validate house number is in valid range
    
    Args:
        house: House number to validate
        allow_zero: If True, allows 0 (for 0-based indexing)
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If house number is invalid
    
    Examples:
        >>> validate_house_number(1)
        True
        >>> validate_house_number(0, allow_zero=True)
        True
        >>> validate_house_number(13)
        ValueError: House number out of range: 13
    """
    if not isinstance(house, int):
        raise ValueError(f"House must be integer, got {type(house).__name__}")
    
    min_house = 0 if allow_zero else MIN_HOUSE_NUMBER
    max_house = MAX_HOUSE_NUMBER if not allow_zero else MAX_HOUSE_NUMBER - 1
    
    if not (min_house <= house <= max_house):
        raise ValueError(
            f"House number out of range "
            f"(expected {min_house}-{max_house}, got {house})"
        )
    
    return True


# =============================================================================
# SIGN/DEGREE VALIDATION
# =============================================================================

def validate_sign_index(sign: int) -> bool:
    """
    Validate sign/rasi index (0-11)
    
    Args:
        sign: Sign index to validate
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If sign index is invalid
    """
    if not isinstance(sign, int):
        raise ValueError(f"Sign must be integer, got {type(sign).__name__}")
    
    if not (MIN_SIGN_INDEX <= sign <= MAX_SIGN_INDEX):
        raise ValueError(
            f"Sign index out of range "
            f"(expected {MIN_SIGN_INDEX}-{MAX_SIGN_INDEX}, got {sign})"
        )
    
    return True


def validate_degree(degree: float) -> bool:
    """
    Validate degree value (0-30)
    
    Args:
        degree: Degree value to validate
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If degree is invalid
    """
    if not isinstance(degree, (int, float)):
        raise ValueError(f"Degree must be numeric, got {type(degree).__name__}")
    
    if not (MIN_DEGREE <= degree < MAX_DEGREE):
        raise ValueError(
            f"Degree out of range "
            f"(expected {MIN_DEGREE}-{MAX_DEGREE}, got {degree:.4f})"
        )
    
    return True


# =============================================================================
# STRUCTURE VALIDATION
# =============================================================================

def validate_rasi_degree_tuple(rasi_deg: Tuple) -> bool:
    """
    Validate (rasi, degree) tuple structure
    
    Args:
        rasi_deg: Tuple of (sign_index, degree)
    
    Returns:
        True if valid
    
    Raises:
        ValueError: If structure is invalid
    """
    if not isinstance(rasi_deg, (list, tuple)):
        raise ValueError(f"rasi_deg must be tuple/list, got {type(rasi_deg).__name__}")
    
    if len(rasi_deg) < 2:
        raise ValueError(f"rasi_deg must have 2 elements, got {len(rasi_deg)}")
    
    validate_sign_index(rasi_deg[0])
    validate_degree(rasi_deg[1])
    
    return True


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'validate_planet_positions',
    'validate_planet_positions_safe',
    'normalize_chart_id',
    'sanitize_language',
    'validate_house_number',
    'validate_sign_index',
    'validate_degree',
    'validate_rasi_degree_tuple',
]
