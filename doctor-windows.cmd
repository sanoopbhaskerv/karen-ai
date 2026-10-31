@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Run bootstrap-windows.cmd first. Do not copy a Mac .venv to Windows.
    if "%~1"=="" pause
    exit /b 1
)
"%~dp0.venv\Scripts\python.exe" "%~dp0scripts\doctor.py" %*
set "karenExit=%errorlevel%"
if "%~1"=="" pause
endlocal & exit /b %karenExit%
