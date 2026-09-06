@echo off
setlocal
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" scripts\windows_entry.py launch
  goto done
)
py -3 -c "import sys; sys.exit(sys.version_info < (3,11))" >nul 2>&1
if not errorlevel 1 (
  py -3 scripts\windows_entry.py launch
  goto done
)
python -c "import sys; sys.exit(sys.version_info < (3,11))" >nul 2>&1
if not errorlevel 1 (
  python scripts\windows_entry.py launch
  goto done
)
echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
echo Then extract this ZIP completely and run this file again.
:done
pause
