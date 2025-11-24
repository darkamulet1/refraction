# Refraction Engine V1: Bug Analysis & Implementation Plan

**Date**: November 24, 2025  
**Status**: Phase 0 — Architectural Reset  
**Version**: 3.0

## Executive Summary

Legacy `v0min` code (data, bridges, adapters) is stored in `maintenance/legacy-v0min-archive` and no longer part of the recommended flow. Refraction Engine V1 implements a thin wrapper (`src/refraction_engine/core_chart.py`) that validates ingress against `docs/specs/core_chart_spec_v1.md`, calls `jhora.panchanga.drik` + `jhora.horoscope.chart.charts` directly, and emits JSON/YAML ready results. All bug fixes continue to rely on the official PyJHora packages and imports (e.g. `drik.tithi`, `drik.nakshatra`, `charts.divisional_chart`).

---

## Critical Bugs & Fixes

1. Replace incorrect PyJHora calls (e.g., `const.get_ayanamsa_value`, `drik.yoga`, `utils.weekday_from_julian`) with the direct APIs described in `PYJHORA_API_COMPLETE_REFERENCE.md`.  
2. Ensure `jhora.panchanga.drik`, `jhora.horoscope.chart.charts`, and related modules are imported directly rather than relying on the archived `pyjhora_v0min_integration`.  
3. Build outputs according to the data structures in `PYJHORA_DATA_STRUCTURES.md`, populating ascendant/planet positions, dasas, yogas, and strength metrics.

---

## Strategic Decision Matrix

| Option | Description | Status |
|--------|-------------|--------|
| **Option A: Direct PyJHora Wrapper / Refraction Engine V1 (Recommended)** | Use `refraction_engine.core_chart` to validate payloads against `core_chart_spec_v1`, compute JD/place, call PyJHora modules (drik, charts, dhasa, strength, yoga), and emit JSON/YAML outputs. | ✅ |
| Option B: Full PyJHora Refactor Later | Keep PyJHora as the backend but plan a larger refactor to split modules, improve tests, and replace legacy glue in later phases. | Planned |
| Option C: v0min as Legacy Archive | Treat v0min code as historical reference only; no new features depend on it. | Archived (`maintenance/legacy-v0min-archive`) |

**Recommendation:** execute **Option A** now, bypassing v0min entirely.

---

## Phase 0: Stabilize (Days 1-3)

1. Build `src/refraction_engine/core_chart.py` stub (already in place).  
2. Keep `core_chart_spec_v1` as the contract for inputs/outputs.  
3. Fix imports and direct PyJHora usages; ensure every helper references `drik`/`charts` and not v0min.

## Phase 1: Core Extractors (Days 4-10)

- Implement divisional charts, dashas, strengths, yogas, special points directly via PyJHora helpers.  
- Call `charts.divisional_chart`, `dhasa.*`, `strength.*`, `yoga.*` with error handling and JSON formatting.

## Phase 2+: Integration & Testing

- Build FastAPI/React slices that consume Refraction Engine outputs.  
- Align tests with `pyjhora_knowledge/tests_contract` suites.  
- Archive any legacy v0min instructions in documentation, keeping the narrative PyJHora-centric.

---

## Implementation Notes

- **Refraction Engine class sketch**
  ```python
  from typing import Dict
  import jhora.panchanga.drik as drik
  import jhora.horoscope.chart.charts as charts

  class RefractionEngine:
      def __init__(self, payload: Dict):
          self.payload = payload
          self.jd, self.place = self._parse_payload(payload)

      def run_core_chart(self) -> Dict:
          raise NotImplementedError("Implement PyJHora calls per core_chart_spec_v1")
  ```

- **Testing checklist**: continue verifying `drik.tithi`, `drik.nakshatra`, `charts.divisional_chart`, etc., while ignoring all v0min-specific tests.
*** End Patch*** 
