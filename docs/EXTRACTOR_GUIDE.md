# Extractor Guide

This guide describes the public `run_*` extractors exposed by `refraction_engine`. Each extractor expects a `core_input_spec_v1`-compliant payload (birth datetime, timezone, lat/lon, config) and returns a JSON object that conforms to the corresponding `*_spec_v1.schema.json` file.

| Extractor | Description | Output schema | Key guarantees |
|---|---|---|---|
| `run_core_chart(payload)` | Builds the natal D1 chart (ascendant, planets, houses) with Nakshatra tagging | `docs/specs/core_chart_spec_v1.schema.json` | includes nakshatra/pada for ascendant and planets, house occupancy, `meta.schema_version` | 
| `run_panchanga(payload)` | Panchanga details (tithi, nakshatra, yoga, karana, hora, windows) | `docs/specs/panchanga_spec_v1.schema.json` | Moon nakshatra coded, sunrise/sunset timestamps, auspicious windows list |
| `run_dashas_vimshottari(payload)` | Vimshottari mahadasa periods | `docs/specs/dashas_vimshottari_spec_v1.schema.json` | fixed 9 mahadasas, ISO start/end, current period flag |
| `run_strengths(payload)` | Shadbala-based strengths summary | `docs/specs/strengths_spec_v1.schema.json` | total strength per graha + strong/weak lists |
| `run_special_points(payload)` | Special lagnas (Bhava, Hora, Ghati, Sree) | `docs/specs/special_points_spec_v1.schema.json` | each lagna includes sign + nakshatra meta |
| `run_transit(payload)` | Transit frames (day-of details, Panchanga) | `docs/specs/transit_spec_v1.schema.json` | reuses `run_core_chart` raw data to ensure consistency |
| `run_yogas(payload)` | Yoga detection (Gaja Kesari, Kala Sarpa, etc.) | `docs/specs/yogas_spec_v1.schema.json` | summary includes counts, malefic score, strength scoring |
| `run_refraction_core(payload)` | Runs all of the above and bundles | `docs/specs/refraction_core_bundle_spec_v1.schema.json` | `frames` dictionary with each sub-extractor result |

## Payload tips

* Always include `person` metadata for logging (`id`, `label`).
* Provide `config` values for `zodiac_type`, `ayanamsa_mode`, `house_system`, `node_mode`, and `include_bodies`. Defaults defined in `docs/specs/engine_config_spec_v1.example.yaml`.
* When you vary `include_bodies`, the core chart output will include only that set; other extractors (dashas, strengths) respect the same payload.

## Testing & validation

* Run `pytest tests/specs` to ensure extractors still satisfy their schema and golden fixtures.
* Run `./scripts/run_guard_suite.sh` (or `.bat`) to re-execute guard + parity suites.
* For parity checks use `tests/parity/test_pl9_parity_new_engine.py` and the CSV in `references/parity/`.

## Export path

All functions are exported through `src/refraction_engine/__init__.py`, so you can `from refraction_engine import run_core_chart, run_refraction_core, ...` without touching internals.
