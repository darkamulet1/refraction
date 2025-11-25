"""
Unit tests for validators module

Tests validation functions for:
- planet_positions structure
- chart IDs
- languages
- house numbers
- degrees and signs
"""

import pytest
from refraction_engine.validators import (
    validate_planet_positions,
    validate_planet_positions_safe,
    normalize_chart_id,
    sanitize_language,
    validate_house_number,
    validate_sign_index,
    validate_degree,
    validate_rasi_degree_tuple,
)


# =============================================================================
# PLANET POSITIONS VALIDATION TESTS
# =============================================================================

def test_validate_planet_positions_valid():
    """Test with valid 9-planet structure"""
    positions = [
        (0, (0, 15.5), (1, 0), False),   # Sun
        (1, (1, 25.3), (2, 1), False),   # Moon
        (2, (2, 10.2), (3, 2), False),   # Mars
        (3, (3, 5.7), (4, 3), False),    # Mercury
        (4, (4, 20.1), (5, 4), False),   # Jupiter
        (5, (5, 12.8), (6, 1), False),   # Venus
        (6, (6, 8.3), (7, 2), False),    # Saturn
        (7, (7, 22.5), (8, 3), False),   # Rahu
        (8, (8, 11.1), (9, 1), False),   # Ketu
    ]
    assert validate_planet_positions(positions) == True


def test_validate_planet_positions_empty():
    """Test with empty list"""
    with pytest.raises(ValueError, match="empty"):
        validate_planet_positions([])


def test_validate_planet_positions_none():
    """Test with None"""
    with pytest.raises(ValueError, match="None"):
        validate_planet_positions(None)


def test_validate_planet_positions_too_few():
    """Test with too few planets"""
    positions = [
        (0, (0, 15.5), (1, 0), False),  # Only 1 planet
    ]
    with pytest.raises(ValueError, match="Expected at least 9"):
        validate_planet_positions(positions)


def test_validate_planet_positions_invalid_structure():
    """Test with invalid tuple structure"""
    positions = [
        "not a tuple",  # Invalid
    ] + [(i, (i, 15.0), (i, 0), False) for i in range(1, 9)]
    
    with pytest.raises(ValueError, match="not a tuple/list"):
        validate_planet_positions(positions)


def test_validate_planet_positions_invalid_rasi():
    """Test with out-of-range rasi"""
    positions = [
        (0, (15, 15.5), (1, 0), False),  # Rasi 15 is invalid (should be 0-11)
    ] + [(i, (i, 15.0), (i, 0), False) for i in range(1, 9)]
    
    with pytest.raises(ValueError, match="rasi out of range"):
        validate_planet_positions(positions)


def test_validate_planet_positions_invalid_degree():
    """Test with out-of-range degree"""
    positions = [
        (0, (0, 35.0), (1, 0), False),  # Degree 35 is invalid (should be 0-30)
    ] + [(i, (i, 15.0), (i, 0), False) for i in range(1, 9)]
    
    with pytest.raises(ValueError, match="degree out of range"):
        validate_planet_positions(positions)


def test_validate_planet_positions_safe():
    """Test safe version that returns tuple"""
    valid_positions = [(i, (i, 15.0), (i, 0), False) for i in range(9)]
    
    valid, error = validate_planet_positions_safe(valid_positions)
    assert valid == True
    assert error is None
    
    invalid_positions = [(0, (15, 15.0), (1, 0), False)]  # Invalid rasi
    valid, error = validate_planet_positions_safe(invalid_positions)
    assert valid == False
    assert error is not None
    assert "rasi out of range" in error or "at least 9" in error


# =============================================================================
# CHART ID NORMALIZATION TESTS
# =============================================================================

def test_normalize_chart_id_none():
    """Test with None"""
    assert normalize_chart_id(None) == "D1"
    assert normalize_chart_id(None, default="D9") == "D9"


def test_normalize_chart_id_integer():
    """Test with integer"""
    assert normalize_chart_id(1) == "D1"
    assert normalize_chart_id(9) == "D9"
    assert normalize_chart_id(60) == "D60"


def test_normalize_chart_id_string_with_d():
    """Test with string already having D prefix"""
    assert normalize_chart_id("D1") == "D1"
    assert normalize_chart_id("D9") == "D9"
    assert normalize_chart_id("d9") == "D9"  # Lowercase


def test_normalize_chart_id_string_without_d():
    """Test with string number"""
    assert normalize_chart_id("1") == "D1"
    assert normalize_chart_id("9") == "D9"
    assert normalize_chart_id("60") == "D60"


def test_normalize_chart_id_string_name():
    """Test with divisional chart name"""
    assert normalize_chart_id("navamsa") == "DNAVAMSA"
    assert normalize_chart_id("rasi") == "DRASI"


# =============================================================================
# LANGUAGE SANITIZATION TESTS
# =============================================================================

def test_sanitize_language_valid():
    """Test with valid languages"""
    assert sanitize_language("en") == "en"
    assert sanitize_language("ta") == "ta"
    assert sanitize_language("hi") == "hi"


def test_sanitize_language_case_insensitive():
    """Test case insensitivity"""
    assert sanitize_language("EN") == "en"
    assert sanitize_language("Ta") == "ta"
    assert sanitize_language("HI") == "hi"


def test_sanitize_language_invalid():
    """Test with invalid language"""
    assert sanitize_language("invalid") == "en"
    assert sanitize_language("fr") == "en"  # French not supported


def test_sanitize_language_none():
    """Test with None"""
    assert sanitize_language(None) == "en"


def test_sanitize_language_custom_default():
    """Test with custom default"""
    assert sanitize_language("invalid", default="ta") == "ta"


# =============================================================================
# HOUSE NUMBER VALIDATION TESTS
# =============================================================================

def test_validate_house_number_valid():
    """Test with valid house numbers"""
    assert validate_house_number(1) == True
    assert validate_house_number(6) == True
    assert validate_house_number(12) == True


def test_validate_house_number_zero_allowed():
    """Test with zero when allowed"""
    assert validate_house_number(0, allow_zero=True) == True


def test_validate_house_number_zero_not_allowed():
    """Test with zero when not allowed"""
    with pytest.raises(ValueError, match="out of range"):
        validate_house_number(0, allow_zero=False)


def test_validate_house_number_out_of_range():
    """Test with out-of-range house numbers"""
    with pytest.raises(ValueError, match="out of range"):
        validate_house_number(13)
    
    with pytest.raises(ValueError, match="out of range"):
        validate_house_number(-1)


def test_validate_house_number_not_integer():
    """Test with non-integer"""
    with pytest.raises(ValueError, match="must be integer"):
        validate_house_number(1.5)
    
    with pytest.raises(ValueError, match="must be integer"):
        validate_house_number("1")


# =============================================================================
# SIGN INDEX VALIDATION TESTS
# =============================================================================

def test_validate_sign_index_valid():
    """Test with valid sign indices"""
    assert validate_sign_index(0) == True
    assert validate_sign_index(6) == True
    assert validate_sign_index(11) == True


def test_validate_sign_index_out_of_range():
    """Test with out-of-range signs"""
    with pytest.raises(ValueError, match="out of range"):
        validate_sign_index(12)
    
    with pytest.raises(ValueError, match="out of range"):
        validate_sign_index(-1)


# =============================================================================
# DEGREE VALIDATION TESTS
# =============================================================================

def test_validate_degree_valid():
    """Test with valid degrees"""
    assert validate_degree(0.0) == True
    assert validate_degree(15.5) == True
    assert validate_degree(29.999) == True


def test_validate_degree_boundary():
    """Test boundary values"""
    assert validate_degree(0.0) == True
    
    with pytest.raises(ValueError, match="out of range"):
        validate_degree(30.0)  # Should be < 30
    
    with pytest.raises(ValueError, match="out of range"):
        validate_degree(-0.1)


def test_validate_degree_integer():
    """Test with integer degrees"""
    assert validate_degree(15) == True
    assert validate_degree(0) == True


# =============================================================================
# RASI-DEGREE TUPLE VALIDATION TESTS
# =============================================================================

def test_validate_rasi_degree_tuple_valid():
    """Test with valid tuple"""
    assert validate_rasi_degree_tuple((0, 15.5)) == True
    assert validate_rasi_degree_tuple([6, 22.3]) == True


def test_validate_rasi_degree_tuple_invalid_type():
    """Test with invalid types"""
    with pytest.raises(ValueError, match="must be tuple/list"):
        validate_rasi_degree_tuple("not a tuple")


def test_validate_rasi_degree_tuple_too_short():
    """Test with too few elements"""
    with pytest.raises(ValueError, match="must have 2 elements"):
        validate_rasi_degree_tuple((0,))


def test_validate_rasi_degree_tuple_invalid_values():
    """Test with invalid rasi or degree"""
    with pytest.raises(ValueError, match="out of range"):
        validate_rasi_degree_tuple((12, 15.0))  # Invalid rasi
    
    with pytest.raises(ValueError, match="out of range"):
        validate_rasi_degree_tuple((6, 35.0))  # Invalid degree


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

def test_validators_integration():
    """Test multiple validators together"""
    # Valid planet positions
    positions = [(i, (i, 15.0), (i, 0), False) for i in range(9)]
    assert validate_planet_positions(positions)
    
    # Valid chart ID
    chart_id = normalize_chart_id(9)
    assert chart_id == "D9"
    
    # Valid language
    lang = sanitize_language("EN")
    assert lang == "en"
    
    # Valid house
    assert validate_house_number(7)
