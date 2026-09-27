@echo off
setlocal
cd /d "%~dp0"
echo Starting aenf // live debate HUD...
uv run aenf %*
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo aenf exited with error code %ERRORLEVEL%.
    pause
)
