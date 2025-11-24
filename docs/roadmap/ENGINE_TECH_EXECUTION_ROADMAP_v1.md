# Refraction Engine V1: Technical Execution Roadmap

## Executive Summary

Refraction Engine V1 is built as a thin wrapper around PyJHora. The v0min layer is now legacy-only and archived in `maintenance/legacy-v0min-archive`. Future work lives in `src/refraction_engine/core_chart.py` and the extractor spec in `docs/specs/core_chart_spec_v1.md`.

**Architectural decision (Nov 2025):**  
The chosen path is a direct PyJHora integration plus a lightweight validation layer. The v0min artifacts are not part of Refraction Engine V1.

---

## Phase 0 – Core API Alignment (Day 1-3)

1. **Day 1 — Validate inputs & imports**
   - Parse incoming payloads (birth data, timezone, city) and compute JD/place tuples.
   - Use `import jhora.panchanga.drik as drik` and `import jhora.horoscope.chart.charts as charts` (no v0min).
   - Create `src/refraction_engine/core_chart.py::run_core_chart`, validate payload via `core_chart_spec_v1`, raise `NotImplementedError` until implemented.

2. **Day 2 — Panchanga builders**
   - Implement helpers that call `drik.tithi()`, `drik.nakshatra()`, `drik.yogam()`, `drik.karana()`, `drik.vaara()`, sunrise/sunset/moonrise/moonset.
   - Keep formatting logic consistent with the full API reference tables.

3. **Day 3 — Core chart positions**
   - Wrap `charts.divisional_chart(jd, place, divisional_chart_factor=1)` to retrieve ascendant, planets, house lists.
   - Ensure output matches `core_chart_spec_v1` shape while referencing `utils.RASHIS`, `utils.PLANET_NAMES`, and other PyJHora constants.

---

## Phase 1 – Extractor Implementation (Day 4-10)

1. **Divisional charts (D1…D144)**: iterate supported factors, call `charts.divisional_chart`, capture results for the spec. Use caching (`functools.lru_cache`) and optional multithreading only around PyJHora API calls.

2. **Dashas & strengths**: call `jhora.horoscope.dhasa.graha.vimsottari`, `narayana`, `sudasa`, etc., plus `strength.shadbala`, `strength.bhava_bala`, `strength.ashtakavarga`.

3. **Yoga detection**: wrap `jhora.horoscope.chart.yoga` helpers through a deterministic aggregator matching 100+ yogas. No v0min bridging is referenced.

4. **Special points & transit calculations**: rely on `charts.bhava_lagna`, `charts.sree_lagna`, `transit.tajaka`, `transit.saham`, etc., with outputs shaped for JSON/YAML.

---

## Phase 2 – API & UI Integration

1. **FastAPI endpoints**: expose `/api/v1/calculate` powered by `RefractionEngine` (which internally uses `refraction_engine.core_chart`), not v0min.
2. **React UI**: call backend via standard fetch, display results from JSON shaped by the spec.
3. **Testing**: run pytest, coverage, golden outputs referencing `pyjhora_knowledge/tests_contract` scripts while keeping focus on PyJHora modules.

---

## Phase 3 – Operational Readiness

- **Optimization**: use caching, `ThreadPoolExecutor`, and lazy loading around PyJHora functions rather than any v0min infrastructure.
- **Documentation & deployment**: keep instructions for Docker, env vars, and dependency management focused on the direct PyJHora -> FastAPI path.
