# CI Integration Checklist – Gap #3

## Goal
Ensure every push/PR runs both:

- `pytest tests/specs` (the guard suite)
- `./scripts/run_parity_suite.sh` (the PL9 parity checks)

## Essentials

- [x] Guard suite scripts already exist (`scripts/run_guard_suite.sh/.bat`)
- [x] Parity scripts now live under `scripts/run_parity_suite.sh` and `.bat`
- [x] GitHub workflow `.github/workflows/engine_guard_suite.yml` orchestrates both jobs

## Workflow summary

The existing workflow now has:

1. **guard-suite job** (runs specs/schemas)
2. **parity-suite job** (depends on guard-suite, runs `scripts/run_parity_suite.sh`)

Each job uses Python 3.11, installs dependencies from `requirements.txt` or `pyproject.toml`, and keeps working directory at repo root.

## Local verification

```bash
# Guard suite
pytest tests/specs -v

# Parity suite
chmod +x scripts/run_parity_suite.sh
./scripts/run_parity_suite.sh -v

# Run both sequentially
pytest tests/specs -v && ./scripts/run_parity_suite.sh -v
```

## When parity script fails

- Make sure `references/parity` contains the PL9 CSV and `references/in/` has the matching birth fixtures (`arezoo`, `arman`, …).
- Adjust `tests/parity/test_pl9_parity_new_engine.py` to skip missing fixtures via `pytest.skip`.
- Parity runs only after guard suite passes; failures prevent merges just like any other job.

## Additions to docs/README

Document that `scripts/run_parity_suite.sh` is the canonical way to exercise parity locally and that the workflow runs both suites on main – point to `.github/workflows/engine_guard_suite.yml`.
