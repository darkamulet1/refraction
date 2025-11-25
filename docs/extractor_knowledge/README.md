# Extractor Knowledge Workspace

`docs/extractor_knowledge/` is **the PyJHora knowledge factory**, not a runtime engine.
It gathers metadata, golden samples, and CLI helpers that feed the `docs/pyjhora_knowledge/` pack,
but Refraction Engine V1 does not import or depend on these scripts at runtime.

## What lives here

- `build_knowledge_artifacts.py` + `knowledge_scan_full.py` – rake the PyJHora sources,
  parse constants/AST, and emit the JSON/MD artifacts (`CorePrimitives.json`,
  `PyJHora_API_Inventory.json`, `PyJHora_Data_Files_Map.json`, etc.) that drive the new knowledge repository.
- CLI helpers (e.g., `core_chart_cli.py`, `panchanga_*`, `dasha_cli.py`,
  `muhurta_cli.py`, `strength_trends_cli.py`, `transit_cli.py`…) – exercise real PyJHora flows
  and serve as golden-data producers/guides for chart/panchanga/dasha/yoga/extractor outputs.
- `v0min_core_spec.md` and the older `v0min_*` extractors are **legacy references**; they document
  a frozen `v0min` architecture and should not be used as the primary design surface for Refraction Engine V1.

## How to use this workspace

1. Whenever PyJHora is updated, regenerate the knowledge assets:
   * Run `knowledge_scan_full.py` to refresh the API inventory, experimental flags, and function signatures.
   * Run `build_knowledge_artifacts.py` to rebuild `CorePrimitives.json`, the data map, and tests contract manifests.
   * Copy the generated JSON/MD into `docs/pyjhora_knowledge/`.
2. Align the Refraction Engine specs (`engine_config_spec_v1`, `api_whitelist_core_chart_v1`, `tests_binding_core_chart_v1`)
   with the refreshed artifacts so the extractor expectations stay in sync with the underlying PyJHora capabilities.
3. Keep the CLI scripts as reference implementations/golden data producers, but do not import them from `src/refraction_engine/`.

## Runtime vs knowledge separation

Refraction Engine V1 (`src/refraction_engine/`) consumes the JSON/MD artifacts produced from this folder, but it does **not** import or execute any `docs/extractor_knowledge/` scripts in production.
Use this workspace to **refresh knowledge** (golden data, primitives, APIs, tests), and then point the runtime toward the generated artifacts in `docs/pyjhora_knowledge/`.
