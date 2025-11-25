#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.."; pwd)"
cd "${ROOT_DIR}"

echo "Running parity suite (tests/parity)..."
pytest tests/parity -v --tb=short
