# setup.ps1 - Automated 1-Click Setup for Elenchus (Windows)
$ErrorActionPreference = "Stop"

Write-Host "`n=== Elenchus 1-Click Setup & Verification ===" -ForegroundColor Cyan

# 1. Check or install uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "[1/5] uv not found. Installing Astral uv..." -ForegroundColor Yellow
    Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "User") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "Machine")
} else {
    Write-Host "[1/5] uv package manager detected." -ForegroundColor Green
}

# 2. Ensure Python 3.12 is available
Write-Host "[2/5] Ensuring managed Python 3.12..." -ForegroundColor Yellow
uv python install 3.12

# 3. Deterministic Dependency Sync
Write-Host "[3/5] Syncing pinned dependencies via uv.lock..." -ForegroundColor Yellow
uv sync

# 4. Check Ollama daemon & model
Write-Host "[4/5] Checking Ollama reasoning engine..." -ForegroundColor Yellow
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    try {
        $null = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
        Write-Host "      Ollama daemon is running." -ForegroundColor Green
        Write-Host "      Ensuring qwen2.5-coder:3b model is pulled..." -ForegroundColor Yellow
        ollama pull qwen2.5-coder:3b
    } catch {
        Write-Host "      WARNING: Ollama service is offline. Start it via: ollama serve" -ForegroundColor DarkYellow
    }
} else {
    Write-Host "      WARNING: Ollama not installed. Download from https://ollama.com" -ForegroundColor DarkYellow
}

# 5. Pre-cache Whisper STT weights
Write-Host "[5/5] Pre-caching faster-whisper base.en weights..." -ForegroundColor Yellow
uv run python -c "from faster_whisper import WhisperModel; WhisperModel('base.en', device='cpu', compute_type='int8')"

# 6. Sanity Health Checks
Write-Host "`n=== Running Health Verification Tests ===" -ForegroundColor Cyan
uv run python -m unittest tests/test_core.py

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " [OK] Setup completed successfully! Everything is ready." -ForegroundColor Green
Write-Host " Launch HUD anytime:  uv run elenchus" -ForegroundColor Cyan
Write-Host " Or double-click:    .\run.bat" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Green
