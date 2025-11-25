## Project Status – Refraction Engine V1

### Current Scope & Steps Completed
1. **Engine Extractors:** Implemented and stabilized four primary extractors (`core_chart`, `panchanga`, `dashas_vimshottari`, `strengths`) with shared input parsing and config mapping.
2. **Specs & Schemas:** Each extractor has a normative spec (`docs/specs/*_spec_v1.*`), JSON Schema, and example payload. Bundle spec (`refraction_core_bundle_spec_v1`) wraps the four outputs.
3. **Fixtures & Bundles:** Reference inputs exist for Mehran, Athena, Arezoo, Arman (`references/in/*.json`), and the corresponding bundle outputs live in `references/out/*.json`.
4. **Parity Work:** PL9 parity tests now cover Arezoo + Arman for Lagna and 9 grahas, keeping refraction-engine outputs within 90″ of PL9 values and matching sign/nakshatra/pada.
5. **Tools & Automation:** Guard scripts (`scripts/run_guard_suite.sh|bat`) run `pytest tests/specs`; CI workflow mirrors this. Parity CSV analyzer (`scripts/analyze_pl9_parity.py`) plus parity tests under `tests/parity/`.

### Tooling & Test Status
- **Guard Suite:** `pytest tests/specs` – 26 tests (core extractor bindings + schemas + PL9 parity) currently passing.
- **Parity Analyzer:** `python -m scripts.analyze_pl9_parity` summarizes legacy PL9 vs old engine gaps.
- **Parity Tests:** `pytest tests/parity` (manual) – CSV sanity check + new-engine parity placeholder. Only Arezoo/Arman parity included in spec suite so far.
- **Entry Points:** `run_refraction_core` bundles all extractors; CLI loaders exist in `scripts/`.

### Known Gaps / Bugs / Technical Debt
1. **Graha Mapping Utilities Missing:** Planet ID/name mappings are duplicated across extractors; future changes risk reintroducing mapping bugs.
2. **Parity Coverage Limited:** Only Arezoo/Arman charts have PL9 parity tests; Mehran/Athena (and future charts) are unverified against external references.
3. **Parity Not in CI:** Guard suite excludes parity directory; regressions slip unless parity tests are run manually.
4. **CSV Parity Tests:** They only validate the legacy PL9 vs old-engine numbers; no automated comparison against the new engine yet.
5. **Docs:** Need an explicit README/guide describing parity workflow, fixture maintenance, and how to add PL9 references.
6. **Output Verification:** `references/out/*.json` aren’t schema-validated automatically during bundle generation; changes may drift silently.
7. **Rahu/Ketu Derivation:** Currently uses Swiss Ephemeris TRUE_NODE for Rahu and offsets Ketu; if config switches (e.g., mean node), there’s no toggle.

### Next Steps (Suggested)
1. Centralize graha mapping helpers so every extractor and test reads the same ID/const/name tables.
2. Expand PL9 parity fixtures to Mehran/Athena (and additional charts) once reference data is available; consider hooking parity suite into CI.
3. Document parity workflow and bundle generation in a dedicated README section.
4. Add bundle schema validation or snapshot tests for `references/out`.
5. Build parity tests for Panchanga/Vimshottari/Strengths using existing knowledge pack references.

### Sharing With Another AI
Provide:
- This status file (`PROJECT_STATUS.md`) for a quick overview.
- `tests/specs/test_core_chart_pl9_parity.py` for reference parity logic.
- Guard suite command (`python -m pytest tests/specs`) to verify core contracts.
- Any new PL9 reference degrees + input JSONs when extending parity coverage.
