#!/usr/bin/env bash
#
# Refraction Engine V1 - Parity Test Suite
# =========================================
#
# Runs PL9 parity tests to verify accuracy against reference calculations.
# 
# Usage:
#   ./scripts/run_parity_suite.sh                    # Run all parity tests
#   ./scripts/run_parity_suite.sh -v                 # Verbose output
#   ./scripts/run_parity_suite.sh --chart=arezoo     # Run specific chart
#   ./scripts/run_parity_suite.sh --threshold=90     # Custom threshold (arcseconds)
#
# Exit codes:
#   0 = All tests passed
#   1 = Tests failed or threshold exceeded
#   2 = Script error (missing dependencies, etc.)

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TESTS_DIR="$ROOT_DIR/tests/parity"

# Default threshold: 90 arcseconds (1.5 arcminutes)
THRESHOLD_ARCSEC="${PARITY_THRESHOLD:-90}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*"
}

log_success() {
    echo -e "${GREEN}[PASS]${NC} $*"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[FAIL]${NC} $*"
}

print_header() {
    echo ""
    echo "================================================================"
    echo "  Refraction Engine V1 - Parity Test Suite"
    echo "================================================================"
    echo "  Root:      $ROOT_DIR"
    echo "  Tests:     $TESTS_DIR"
    echo "  Threshold: $THRESHOLD_ARCSEC arcseconds"
    echo "================================================================"
    echo ""
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check Python
    if ! command -v python &> /dev/null; then
        log_error "Python not found. Please install Python 3.8+."
        exit 2
    fi
    
    # Check pytest
    if ! python -m pytest --version &> /dev/null; then
        log_error "pytest not found. Install with: pip install pytest"
        exit 2
    fi
    
    # Check test directory
    if [ ! -d "$TESTS_DIR" ]; then
        log_error "Parity tests directory not found: $TESTS_DIR"
        exit 2
    fi
    
    log_success "All dependencies OK"
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
    print_header
    check_dependencies
    
    # Change to root directory
    cd "$ROOT_DIR"
    
    # Parse arguments
    PYTEST_ARGS=()
    CHART_FILTER=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                PYTEST_ARGS+=("-v")
                shift
                ;;
            -vv)
                PYTEST_ARGS+=("-vv")
                shift
                ;;
            --chart=*)
                CHART_FILTER="${1#*=}"
                PYTEST_ARGS+=("-k" "$CHART_FILTER")
                shift
                ;;
            --threshold=*)
                THRESHOLD_ARCSEC="${1#*=}"
                shift
                ;;
            --tb=*)
                PYTEST_ARGS+=("--tb=${1#*=}")
                shift
                ;;
            *)
                PYTEST_ARGS+=("$1")
                shift
                ;;
        esac
    done
    
    # Set threshold as environment variable for tests to read
    export PARITY_THRESHOLD="$THRESHOLD_ARCSEC"
    
    # Run parity tests
    log_info "Running parity tests..."
    log_info "Command: pytest $TESTS_DIR ${PYTEST_ARGS[*]}"
    echo ""
    
    # Run pytest with custom args
    if python -m pytest "$TESTS_DIR" "${PYTEST_ARGS[@]}" --tb=short; then
        echo ""
        log_success "All parity tests passed! ✨"
        log_info "Maximum deviation: < $THRESHOLD_ARCSEC arcseconds"
        echo ""
        exit 0
    else
        echo ""
        log_error "Parity tests failed! ❌"
        log_error "Some calculations deviate > $THRESHOLD_ARCSEC arcseconds from PL9 reference"
        log_warning "Review test output above for details"
        echo ""
        exit 1
    fi
}

# ============================================================================
# HELP
# ============================================================================

if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    cat << EOF
Refraction Engine V1 - Parity Test Suite
=========================================

Usage:
  $0 [OPTIONS]

Options:
  -v, --verbose              Verbose output (show each test)
  -vv                        Very verbose output (show each assertion)
  --chart=NAME               Run tests for specific chart only (e.g., arezoo, arman)
  --threshold=ARCSEC         Set custom threshold in arcseconds (default: 90)
  --tb=short|long|line       Traceback style for failures (default: short)
  -h, --help                 Show this help message

Environment Variables:
  PARITY_THRESHOLD           Default threshold in arcseconds (default: 90)

Examples:
  # Run all parity tests
  $0

  # Run with verbose output
  $0 -v

  # Run only Arezoo's chart
  $0 --chart=arezoo

  # Use stricter threshold (60 arcseconds = 1 arcminute)
  $0 --threshold=60

  # Show detailed traceback on failures
  $0 --tb=long

Exit Codes:
  0 = All tests passed
  1 = Tests failed or threshold exceeded
  2 = Script error (missing dependencies, etc.)

EOF
    exit 0
fi

# Run main function
main "$@"
