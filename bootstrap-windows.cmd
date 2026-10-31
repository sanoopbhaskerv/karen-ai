@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
    if not errorlevel 1 goto existing
)
py -3.15 -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto python315
py -3.14 -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto python314
py -3.13 -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto python313
py -3.12 -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto python312
python -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto pythonpath
python3 -c "import sys; sys.exit(not ((3,12) <= sys.version_info[:2] < (3,16)))" >nul 2>&1
if not errorlevel 1 goto python3path
echo No supported Python 3.12-3.15 was found on PATH or through the launcher. Install Python 3.14 from:
echo https://www.python.org/downloads/windows/
echo Choose Windows installer ^(64-bit^) for a usual Intel/AMD PC.
echo Include the Python launcher, then reopen this file. See README.md.
set "karenExit=1"
goto finished
:existing
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\bootstrap.py" %*
goto result
:python315
py -3.15 "%~dp0scripts\bootstrap.py" %*
goto result
:python314
py -3.14 "%~dp0scripts\bootstrap.py" %*
goto result
:python313
py -3.13 "%~dp0scripts\bootstrap.py" %*
goto result
:python312
py -3.12 "%~dp0scripts\bootstrap.py" %*
goto result
:pythonpath
python "%~dp0scripts\bootstrap.py" %*
goto result
:python3path
python3 "%~dp0scripts\bootstrap.py" %*
:result
set "karenExit=%errorlevel%"
:finished
if "%~1"=="" pause
endlocal & exit /b %karenExit%
