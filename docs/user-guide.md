# User guide and HUD controls

This guide covers how to position the desktop overlay, select audio devices, choose voice detection modes, and configure local Ollama models.

---

## Operating the desktop HUD

The Elenchus overlay is a minimal, translucent window designed to stay in your peripheral vision during live calls without blocking other windows.

### Moving and positioning
- Click and drag anywhere on the HUD header or background to move it across monitors.
- The window sets `Qt.WindowStaysOnTopHint`, keeping it visible when other apps (Discord, Zoom, Google Meet) have focus.

### Status indicators
- **Green LED (`#98ff38`)**: Ready and listening for spoken statements.
- **Amber LED (`#d97706`)**: Transcribing audio or running fallacy inference.
- **Red LED (`#ef4444`)**: Warning state (such as an unreachable Ollama instance).

### Audio waveform meter
The Monochart energy meter shows incoming audio amplitude in real time. Bars illuminate green once voice energy rises above the baseline noise floor.

---

## Voice activity detection modes

Elenchus supports two listening modes depending on your setting:

### Manual push-to-talk (recommended for debates)
- Click the HUD action bar or press `Space` to start recording when your opponent speaks. Click again when they finish.
- This avoids background noise, interruptions, or coughing from triggering unneeded model runs.

### Continuous automatic VAD
- The engine calculates real-time RMS energy automatically.
- When speech remains above the noise threshold for 300 ms, recording starts. When silence persists for 700 ms, the audio slice sends to the transcriber.
- Useful for hands-free listening.

---

## Configuring audio capture

### Capturing opponent audio with loopback

To analyze an opponent over Discord or a web browser on Windows:

1. Set your system output to your normal headphones or speakers.
2. In `config.py` (or through `--device` in the CLI), pick the loopback endpoint matching your output device.
3. Elenchus captures the WASAPI loopback stream directly without needing virtual audio cable drivers.

### Capturing microphone audio

To practice statements yourself or analyze an in-person room debate, select your physical USB microphone or headset input in `config.py`.

---

## Ollama configuration

Elenchus communicates with your local Ollama daemon at `http://localhost:11434`.

### Switching models

Specify your preferred model in `config.py`:

```python
# Default model for concise fallacy detection
OLLAMA_MODEL = "qwen2.5-coder:3b"
```

Tested options:

- **`qwen2.5-coder:3b`** (default): Fast inference and reliable on informal fallacy detection with concise phrasing.
- **`qwen2.5:3b`**: Good general reasoning alternative.
- **`llama3.2:3b`**: Lightweight alternative with low memory usage.
- **`mistral:7b`**: Provides longer, more nuanced refutations at higher VRAM usage.

For benchmark comparisons and latency breakdown, see [Runtime specifications](specifications.md#latency-budget-breakdown). For the design rationale behind selecting coder models, see [Why a coder model? Brevity](philosophy.md#2-why-a-coder-model-brevity).


### Starting Ollama
Make sure Ollama is running before starting Elenchus:
```bash
ollama list
```
If it is not running, start it in a separate terminal:
```bash
ollama serve
```
