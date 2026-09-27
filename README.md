# aenf (all ears no foul)

`aenf` is a desktop overlay that listens to debate audio, transcribes speech locally, and uses a local language model via Ollama to detect logical fallacies and generate immediate counter-arguments.

The pipeline is tuned for systems with 8 GB RAM and 4 GB VRAM, keeping speech recognition on the CPU so the GPU is dedicated to the language model.

---

## Architecture and hardware budget

| Subsystem | Library or engine | Hardware device | Footprint |
| :--- | :--- | :--- | :--- |
| Speech-to-text | faster-whisper (base.en) | CPU (INT8) | 500 MB to 1 GB RAM, 0 MB VRAM |
| Debate reasoning engine | qwen2.5-coder:3b / qwen2.5:3b | GPU (4-bit Q4_K_M) | 2.0 to 2.2 GB VRAM |
| Audio capture and VAD | sounddevice + sample-accurate RMS VAD | CPU | 40 MB RAM |
| HUD overlay | PyQt6 (frameless, translucent, draggable) | CPU / compositor | 80 MB RAM |

---

## Setup

### Windows
Run the setup script in PowerShell:
```powershell
.\setup.ps1
```
This script checks for `uv`, installs Python 3.12 if needed, syncs pinned dependencies from `uv.lock`, downloads the Ollama model, and pre-caches the Whisper model weights.

### Linux / macOS / WSL
```bash
chmod +x setup.sh && ./setup.sh
```

---

## Running the application

### Starting the HUD
Launch using `uv`:
```bash
uv run aenf
```
On Windows, you can also double-click `run.bat`.

### Selecting an audio device
List all input devices to find your microphone or loopback cable:
```bash
uv run aenf --list-devices
```
Test an input device before starting to see live volume levels:
```bash
uv run aenf --test-device 17
```
Run `aenf` bound to a specific device index:
```bash
uv run aenf --device 17
```

### Specifying models
```bash
uv run aenf --model qwen2.5-coder:3b --whisper-model base.en
```

---

## Controls and usage

- Push-to-talk listening (default): Click "Start Listening" (or press Space) when an opponent begins speaking. Click "Stop & Analyze Now" when they finish. The app cuts audio immediately without waiting for silence.
- Automatic silence cutting: Click "Manual" in the header to switch to automatic mode, where silence thresholds cut speech segments automatically. You can also start the app in this mode using `uv run aenf --auto`.
- Dragging: Click and drag anywhere on the card to reposition it.
- Window stacking: The card uses always-on-top window hints, keeping it visible over Discord, Zoom, or web browsers.
- Minimizing: Click the collapse button on the top right to shrink the card into a compact status bar.
- Audio activity meter: The bottom progress bar indicates incoming audio energy and speech detection in real time.
- Fallacy breakdown: Displays the opponent transcript, identified rhetorical defect, and a one-sentence counter-argument. Statements lacking an argument structure (filler or trailing fragments) are labeled as incomplete rather than shoehorned into a fallacy.

---

## Running tests

```bash
# Unit tests
uv run python -m unittest tests/test_core.py

# End-to-end integration test (requires Ollama running)
uv run python -m unittest tests/test_integration.py
```
