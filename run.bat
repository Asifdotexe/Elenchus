@echo off
setlocal
cd /d "%~dp0"
echo Starting Elenchus // Socratic debate analysis HUD...
uv run elenchus %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Elenchus exited with error code %ERRORLEVEL%.
    pause
)
