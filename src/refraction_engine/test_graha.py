"""
Tests for refraction_engine/graha.py - Central Mapping Utilities

Tests cover:
- Graha ID/name conversions
- Rasi calculations from longitude
- Nakshatra calculations from longitude
- Vaara mappings
- CorePrimitives.json validation (if available)
"""

import pytest
from refraction_engine.graha import (
    # Graha
    GrahaID, GRAHA_STRING_IDS, GRAHA_NAMES, GRAHA_ORDER,
    graha_id_to_string, graha_id_to_name,
    graha_string_to_id, graha_name_to_id,
    # Rasi
    RasiID, RASI_NAMES,
    rasi_index_to_name, rasi_name_to_index,
    rasi_index_from_longitude, degree_in_rasi,
    # Nakshatra
    NakshatraID, NAKSHATRA_NAMES, NAKSHATRA_LORDS,
    nakshatra_index_to_name, nakshatra_name_to_index,
    nakshatra_from_longitude, nakshatra_lord,
    # Vaara
    VaaraID, VAARA_NAMES, vaara_index_to_name,
    # Validation
    validate_against_core_primitives,
)


# ============================================================================
# GRAHA TESTS
# ============================================================================

class TestGrahaMapping:
    """Test planet ID/name mappings"""
    
    def test_graha_id_to_string(self):
        """Test GrahaID → string conversion"""
        assert graha_id_to_string(GrahaID.SUN) == "SUN"
        assert graha_id_to_string(GrahaID.MOON) == "MOON"
        assert graha_id_to_string(GrahaID.RAHU) == "RAHU"
        assert graha_id_to_string(GrahaID.KETU) == "KETU"
    
    def test_graha_id_to_name(self):
        """Test GrahaID → display name conversion"""
        assert graha_id_to_name(GrahaID.SUN) == "Sun"
        assert graha_id_to_name(GrahaID.JUPITER) == "Jupiter"
        assert graha_id_to_name(GrahaID.SATURN) == "Saturn"
    
    def test_graha_string_to_id(self):
        """Test string → GrahaID conversion"""
        assert graha_string_to_id("SUN") == GrahaID.SUN
        assert graha_string_to_id("sun") == GrahaID.SUN  # case insensitive
        assert graha_string_to_id("INVALID") is None
    
    def test_graha_name_to_id(self):
        """Test display name → GrahaID conversion"""
        assert graha_name_to_id("Sun") == GrahaID.SUN
        assert graha_name_to_id("Mercury") == GrahaID.MERCURY
        assert graha_name_to_id("Invalid") is None
    
    def test_graha_order(self):
        """Test standard planet order"""
        assert len(GRAHA_ORDER) == 9
        assert GRAHA_ORDER[0] == GrahaID.SUN
        assert GRAHA_ORDER[1] == GrahaID.MOON
        assert GRAHA_ORDER[-2] == GrahaID.RAHU
        assert GRAHA_ORDER[-1] == GrahaID.KETU
    
    def test_graha_bidirectional_mapping(self):
        """Test round-trip conversions"""
        for graha_id in GRAHA_ORDER:
            string_id = graha_id_to_string(graha_id)
            assert graha_string_to_id(string_id) == graha_id
            
            name = graha_id_to_name(graha_id)
            assert graha_name_to_id(name) == graha_id


# ============================================================================
# RASI TESTS
# ============================================================================

class TestRasiMapping:
    """Test sign index/name mappings"""
    
    def test_rasi_index_to_name(self):
        """Test index → name conversion"""
        assert rasi_index_to_name(1) == "ARIES"
        assert rasi_index_to_name(6) == "VIRGO"
        assert rasi_index_to_name(12) == "PISCES"
    
    def test_rasi_name_to_index(self):
        """Test name → index conversion"""
        assert rasi_name_to_index("ARIES") == 1
        assert rasi_name_to_index("aries") == 1  # case insensitive
        assert rasi_name_to_index("VIRGO") == 6
        assert rasi_name_to_index("INVALID") is None
    
    def test_rasi_index_from_longitude(self):
        """Test longitude → rasi index calculation"""
        # 0° = start of Aries
        assert rasi_index_from_longitude(0) == 1
        assert rasi_index_from_longitude(15) == 1  # mid-Aries
        assert rasi_index_from_longitude(29.9) == 1
        
        # 30° = start of Taurus
        assert rasi_index_from_longitude(30) == 2
        assert rasi_index_from_longitude(45) == 2  # mid-Taurus
        
        # 330° = start of Pisces
        assert rasi_index_from_longitude(330) == 12
        assert rasi_index_from_longitude(359.9) == 12
    
    def test_degree_in_rasi(self):
        """Test longitude → degree within rasi"""
        assert degree_in_rasi(0) == 0
        assert degree_in_rasi(15) == 15
        assert degree_in_rasi(30) == 0  # start of next rasi
        assert degree_in_rasi(45.5) == 15.5
        assert abs(degree_in_rasi(359.9) - 29.9) < 0.01
    
    def test_rasi_mehran_example(self):
        """Test with Mehran's Sun position (from golden data)"""
        # Sun at 187.627° (from arezoo_core_bundle.json actually, but using as example)
        sun_long = 187.627
        rasi_idx = rasi_index_from_longitude(sun_long)
        degree = degree_in_rasi(sun_long)
        
        assert rasi_idx == 7  # Libra
        assert rasi_index_to_name(rasi_idx) == "LIBRA"
        assert 7 < degree < 8  # approximately 7.627°
    
    def test_rasi_bidirectional_mapping(self):
        """Test round-trip conversions"""
        for rasi_id in RasiID:
            name = rasi_index_to_name(int(rasi_id))
            assert rasi_name_to_index(name) == int(rasi_id)


# ============================================================================
# NAKSHATRA TESTS
# ============================================================================

class TestNakshatraMapping:
    """Test nakshatra index/name mappings"""
    
    def test_nakshatra_index_to_name(self):
        """Test index → name conversion"""
        assert nakshatra_index_to_name(1) == "ASHWINI"
        assert nakshatra_index_to_name(7) == "PUNARPOOSAM"
        assert nakshatra_index_to_name(27) == "REVATHI"
    
    def test_nakshatra_name_to_index(self):
        """Test name → index conversion"""
        assert nakshatra_name_to_index("ASHWINI") == 1
        assert nakshatra_name_to_index("ashwini") == 1  # case insensitive
        assert nakshatra_name_to_index("ROHINI") == 4
        assert nakshatra_name_to_index("INVALID") is None
    
    def test_nakshatra_from_longitude_basic(self):
        """Test longitude → nakshatra calculation (basic cases)"""
        # 0° = Ashwini, Pada 1
        nak_idx, pada, span = nakshatra_from_longitude(0)
        assert nak_idx == 1
        assert pada == 1
        assert abs(span) < 0.01
        
        # Mid-Ashwini
        nak_idx, pada, span = nakshatra_from_longitude(6.666)
        assert nak_idx == 1
        assert pada == 2  # second pada
        
        # Start of Bharani
        nak_idx, pada, span = nakshatra_from_longitude(13.333)
        assert nak_idx == 2
        assert pada == 1
    
    def test_nakshatra_from_longitude_mehran(self):
        """Test with Mehran's Moon position (from golden data)"""
        # Moon at 325.252° (from arezoo_core_bundle.json)
        moon_long = 325.252
        nak_idx, pada, span = nakshatra_from_longitude(moon_long)
        
        assert nak_idx == 25  # Poorattathi
        assert nakshatra_index_to_name(nak_idx) == "POORATTATHI"
        assert pada == 2
        assert 5 < span < 6  # approximately matching golden data
    
    def test_nakshatra_lord(self):
        """Test nakshatra lord mappings"""
        assert nakshatra_lord(1) == "Ketu"  # Ashwini
        assert nakshatra_lord(7) == "Jupiter"  # Punarpoosam
        assert nakshatra_lord(27) == "Mercury"  # Revathi
    
    def test_nakshatra_bidirectional_mapping(self):
        """Test round-trip conversions"""
        for nak_id in NakshatraID:
            name = nakshatra_index_to_name(int(nak_id))
            assert nakshatra_name_to_index(name) == int(nak_id)


# ============================================================================
# VAARA TESTS
# ============================================================================

class TestVaaraMapping:
    """Test weekday mappings"""
    
    def test_vaara_index_to_name(self):
        """Test weekday index → name"""
        assert vaara_index_to_name(0) == "SUNDAY"
        assert vaara_index_to_name(3) == "WEDNESDAY"
        assert vaara_index_to_name(6) == "SATURDAY"
    
    def test_vaara_all_days(self):
        """Test all weekday mappings"""
        expected = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", 
                    "THURSDAY", "FRIDAY", "SATURDAY"]
        for i, expected_name in enumerate(expected):
            assert vaara_index_to_name(i) == expected_name


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests using golden data from test files"""
    
    def test_arezoo_sun_position(self):
        """Test with Arezoo's Sun position from golden data"""
        # From arezoo_core_bundle.json: Sun at 187.627°
        sun_long = 187.62732919614854
        
        # Rasi
        rasi_idx = rasi_index_from_longitude(sun_long)
        degree = degree_in_rasi(sun_long)
        assert rasi_idx == 7
        assert rasi_index_to_name(rasi_idx) == "LIBRA"
        assert abs(degree - 7.627) < 0.01
        
        # Nakshatra
        nak_idx, pada, span = nakshatra_from_longitude(sun_long)
        assert nak_idx == 15
        assert nakshatra_index_to_name(nak_idx) == "SWAATHI"
        assert pada == 1
        assert nakshatra_lord(nak_idx) == "Rahu"
    
    def test_arezoo_moon_position(self):
        """Test with Arezoo's Moon position from golden data"""
        # From arezoo_core_bundle.json: Moon at 325.252°
        moon_long = 325.25183646616665
        
        # Rasi
        rasi_idx = rasi_index_from_longitude(moon_long)
        assert rasi_idx == 11
        assert rasi_index_to_name(rasi_idx) == "AQUARIUS"
        
        # Nakshatra
        nak_idx, pada, span = nakshatra_from_longitude(moon_long)
        assert nak_idx == 25
        assert nakshatra_index_to_name(nak_idx) == "POORATTATHI"
        assert pada == 2
        assert nakshatra_lord(nak_idx) == "Jupiter"
    
    def test_arman_ascendant(self):
        """Test with Arman's Ascendant from golden data"""
        # From arman_core_bundle.json: Ascendant at 156.525°
        asc_long = 156.52501948804075
        
        # Rasi
        rasi_idx = rasi_index_from_longitude(asc_long)
        assert rasi_idx == 6
        assert rasi_index_to_name(rasi_idx) == "VIRGO"
        
        # Nakshatra
        nak_idx, pada, span = nakshatra_from_longitude(asc_long)
        assert nak_idx == 12
        assert nakshatra_index_to_name(nak_idx) == "UTHIRAM"
        assert pada == 3


# ============================================================================
# VALIDATION TESTS (Optional - requires CorePrimitives.json)
# ============================================================================

class TestCorePrimitivesValidation:
    """Test validation against CorePrimitives.json"""
    
    def test_validate_against_core_primitives(self):
        """
        Validate mappings against CorePrimitives.json.
        
        This test will be skipped if CorePrimitives.json is not found.
        """
        results = validate_against_core_primitives()
        
        if "error" in results:
            pytest.skip("CorePrimitives.json not found - validation skipped")
        
        # Check all validations passed
        assert results.get("grahas", False), "Graha mappings don't match CorePrimitives"
        assert results.get("rasis", False), "Rasi mappings don't match CorePrimitives"
        assert results.get("nakshatras", False), "Nakshatra mappings don't match CorePrimitives"


# ============================================================================
# PERFORMANCE TESTS (Optional)
# ============================================================================

class TestPerformance:
    """Performance tests for frequently-called functions"""
    
    def test_rasi_calculation_performance(self):
        """Test performance of rasi calculations"""
        import time
        
        start = time.perf_counter()
        for i in range(10000):
            long = (i * 13.7) % 360  # generate different longitudes
            rasi_index_from_longitude(long)
            degree_in_rasi(long)
        elapsed = time.perf_counter() - start
        
        # Should complete 10k calculations in < 0.1 seconds
        assert elapsed < 0.1, f"Rasi calculation too slow: {elapsed:.3f}s"
    
    def test_nakshatra_calculation_performance(self):
        """Test performance of nakshatra calculations"""
        import time
        
        start = time.perf_counter()
        for i in range(10000):
            long = (i * 13.7) % 360
            nakshatra_from_longitude(long)
        elapsed = time.perf_counter() - start
        
        # Should complete 10k calculations in < 0.2 seconds
        assert elapsed < 0.2, f"Nakshatra calculation too slow: {elapsed:.3f}s"


# ============================================================================
# USAGE EXAMPLES (for documentation)
# ============================================================================

def example_usage():
    """
    Example usage of graha.py in extractors.
    
    This is not a test, but serves as documentation.
    """
    # Example 1: Convert PyJHora planet index to output format
    pyjhora_planet_idx = 0  # Sun from PyJHora
    graha_id = GrahaID(pyjhora_planet_idx)
    planet_string_id = graha_id_to_string(graha_id)  # "SUN"
    planet_name = graha_id_to_name(graha_id)  # "Sun"
    
    # Example 2: Calculate rasi and degree from longitude
    planet_longitude = 187.627
    rasi_idx = rasi_index_from_longitude(planet_longitude)  # 7 (Libra)
    rasi_name = rasi_index_to_name(rasi_idx)  # "LIBRA"
    degree = degree_in_rasi(planet_longitude)  # 7.627
    
    # Example 3: Calculate nakshatra from longitude
    nak_idx, pada, span = nakshatra_from_longitude(planet_longitude)
    nak_name = nakshatra_index_to_name(nak_idx)  # "SWAATHI"
    nak_lord_name = nakshatra_lord(nak_idx)  # "Rahu"
    
    # Example 4: Build planet dict for JSON output
    planet_dict = {
        "id": planet_string_id,
        "name": planet_name,
        "longitude_deg": planet_longitude,
        "degree_in_sign": degree,
        "sign_index": rasi_idx,
        "sign_name": rasi_name,
        "nakshatra_index": nak_idx,
        "nakshatra_name": nak_name,
        "nakshatra_pada": pada,
    }
    
    return planet_dict


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
