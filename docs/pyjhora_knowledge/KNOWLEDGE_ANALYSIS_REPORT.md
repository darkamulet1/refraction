# Knowledge Analysis Report

All primary PyJHora reference markdowns now reside under `docs/docs/pyjhora_knowledge/reference/`.

## 1. High-Level Map

### Root spec files
- `PYJHORA_API_COMPLETE_REFERENCE.md`: enumerates the actual engine surface—constructor parameters, Panchanga/Chart/Dasha/... methods, data structure conventions, appendices with planet/raasi/ayanamsa tables and usage snippets.
- `PYJHORA_CONFIGURATION_OPTIONS.md`: catalogs every runtime option (ayanamsas, house systems, divisional charts, dashas, chart display and language toggles, ephemeris paths, etc.) that controls how the engine behaves.
- `PYJHORA_DATA_STRUCTURES.md`: defines the payload shapes (dates, place tuples, planet lists, house/planet dictionaries, Panchanga and Dasha outputs) that callers need to consume or produce.
- `PYJHORA_EXTRACTOR_BLUEPRINT.md`: lays out the extractor architecture and phased checklist that an automation layer should follow, together with output expectations and safe-entry guidance.
- `PYJHORA_FUNCTION_INVENTORY.md`: captures a module-by-module function catalog (counts per subsystem, appendices for constants/resources) that mirrors the modules listed in the API reference.
- `PYJHORA_GAPS_ANALYSIS.md`: highlights coverage gaps (missing modules, uninspected test files, UI/compatibility analysis) and recommends follow-up phases.
- `PYJHORA_HIDDEN_FEATURES.md`: surfaces experimental or non-obvious capabilities (custom vargas, ancient time systems, KP/Prasna helpers, latent CLI extractors) that extend beyond the documented API.
- `PYJHORA_INTEGRATION_PATTERNS.md`: summarizes real-world workflows (Horoscope initialization, Panchanga usage, transit/dasha flows, UI localization, batching patterns) to show how the modules are stitched together.

### Knowledge folders
- `data_map`: maps every packaged data file (ephemeris blobs, festival lists, compatibility CSVs, city databases) to its primary consuming module, serving as a canonical data-dependency matrix for the extractor.
- `inventory`: contains the exhaustive API inventory JSON, including module-level experimental flags, signatures, and docstrings, derived from runtime introspection.
- `maps`: records the structural map (full markdown walkthrough plus distilled JSON summary) that mirrors the package tree, primitives, defaults, and experimental tags used in the blueprint.
- `primitives`: encodes the engine’s literal primitives (planet/raasi representations, ayanamsa metadata, house-system catalog, multilingual labels) so code generation or validation can rely on a single JSON manifest.
- `tests_contract`: lists the canonical test suites (`pvr_tests`, `test_yogas`, `test_ui`) and representative cases that any future validator must honor.
- `experimental`: documents the “hidden”/unstable capabilities (module markers + v0min extracts) that either need caution or may feed a sandboxed release channel.
- `ui_catalog`: enumerates every PyQt6 presentation module so the extractor can separate pure API surfaces from UI-only widgets.
- `logs`: captures the scan log (mode, totals, generated file paths) confirming the importer + AST crawl that produced the knowledge assets.

## 2. Relationships

- The knowledge artifacts stem directly from the spec sources: `inventory`/`maps` operationalize the API and structural descriptions in `PYJHORA_API_COMPLETE_REFERENCE.md`, while `primitives/CorePrimitives.json` expresses the constants enumerated under configuration options and default tables.  
- The `data_map` JSON maps described data files into the usage contexts that the API reference and extractor blueprint call out (for Panchanga, match, or export helpers).  
- `tests_contract` codifies the regression suites that `PYJHORA_GAPS_ANALYSIS.md` singled out as mission-critical, and `experimental/Experimental_and_Hidden.md` preserves the hidden features that extend beyond the “stable” API surface.
- `ui_catalog` mirrors the UI modules referenced in `PYJHORA_API_COMPLETE_REFERENCE.md`/`PYJHORA_INTEGRATION_PATTERNS.md`, keeping the presentation layer separate from the engine core.

### Concept mapping

| Concept | Defining spec(s) | Structured knowledge asset(s) |
|---|---|---|
| Ayanamsa & house systems | `PYJHORA_CONFIGURATION_OPTIONS.md`, `PYJHORA_API_COMPLETE_REFERENCE.md` | `docs/pyjhora_knowledge/primitives/CorePrimitives.json`, `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map.md` |
| Divisional charts / vargas | `PYJHORA_API_COMPLETE_REFERENCE.md`, `PYJHORA_CONFIGURATION_OPTIONS.md` | `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map.md`, `docs/pyjhora_knowledge/primitives/CorePrimitives.json` |
| Core API surface (Panchanga/Chart/Dasha strength) | `PYJHORA_API_COMPLETE_REFERENCE.md`, `PYJHORA_FUNCTION_INVENTORY.md` | `docs/pyjhora_knowledge/inventory/PyJHora_API_Inventory.json`, `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map.md` |
| Data files / ephemeris | `PYJHORA_EXTRACTOR_BLUEPRINT.md`, `PYJHORA_API_COMPLETE_REFERENCE.md` | `docs/pyjhora_knowledge/data_map/PyJHora_Data_Files_Map.json` |
| Tests & validation | `PYJHORA_GAPS_ANALYSIS.md` | `docs/pyjhora_knowledge/tests_contract/PyJHora_Tests_Contract.json` |
| UI modules | `PYJHORA_API_COMPLETE_REFERENCE.md`, `PYJHORA_INTEGRATION_PATTERNS.md`, `PYJHORA_HIDDEN_FEATURES.md` | `docs/pyjhora_knowledge/ui_catalog/UI_Modules.md` |
| Hidden/experimental behaviors | `PYJHORA_HIDDEN_FEATURES.md`, `PYJHORA_GAPS_ANALYSIS.md` | `docs/pyjhora_knowledge/experimental/Experimental_and_Hidden.md`, `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map_summary.json` (flags) |

## 3. For a future “Calculator Engine V1”

### Sources of truth
- **Engine configuration options**: `PYJHORA_CONFIGURATION_OPTIONS.md` + defaults recorded in `docs/pyjhora_knowledge/maps/PyJHora_Structural_Map_summary.json` capture valid modes, chart flags, language toggles, and house/dasha choices.
- **Core API surface**: `PYJHORA_API_COMPLETE_REFERENCE.md` (with data structures sections) combined with `docs/pyjhora_knowledge/inventory/PyJHora_API_Inventory.json` ensure every callable and signature is documented and discoverable.
- **Primitives/IDs**: `docs/pyjhora_knowledge/primitives/CorePrimitives.json` (including ayanamsa metadata, house-system catalog, multilingual lists) plus the structural map tables supply the canonical IDs that drive position math.
- **Tests/golden references**: `docs/pyjhora_knowledge/tests_contract/PyJHora_Tests_Contract.json` lists the regression suites that capture expected behavior for Panchanga, charts, and UI smoke flows.

### Minimal spec artifacts for Calculator Engine V1
1. `engine_config_spec.json` – synthesized from `PYJHORA_CONFIGURATION_OPTIONS.md` + `PyJHora_Structural_Map_summary.json`, listing configurable ayanamsas, house systems, vargas, and language/default values.
2. `api_whitelist.json` – curated from `PYJHORA_API_COMPLETE_REFERENCE.md` and cross-checked against `PyJHora_API_Inventory.json` to expose only the stable/public methods (Panchanga, chart, dasha, strength, yoga helpers).
3. `primitives_catalog.json` – reuses `primitives/CorePrimitives.json` to publish planets, rasis, ayanamsa constants, house systems, and localization strings for downstream clients.
4. `tests_contract.json` – reuses the existing `docs/pyjhora_knowledge/tests_contract/PyJHora_Tests_Contract.json` to declare mandatory regression suites and representative cases.
5. `data_files_manifest.json` – distilled view of `docs/pyjhora_knowledge/data_map/PyJHora_Data_Files_Map.json` so the engine knows which CSV/ephemeris inputs match which subsystems.

## 4. Gaps / TODOs

- No single canonical file currently unifies the configuration defaults, experimental flags, and safe entry points (the structural map notes “no safe entry points captured”). Consider amending `PyJHora_Structural_Map_summary.json` or adding a dedicated `engine_defaults.json`.
- The UI catalog is descriptive but not tied back to API capabilities—align `docs/pyjhora_knowledge/ui_catalog/UI_Modules.md` entries with the integration patterns or API reference to expose whichever data endpoints populate each widget.
- Hidden/external v0min extractors (`Experimental_and_Hidden.md`) remain undocumented in the API reference; if they are to be surfaced, add dedicated sections or connectors in future wiring documents.
- Tests are well cataloged but flagged gaps (`PYJHORA_GAPS_ANALYSIS.md` items 6/7/8) warn that 6,300+ tests, UI coverage, and prediction/compatibility modules still need proper analysis; capture those in a follow-up report or checklist.
- The data map enumerates hundreds of ephemeris files, but no higher-level schema documents which file ranges correspond to which date spans; adding that metadata would help `engine_config_spec` understand when to swap ephemeris files.
