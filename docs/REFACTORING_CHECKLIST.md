# Refactoring Checklist - Practical Steps

## 🎯 Goal
Replace local mappings in extractors with graha.py utilities.

---

## ✅ Pre-Flight Check

Before starting, verify:

```bash
# 1. graha.py is installed
python -c "from refraction_engine.graha import GrahaID; print('✅ graha.py OK')"

# 2. Tests pass
pytest tests/refraction_engine/test_graha.py -v
# Expected: 50+ tests passing

# 3. Backup current state
git commit -am "Backup before graha.py refactoring"
```

---

## 📝 Refactoring Steps

### File 1: core_chart.py (Estimated: 10 min)

#### Step 1.1: Add imports at top
```python
# ADD THIS at top of file:
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
```

#### Step 1.2: Find and DELETE local mappings
```python
# DELETE THESE (search for them):
PLANET_IDS = {...}      # Remove entire dict
PLANET_NAMES = {...}    # Remove entire dict
RASI_NAMES = {...}      # Remove entire dict
NAKSHATRA_NAMES = {...} # Remove entire dict (if exists)
```

#### Step 1.3: Replace planet formatting
```python
# FIND this pattern:
planet_id = PLANET_IDS[planet_idx]
planet_name = PLANET_NAMES[planet_idx]

# REPLACE with:
graha_id = GrahaID(planet_idx)
planet_id = graha_id_to_string(graha_id)
planet_name = graha_id_to_name(graha_id)
```

#### Step 1.4: Replace rasi calculation
```python
# FIND this pattern:
rasi_idx = int(longitude // 30) + 1
degree = longitude % 30
rasi_name = RASI_NAMES[rasi_idx]

# REPLACE with:
rasi_idx = rasi_index_from_longitude(longitude)
degree = degree_in_rasi(longitude)
rasi_name = rasi_index_to_name(rasi_idx)
```

#### Step 1.5: Replace nakshatra calculation
```python
# FIND this pattern:
nak_span = 360.0 / 27
nak_idx = int(longitude / nak_span) + 1
pada = int((longitude % nak_span) / (nak_span / 4)) + 1

# REPLACE with:
nak_idx, pada, span_deg = nakshatra_from_longitude(longitude)
nak_name = nakshatra_index_to_name(nak_idx)
```

#### Step 1.6: Test
```bash
# Run core_chart tests
pytest tests/specs/test_core_chart_binding_mehran.py -v
pytest tests/specs/test_core_chart_schema.py -v

# Expected: All tests still passing ✅
```

---

### File 2: panchanga.py (Estimated: 5 min)

#### Step 2.1: Add imports
```python
from refraction_engine.graha import (
    nakshatra_index_to_name,
    nakshatra_lord,
    vaara_index_to_name,
)
```

#### Step 2.2: DELETE local mappings
```python
# DELETE:
NAKSHATRA_NAMES = {...}
NAKSHATRA_LORDS = {...}
VAARA_NAMES = {...}
```

#### Step 2.3: Replace nakshatra formatting
```python
# FIND:
nak_name = NAKSHATRA_NAMES[nak_idx]
nak_lord = NAKSHATRA_LORDS[nak_idx]

# REPLACE:
nak_name = nakshatra_index_to_name(nak_idx)
nak_lord = nakshatra_lord(nak_idx)
```

#### Step 2.4: Replace vaara formatting
```python
# FIND:
vaara_name = VAARA_NAMES[vaara_idx]

# REPLACE:
vaara_name = vaara_index_to_name(vaara_idx)
```

#### Step 2.5: Test
```bash
pytest tests/specs/test_panchanga_binding_mehran.py -v
pytest tests/specs/test_panchanga_schema.py -v
```

---

### File 3: dashas_vimshottari.py (Estimated: 5 min)

#### Step 3.1: Add imports
```python
from refraction_engine.graha import (
    graha_id_to_string,
)
```

#### Step 3.2: DELETE local mappings
```python
# DELETE:
PLANET_IDS = {...}
```

#### Step 3.3: Replace planet_id field
```python
# FIND:
planet_id = PLANET_IDS[planet_idx]

# REPLACE:
planet_id = graha_id_to_string(GrahaID(planet_idx))
```

#### Step 3.4: Test
```bash
pytest tests/specs/test_dashas_vimshottari_binding_mehran.py -v
pytest tests/specs/test_dashas_vimshottari_schema.py -v
```

---

### File 4: strengths.py (Estimated: 5 min)

#### Step 4.1: Add imports
```python
from refraction_engine.graha import (
    GrahaID,
    graha_id_to_string,
)
```

#### Step 4.2: DELETE local mappings
```python
# DELETE:
PLANET_IDS = {...}
```

#### Step 4.3: Replace planet_id field
```python
# FIND:
planet_id = PLANET_IDS[planet_idx]

# REPLACE:
planet_id = graha_id_to_string(GrahaID(planet_idx))
```

#### Step 4.4: Test
```bash
pytest tests/specs/test_strengths_binding_mehran.py -v
```

---

## 🧪 Final Verification

After refactoring all files:

### 1. Run full test suite
```bash
# All specs tests
pytest tests/specs -v

# Expected: All 26 tests passing ✅
```

### 2. Generate test outputs
```bash
# Generate bundles
python -m refraction_engine.cli mehran_birth.json > /tmp/mehran_after.json
python -m refraction_engine.cli arezoo_birth.json > /tmp/arezoo_after.json

# Compare with golden references
diff references/out/mehran_core_bundle.json /tmp/mehran_after.json
diff references/out/arezoo_core_bundle.json /tmp/arezoo_after.json

# Expected: No differences (or only timestamp differences) ✅
```

### 3. Check parity (if available)
```bash
pytest tests/parity -v
# Expected: Arezoo + Arman parity still passing ✅
```

---

## 🎉 Success Criteria

After refactoring, you should see:

✅ All extractors use graha.py imports  
✅ No local PLANET_IDS/RASI_NAMES/etc. dicts remain  
✅ All 26 tests in tests/specs passing  
✅ Generated outputs identical to golden references  
✅ Parity tests still passing (if applicable)  

**Code reduction**: ~200-250 lines removed across all files

---

## 🐛 Troubleshooting

### Problem: ImportError: cannot import name 'GrahaID'

**Solution**:
```bash
# Check graha.py is in correct location
ls -la src/refraction_engine/graha.py

# Verify Python path
python -c "import sys; print(sys.path)"

# Try explicit import
cd src && python -c "from refraction_engine.graha import GrahaID; print('OK')"
```

---

### Problem: Tests fail after refactoring

**Solution**:
```bash
# Check which test failed
pytest tests/specs -v --tb=short

# Common issues:
# 1. Missing import
# 2. Wrong function name (graha_id_to_name vs graha_name_to_id)
# 3. Forgot to convert planet_idx to GrahaID enum

# Revert and try again:
git checkout -- src/refraction_engine/[file].py
# Then redo that file more carefully
```

---

### Problem: Output differs from golden reference

**Solution**:
```bash
# Check what differs
diff references/out/mehran_core_bundle.json /tmp/mehran_after.json | head -20

# If only timestamp differs → OK ✅
# If planet positions differ → Bug in refactoring ❌

# Debug:
# 1. Check longitude calculations
# 2. Verify rasi_index calculation
# 3. Verify nakshatra calculation
```

---

## 📊 Time Estimate

| Task | Time |
|------|------|
| Pre-flight check | 5 min |
| core_chart.py refactor | 10 min |
| panchanga.py refactor | 5 min |
| dashas_vimshottari.py refactor | 5 min |
| strengths.py refactor | 5 min |
| Final verification | 10 min |
| **Total** | **40 min** |

---

## 🚀 Quick Commands

```bash
# 1. Backup
git commit -am "Before graha.py refactoring"

# 2. Verify graha.py works
pytest tests/refraction_engine/test_graha.py -v

# 3. Refactor files (one by one, test after each)
# ... edit core_chart.py ...
pytest tests/specs/test_core_chart*.py -v

# ... edit panchanga.py ...
pytest tests/specs/test_panchanga*.py -v

# ... edit dashas_vimshottari.py ...
pytest tests/specs/test_dashas*.py -v

# ... edit strengths.py ...
pytest tests/specs/test_strengths*.py -v

# 4. Final check
pytest tests/specs -v

# 5. Commit
git commit -am "Refactor: Use graha.py for all mappings (Gap #1)"
```

---

## ✅ You're Done!

When all tests pass and outputs match, Gap #1 is complete! 🎉

Next step: Gap #3 (Parity in CI) → See next checklist.
