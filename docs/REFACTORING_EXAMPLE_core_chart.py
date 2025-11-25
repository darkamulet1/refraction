"""
Example: Refactoring core_chart.py to use graha.py

This shows BEFORE and AFTER code for a typical extractor.
"""

# ==============================================================================
# BEFORE: Using local mappings (BAD ❌)
# ==============================================================================

# Old code with duplicate mappings
PLANET_IDS_OLD = {
    0: "SUN",
    1: "MOON",
    2: "MARS",
    3: "MERCURY",
    4: "JUPITER",
    5: "VENUS",
    6: "SATURN",
    7: "RAHU",
    8: "KETU",
}

PLANET_NAMES_OLD = {
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

RASI_NAMES_OLD = {
    1: "ARIES",
    2: "TAURUS",
    3: "GEMINI",
    4: "CANCER",
    5: "LEO",
    6: "VIRGO",
    7: "LIBRA",
    8: "SCORPIO",
    9: "SAGITTARIUS",
    10: "CAPRICORN",
    11: "AQUARIUS",
    12: "PISCES",
}

def format_planet_OLD(planet_idx: int, longitude_deg: float) -> dict:
    """OLD VERSION: Manual calculations and local dicts"""
    # Manual rasi calculation
    rasi_idx = int(longitude_deg // 30) + 1
    degree_in_sign = longitude_deg % 30
    
    # Manual nakshatra calculation
    nakshatra_span = 360.0 / 27  # 13.333...
    nakshatra_idx = int(longitude_deg / nakshatra_span) + 1
    span_in_nak = longitude_deg % nakshatra_span
    pada = int(span_in_nak / (nakshatra_span / 4)) + 1
    
    return {
        "id": PLANET_IDS_OLD[planet_idx],
        "name": PLANET_NAMES_OLD[planet_idx],
        "longitude_deg": longitude_deg,
        "degree_in_sign": degree_in_sign,
        "sign_index": rasi_idx,
        "sign_name": RASI_NAMES_OLD.get(rasi_idx, "UNKNOWN"),
        "nakshatra_index": nakshatra_idx,
        "nakshatra_pada": pada,
    }


# ==============================================================================
# AFTER: Using graha.py (GOOD ✅)
# ==============================================================================

from refraction_engine.graha import (
    GrahaID,
    graha_id_to_string,
    graha_id_to_name,
    rasi_index_from_longitude,
    degree_in_rasi,
    rasi_index_to_name,
    nakshatra_from_longitude,
    nakshatra_index_to_name,
)

def format_planet_NEW(planet_idx: int, longitude_deg: float) -> dict:
    """NEW VERSION: Using graha.py utilities"""
    # Convert planet index to ID/name
    graha_id = GrahaID(planet_idx)
    planet_string_id = graha_id_to_string(graha_id)
    planet_name = graha_id_to_name(graha_id)
    
    # Calculate rasi using utility
    rasi_idx = rasi_index_from_longitude(longitude_deg)
    degree_in_sign = degree_in_rasi(longitude_deg)
    rasi_name = rasi_index_to_name(rasi_idx)
    
    # Calculate nakshatra using utility
    nakshatra_idx, pada, span_deg = nakshatra_from_longitude(longitude_deg)
    nakshatra_name = nakshatra_index_to_name(nakshatra_idx)
    
    return {
        "id": planet_string_id,
        "name": planet_name,
        "longitude_deg": longitude_deg,
        "degree_in_sign": degree_in_sign,
        "sign_index": rasi_idx,
        "sign_name": rasi_name,
        "nakshatra_index": nakshatra_idx,
        "nakshatra_name": nakshatra_name,
        "nakshatra_pada": pada,
    }


# ==============================================================================
# VERIFICATION: Both should produce identical output
# ==============================================================================

if __name__ == "__main__":
    # Test with Sun at 187.627° (from Arezoo's chart)
    test_longitude = 187.627
    test_planet_idx = 0  # Sun
    
    print("Testing planet formatting...")
    print("=" * 60)
    
    # Old version
    old_result = format_planet_OLD(test_planet_idx, test_longitude)
    print("OLD VERSION:")
    print(f"  ID: {old_result['id']}")
    print(f"  Name: {old_result['name']}")
    print(f"  Sign: {old_result['sign_name']} ({old_result['sign_index']})")
    print(f"  Degree: {old_result['degree_in_sign']:.3f}°")
    print(f"  Nakshatra: {old_result['nakshatra_index']} (pada {old_result['nakshatra_pada']})")
    print()
    
    # New version
    new_result = format_planet_NEW(test_planet_idx, test_longitude)
    print("NEW VERSION:")
    print(f"  ID: {new_result['id']}")
    print(f"  Name: {new_result['name']}")
    print(f"  Sign: {new_result['sign_name']} ({new_result['sign_index']})")
    print(f"  Degree: {new_result['degree_in_sign']:.3f}°")
    print(f"  Nakshatra: {new_result['nakshatra_name']} ({new_result['nakshatra_index']}, pada {new_result['nakshatra_pada']})")
    print()
    
    # Verify they match
    print("VERIFICATION:")
    print("=" * 60)
    assert old_result['id'] == new_result['id'], "ID mismatch!"
    assert old_result['name'] == new_result['name'], "Name mismatch!"
    assert old_result['sign_index'] == new_result['sign_index'], "Sign index mismatch!"
    assert old_result['sign_name'] == new_result['sign_name'], "Sign name mismatch!"
    assert abs(old_result['degree_in_sign'] - new_result['degree_in_sign']) < 0.001, "Degree mismatch!"
    assert old_result['nakshatra_index'] == new_result['nakshatra_index'], "Nakshatra index mismatch!"
    assert old_result['nakshatra_pada'] == new_result['nakshatra_pada'], "Pada mismatch!"
    
    print("✅ All checks passed! Old and new versions produce identical output.")
    print()
    print("BENEFITS OF NEW VERSION:")
    print("- No duplicate mappings")
    print("- Type-safe enums")
    print("- Tested utility functions")
    print("- Single source of truth")
    print("- Easier maintenance")
