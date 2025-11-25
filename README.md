# Refraction Engine

Refraction Engine is a lightweight reflection layer over PyJHora that delivers tightly specified Vedic astrology extractors (core chart, panchanga, dashas, strengths, special points, transit, yogas) with JSON/YAML contracts, guard tests, and parity checkpoints.

## Highlights

- **Architecture:** `graha.py` is the single source for Graha/Rasi/Nakshatra metadata; extractors follow `spec → schema → implementation → binding/schema tests` described in `docs/specs/EXTRACTOR_TEMPLATE_V1.md`.
- **Extractors:** `run_core_chart`, `run_panchanga`, `run_dashas_vimshottari`, `run_strengths`, `run_special_points`, `run_transit`, `run_yogas` all export `schema_version` tagged, JSON-schema validated payloads.
- **Bundles & pipeline:** `run_refraction_core` runs every extractor and emits the `refraction_core_bundle_spec_v1` output consumed by dashboards or downstream services.
- **Testing:** `pytest tests/specs` enforces contracts, `scripts/run_parity_suite.(sh|bat)` exercises PL9 parity fixtures, and `.github/workflows/engine_guard_suite.yml` runs both suites on each push.

## Quick start

```python
from refraction_engine import run_core_chart, run_refraction_core

payload = { ... }  # see references/in/mehran_birth.json
core = run_core_chart(payload)
bundle = run_refraction_core(payload)
```

## Documentation Roadmap

1. `docs/EXTRACTOR_GUIDE.md` – per-extractor usage and API reference.
2. `docs/ARCHITECTURE.md` – layered diagram (PyJHora → refraction helpers → extractors → UI).
3. `docs/specs/*.md` & `.schema.json` – contract source of truth.
4. `docs/CI_INTEGRATION_CHECKLIST.md` – how to run guard + parity + future deployments.

## Next steps

1. **Documentation (Phase 4)** already in progress: README, EXTRACTOR_GUIDE, API reference, usage samples.
2. **Examples & demos** (phase 5): sample scripts, notebooks, `references/out` snapshots.
3. **Polish**: docstrings, formatting, optional Docker/CI upgrades.

---

Build instructions:

```bash
git clone ...
pip install -e .
pytest tests/specs
./scripts/run_parity_suite.sh
```
