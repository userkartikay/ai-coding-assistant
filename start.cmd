@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if not errorlevel 1 (
  python "%~dp0scripts\start_dev.py" %*
  exit /b
)
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "%~dp0scripts\start_dev.py" %*
  exit /b
)
echo Python 3.11+ was not found. Install Python from https://www.python.org/downloads/windows/ and enable PATH.
exit /b 1
