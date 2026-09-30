#!/usr/bin/env bash
# setup.sh - Automated Setup for Elenchus (Linux / macOS / WSL)
set -euo pipefail

echo ""
echo "=== Elenchus Setup & Verification (Unix) ==="

# 1. Check or install uv
if ! command -v uv &> /dev/null; then
    echo "[1/5] Installing Astral uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source "$HOME/.local/bin/env"
else
    echo "[1/5] uv detected."
fi

# 2. Ensure managed Python 3.12
echo "[2/5] Ensuring managed Python 3.12..."
uv python install 3.12

# 3. Deterministic Dependency Sync
echo "[3/5] Syncing pinned dependencies via uv.lock..."
uv sync

# 4. Check Ollama & Model
echo "[4/5] Checking Ollama reasoning engine..."
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "      Ollama daemon is running."
        echo "      Ensuring qwen2.5-coder:3b model is pulled..."
        ollama pull qwen2.5-coder:3b
    else
        echo "      WARNING: Ollama service is offline. Start it via: ollama serve"
    fi
else
    echo "      WARNING: Ollama not found. Download from https://ollama.com"
fi

# 5. Pre-cache Whisper STT weights
echo "[5/5] Pre-caching faster-whisper base.en weights..."
uv run python -c "from faster_whisper import WhisperModel; WhisperModel('base.en', device='cpu', compute_type='int8')"

# 6. Sanity Health Checks
echo ""
echo "=== Running Health Verification Tests ==="
QT_QPA_PLATFORM=offscreen uv run python -m unittest tests/test_core.py

echo ""
echo "========================================================"
echo " [OK] Setup completed successfully! Everything is ready."
echo " Launch HUD anytime:  uv run elenchus"
echo "========================================================"
echo ""
