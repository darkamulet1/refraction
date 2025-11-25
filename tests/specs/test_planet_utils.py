"""
Unit tests for planet_utils module

Tests planet utility functions for:
- Planet name normalization
- Planet index lookup
- Planet position access
- House calculations
"""

import pytest
from refraction_engine.planet_utils import (
    normalize_planet_name,
    get_planet_index,
    get_planet_name,
    get_planet_house,
    get_planet_rasi_degree,
    get_planet_longitude,
    calculate_house_from_ascendant,
    get_house_difference,
    is_kendra_from_house,
)


# Sample test data
SAMPLE_POSITIONS = [
    (0, (0, 15.5), (1, 0), False),   # Sun at Aries 15.5°
    (1, (5, 25.3), (12, 1), False),  # Moon at Virgo 25.3°
    (2, (9, 10.2), (19, 2), False),  # Mars at Capricorn 10.2°
    (3, (2, 5.7), (5, 3), False),    # Mercury at Gemini 5.7°
    (4, (8, 20.1), (17, 4), False),  # Jupiter at Sagittarius 20.1°
    (5, (1, 12.8), (3, 1), False),   # Venus at Taurus 12.8°
    (6, (6, 8.3), (14, 2), False),   # Saturn at Libra 8.3°
    (7, (7, 22.5), (16, 3), False),  # Rahu at Scorpio 22.5°
    (8, (1, 22.5), (4, 3), False),   # Ketu at Taurus 22.5° (opposite Rahu)
]


# =============================================================================
# PLANET NAME NORMALIZATION TESTS
# =============================================================================

def test_normalize_planet_name_standard():
    """Test with standard planet names"""
    assert normalize_planet_name("sun") == "SUN"
    assert normalize_planet_name("MARS") == "MARS"
    assert normalize_planet_name("Jupiter") == "JUPITER"


def test_normalize_planet_name_aliases():
    """Test with alternative spellings"""
    assert normalize_planet_name("ragu") == "RAHU"
    assert normalize_planet_name("RAAHU") == "RAHU"
    assert normalize_planet_name("kethu") == "KETU"


def test_normalize_planet_name_invalid():
    """Test with invalid planet name"""
    with pytest.raises(ValueError, match="Unknown planet"):
        normalize_planet_name("pluto")
    
    with pytest.raises(ValueError, match="Unknown planet"):
        normalize_planet_name("invalid")


def test_normalize_planet_name_not_string():
    """Test with non-string input"""
    with pytest.raises(ValueError, match="must be string"):
        normalize_planet_name(123)


# =============================================================================
# PLANET INDEX TESTS
# =============================================================================

def test_get_planet_index_by_name():
    """Test getting index from planet name"""
    assert get_planet_index("SUN") == 0
    assert get_planet_index("moon") == 1
    assert get_planet_index("MARS") == 2
    assert get_planet_index("Jupiter") == 4


def test_get_planet_index_by_number():
    """Test with integer index"""
    assert get_planet_index(0) == 0
    assert get_planet_index(4) == 4
    assert get_planet_index(8) == 8


def test_get_planet_index_invalid():
    """Test with invalid planet"""
    with pytest.raises(ValueError):
        get_planet_index("invalid")
    
    with pytest.raises(ValueError):
        get_planet_index(99)
    
    with pytest.raises(ValueError):
        get_planet_index(-1)


# =============================================================================
# PLANET NAME LOOKUP TESTS
# =============================================================================

def test_get_planet_name_from_index():
    """Test getting name from index"""
    assert get_planet_name(0) == "SUN"
    assert get_planet_name(1) == "MOON"
    assert get_planet_name(4) == "JUPITER"


def test_get_planet_name_from_string():
    """Test normalizing name from string"""
    assert get_planet_name("mars") == "MARS"
    assert get_planet_name("RAGU") == "RAHU"


def test_get_planet_name_invalid():
    """Test with invalid input"""
    with pytest.raises(ValueError):
        get_planet_name(99)
    
    with pytest.raises(ValueError):
        get_planet_name("invalid")


# =============================================================================
# PLANET HOUSE ACCESS TESTS
# =============================================================================

def test_get_planet_house_by_name():
    """Test getting house by planet name"""
    assert get_planet_house(SAMPLE_POSITIONS, "SUN") == 0  # Aries
    assert get_planet_house(SAMPLE_POSITIONS, "MOON") == 5  # Virgo
    assert get_planet_house(SAMPLE_POSITIONS, "MARS") == 9  # Capricorn


def test_get_planet_house_by_index():
    """Test getting house by planet index"""
    assert get_planet_house(SAMPLE_POSITIONS, 0) == 0  # Sun
    assert get_planet_house(SAMPLE_POSITIONS, 1) == 5  # Moon


def test_get_planet_house_case_insensitive():
    """Test case insensitivity"""
    assert get_planet_house(SAMPLE_POSITIONS, "sun") == 0
    assert get_planet_house(SAMPLE_POSITIONS, "SUN") == 0
    assert get_planet_house(SAMPLE_POSITIONS, "Sun") == 0


def test_get_planet_house_without_validation():
    """Test skipping validation for performance"""
    # Should work faster without validation
    house = get_planet_house(SAMPLE_POSITIONS, "MARS", validate=False)
    assert house == 9


def test_get_planet_house_invalid_planet():
    """Test with invalid planet"""
    with pytest.raises(ValueError):
        get_planet_house(SAMPLE_POSITIONS, "INVALID")


def test_get_planet_house_empty_positions():
    """Test with empty positions list"""
    with pytest.raises(ValueError):
        get_planet_house([], "SUN")


# =============================================================================
# RASI AND DEGREE TESTS
# =============================================================================

def test_get_planet_rasi_degree():
    """Test getting rasi and degree"""
    rasi, degree = get_planet_rasi_degree(SAMPLE_POSITIONS, "SUN")
    assert rasi == 0  # Aries
    assert abs(degree - 15.5) < 0.01
    
    rasi, degree = get_planet_rasi_degree(SAMPLE_POSITIONS, "MOON")
    assert rasi == 5  # Virgo
    assert abs(degree - 25.3) < 0.01


def test_get_planet_rasi_degree_by_index():
    """Test with planet index"""
    rasi, degree = get_planet_rasi_degree(SAMPLE_POSITIONS, 4)  # Jupiter
    assert rasi == 8  # Sagittarius
    assert abs(degree - 20.1) < 0.01


# =============================================================================
# LONGITUDE TESTS
# =============================================================================

def test_get_planet_longitude():
    """Test calculating absolute longitude"""
    # Sun at Aries 15.5° = 0*30 + 15.5 = 15.5°
    long_sun = get_planet_longitude(SAMPLE_POSITIONS, "SUN")
    assert abs(long_sun - 15.5) < 0.01
    
    # Moon at Virgo 25.3° = 5*30 + 25.3 = 175.3°
    long_moon = get_planet_longitude(SAMPLE_POSITIONS, "MOON")
    assert abs(long_moon - 175.3) < 0.01
    
    # Mars at Capricorn 10.2° = 9*30 + 10.2 = 280.2°
    long_mars = get_planet_longitude(SAMPLE_POSITIONS, "MARS")
    assert abs(long_mars - 280.2) < 0.01


# =============================================================================
# HOUSE CALCULATION TESTS
# =============================================================================

def test_calculate_house_from_ascendant():
    """Test house calculation from ascendant"""
    # If ascendant is Aries (0), then:
    # Aries (0) is 1st house
    # Taurus (1) is 2nd house
    # Libra (6) is 7th house
    assert calculate_house_from_ascendant(0, 0) == 1
    assert calculate_house_from_ascendant(1, 0) == 2
    assert calculate_house_from_ascendant(6, 0) == 7
    assert calculate_house_from_ascendant(11, 0) == 12
    
    # If ascendant is Libra (6), then:
    # Libra (6) is 1st house
    # Aries (0) is 7th house
    assert calculate_house_from_ascendant(6, 6) == 1
    assert calculate_house_from_ascendant(0, 6) == 7


def test_calculate_house_wrap_around():
    """Test wrap-around at 12 houses"""
    # If ascendant is Pisces (11), next sign Aries (0) is 2nd house
    assert calculate_house_from_ascendant(0, 11) == 2
    assert calculate_house_from_ascendant(1, 11) == 3


# =============================================================================
# HOUSE DIFFERENCE TESTS
# =============================================================================

def test_get_house_difference():
    """Test calculating house difference"""
    # Adjacent houses
    assert get_house_difference(1, 2) == 1
    assert get_house_difference(2, 1) == 1  # Symmetric
    
    # Opposite houses
    assert get_house_difference(1, 7) == 6
    assert get_house_difference(7, 1) == 6
    
    # Same house
    assert get_house_difference(5, 5) == 0
    
    # Kendra (angular)
    assert get_house_difference(1, 4) == 3
    assert get_house_difference(1, 10) == 3  # Shortest path


def test_get_house_difference_wrap_around():
    """Test wrap-around behavior"""
    # 1st to 12th is 1 house difference (backward)
    assert get_house_difference(1, 12) == 1
    assert get_house_difference(12, 1) == 1


# =============================================================================
# KENDRA CHECK TESTS
# =============================================================================

def test_is_kendra_from_house():
    """Test kendra (angular) house detection"""
    # From 1st house: 1, 4, 7, 10 are kendras
    assert is_kendra_from_house(1, 1) == True
    assert is_kendra_from_house(1, 4) == True
    assert is_kendra_from_house(1, 7) == True
    assert is_kendra_from_house(1, 10) == True
    
    # Non-kendra
    assert is_kendra_from_house(1, 2) == False
    assert is_kendra_from_house(1, 5) == False
    assert is_kendra_from_house(1, 8) == False


def test_is_kendra_from_any_house():
    """Test kendra from various reference houses"""
    # From 5th house: 5, 8, 11, 2 are kendras
    assert is_kendra_from_house(5, 5) == True
    assert is_kendra_from_house(5, 8) == True
    assert is_kendra_from_house(5, 11) == True
    assert is_kendra_from_house(5, 2) == True


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_planet_utils_integration():
    """Test multiple utilities together"""
    # Get planet index
    mars_idx = get_planet_index("MARS")
    assert mars_idx == 2
    
    # Get planet name
    planet_name = get_planet_name(mars_idx)
    assert planet_name == "MARS"
    
    # Get house
    mars_house = get_planet_house(SAMPLE_POSITIONS, "MARS")
    assert mars_house == 9  # Capricorn
    
    # Get rasi and degree
    rasi, degree = get_planet_rasi_degree(SAMPLE_POSITIONS, "MARS")
    assert rasi == 9
    assert abs(degree - 10.2) < 0.01
    
    # Calculate longitude
    longitude = get_planet_longitude(SAMPLE_POSITIONS, "MARS")
    expected = 9 * 30 + 10.2  # 280.2°
    assert abs(longitude - expected) < 0.01


def test_yoga_detection_helpers():
    """Test utilities useful for yoga detection"""
    # Get Jupiter and Moon houses
    jupiter_house = get_planet_house(SAMPLE_POSITIONS, "JUPITER")
    moon_house = get_planet_house(SAMPLE_POSITIONS, "MOON")
    
    # Check if Jupiter in kendra from Moon (Gaja Kesari yoga)
    # Jupiter at Sagittarius (8), Moon at Virgo (5)
    # Difference: (8 - 5) % 12 = 3 → Kendra!
    diff = get_house_difference(jupiter_house + 1, moon_house + 1)
    is_gaja_kesari = diff in [0, 3, 6, 9]
    assert is_gaja_kesari == True
