# Technical blueprint: aenf (all ears no foul)

## 1. Project overview and objective

`aenf` is a lightweight desktop overlay that listens to live debate audio, transcribes speech locally, and flags logical flaws with an immediate counter-argument using a local quantized language model. The interface is a frameless, translucent card that stays pinned on top of other windows.

### Hardware constraints
- Host memory: 8 GB system RAM.
- GPU: 4 GB dedicated VRAM (NVIDIA CUDA).
- Target latency: Under 3 seconds from speech end to displayed rebuttal.
- Memory isolation: Whisper and the language model cannot both reside in GPU memory on a 4 GB card without triggering swap thrashing. Speech transcription runs on the CPU in INT8; the language model runs on the GPU in 4-bit quantization.

## 2. Resource budget

Target allocations for an 8 GB RAM and 4 GB VRAM system:

| Subsystem | Library or engine | Hardware | Target footprint |
| :--- | :--- | :--- | :--- |
| Host operating system | Windows or Linux | CPU / host | 3.0 to 3.5 GB RAM, 500 MB VRAM |
| Speech-to-text | faster-whisper (base.en) | CPU (INT8) | 500 MB to 1.0 GB RAM, 0 MB VRAM |
| Debate reasoning engine | qwen2.5-coder:3b via Ollama | GPU (4-bit Q4_K_M) | 2.0 to 2.4 GB VRAM |
| Audio capture and VAD | sounddevice and numpy RMS | CPU | 40 MB RAM |
| Overlay interface | PyQt6 frameless widget | CPU / compositor | 80 MB RAM |

## 3. Data flow

```text
[Audio stream: loopback or mic]
              │
              ▼
[RMS voice activity detection and sample buffer]
              │ (speech slice extracted)
              ▼
[faster-whisper worker (CPU INT8)]
              │ (clean transcript string)
              ▼
[Argument pre-filter]
              │ (drops filler, checks premise and claim)
              ▼
[Ollama local REST API (localhost:11434)]
              │ (extracts flaw and one-sentence counter)
              ▼
[PyQt6 pipeline controller]
              │ (dispatches via Qt signals)
              ▼
[HUD card overlay]
```

## 4. Subsystem design

### 4.1 Audio ingestion
- Capture mono float32 audio at 16,000 Hz using `sounddevice`.
- Inspect the device native sample rate (often 44.1 kHz or 48 kHz on Windows WASAPI) and resample to 16 kHz in memory.
- Dynamic chunking: Read 100 ms audio slices into a thread-safe queue. In automatic mode, cut the segment when silence lasts at least 600 to 800 ms or the buffer reaches 5 seconds. In manual mode, accumulate chunks on button press and cut immediately on release.

### 4.2 Transcription
- Engine: `faster-whisper` using `base.en` with `compute_type="int8"` and `beam_size=1` on CPU.
- Filtering: Discard transcripts under 15 characters, repeated identical phrases, and common silence hallucinations like "thank you for watching" or "[music]".

### 4.3 Debate reasoning backend
- Endpoint: Ollama REST API (`/api/generate`).
- Model: `qwen2.5-coder:3b` or `qwen2.5:3b`.
- Parameters: Temperature 0.2 to 0.25, max tokens 60 to 80.
- System prompt rules:
  1. An argument requires a premise and an inferred conclusion.
  2. If the statement is incomplete, an interjection, or conversational filler, output `Flaw: None (Incomplete / Non-Argument)` and note the missing premise.
  3. If the statement is valid and logical, output `Flaw: None (Valid claim)` and provide counter-evidence.
  4. If a fallacy exists, name the exact fallacy and write a direct one-sentence counter-argument.
  5. Keep total output under 30 words without conversational filler.

### 4.4 HUD overlay
- Window flags: `FramelessWindowHint`, `WindowStaysOnTopHint`, and `Tool`.
- Translucent background with a dark card style (`rgba(18, 18, 24, 0.93)`), rounded borders, and drop shadow.
- Controls: Click-and-drag positioning, collapse toggle, close button, live audio VU progress bar, and mode toggle between manual push-to-talk and automatic silence detection.
- Dynamic tags: Red or amber badge for logical flaws; neutral blue badge for incomplete statements or valid claims.

## 5. Code layout

```text
aenf/
├── pyproject.toml        # Pinned dependencies and CLI script entrypoint
├── uv.lock               # Reproducible lockfile
├── setup.ps1             # Automated Windows setup
├── setup.sh              # Automated Unix setup
├── run.bat               # Desktop launcher
├── config.py             # Configuration dataclass
├── core/
│   ├── audio_capture.py  # sounddevice stream with auto-resampling
│   ├── vad.py            # Sample-accurate RMS VAD
│   ├── transcriber.py    # faster-whisper CPU worker
│   ├── llm_client.py     # Ollama client and argument pre-filter
│   └── pipeline.py       # Background QThread coordinator
├── ui/
│   └── overlay.py        # PyQt6 glassmorphic HUD
└── tests/
    ├── test_core.py      # Unit tests
    └── test_integration.py # End-to-end integration test
```

## 6. Threading model

1. GUI thread (Thread 0): Handles Qt rendering, paint events, window dragging, and button interactions. Does not execute network or inference calls.
2. Audio recorder thread: Continuously pulls audio blocks from `sounddevice` and places them into a thread-safe queue.
3. Pipeline QThread: Pops audio chunks, runs VAD, executes CPU transcription, queries Ollama, and delivers structured results to the UI thread via `pyqtSignal`.

## 7. Edge cases and failure recovery

- Ollama offline: Catch connection errors and display an offline warning on the HUD with the command to start the model.
- Inference latency: If Ollama takes longer than 10 seconds, drop the request gracefully with a warning to keep real-time sync.
- Audio sample rate mismatch: Query the host device native sample rate and resample to 16 kHz using linear interpolation.
- Window close hang: Explicitly call `QApplication.quit()` in `closeEvent` and stop worker streams so the process exits cleanly without leaving zombie threads.

## 8. Verification checklist

- [ ] STT runs on CPU using INT8 with 0 MB GPU VRAM allocation.
- [ ] Overlay remains visible on top when focusing third-party apps like Discord or a web browser.
- [ ] Total VRAM usage stays under 3.0 GB during active inference.
- [ ] System handles connection dropouts or slow Ollama responses without freezing the GUI.
- [ ] The application exits cleanly when the close button is clicked.