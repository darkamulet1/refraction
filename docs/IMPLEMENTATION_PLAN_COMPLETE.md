# 🚀 Implementation Plan - Complete Step-by-Step

**بر اساس**: PyJHora Knowledge Pack + Gap #1 & #3  
**هدف**: پیاده‌سازی کامل Refraction Engine V1 Architecture

---

## 📋 Phase Map

```
Phase 0: Foundation ✅ (Gap #1 & #3 - DONE)
    ↓
Phase 1: Core Infrastructure 🔄 (این هفته)
    ↓
Phase 2: Extractor Refactoring 🔄 (این هفته)
    ↓
Phase 3: New Extractors 📝 (هفته بعد)
    ↓
Phase 4: Testing & QA 🧪 (هفته بعد)
    ↓
Phase 5: Documentation & Release 📚 (دو هفته بعد)
```

---

## ✅ Phase 0: Foundation (DONE)

### Completed:
1. ✅ graha.py (500 lines) - Single source of truth
2. ✅ test_graha.py (400 lines) - 50+ tests
3. ✅ run_parity_suite.sh/bat - Parity automation
4. ✅ CI workflow - GitHub Actions integration

### Impact:
- ~250 lines removed (duplicates)
- 47% performance improvement
- 156+ tests total
- Automated parity in CI

---

## 🔄 Phase 1: Core Infrastructure (Days 1-3)

### Day 1: CorePrimitives Parser (4 hours)

#### 1.1. Create primitives_parser.py
```bash
# Create file
touch src/refraction_engine/core/primitives_parser.py
```

**Implementation**:
- [ ] PrimitivesParser class
- [ ] Parse string tuples to actual tuples
- [ ] Load CorePrimitives.json
- [ ] Validation methods
- [ ] Singleton pattern
- [ ] Test: `pytest tests/refraction_engine/test_primitives_parser.py -v`

**Expected Output**:
```python
from refraction_engine.core.primitives_parser import get_primitives

prims = get_primitives()
assert prims.get_ayanamsa_id('LAHIRI') == 7
assert prims.get_nakshatra_lord(0) == 8  # Ashwini -> Ketu
```

**Time**: 4 hours

---

#### 1.2. Sync graha.py with CorePrimitives (2 hours)

**Task**: Add validation function to graha.py

```python
def validate_against_core_primitives() -> bool:
    """Validate graha.py constants against CorePrimitives.json"""
    from .primitives_parser import get_primitives
    
    prims = get_primitives()
    
    # Validate nakshatra lords
    for nak_idx in range(27):
        expected = prims.get_nakshatra_lord(nak_idx)
        actual = NAKSHATRA_LORDS[nak_idx]
        assert expected == actual, f"Nakshatra {nak_idx}: expected {expected}, got {actual}"
    
    # Validate ayanamsa modes
    # ... more validations
    
    return True
```

**Test**:
```bash
pytest tests/refraction_engine/test_graha.py::test_core_primitives_validation -v
```

**Time**: 2 hours

---

### Day 2: Configuration System (6 hours)

#### 2.1. Create config.py (4 hours)

```bash
touch src/refraction_engine/core/config.py
```

**Implementation**:
- [ ] EngineConfig class (Pydantic)
- [ ] Validators for ayanamsa, house_system, bodies
- [ ] to_pyjhora_params() method
- [ ] DEFAULT_CONFIG constant
- [ ] Test: `pytest tests/refraction_engine/test_config.py -v`

**Expected Usage**:
```python
config = EngineConfig(
    ayanamsa_mode="LAHIRI",
    house_system="5",
    node_mode="TRUE"
)

pyjhora_params = config.to_pyjhora_params()
assert pyjhora_params['ayanamsa_id'] == 7
```

**Time**: 4 hours

---

#### 2.2. Create engine_config_spec_v1.yaml (2 hours)

```bash
touch docs/specs/engine_config_spec_v1.yaml
```

**Content** (based on PYJHORA_CONFIGURATION_OPTIONS.md):

```yaml
ayanamsa:
  description: "Sidereal mode for chart calculations"
  default: "LAHIRI"
  allowed:
    - FAGAN
    - LAHIRI
    - RAMAN
    - KP
    - TRUE_CITRA
    - SURYASIDDHANTA
  mapping:
    LAHIRI: 7
    KP: 5
    RAMAN: 8

house_systems:
  description: "House system for bhava calculations"
  default: "5"
  allowed:
    - "1"   # Equal
    - "2"   # Whole Sign
    - "3"   # Sripathi
    - "5"   # Placidus
  mapping:
    "1": "equal"
    "5": "placidus"

node_mode:
  description: "Rahu/Ketu calculation mode"
  default: "TRUE"
  allowed:
    - TRUE
    - MEAN

include_bodies:
  description: "Planets to include in calculations"
  default:
    - SUN
    - MOON
    - MERCURY
    - VENUS
    - MARS
    - JUPITER
    - SATURN
    - RAHU
    - KETU
```

**Time**: 2 hours

---

### Day 3: Validation Layer (4 hours)

#### 3.1. Create validation.py (3 hours)

```bash
touch src/refraction_engine/core/validation.py
```

**Implementation**:
- [ ] BirthInput class (Pydantic)
- [ ] CoreInputPayload class
- [ ] validate_input() function (JSON schema)
- [ ] validate_core_input() function (Pydantic)
- [ ] Test: `pytest tests/refraction_engine/test_validation.py -v`

**Expected Usage**:
```python
payload = {...}
validated = validate_core_input(payload)
assert validated.birth.datetime_local == "2004-10-24T18:30:00"
```

**Time**: 3 hours

---

#### 3.2. Create exceptions.py (1 hour)

```bash
touch src/refraction_engine/core/exceptions.py
```

**Content**:
```python
class RefractionEngineError(Exception):
    """Base exception"""
    pass

class ValidationError(RefractionEngineError):
    """Input validation failed"""
    pass

class ConfigurationError(RefractionEngineError):
    """Invalid configuration"""
    pass

class ExtractionError(RefractionEngineError):
    """Extraction failed"""
    pass
```

**Time**: 1 hour

---

## 🔄 Phase 2: Extractor Refactoring (Days 4-6)

### Day 4: Base Extractor + Factory (4 hours)

#### 4.1. Create base.py (2 hours)

```bash
touch src/refraction_engine/extractors/base.py
```

**Implementation**: (see COMPLETE_ARCHITECTURE_DESIGN_V2_EXTRACTORS.md)

**Time**: 2 hours

---

#### 4.2. Create factory.py (2 hours)

```bash
touch src/refraction_engine/factory.py
```

**Implementation**: (see COMPLETE_ARCHITECTURE_DESIGN_V1.md)

**Test**:
```python
from refraction_engine.factory import ExtractorFactory

factory = ExtractorFactory()
core_chart = factory.create_extractor('core_chart', payload)
result = core_chart.extract()
```

**Time**: 2 hours

---

### Day 5: Refactor Existing Extractors (6 hours)

#### 5.1. Refactor core_chart.py (2 hours)

**Changes**:
- [ ] Inherit from BaseExtractor
- [ ] Use graha.py utilities
- [ ] Remove local mappings
- [ ] Test: `pytest tests/specs/test_core_chart*.py -v`

**Time**: 2 hours

---

#### 5.2. Refactor panchanga.py (1.5 hours)

**Changes**:
- [ ] Inherit from BaseExtractor
- [ ] Use graha.py for nakshatra/vaara
- [ ] Remove local mappings
- [ ] Test: `pytest tests/specs/test_panchanga*.py -v`

**Time**: 1.5 hours

---

#### 5.3. Refactor dashas_vimshottari.py (1.5 hours)

**Changes**:
- [ ] Inherit from BaseExtractor
- [ ] Use graha.py for planet IDs
- [ ] Test: `pytest tests/specs/test_dashas*.py -v`

**Time**: 1.5 hours

---

#### 5.4. Refactor strengths.py (1 hour)

**Changes**:
- [ ] Inherit from BaseExtractor
- [ ] Use graha.py for planet IDs
- [ ] Test: `pytest tests/specs/test_strengths*.py -v`

**Time**: 1 hour

---

### Day 6: Integration Testing (4 hours)

#### 6.1. Full guard suite (1 hour)

```bash
pytest tests/specs -v
# Expected: All 26 tests passing ✅
```

---

#### 6.2. Parity suite (1 hour)

```bash
./scripts/run_parity_suite.sh -v
# Expected: Arezoo + Arman passing ✅
```

---

#### 6.3. Bundle generation (1 hour)

```bash
python -m refraction_engine mehran_birth.json > mehran_bundle.json
python -m refraction_engine arezoo_birth.json > arezoo_bundle.json

# Compare with golden
diff references/out/mehran_core_bundle.json mehran_bundle.json
# Expected: No differences ✅
```

---

#### 6.4. Performance testing (1 hour)

```python
import time

start = time.time()
for _ in range(100):
    bundle = factory.extract_all(payload)
elapsed = time.time() - start

print(f"100 bundles in {elapsed:.2f}s")
print(f"Average: {elapsed/100*1000:.2f}ms per bundle")

# Target: <500ms per bundle
```

---

## 📝 Phase 3: New Extractors (Days 7-10)

### Day 7: Special Points Extractor (4 hours)

#### 7.1. Create special_points.py

**Extracts**:
- Bhava Lagna
- Hora Lagna
- Ghati Lagna
- Sree Lagna
- Pranapada Lagna
- Indu Lagna

**PyJHora APIs**:
```python
import jhora.horoscope.chart.charts as charts

bhava_lagna = charts.bhava_lagna(jd, place)
hora_lagna = charts.hora_lagna(jd, place)
sree_lagna = charts.sree_lagna(jd, place)
```

**Spec**: `docs/specs/special_points_spec_v1.md`

**Time**: 4 hours

---

### Day 8: Yogas Extractor (6 hours)

#### 8.1. Create yogas.py

**Extracts**:
- Pancha Mahapurusha Yogas (Hamsa, Malavya, Ruchaka, Bhadra, Sasa)
- Raja Yogas
- Dhana Yogas
- Arishta Yogas

**PyJHora APIs**:
```python
import jhora.horoscope.chart.yoga as yoga

has_hamsa = yoga.hamsa_yoga(planet_positions)
has_malavya = yoga.malavya_yoga(planet_positions)
raja_yogas = yoga.get_raja_yogas(planet_positions)
```

**Spec**: `docs/specs/yogas_spec_v1.md`

**Time**: 6 hours

---

### Day 9-10: Transits Extractor (8 hours)

#### 10.1. Create transits.py

**Extracts**:
- Planet sign entries
- Retrograde periods
- Sankranti dates
- Eclipse dates

**PyJHora APIs**:
```python
import jhora.horoscope.transit.transit as transit

next_entry = transit.next_planet_entry(planet_id, start_jd, target_rasi)
retro_start = transit.vakra_start_date(planet_id, start_jd)
```

**Spec**: `docs/specs/transits_spec_v1.md`

**Time**: 8 hours

---

## 🧪 Phase 4: Testing & QA (Days 11-14)

### Day 11: Expand Parity Coverage

#### 11.1. Add Mehran PL9 Reference
- [ ] Generate Mehran chart in PL9
- [ ] Export to fixture
- [ ] Create test_parity_mehran.py
- [ ] Run: `./scripts/run_parity_suite.sh --chart=mehran`

**Time**: 2 hours

---

#### 11.2. Add Athena PL9 Reference
- [ ] Generate Athena chart in PL9
- [ ] Export to fixture
- [ ] Create test_parity_athena.py
- [ ] Run: `./scripts/run_parity_suite.sh --chart=athena`

**Time**: 2 hours

---

### Day 12: Edge Cases Testing

#### 12.1. Extreme Dates
```python
# BCE dates
payload_bce = {..., "birth_date": "-500-01-01"}

# Future dates
payload_future = {..., "birth_date": "2100-12-31"}

# Boundary latitudes
payload_arctic = {..., "location": {"lat": 89.9, "lon": 0}}
```

**Time**: 4 hours

---

### Day 13: Bundle Schema Validation

#### 13.1. Create test_bundle_validation.py

```python
def test_bundle_matches_schema():
    bundle = factory.extract_all(payload)
    
    # Validate against refraction_core_bundle_spec_v1
    schema = load_schema('refraction_core_bundle_spec_v1')
    jsonschema.validate(bundle, schema)
    
    # Validate each frame
    for frame_name, frame_data in bundle['frames'].items():
        schema_name = frame_data['meta']['schema_version']
        schema = load_schema(schema_name)
        jsonschema.validate(frame_data, schema)
```

**Time**: 4 hours

---

### Day 14: Performance Benchmarking

#### 14.1. Create benchmark suite

```python
import time
import statistics

def benchmark_extractor(name, payload, n=100):
    times = []
    factory = ExtractorFactory()
    
    for _ in range(n):
        start = time.time()
        extractor = factory.create_extractor(name, payload)
        result = extractor.extract()
        elapsed = time.time() - start
        times.append(elapsed)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times),
        'min': min(times),
        'max': max(times),
    }

# Run benchmarks
for extractor in ['core_chart', 'panchanga', 'dashas_vimshottari', 'strengths']:
    results = benchmark_extractor(extractor, payload)
    print(f"{extractor}: {results['mean']*1000:.2f}ms ± {results['stdev']*1000:.2f}ms")
```

**Targets**:
- core_chart: <300ms
- panchanga: <100ms
- dashas_vimshottari: <50ms
- strengths: <200ms
- **Total bundle: <650ms**

**Time**: 4 hours

---

## 📚 Phase 5: Documentation & Release (Days 15-17)

### Day 15: Documentation

#### 15.1. Update README.md
- [ ] Architecture overview
- [ ] Installation guide
- [ ] Quick start
- [ ] API reference
- [ ] Configuration guide

**Time**: 3 hours

---

#### 15.2. Create CHANGELOG.md
```markdown
# Changelog

## [1.0.0] - 2025-12-01

### Added
- ✅ graha.py - Central mapping utilities (Gap #1)
- ✅ Parity suite in CI (Gap #3)
- ✅ CorePrimitives parser
- ✅ Configuration system
- ✅ Validation layer
- ✅ Extractor factory
- ✅ Refactored extractors (4)
- ✅ New extractors (3): special_points, yogas, transits
- ✅ 156+ tests
- ✅ CI with parity

### Changed
- Refactored core_chart.py to use graha.py
- Refactored panchanga.py to use graha.py
- Refactored dashas_vimshottari.py to use graha.py
- Refactored strengths.py to use graha.py

### Removed
- ~250 lines of duplicate mappings
- v0min dependency

### Performance
- 47% faster calculations (80ms vs 150ms for 10k ops)
- <650ms for complete bundle generation

### Testing
- 26 → 156+ tests
- Automated parity testing (4 charts)
- CI pipeline (<2 min)
```

**Time**: 1 hour

---

### Day 16: API Documentation

#### 16.1. Generate API docs

```bash
# Install sphinx
pip install sphinx sphinx-rtd-theme

# Generate docs
sphinx-quickstart docs/api
sphinx-apidoc -o docs/api/source src/refraction_engine
cd docs/api && make html
```

**Time**: 4 hours

---

### Day 17: Release Preparation

#### 17.1. Version tagging
```bash
git tag -a v1.0.0 -m "Release v1.0.0 - Complete Refraction Engine V1"
git push origin v1.0.0
```

---

#### 17.2. Create release notes
- [ ] GitHub release page
- [ ] Highlights
- [ ] Breaking changes
- [ ] Migration guide

---

#### 17.3. Publish package
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

**Time**: 4 hours

---

## 📊 Success Metrics

### Code Quality
- [ ] All tests passing (156+)
- [ ] CI green (<2 min)
- [ ] Code coverage >80%
- [ ] No duplicate mappings
- [ ] Type hints >90%

### Performance
- [ ] <650ms for complete bundle
- [ ] 47% faster than before
- [ ] Memory usage <100MB

### Documentation
- [ ] README complete
- [ ] API docs generated
- [ ] All specs written (7)
- [ ] Examples provided

### Testing
- [ ] 26 → 156+ tests
- [ ] 4 charts in parity
- [ ] Edge cases covered
- [ ] Schema validation

---

## 🎯 Timeline Summary

| Phase | Duration | Status |
|-------|----------|--------|
| Phase 0: Foundation | 3 days | ✅ DONE |
| Phase 1: Core Infrastructure | 3 days | 🔄 Current |
| Phase 2: Extractor Refactoring | 3 days | 📝 Planned |
| Phase 3: New Extractors | 4 days | 📝 Planned |
| Phase 4: Testing & QA | 4 days | 📝 Planned |
| Phase 5: Documentation | 3 days | 📝 Planned |
| **Total** | **20 days** | **3/20 done** |

**Est. Completion**: 2025-12-15

---

## ✅ Next Actions

**این هفته (Days 1-6)**:
1. ✅ Review این طراحی
2. 🔄 Day 1: Create primitives_parser.py
3. 🔄 Day 2: Create config.py + engine_config_spec_v1.yaml
4. 🔄 Day 3: Create validation.py + exceptions.py
5. 🔄 Day 4: Create base.py + factory.py
6. 🔄 Day 5: Refactor all extractors
7. 🔄 Day 6: Integration testing

**Commit points**:
- End of Day 3: "Core infrastructure complete"
- End of Day 6: "Extractor refactoring complete"

**آماده شروع! 🚀**
