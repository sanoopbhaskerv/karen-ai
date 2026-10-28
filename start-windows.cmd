@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
set "PYTHONUTF8=1"
cd /d "%~dp0"
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo Run bootstrap-windows.cmd first. See README.md / READMEMALAYALAM.md.
    pause
    exit /b 1
)
echo Karen AI: keep this window open. Open http://localhost:8080 in your browser.
echo Stop with Ctrl+C. Existing files and saved facts are kept.
"%~dp0.venv\Scripts\python.exe" "%~dp0app.py"
set "karenExit=%errorlevel%"
if not "%karenExit%"=="0" pause
endlocal & exit /b %karenExit%
