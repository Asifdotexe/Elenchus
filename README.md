<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/branding/kit/elenchus-symbol-white.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/branding/kit/elenchus-symbol-black.svg">
    <img alt="Elenchus (ἔλεγχος)" src="assets/branding/kit/elenchus-symbol-white.svg" width="140" height="140">
  </picture>

  <h1>Elenchus (ἔλεγχος)</h1>

  <p>
    <strong>Real-time Socratic debate analysis and fallacy detection engine.</strong><br>
    <em>100% offline. Local Whisper speech-to-text and Ollama reasoning rendered over your desktop.</em>
  </p>

  <p>
    <a href="https://github.com/Asifdotexe/elenchus/actions/workflows/ci.yml"><img src="https://github.com/Asifdotexe/elenchus/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://asifdotexe.github.io/elenchus/"><img src="https://img.shields.io/badge/website-live-101010?style=flat&logo=safari&logoColor=white" alt="Website"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-101010?style=flat&logo=python&logoColor=white" alt="Python 3.12"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-101010?style=flat" alt="MIT License"></a>
  </p>

  <p>
    <a href="https://asifdotexe.github.io/elenchus/"><strong>Website</strong></a> &nbsp;•&nbsp;
    <a href="https://asifdotexe.github.io/elenchus/#simulator"><strong>Interactive HUD Demo</strong></a> &nbsp;•&nbsp;
    <a href="docs/ARCHITECTURE.md"><strong>Architecture Spec</strong></a> &nbsp;•&nbsp;
    <a href="assets/branding/BRAND_GUIDELINES.md"><strong>Brand Guidelines</strong></a>
  </p>
</div>

---

> **/ɪˈlɛŋ.kəs/** (Ancient Greek: **ἔλεγχος**, *elenchos*): The Socratic method of dialectical inquiry. Examining claims to test logical consistency, expose fallacies, and surface direct counter-arguments.

**Elenchus** is a privacy-first, offline debate assistant designed for live conversations, panel discussions, and recorded speech. It continuously monitors audio, extracts discrete claims, isolates rhetorical fallacies, and delivers concise, one-sentence Socratic rebuttals on a translucent, always-on-top desktop Heads-Up Display (HUD).

Engineered to run entirely on consumer hardware (8 GB RAM, 4 GB GPU VRAM) with zero data leaving your machine.

---

## Quick Install

### 1-Line Standalone Binaries (No Python or uv Required)

#### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Asifdotexe/elenchus/main/install.ps1 | iex
```

#### macOS / Linux
```bash
curl -fsSL https://raw.githubusercontent.com/Asifdotexe/elenchus/main/install.sh | bash
```

Once installed, simply run `elenchus` from any terminal.

---

### Developer Setup (via `uv`)

```bash
# Clone repository
git clone https://github.com/Asifdotexe/elenchus.git
cd elenchus

# Automated setup (installs dependencies, checks Ollama & Whisper weights)
# Windows:
.\setup.ps1
# Linux / macOS:
./setup.sh

# Launch HUD
uv run elenchus
```

---

## Interface & Controls

The desktop overlay features an Obsidian (`#101010`) palette with 1px hairline borders inspired by the Hyperstudio aesthetic. It floats unobtrusively over Discord, Zoom, Google Meet, or presentation windows.

| Control | Action | Details |
| :--- | :--- | :--- |
| `Space` or **Click** | **Push-to-Talk** | Instant slice: cuts audio immediately and processes without waiting for silence. |
| **Manual / Auto** | **Mode Toggle** | Switch between manual push-to-talk and continuous Voice Activity Detection (VAD). |
| `—` Button | **Collapse HUD** | Shrinks the card to an ultra-minimal status bar showing audio energy and system state. |
| **Drag Header** | **Reposition** | Move overlay anywhere across multi-monitor desktop workspaces. |
| **Monochart** | **Live Meter** | 30-bar visualizer indicating RMS speech energy and silence detection thresholds. |

---

## CLI Reference

```bash
# Launch the desktop HUD overlay
uv run elenchus

# List all available audio devices (microphones & loopback monitors)
uv run elenchus --list-devices

# Test input levels on a specific audio device before debate
uv run elenchus --test-device 17

# Launch bound to a specific audio input
uv run elenchus --device 17

# Launch in continuous auto-VAD mode
uv run elenchus --auto

# Specify a custom Ollama or Whisper model
uv run elenchus --model qwen2.5-coder:3b --whisper-model base.en
```

---

## Systems Architecture & Hardware Budget

Elenchus divides workloads across hardware boundaries so that speech transcription never starves the local LLM of GPU VRAM:

```
  [ Microphone / Audio Loopback ]
                 │
                 ▼
   faster-whisper (CPU, INT8) ────► 500 MB – 1 GB RAM, 0 MB VRAM (< 350 ms)
                 │
                 ▼
   Ollama Qwen2.5 (GPU, Q4_K_M) ──► 2.0 – 2.4 GB VRAM (< 250 ms)
                 │
                 ▼
   PyQt6 Obsidian HUD ───────────► Hardware-composited desktop overlay
```

| Subsystem | Engine | Device Target | Resource Footprint |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text** | faster-whisper (`base.en`) | CPU (INT8, 4 threads) | 500 MB – 1 GB RAM, 0 MB VRAM |
| **Socratic Reasoning** | `qwen2.5:3b` / `qwen2.5-coder:3b` | GPU (Q4_K_M via Ollama) | ~2.2 GB VRAM |
| **Audio Capture & VAD** | `sounddevice` + RMS VAD | CPU | < 40 MB RAM |
| **Desktop HUD Overlay** | PyQt6 frameless compositor | GPU / Compositor | < 80 MB RAM |

---

## Security & Verification

Elenchus has undergone an end-to-end security review:
- **Zero Cloud Leakage**: Audio waveforms and model queries never leave `localhost`.
- **Prompt Injection Defense**: Speech transcripts are strictly isolated within structural boundary `<opponent_statement>` tags.
- **RichText Injection Immunity**: HUD labels enforce `Qt.TextFormat.PlainText` preventing HTML rendering of untrusted transcripts.
- **Cryptographic Binary Validation**: Installers compute local SHA-256 digests against release checksums prior to installation.

### Running Test Suite

```bash
# Run automated regression & unit tests
uv run python -m unittest tests/test_core.py

# Run ruff code linter & formatter
uv run ruff check .
uv run ruff format --check
```

---

## Project Documentation

- [Architecture & Threading Specification](docs/ARCHITECTURE.md)
- [Milestone Blueprint & Tracking](docs/BLUEPRINT.md)
- [Official Brand Identity Guidelines](assets/branding/BRAND_GUIDELINES.md)
- [MIT License](LICENSE)
