@echo off
setlocal enabledelayedexpansion
set ROOT_DIR=%~dp0..
cd /d "%ROOT_DIR%"
python -m pytest tests/specs %*
endlocal
