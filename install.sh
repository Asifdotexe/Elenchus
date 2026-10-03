#!/usr/bin/env bash
# install.sh - Automated 1-line curl installer for Elenchus (Linux / macOS)
set -euo pipefail

echo ""
echo "=== Elenchus (ἔλεγχος) Installer ==="

REPO="Asifdotexe/elenchus"
INSTALL_DIR="$HOME/.local/bin"
TARGET_FILE="$INSTALL_DIR/elenchus"

mkdir -p "$INSTALL_DIR"

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
    Linux)
        ASSET="elenchus-linux-x86_64"
        ;;
    Darwin)
        if [ "$ARCH" = "arm64" ]; then
            ASSET="elenchus-darwin-arm64"
        else
            ASSET="elenchus-darwin-x86_64"
        fi
        ;;
    *)
        echo "Error: Unsupported operating system: $OS"
        exit 1
        ;;
esac

echo "[1/3] Resolving latest binary ($ASSET)..."
DOWNLOAD_URL="https://github.com/$REPO/releases/latest/download/$ASSET"

echo "[2/3] Downloading $ASSET to $TARGET_FILE..."
curl -fsSL "$DOWNLOAD_URL" -o "$TARGET_FILE"

SHA_URL="${DOWNLOAD_URL}.sha256"
if curl -fsSL "$SHA_URL" -o "${TARGET_FILE}.sha256" 2>/dev/null; then
    EXPECTED_SHA=$(awk '{print $1}' "${TARGET_FILE}.sha256" | tr '[:upper:]' '[:lower:]')
    if command -v sha256sum &> /dev/null; then
        ACTUAL_SHA=$(sha256sum "$TARGET_FILE" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
    elif command -v shasum &> /dev/null; then
        ACTUAL_SHA=$(shasum -a 256 "$TARGET_FILE" | awk '{print $1}' | tr '[:upper:]' '[:lower:]')
    else
        ACTUAL_SHA=""
    fi
    rm -f "${TARGET_FILE}.sha256"
    if [ -n "$ACTUAL_SHA" ]; then
        if [ "$EXPECTED_SHA" != "$ACTUAL_SHA" ]; then
            echo "Error: SHA-256 checksum mismatch! Expected $EXPECTED_SHA, got $ACTUAL_SHA. Aborting."
            rm -f "$TARGET_FILE"
            exit 1
        fi
        echo "      Checksum verified: $ACTUAL_SHA"
    fi
else
    echo "      [NOTE] Checksum verification skipped (release asset hash unavailable)."
fi

chmod +x "$TARGET_FILE"

echo "[3/3] Checking PATH environment..."
case ":$PATH:" in
    *":$INSTALL_DIR:"*)
        echo "      $INSTALL_DIR is already in PATH."
        ;;
    *)
        echo "      Adding $INSTALL_DIR to PATH recommended. Run:"
        echo "      export PATH=\"\$HOME/.local/bin:\$PATH\" >> ~/.bashrc (or ~/.zshrc)"
        ;;
esac

echo ""
if ! command -v ollama &> /dev/null; then
    echo "[NOTE] Ollama not detected. Download from https://ollama.com to enable local fallacy reasoning."
else
    echo "[OK] Ollama detected on system."
fi

echo ""
echo "========================================================"
echo " [OK] Elenchus installed successfully!"
echo " Launch HUD anytime:  elenchus"
echo "========================================================"
echo ""
