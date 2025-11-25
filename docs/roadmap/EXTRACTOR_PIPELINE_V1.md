# Extractor Pipeline V1

Structured guide for building and maintaining Refraction Engine extractors.

---

## 0. Knowledge Refresh (only after PyJHora updates)
1. `python docs/extractor_knowledge/knowledge_scan_full.py`
2. `python docs/extractor_knowledge/build_knowledge_artifacts.py`
3. Copy generated JSON/MD into `docs/pyjhora_knowledge/`
4. Update downstream specs (`engine_config_spec_v1`, `api_whitelist_core_chart_v1`, `tests_binding_core_chart_v1`) to reflect refreshed artifacts

---

## 1. Define the contract
1. **Input Spec** – author/extend `core_input_spec_v1` and schema if new knobs are needed.
2. **Output Spec** – write `docs/specs/<extractor>_spec_v1.md` + `.schema.json`
3. Capture any supporting docs (primitives, tables) inside `docs/specs/` so they version with the repo.

---

## 2. Implement extractor
1. Create module under `src/refraction_engine/`:
   - parse payload via `_parse_core_chart_input` or a tailored helper
   - map config through `CorePrimitives` (never call PyJHora constants directly)
   - call PyJHora using the API whitelist
   - shape output per spec
2. Expose the entry point in `src/refraction_engine/__init__.py`
3. Ensure `CorePrimitives` is referenced from `docs/pyjhora_knowledge/primitives/CorePrimitives.json`

---

## 3. Tests & Guards
### Golden tests
1. Add canonical fixtures under `references/in/` (same config unless test requires variation)
2. `tests/specs/test_<extractor>_binding_<name>.py`
   - assert on stable IDs/indexes (not localized names)
   - include at least two charts (different dates/locations)

### Schema tests
1. Parametrize `tests/specs/test_<extractor>_schema.py` across all fixtures
2. Include a minimal payload to prove optional fields truly optional
3. Add a “negative” case if schema should reject invalid input

### Input schema tests
1. `tests/specs/test_core_input_schema.py` must cover every fixture (and minimal payload)
2. Add new fixtures to that parametrized test automatically

### Smoke tests
1. `tests/specs/test_minimal_payloads.py` ensures minimal payload runs for both chart and panchanga
2. Extend with new extractors as they appear

---

## 4. Guard suite & CI
1. `pytest tests/specs` is the canonical guard suite
2. Run locally before every commit and wire into CI/GitHub Actions

---

## 5. Rolling a new extractor (checklist)
1. Refresh knowledge (if PyJHora changed)  
2. Update `core_input_spec_v1` if new config is needed  
3. Draft output spec + schema  
4. Implement extractor module + expose entry point  
5. Add fixtures, golden tests, schema tests, input tests  
6. Run `pytest tests/specs`  
7. Update docs (roadmap, knowledge analysis) if pipelines change

This pipeline keeps every extractor aligned: One input contract, one output spec, golden facts, schema enforcement, and automated guard suite.
