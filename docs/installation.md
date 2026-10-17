# Installation and distribution

Elenchus provides prebuilt standalone binaries with SHA-256 integrity verification, along with an Astral `uv` setup for running directly from source.

---

## Single-command installers

=== "Windows (PowerShell)"

    Open PowerShell and run:

    ```powershell
    irm https://github.com/Asifdotexe/elenchus/releases/latest/download/install.ps1 | iex
    ```

    - Saves `elenchus-windows-x86_64.exe` into `$env:LOCALAPPDATA\Programs\Elenchus\`
    - Verifies the SHA-256 checksum against the release digest
    - Adds the binary to your user `PATH`

=== "macOS (Apple Silicon)"

    Open Terminal and run:

    ```bash
    curl -fsSL https://github.com/Asifdotexe/elenchus/releases/latest/download/install.sh | bash
    ```

    - Downloads `elenchus-darwin-arm64` (native M1 to M4) into `~/.local/bin/elenchus`
    - Checks the SHA-256 checksum against the release digest
    - Marks the file executable (`chmod +x`)

=== "macOS (Intel)"

    Open Terminal and run:

    ```bash
    curl -fsSL https://github.com/Asifdotexe/elenchus/releases/latest/download/install.sh | bash
    ```

    - Detects x86_64 architecture and downloads `elenchus-darwin-x86_64`
    - Verifies the SHA-256 checksum and installs to `~/.local/bin/elenchus`

=== "Linux (Ubuntu, Debian, Fedora, Arch)"

    Open Terminal and run:

    ```bash
    curl -fsSL https://github.com/Asifdotexe/elenchus/releases/latest/download/install.sh | bash
    ```

    - Downloads `elenchus-linux-x86_64` to `~/.local/bin/elenchus`
    - Checks the release checksum and sets executable permissions

---

## Standalone binary packages

If you work in airgapped environments or prefer manual installs, download the binaries directly from GitHub Releases.

| Platform | Architecture | Release file | Integrity check | Default path |
| :--- | :--- | :--- | :--- | :--- |
| **Windows (64-bit)** | `x86_64` | `elenchus-windows-x86_64.exe` | SHA-256 verified | `%LOCALAPPDATA%\Programs\Elenchus\` |
| **macOS (Apple Silicon)** | `arm64` (M1 to M4) | `elenchus-darwin-arm64` | SHA-256 verified | `~/.local/bin/elenchus` |
| **macOS (Intel)** | `x86_64` | `elenchus-darwin-x86_64` | SHA-256 verified | `~/.local/bin/elenchus` |
| **Linux (glibc 2.31+)** | `x86_64` | `elenchus-linux-x86_64` | SHA-256 verified | `~/.local/bin/elenchus` |

### Manual verification

To check the hash of a downloaded binary yourself:

**Windows (PowerShell):**
```powershell
Get-FileHash .\elenchus-windows-x86_64.exe -Algorithm SHA256
```

**macOS:**
```bash
shasum -a 256 elenchus-darwin-arm64
```

**Linux:**
```bash
sha256sum elenchus-linux-x86_64
```

Compare the output hash with the values listed in `checksums.txt` on the release page.

---

## Running from source

If you want to modify Elenchus or inspect the code, run it through Astral `uv`:

### Prerequisites
- Python 3.12 or newer
- Astral `uv` (`curl -LsSf https://astral.sh/uv/install.sh | sh` or `irm https://astral.sh/uv/install.ps1 | iex`)
- [Ollama](https://ollama.ai) installed and running locally

### Clone and run
```bash
git clone https://github.com/Asifdotexe/elenchus.git
cd elenchus

# uv sets up the virtual environment and starts the app
uv run elenchus
```

### Pull an Ollama model
Elenchus defaults to fast, lightweight models to keep latency low:

```bash
ollama pull qwen2.5-coder:3b
# Alternatively:
ollama pull qwen2.5:3b
```

To configure alternative models or adjust endpoints, see [Ollama configuration](user-guide.md#ollama-configuration). For model latency impacts, see [Latency budget breakdown](specifications.md#latency-budget-breakdown).
