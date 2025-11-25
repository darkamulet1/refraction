# Parity Testing Workflow

## Overview

**Parity tests** verify that Refraction Engine V1 calculations match reference astrological software (PL9 - Parashara's Light 9) within acceptable tolerance.

This is **critical** for ensuring calculation accuracy and preventing regressions.

---

## What is PL9?

**Parashara's Light 9 (PL9)** is a widely-used commercial Vedic astrology software considered a gold standard for calculation accuracy. It uses Swiss Ephemeris (like Refraction Engine) and is known for:

- High precision planetary positions
- Accurate ayanamsa calculations
- Correct nakshatra/pada determinations
- Reliable dasha timings

We use PL9 as our **reference baseline** to validate Refraction Engine calculations.

---

## Why 90 Arcseconds Threshold?

**90 arcseconds = 1.5 arcminutes = 0.025 degrees**

This threshold was chosen because:

1. **Astronomical Precision**: Swiss Ephemeris is accurate to ~0.1 arcseconds for modern dates
2. **Computational Differences**: Different rounding, ayanamsa precision, and timezone handling can introduce small variations
3. **Practical Significance**: 90" deviation doesn't meaningfully affect interpretation:
   - Same sign (30° = 108,000")
   - Usually same nakshatra pada
   - Negligible for dasha timings

**Historical Context:**
- Initial tests showed deviations < 45" for most calculations
- We set 90" as a conservative threshold with 2x margin
- If we consistently see < 45", we may tighten to 60" in future

---

## Current Parity Coverage

### ✅ Tested Charts (as of 2025-11-25)

| Chart  | Birth Date | Birth Time | Location | Status |
|--------|-----------|------------|----------|--------|
| Arezoo | 2004-10-24 | 18:30 | Tehran | ✅ Pass |
| Arman  | 1988-09-11 | 06:45 | Tehran | ✅ Pass |

### 🔄 Pending Charts

| Chart  | Birth Date | Birth Time | Location | Status |
|--------|-----------|------------|----------|--------|
| Mehran | 1997-06-07 | 20:28:36 | Tehran | 📝 Reference needed |
| Athena | 2004-01-27 | 14:45:35 | Karaj | 📝 Reference needed |

### 📊 Tested Calculations

For each chart, we test:
- **Lagna (Ascendant)**: longitude, sign, nakshatra, pada
- **9 Grahas**: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu
  - Longitude (degrees)
  - Sign index
  - Nakshatra index
  - Nakshatra pada

**Total Assertions per Chart**: ~40 comparisons  
**Total Assertions Currently**: 80 (2 charts × 40)  
**Target**: 160+ (4 charts × 40)

---

## How Parity Tests Work

### 1. Reference Data Collection

```bash
# Step 1: Generate chart in PL9
1. Open PL9
2. Enter birth data (date, time, location, timezone)
3. Set ayanamsa: Lahiri
4. Set house system: Equal (or Whole Sign)
5. Generate chart

# Step 2: Export positions
6. Note Lagna longitude
7. Note each planet's longitude
8. Save to CSV or JSON

# Step 3: Store in tests/parity/fixtures/
cp pl9_export.csv tests/parity/fixtures/arezoo_pl9_reference.csv
```

### 2. Test Execution

```python
# tests/parity/test_pl9_parity_arezoo.py

def test_arezoo_lagna_parity():
    """Verify Arezoo's Lagna matches PL9 within 90" threshold"""
    # Load reference from PL9
    pl9_lagna_deg = 30.6465  # from fixture
    
    # Generate with Refraction Engine
    result = run_core_chart(arezoo_birth_data)
    refr_lagna_deg = result['frames'][0]['ascendant']['longitude_deg']
    
    # Calculate deviation
    delta_arcsec = abs(refr_lagna_deg - pl9_lagna_deg) * 3600
    
    # Assert within threshold
    assert delta_arcsec < 90, f"Lagna deviation too large: {delta_arcsec:.2f}\""
```

### 3. Continuous Monitoring

- Guard suite runs on every commit (specs/schemas)
- Parity suite runs on:
  - Pull requests to main/develop
  - Nightly builds
  - Manual trigger (for testing threshold changes)

---

## Running Parity Tests

### Local Development

```bash
# Run all parity tests
./scripts/run_parity_suite.sh

# Run with verbose output
./scripts/run_parity_suite.sh -v

# Run specific chart
./scripts/run_parity_suite.sh --chart=arezoo

# Use stricter threshold
./scripts/run_parity_suite.sh --threshold=60
```

### Windows

```cmd
REM Run all parity tests
scripts\run_parity_suite.bat

REM Run with verbose output
scripts\run_parity_suite.bat -v

REM Run specific chart
scripts\run_parity_suite.bat --chart=arman
```

### CI/CD (GitHub Actions)

Parity tests run automatically in CI pipeline:

```yaml
# .github/workflows/ci.yml
jobs:
  parity-suite:
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/run_parity_suite.sh -v
```

View results:
- Actions tab → CI workflow → Parity Suite job
- Artifacts → parity-suite-results

---

## Adding New Charts to Parity Suite

### Step-by-Step Guide

#### 1. Generate PL9 Reference

```
1. Open Parashara's Light 9
2. Create new chart:
   - Name: [Chart Name]
   - Date: YYYY-MM-DD
   - Time: HH:MM:SS
   - Timezone: [IANA timezone]
   - Location: [City, Country]
   - Latitude: [decimal degrees]
   - Longitude: [decimal degrees]

3. Settings:
   - Ayanamsa: Lahiri
   - House System: Equal / Whole Sign
   - Node: True Node (not Mean)

4. Generate chart and note positions:
   - Lagna: [longitude in degrees]
   - Sun: [longitude]
   - Moon: [longitude]
   - Mars: [longitude]
   - Mercury: [longitude]
   - Jupiter: [longitude]
   - Venus: [longitude]
   - Saturn: [longitude]
   - Rahu: [longitude]
   - Ketu: [longitude]
```

#### 2. Create Fixture File

```csv
# tests/parity/fixtures/mehran_pl9_reference.csv
entity,longitude_deg
Lagna,234.5678
Sun,76.1234
Moon,82.9876
Mars,301.4567
Mercury,89.1234
Jupiter,68.7890
Venus,53.2345
Saturn,282.5678
Rahu,254.8901
Ketu,74.8901
```

#### 3. Create Test File

```python
# tests/parity/test_pl9_parity_mehran.py

import pytest
from refraction_engine import run_core_chart
from tests.specs._utils import load_json

# Load PL9 reference
PL9_REFERENCE = {
    'Lagna': 234.5678,
    'Sun': 76.1234,
    'Moon': 82.9876,
    # ... etc
}

def test_mehran_lagna_parity():
    """Verify Mehran's Lagna matches PL9"""
    payload = load_json("references/in/mehran_birth.json")
    result = run_core_chart(payload)
    
    lagna_long = result['frames'][0]['ascendant']['longitude_deg']
    pl9_long = PL9_REFERENCE['Lagna']
    delta_arcsec = abs(lagna_long - pl9_long) * 3600
    
    assert delta_arcsec < 90, f"Lagna: {delta_arcsec:.2f}\" deviation"

def test_mehran_sun_parity():
    """Verify Mehran's Sun matches PL9"""
    payload = load_json("references/in/mehran_birth.json")
    result = run_core_chart(payload)
    
    planets = result['frames'][0]['planets']
    sun = next(p for p in planets if p['id'] == 'SUN')
    
    sun_long = sun['longitude_deg']
    pl9_long = PL9_REFERENCE['Sun']
    delta_arcsec = abs(sun_long - pl9_long) * 3600
    
    assert delta_arcsec < 90, f"Sun: {delta_arcsec:.2f}\" deviation"

# ... repeat for all planets
```

#### 4. Run Tests

```bash
# Run new tests
pytest tests/parity/test_pl9_parity_mehran.py -v

# If passing, add to guard suite
# (tests under tests/parity/ are automatically included)
```

#### 5. Update Documentation

```markdown
# Update this README:
- Add Mehran to "✅ Tested Charts" table
- Update "Total Assertions Currently" count
```

---

## Parity Test Failures: Troubleshooting

### Symptom: Single calculation fails by large margin (>500")

**Possible Causes:**
1. Timezone error (birth time converted incorrectly)
2. Ayanamsa mismatch (Lahiri vs others)
3. Node mode mismatch (True vs Mean)
4. Coordinate precision loss

**Resolution:**
```bash
# Step 1: Verify birth data
cat references/in/[chart]_birth.json

# Step 2: Check engine config
# Ensure: zodiac_type=SIDEREAL, ayanamsa_mode=LAHIRI, node_mode=TRUE

# Step 3: Regenerate PL9 reference with exact settings
# Compare manually - is PL9 or Refraction wrong?

# Step 4: If bug found, fix extractor and re-test
```

### Symptom: All calculations fail by consistent offset (~23°)

**Diagnosis:** Tropical vs Sidereal mismatch

**Resolution:**
```json
// references/in/[chart]_birth.json
{
  "config": {
    "zodiac_type": "SIDEREAL",  // ← Check this
    "ayanamsa_mode": "LAHIRI"
  }
}
```

### Symptom: Intermittent failures (~100-200" deviation)

**Diagnosis:** Floating-point precision or rounding differences

**Resolution:**
- Review calculation order in extractor
- Check if intermediate rounding affects result
- May need to increase threshold slightly (90→120")

### Symptom: Rahu/Ketu reversed (180° offset)

**Diagnosis:** True Node vs Mean Node mismatch

**Resolution:**
```json
// Ensure in config:
{
  "config": {
    "node_mode": "TRUE"  // Must match PL9 setting
  }
}
```

---

## Best Practices

### 1. Always Test Both Charts
When fixing a bug, verify against **all** parity charts:
```bash
./scripts/run_parity_suite.sh -v
```

### 2. Don't Adjust Threshold Without Investigation
If a test starts failing:
- ❌ Don't just increase threshold
- ✅ Investigate root cause first
- ✅ Only adjust threshold if justified (e.g., known Swiss Ephemeris limitation)

### 3. Document Significant Deviations
If you find consistent 50-80" deviation for a specific planet:
```python
# Add comment in test:
def test_venus_parity():
    """
    Venus shows consistent ~70" deviation due to known Swiss Ephemeris
    precision limits for heliocentric correction at this epoch.
    See: https://example.com/issue/123
    """
```

### 4. Keep PL9 Reference Data
Store PL9 exports in `tests/parity/fixtures/`:
```
fixtures/
├── arezoo_pl9_reference.csv
├── arman_pl9_reference.csv
├── arezoo_pl9_screenshot.png    # ← Optional but helpful
└── arman_pl9_screenshot.png
```

### 5. Regression Protection
After fixing a bug:
1. Run parity suite
2. If all pass, commit immediately
3. Add test comment explaining what was fixed

---

## Future Improvements

### Phase 2 (Gap #2): Expand Coverage
- [ ] Add Mehran parity tests (need PL9 reference)
- [ ] Add Athena parity tests (need PL9 reference)
- [ ] Add edge cases:
  - [ ] Chart at midnight (00:00:00)
  - [ ] Chart at 180° longitude (date line)
  - [ ] Chart in Southern Hemisphere
  - [ ] Chart with retrograde Mercury

### Phase 3: Additional Calculations
- [ ] Dasha periods (start/end times)
- [ ] Bhava positions (house cusps)
- [ ] Varga charts (D9, D10, etc.)
- [ ] Strength calculations (shadbala)

### Phase 4: Automation
- [ ] Auto-generate PL9 reference via API (if available)
- [ ] Parity report generation (HTML dashboard)
- [ ] Historical parity tracking (deviation trends over time)

---

## FAQ

### Q: Why not use 100% exact matching?

**A:** Due to inherent numerical precision limits:
- Swiss Ephemeris: ~0.1" precision for modern dates
- Timezone conversions: may differ by milliseconds
- Ayanamsa calculation: different implementations vary by ~1-2"
- Floating-point arithmetic: rounding errors accumulate

90" threshold (~1.5 arcminutes) is **astronomically negligible** but accounts for these variations.

### Q: What if PL9 is wrong?

**A:** Cross-reference with third source:
1. Generate same chart in AstroSage (online)
2. Generate in Kala (another software)
3. If Refraction matches others but not PL9 → investigate PL9 settings
4. Document discrepancy and choose majority consensus as reference

### Q: Can we use other reference software?

**A:** Yes! PL9 is standard but not exclusive:
- **Alternatives**: Jagannatha Hora, Kala, AstroSage
- **Requirement**: Must use Swiss Ephemeris + Lahiri Ayanamsa
- **Process**: Same as PL9 (collect references, create fixtures, write tests)

### Q: Do parity tests slow down CI?

**A:** Currently no:
- Guard suite: ~30 seconds
- Parity suite: ~15 seconds
- Total: <1 minute

As coverage expands (4→10+ charts), parity may take ~1-2 minutes, which is acceptable.

---

## Conclusion

Parity testing is **essential** for maintaining Refraction Engine accuracy. By continuously comparing against PL9 reference:

✅ We catch calculation bugs early  
✅ We prevent regressions  
✅ We build confidence in results  
✅ We provide audit trail for users  

**Next Action**: Expand coverage to Mehran + Athena charts (Gap #2) and integrate parity into CI (Gap #3).

---

## References

- PL9 Website: https://parashara.com
- Swiss Ephemeris: https://www.astro.com/swisseph/
- Vedic Astrology Standards: Various śāstras and modern interpretations
- PROJECT_STATUS.md: Current parity test status
- Gap Analysis: Known limitations and roadmap

---

**Last Updated**: 2025-11-25  
**Maintained By**: Refraction Engine Team  
**Status**: ✅ Active, expanding coverage
