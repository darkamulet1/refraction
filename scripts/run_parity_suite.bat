@echo off
setlocal enabledelayedexpansion
pushd %~dp0\..
echo Running parity suite (tests/parity)...
python -m pytest tests/parity -v --tb=short
popd
