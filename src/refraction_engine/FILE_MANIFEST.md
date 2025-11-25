# File Manifest - Gap #1 & #3 Implementation

## 📦 Complete List of Deliverables

All files are ready in `/mnt/user-data/outputs/` for download.

---

## 1️⃣ Core Implementation Files

### graha.py
**Purpose**: Central mapping utilities for Graha/Rasi/Nakshatra  
**Size**: ~500 lines  
**Location**: Copy to `src/refraction_engine/graha.py`

**Installation**:
```bash
# Assuming you're in project root
cp /path/to/outputs/graha.py src/refraction_engine/
```

**Verification**:
```bash
python -c "from refraction_engine.graha import GrahaID; print(GrahaID.SUN)"
# Expected output: GrahaID.SUN or 0
```

---

### test_graha.py
**Purpose**: Comprehensive test suite for graha.py  
**Size**: ~400 lines  
**Location**: Copy to `tests/refraction_engine/test_graha.py`

**Installation**:
```bash
mkdir -p tests/refraction_engine
cp /path/to/outputs/test_graha.py tests/refraction_engine/
```

**Verification**:
```bash
pytest tests/refraction_engine/test_graha.py -v
# Expected: 50+ tests passing
```

---

## 2️⃣ Scripts

### run_parity_suite.sh
**Purpose**: Linux/Mac script for running parity tests  
**Size**: ~200 lines  
**Location**: Copy to `scripts/run_parity_suite.sh`

**Installation**:
```bash
mkdir -p scripts
cp /path/to/outputs/run_parity_suite.sh scripts/
chmod +x scripts/run_parity_suite.sh
```

**Verification**:
```bash
./scripts/run_parity_suite.sh --help
# Expected: Help text displayed
```

---

### run_parity_suite.bat
**Purpose**: Windows script for running parity tests  
**Size**: ~150 lines  
**Location**: Copy to `scripts/run_parity_suite.bat`

**Installation** (Windows):
```cmd
mkdir scripts
copy /path/to/outputs/run_parity_suite.bat scripts\
```

**Verification** (Windows):
```cmd
scripts\run_parity_suite.bat --help
REM Expected: Help text displayed
```

---

## 3️⃣ CI/CD Configuration

### ci_workflow.yml
**Purpose**: GitHub Actions workflow with parity integration  
**Size**: ~250 lines  
**Location**: Copy to `.github/workflows/ci.yml`

**Installation**:
```bash
mkdir -p .github/workflows
cp /path/to/outputs/ci_workflow.yml .github/workflows/ci.yml
```

**Verification**:
```bash
# After pushing to GitHub:
# 1. Go to GitHub repository
# 2. Click "Actions" tab
# 3. Should see "Refraction Engine V1 - CI" workflow
```

---

## 4️⃣ Documentation

### REFACTORING_GUIDE_GRAHA.md
**Purpose**: Step-by-step guide for refactoring extractors  
**Size**: ~600 lines  
**Location**: Copy to `docs/REFACTORING_GUIDE_GRAHA.md`

**Installation**:
```bash
mkdir -p docs
cp /path/to/outputs/REFACTORING_GUIDE_GRAHA.md docs/
```

**Usage**: Read before refactoring extractors

---

### PARITY_WORKFLOW_README.md
**Purpose**: Complete guide to parity testing workflow  
**Size**: ~800 lines  
**Location**: Copy to `docs/PARITY_WORKFLOW_README.md`

**Installation**:
```bash
cp /path/to/outputs/PARITY_WORKFLOW_README.md docs/
```

**Usage**: Reference for understanding parity tests

---

### IMPLEMENTATION_SUMMARY.md
**Purpose**: Executive summary of what was done  
**Size**: ~350 lines  
**Location**: Copy to `docs/IMPLEMENTATION_SUMMARY.md`

**Installation**:
```bash
cp /path/to/outputs/IMPLEMENTATION_SUMMARY.md docs/
```

**Usage**: Review before integrating changes

---

## 📋 Quick Install Script

Save this as `install_gap1_gap3.sh`:

```bash
#!/bin/bash
# Quick install script for Gap #1 & #3 implementation

set -e

OUTPUTS_DIR="/path/to/outputs"  # UPDATE THIS PATH

echo "Installing Gap #1 & #3 implementation..."

# Create directories
mkdir -p src/refraction_engine
mkdir -p tests/refraction_engine
mkdir -p scripts
mkdir -p .github/workflows
mkdir -p docs

# Install core files
echo "📦 Installing core files..."
cp "$OUTPUTS_DIR/graha.py" src/refraction_engine/
cp "$OUTPUTS_DIR/test_graha.py" tests/refraction_engine/

# Install scripts
echo "📜 Installing scripts..."
cp "$OUTPUTS_DIR/run_parity_suite.sh" scripts/
cp "$OUTPUTS_DIR/run_parity_suite.bat" scripts/
chmod +x scripts/run_parity_suite.sh

# Install CI config
echo "🔧 Installing CI configuration..."
cp "$OUTPUTS_DIR/ci_workflow.yml" .github/workflows/ci.yml

# Install documentation
echo "📚 Installing documentation..."
cp "$OUTPUTS_DIR/REFACTORING_GUIDE_GRAHA.md" docs/
cp "$OUTPUTS_DIR/PARITY_WORKFLOW_README.md" docs/
cp "$OUTPUTS_DIR/IMPLEMENTATION_SUMMARY.md" docs/

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Review docs/IMPLEMENTATION_SUMMARY.md"
echo "2. Run: pytest tests/refraction_engine/test_graha.py -v"
echo "3. Follow docs/REFACTORING_GUIDE_GRAHA.md to update extractors"
echo "4. Commit and push to activate CI"
```

**Usage**:
```bash
# 1. Update OUTPUTS_DIR path
# 2. Make executable
chmod +x install_gap1_gap3.sh

# 3. Run
./install_gap1_gap3.sh
```

---

## 🪟 Windows Install Script

Save this as `install_gap1_gap3.bat`:

```batch
@echo off
REM Quick install script for Gap #1 & #3 implementation (Windows)

set "OUTPUTS_DIR=C:\path\to\outputs"

echo Installing Gap #1 & #3 implementation...

REM Create directories
mkdir src\refraction_engine 2>nul
mkdir tests\refraction_engine 2>nul
mkdir scripts 2>nul
mkdir .github\workflows 2>nul
mkdir docs 2>nul

REM Install core files
echo Installing core files...
copy "%OUTPUTS_DIR%\graha.py" src\refraction_engine\
copy "%OUTPUTS_DIR%\test_graha.py" tests\refraction_engine\

REM Install scripts
echo Installing scripts...
copy "%OUTPUTS_DIR%\run_parity_suite.sh" scripts\
copy "%OUTPUTS_DIR%\run_parity_suite.bat" scripts\

REM Install CI config
echo Installing CI configuration...
copy "%OUTPUTS_DIR%\ci_workflow.yml" .github\workflows\ci.yml

REM Install documentation
echo Installing documentation...
copy "%OUTPUTS_DIR%\REFACTORING_GUIDE_GRAHA.md" docs\
copy "%OUTPUTS_DIR%\PARITY_WORKFLOW_README.md" docs\
copy "%OUTPUTS_DIR%\IMPLEMENTATION_SUMMARY.md" docs\

echo.
echo Installation complete!
echo.
echo Next steps:
echo 1. Review docs\IMPLEMENTATION_SUMMARY.md
echo 2. Run: pytest tests\refraction_engine\test_graha.py -v
echo 3. Follow docs\REFACTORING_GUIDE_GRAHA.md to update extractors
echo 4. Commit and push to activate CI
```

**Usage**:
```cmd
REM 1. Update OUTPUTS_DIR path
REM 2. Run
install_gap1_gap3.bat
```

---

## 📊 File Summary

| File | Type | Lines | Purpose |
|------|------|-------|---------|
| graha.py | Python | 500 | Core mappings |
| test_graha.py | Python | 400 | Tests for graha.py |
| run_parity_suite.sh | Bash | 200 | Parity runner (Linux) |
| run_parity_suite.bat | Batch | 150 | Parity runner (Windows) |
| ci_workflow.yml | YAML | 250 | GitHub Actions |
| REFACTORING_GUIDE_GRAHA.md | Markdown | 600 | Refactoring guide |
| PARITY_WORKFLOW_README.md | Markdown | 800 | Parity docs |
| IMPLEMENTATION_SUMMARY.md | Markdown | 350 | Executive summary |
| **TOTAL** | - | **3,250** | **Complete package** |

---

## ✅ Verification Checklist

After installation, verify each component:

### 1. Core Files
```bash
# Test graha.py
python -c "from refraction_engine.graha import GrahaID, rasi_index_from_longitude; print(rasi_index_from_longitude(45))"
# Expected: 2 (Taurus)

# Run tests
pytest tests/refraction_engine/test_graha.py -v
# Expected: 50+ passing
```

### 2. Scripts
```bash
# Test parity script
./scripts/run_parity_suite.sh --help
# Expected: Help text

# Run parity tests
./scripts/run_parity_suite.sh -v
# Expected: Tests run (may fail if PL9 references not present)
```

### 3. CI
```bash
# Check CI file exists
cat .github/workflows/ci.yml | head -20
# Expected: Shows workflow config

# After push, check GitHub Actions
# Should see new workflow running
```

### 4. Documentation
```bash
# Check docs exist
ls docs/
# Expected: REFACTORING_GUIDE_GRAHA.md, PARITY_WORKFLOW_README.md, IMPLEMENTATION_SUMMARY.md
```

---

## 🔧 Troubleshooting

### Problem: Import error "No module named 'refraction_engine.graha'"

**Solution**:
```bash
# Ensure you're in project root
pwd
# Should show: /path/to/refraction-engine-v1

# Check file exists
ls -la src/refraction_engine/graha.py

# Try importing from correct location
python -c "import sys; sys.path.insert(0, 'src'); from refraction_engine.graha import GrahaID; print('OK')"
```

---

### Problem: "pytest: command not found"

**Solution**:
```bash
# Install pytest
pip install pytest

# Or use python -m pytest
python -m pytest tests/refraction_engine/test_graha.py -v
```

---

### Problem: Parity script gives "Permission denied"

**Solution**:
```bash
# Make executable
chmod +x scripts/run_parity_suite.sh

# Or run with bash
bash scripts/run_parity_suite.sh
```

---

## 📞 Support

If you encounter issues:

1. Check `IMPLEMENTATION_SUMMARY.md` - common issues covered
2. Review `REFACTORING_GUIDE_GRAHA.md` - refactoring help
3. Check `PARITY_WORKFLOW_README.md` - parity test help
4. Ask me (Claude) for clarification!

---

## 🎁 Bonus: Combined Archive

All files are also available as a single archive:

```bash
# Create archive
cd /path/to/outputs
tar -czf gap1_gap3_implementation.tar.gz *.py *.sh *.bat *.yml *.md

# Extract later
tar -xzf gap1_gap3_implementation.tar.gz
```

---

**Manifest Created**: 2025-11-25  
**Total Files**: 8  
**Total Lines**: 3,250  
**Ready for Integration**: ✅

---

## 🚀 Final Command

Copy everything at once:

```bash
# Linux/Mac
cp /path/to/outputs/graha.py src/refraction_engine/ && \
cp /path/to/outputs/test_graha.py tests/refraction_engine/ && \
cp /path/to/outputs/run_parity_suite.sh scripts/ && \
cp /path/to/outputs/run_parity_suite.bat scripts/ && \
chmod +x scripts/run_parity_suite.sh && \
cp /path/to/outputs/ci_workflow.yml .github/workflows/ci.yml && \
cp /path/to/outputs/*.md docs/ && \
echo "✅ All files installed!"
```

Good luck! 🎉
