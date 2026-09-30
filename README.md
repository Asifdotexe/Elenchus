# Elenchus (ἔλεγχος)

[![CI](https://github.com/Asifdotexe/aenf/actions/workflows/ci.yml/badge.svg)](https://github.com/Asifdotexe/aenf/actions/workflows/ci.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> **/ɪˈlɛŋ.kəs/** (Ancient Greek: **ἔλεγχος**, *elenchos*): The Socratic method of dialectical inquiry and cross-examination. It examines an interlocutor's propositions to test consistency, uncover unstated premises, expose logical fallacies, and refute unsound arguments.

Elenchus is an offline debate analysis and fallacy detection engine designed for live conversations and recorded speech. It transcribes spoken arguments locally, evaluates rhetorical structure, isolates informal fallacies, and generates direct Socratic counter-arguments using local language models.

The system is engineered to run on consumer hardware (8 GB system RAM and 4 GB GPU VRAM). Speech transcription runs on CPU in INT8 quantization so all GPU VRAM remains dedicated to local model inference.

---

## Architecture & Hardware Budget

| Subsystem | Engine / Library | Hardware Device | Memory & Compute Allocation |
| :--- | :--- | :--- | :--- |
| Speech-to-Text | faster-whisper (`base.en`) | CPU (INT8, 4 threads) | 500 MB to 1 GB RAM, 0 MB VRAM |
| Socratic Reasoning | `qwen2.5-coder:3b` / `qwen2.5:3b` | GPU (4-bit Q4_K_M via Ollama) | 2.0 to 2.4 GB VRAM |
| Audio Capture & VAD | `sounddevice` + sample-accurate RMS VAD | CPU | < 40 MB RAM |
| Desktop HUD Overlay | PyQt6 (frameless, translucent, draggable) | CPU / Window Compositor | < 80 MB RAM |

---

## Setup

### Windows
Run the setup script in PowerShell:
```powershell
.\setup.ps1
```
This script validates or installs `uv`, verifies Python 3.12, syncs dependencies from `uv.lock`, pulls the default Ollama model, and caches Whisper STT model weights.

### Linux / macOS / WSL
```bash
chmod +x setup.sh && ./setup.sh
```

---

## Usage

### Launching the Desktop HUD
Launch using `uv`:
```bash
uv run elenchus
```
On Windows, you can also double-click `run.bat`.

### Selecting Audio Devices
List all available input devices (microphones and loopback monitors):
```bash
uv run elenchus --list-devices
```

Test an input device before starting to observe live audio levels:
```bash
uv run elenchus --test-device 17
```

Bind Elenchus to a specific audio device index or partial name:
```bash
uv run elenchus --device 17
```

### Specifying Models
Override the default Ollama or Whisper models:
```bash
uv run elenchus --model qwen2.5-coder:3b --whisper-model base.en
```

Alternatively, configure the model via environment variable:
```bash
export ELENCHUS_MODEL="qwen2.5:3b"
```

---

## Interface & Controls

- **Push-to-Talk Listening (Default):** Click "Start Listening" (or press Space) when an opponent begins speaking. Click "Stop & Analyze Now" when they conclude. The segment cuts immediately without waiting for silence.
- **Continuous Auto VAD:** Click the "Manual" button in the header or run `uv run elenchus --auto` to enable automatic voice-activity detection.
- **Draggable Window:** Click and drag the header or card body to reposition the overlay anywhere on your screen.
- **Window Stacking:** The card uses always-on-top hints to remain accessible over Discord, Zoom, or presentation windows.
- **Collapsible Mode:** Click the collapse button on the top right to shrink the card into a minimal status bar.
- **Real-Time Audio Meter:** The Monochart visualizer displays input levels and speech detection in real time.
- **Fallacy Analysis:** Displays the transcribed claim, the identified fallacy, and a direct one-sentence rebuttal. Conversational filler and incomplete statements are classified as non-arguments rather than forced into fallacy categories.

---

## Development & Testing

Run pre-commit checks:
```bash
prek run --all-files
```

Run unit tests:
```bash
uv run python -m unittest tests/test_core.py
```

Run integration tests (requires local Ollama service):
```bash
uv run python -m unittest tests/test_integration.py
```

For system specifications and version planning, refer to [BLUEPRINT.md](BLUEPRINT.md).
