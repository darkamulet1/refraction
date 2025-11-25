# Engine Design Gaps Report

## 1. Coverage Map
- **Inputs & configuration** – birth payload schema, config options (ayanamsa, house system, timezone, node_mode, output sections) described in `docs/specs/core_chart_spec_v1.md`, `docs/pyjhora_knowledge/reference/PYJHORA_CONFIGURATION_OPTIONS.md`, and summarized in `docs/pyjhora_knowledge/KNOWLEDGE_ANALYSIS_REPORT.md` (coverage map, Engine configuration options section).  
- **core_chart spec** – `docs/specs/core_chart_spec_v1.md` is the only explicit contract for Refraction Engine V1 inputs/outputs; the roadmap ties back to it as the validation anchor.  
- **PyJHora API surface** – enumerated exhaustively in `docs/pyjhora_knowledge/reference/PYJHORA_API_COMPLETE_REFERENCE.md` and the derived `docs/pyjhora_knowledge/inventory/PyJHora_API_Inventory.json` plus the structural map (`docs/pyjhora_knowledge/maps/PyJHora_Structural_Map.md`).  
- **Extractors list** – `docs/pyjhora_knowledge/reference/PYJHORA_EXTRACTOR_BLUEPRINT.md` plus the roadmap detail (phase-by-phase extractors) outline the high-level extractors (core chart, divisional, dashas, strengths, yogas, special points, transits).  
- **Tests contract** – captured in `docs/pyjhora_knowledge/tests_contract/PyJHora_Tests_Contract.json` and highlighted in the knowledge report section “Tests/golden references”; roadmaps reference these suites for verification coverage.

## 2. Design Gaps & Ambiguities

### a) Input / Config ambiguities
1. **Node mode / retrograde handling not defined**  
   - Why: `core_chart_spec_v1` lists `node_mode` and the roadmap mentions `divisional_chart_factor`, but there is no mapping to the PyJHora primitives (e.g., `const._MOON/_RAHU`).  
   - Where: `docs/specs/core_chart_spec_v1.md` (payload fields) vs. `docs/pyjhora_knowledge/primitives/CorePrimitives.json` (constants).  
   - Suggestion: Add a config subsection showing valid `node_mode` values, how they translate to PyJHora node symbols, and decide defaults.

2. **Default ayanamsa / house system mismatches**  
   - Why: `KNOWLEDGE_ANALYSIS_REPORT` and structural map fix `LAHIRI`/method `1`, but `core_chart_spec_v1` leaves defaults blank and roadmaps refer to `WHOLE_SIGN` houses.  
   - Where: `docs/specs/core_chart_spec_v1.md` vs. `docs/pyjhora_knowledge/reference/PYJHORA_CONFIGURATION_OPTIONS.md` and `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map_summary.json`.  
   - Suggestion: Document the default vs. optional values and how to override them, referencing the primitives file for constant IDs.

### b) Engine–PyJHora integration ambiguities
3. **“Core chart” definition lacks detail**  
   - Why: Roadmaps emphasize `core_chart` but the knowledge pack lists dozens of charts/dashas without clarifying which ones are “core”.  
   - Where: `docs/roadmap/ENGINE_TECH_EXECUTION_ROADMAP_v1.md` vs. `docs/pyjhora_knowledge/reference/PYJHORA_API_COMPLETE_REFERENCE.md`.  
   - Suggestion: Expand `core_chart_spec_v1` to include which PyJHora APIs (e.g., `charts.divisional_chart`, `drik.ascendant`) produce the “core” payload.

4. **Integration paths still refer to legacy data mapping**  
   - Why: `docs/pyjhora_knowledge/data_map/PyJHora_Data_Files_Map.json` enumerates ephemeris files but the roadmaps don’t say whether the engine should load them or rely on editable PyJHora install.  
   - Where: data_map file vs. `docs/roadmap/*` (no mention).  
   - Suggestion: Add a runtime section clarifying how the engine locates ephemeris (standard PyJHora data path) and when those CSVs are used.

### c) Extractor contracts not fully defined
5. **Dashas & strengths lack structured contracts**  
   - Why: Blueprints mention 46 dashas and strength calculations, but there is no per-extractor spec describing input/output shapes, ranking, or subset priorities.  
   - Where: `docs/pyjhora_knowledge/reference/PYJHORA_EXTRACTOR_BLUEPRINT.md` (list only) vs. absence of spec files.  
   - Suggestion: Create `dashas_spec_v1` and `strengths_spec_v1` to describe required outputs, referencing `PyJHora_FUNCTION_INVENTORY` for function names.

6. **Yoga categories & UI sinks vague**  
   - Why: UI catalog lists widgets, but the knowledge report notes the UI catalog isn’t tied back to APIs.  
   - Where: `docs/pyjhora_knowledge/ui_catalog/UI_Modules.md` vs. `docs/roadmap` (UI phase).  
   - Suggestion: Define expected yoga payload sections (maybe per widget) and tie them to `jhora.horoscope.chart.yoga` functions.

### d) Testing & parity gaps
7. **Test contracts lack mapping to current outputs**  
   - Why: `PyJHora_Tests_Contract.json` names canonical files but doesn’t link to `refraction_engine.core_chart` outputs, making automation unclear.  
   - Where: tests contract JSON vs. roadmaps (which say “align tests”).  
   - Suggestion: Build `tests_binding_core_chart_v1.example.yaml` (see Deliverable 2) to show how each suite validates payload sections.

8. **Golden output expectations unspecified**  
   - Why: Roadmaps mention golden outputs (JSON) but no spec describes their format or tolerance.  
   - Where: `docs/roadmap/ENGINE_TECH_EXECUTION_ROADMAP_v1.md` (golden file sections).  
   - Suggestion: Document expected golden schema and tolerance for planetary positions/dashas.

## 3. Conflicts or Inconsistencies
- Knowledge files describe extensive experimental modules (`PyJHora_Structural_Map` & `Experimental_and_Hidden`), but roadmaps now emphasize a **thin wrapper** ignoring those features. Not all experimental modules are marked as excluded, so it’s unclear which ones remain relevant for Phase 1.  
- `core_chart_spec_v1` lacks references to some PyJHora primitives (e.g., there are 23 vargas in `CorePrimitives`, but the spec only covers D1). The blueprint talks about D1–D300, so the spec and engine plan disagree on coverage.  
- Tests contract talks about UI modules (`test_ui.py`) but the latest architecture puts UI in React + FastAPI; there is no mapping from the new orchestrator structure to those tests.  
- The knowledge report notes the engine config defaults, but the implementation plan’s “priority tasks” still mention `v0min` (some references may remain), so there’s a rhetorical conflict between “legacy archive” vs. “use v0min to unblock” (needs clean final pass to ensure docs align).

## 4. Missing Specs for Refraction Engine V1
- `TODO: write panchanga_spec_v1.md to formalize sunrise/tithi/nakshatra/yoga outputs using jhora.panchanga.drik.`  
- `TODO: define dashas_spec_v1.md covering at least Vimshottari, Ashtottari, and Narayana (and how to incrementally add the rest).`  
- `TODO: create strengths_spec_v1.md (Shadbala, Bhava Bala, Ashtakavarga, Vaiseshika) with expected numeric ranges.`  
- `TODO: describe special_points_spec_v1.md (Bhava lagna, Sahams, Arudhas, Sree/Indu lagna) referencing `jhora.horoscope.chart.charts`.`  
- `TODO: add transits_spec_v1.md (Sun/Moon/Ketu entry, retrograde windows) linked to `jhora.horoscope.transit` modules.`  
- `TODO: detail yoga_spec_v1.md for at least Pancha Mahapurusha, Raja, Dhana, Arishta, Surya yogas.`  
- `TODO: capture ui_payload_spec_v1.md to tie FastAPI responses to UI widgets from `docs/pyjhora_knowledge/ui_catalog/UI_Modules.md`.`  
- `TODO: finalize node_and_house_spec_v1.md clarifying how node_mode and house_system select the PyJHora constants from `CorePrimitives.json`.`  
- `TODO: document input_validation_spec_v1.md describing how `core_chart_spec_v1` fields are validated (timezones, lat/lon ranges, required sections).`

## 5. Prioritized TODO List
1. `[P1] Formalize `core_chart_spec_v1` outputs for ascendant/planets/dashas — docs/specs/core_chart_spec_v1.md`  
2. `[P1] Define panchanga_spec_v1 detailing tithi/nakshatra/yoga outputs — docs/specs/panchanga_spec_v1.example.md`  
3. `[P1] Create engine_config_spec_v1.example.yaml based on CONFIG_OPTIONS + CorePrimitives defaults — docs/specs/engine_config_spec_v1.example.yaml`  
4. `[P1] Produce api_whitelist_core_chart_v1.example.json listing required PyJHora functions — docs/specs/api_whitelist_core_chart_v1.example.json`  
5. `[P1] Author tests_binding_core_chart_v1.example.yaml linking `PyJHora_Tests_Contract` suites to `core_chart` payload sections — docs/specs/tests_binding_core_chart_v1.example.yaml`  
6. `[P2] Clarify ayanamsa/house/ node_mode mapping to PyJHora constants — docs/specs/node_house_mapping.md or within engine_config_spec`  
7. `[P2] Document dashas_spec_v1.md to cover Vimshottari/Ashtottari and their data shape — docs/specs/dashas_spec_v1.example.md`  
8. `[P2] Draft strengths_spec_v1.md describing Shadbala/Bhava/Ashtakavarga outputs — docs/specs/strengths_spec_v1.example.md`  
9. `[P2] Create yogas_spec_v1.md tying to `jhora.horoscope.chart.yoga` helpers — docs/specs/yogas_spec_v1.example.md`  
10. `[P2] Capture special_points_spec_v1.md for Bhava/Sree/Indu lagna plus Sahams — docs/specs/special_points_spec_v1.example.md`  
11. `[P3] Add ui_payload_spec_v1.md linking FastAPI responses to `docs/pyjhora_knowledge/ui_catalog/UI_Modules.md` widgets`  
12. `[P3] Document golden_output_schema_v1.md for QA/validation usage`  
13. `[P3] Record data_manifest_spec_v1.md summarizing `docs/pyjhora_knowledge/data_map/PyJHora_Data_Files_Map.json` usage`  
14. `[P3] Outline experimental_exclusions_v1.md listing which `Experimental_and_Hidden.md` features are intentionally left out`  
15. `[P3] Create roadmap_alignment.md ensuring roadmaps no longer mention v0min anywhere`
