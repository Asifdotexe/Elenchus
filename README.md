# aenf (all ears no foul)

Minimal, non-intrusive desktop HUD overlay that listens to live incoming discussion/debate audio, transcribes speech in real time, and uses a local quantized LLM via Ollama to detect logical fallacies and generate instant counter-arguments.

Designed strictly for an 8 GB RAM / 4 GB VRAM hardware profile with zero VRAM thrashing.

---

## Architecture & Hardware Budget

| Subsystem | Engine / Library | Hardware Device | Footprint |
| :--- | :--- | :--- | :--- |
| **STT Engine** | `faster-whisper` (`base.en`) | **CPU (INT8)** | ~500 MB – 1 GB RAM / **0 MB VRAM** |
| **Debate Reasoning Engine** | `qwen2.5-coder:3b` / `qwen2.5:3b` | **GPU (4-bit Q4_K_M)** | ~2.0 – 2.2 GB VRAM |
| **Audio Capture & VAD** | `sounddevice` + Sample-accurate RMS VAD | CPU | ~40 MB RAM |
| **HUD Overlay** | `PyQt6` (Frameless, translucent, draggable) | CPU / Compositor | ~80 MB RAM |

---

## Quickstart

### 1. Prerequisites
- Python 3.12+
- [Ollama](https://ollama.com) running locally:
  ```bash
  ollama run qwen2.5-coder:3b
  # or: ollama run qwen2.5:3b
  ```

### 2. Environment Setup
```bash
uv sync
```

### 3. Check Audio Devices
List all available input devices (microphones and loopback devices like *Stereo Mix* or *VB-Audio Cable*):
```bash
uv run aenf --list-devices
```

### 4. Run `aenf`
```bash
# Launch with default input device
uv run aenf

# Or specify a device index (e.g., Stereo Mix or headset mic)
uv run aenf --device 17

# Launch with custom Ollama model or Whisper model
uv run aenf --model qwen2.5-coder:3b --whisper-model base.en
```

---

## Features & Controls

- **Draggable Window:** Click and drag the card anywhere on screen.
- **Always on Top:** Frameless translucent overlay stays pinned over Discord, Zoom, browsers, or games.
- **Minimize / Expand:** Click the `—` button on the top right to collapse to a minimal status bar or restore full view.
- **Live VU Activity:** Bottom green/cyan progress bar indicates audio level and speech detection.
- **Instant Fallacy Breakdown:** Displays opponent quotation, identified logical fallacy, and 1-sentence counter-argument in under 3 seconds.
- **Pre-warmed GPU Pipeline:** Pre-warms the local model in VRAM at startup to eliminate cold-start spikes.

---

## Running Tests

```bash
# Unit tests
uv run python -m unittest tests/test_core.py

# End-to-end integration test (requires Ollama running)
uv run python -m unittest tests/test_integration.py
```
