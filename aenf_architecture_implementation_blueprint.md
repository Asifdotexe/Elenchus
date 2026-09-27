# Product & Technical Blueprint: `aenf` (all ears no foul)

> **Role & Purpose for AI Implementation Agent:**  
> You are tasked with generating a production-ready, lightweight, standalone desktop HUD application named **`aenf` (all ears no foul)** in Python.  
> Read this complete architectural and hardware profile carefully. Adhere strictly to the memory constraints, threading model, and user interface specifications provided below.

---

## 1. Project Overview & Objective

`aenf` is a minimal, non-intrusive desktop overlay that listens to live incoming discussion/debate audio (either from a virtual loopback device like Discord/Zoom/YouTube or an input mic), automatically detects speech, transcribes it on the fly, and uses a local quantized Large Language Model (LLM) to detect logical fallacies, rhetorical flaws, and supply immediate counter-arguments on a transparent, draggable heads-up display (HUD).

### Key Constraints
- **Hardware Profile:** 8 GB Total System RAM, 4 GB Dedicated VRAM (NVIDIA CUDA preferred).
- **Cost:** 100% Free and open-source (FOSS) / local-first.
- **Latency Target:** $< 3$ seconds total end-to-end (Audio End $\to$ Displayed Rebuttal).
- **Zero VRAM Collision:** VRAM cannot be shared equally between Whisper and LLM without triggering system swap thrashing. Strict hardware partition is required.

---

## 2. Resource Partitioning & Hardware Budget

To operate reliably on 8 GB RAM / 4 GB VRAM without Out-Of-Memory (OOM) crashes:

| Subsystem | Engine / Library | Execution Device | Target Footprint |
| :--- | :--- | :--- | :--- |
| **Operating System & Overhead** | Host OS (Windows / Linux) | Host | ~3.0 - 3.5 GB RAM / ~500 MB VRAM |
| **Speech-to-Text (STT)** | `faster-whisper` (`base.en` or `small.en`) | **CPU (INT8)** | ~500 MB – 1.0 GB RAM / **0 MB VRAM** |
| **Debate Reasoning Engine** | `Qwen2.5-3B-Instruct` or `Phi-4-mini` via Ollama | **GPU (4-bit / Q4_K_M)** | ~2.2 – 2.6 GB VRAM |
| **Audio Capture & VAD** | `sounddevice` + `numpy` RMS / `silero-vad` | CPU | ~40 MB RAM |
| **Overlay UI** | `PyQt6` (Frameless, translucent) | CPU / OS Compositor | ~80 MB RAM |

---

## 3. Core Architecture Pipeline

```text
[Audio Stream: Loopback / Mic]
             │
             ▼
[Voice Activity Detection (RMS threshold or Silero-VAD)]
             │ (Speech segment detected & padded)
             ▼
[faster-whisper Worker (CPU, INT8)]
             │ (Outputs transcribed string)
             ▼
[Debate Filter & Formatter]
             │ (Discards trivial filler, handles dedup)
             ▼
[Ollama Local REST API: http://localhost:11434]
             │ (Runs Qwen2.5:3b with strict JSON/Bullet format)
             ▼
[PyQt6 HUD Controller]
             │ (Dispatches to GUI thread via Qt Signals)
             ▼
[Draggable, Click-Through, Translucent Overlay UI]
```

---

## 4. Subsystem Specifications

### 4.1 Audio Ingestion & Capture
- Use `sounddevice` with configurable sample rate ($16000\text{ Hz}$, mono, 16-bit float32).
- Audio device selection:
  - If a loopback driver (e.g., *VB-Audio Cable*, *Stereo Mix*, or *PulseAudio monitor*) is present, allow selecting it via a config/CLI flag. Default to `default_input`.
- **Chunking / VAD:**
  - Avoid sending fixed raw intervals that cut words in half.
  - Implement dynamic chunking: read small slices (e.g., $100\text{ ms}$), buffer them, and inspect energy (RMS) or run a lightweight VAD.
  - Trigger transcription once silence exceeds $600\text{ ms} - 800\text{ ms}$ or buffer reaches a max of $5\text{ seconds}$.

### 4.2 Transcription (STT)
- **Library:** `faster-whisper`.
- **Model:** `base.en` (fastest) or `small.en` (slightly better vocabulary).
- **Parameters:**
  - `device="cpu"`
  - `compute_type="int8"`
  - `beam_size=1` (greedy decoding for minimal CPU overhead).
- **Validation:**
  - Ignore transcripts with length $< 15$ characters or common hallucination artifacts (e.g., `"Thank you for watching"`, `"[Music]"`).

### 4.3 LLM Reasoning Backend
- **Endpoint:** Ollama REST API (`POST http://localhost:11434/api/generate` or `/api/chat`).
- **Target Model:** `qwen2.5:3b` (Default) or `phi4-mini`.
- **Inference Constraints:**
  - `temperature`: `0.2` to `0.3` (deterministic, low latency).
  - `num_predict`: `60` to `80` tokens max.
- **System Prompt Specification:**
  ```text
  You are an expert, real-time debate analysis engine named aenf. 
  Your job is to identify logical fallacies, faulty premises, or rhetorical tricks in the user's opponent's speech and formulate an immediate, razor-sharp rebuttal.

  RULES:
  1. Do NOT summarize or engage in conversational filler.
  2. Maximum 35 words total.
  3. Output strictly in the following format:
     • Flaw: <Name of fallacy or factual/logical gap>
     • Counter: <Direct, impactful 1-sentence counter-argument>
  ```

### 4.4 HUD Overlay (PyQt6)
- **Window Flags:**
  - `Qt.WindowType.FramelessWindowHint`
  - `Qt.WindowType.WindowStaysOnTopHint`
  - `Qt.WindowType.Tool` or `SubWindow` (to avoid taskbar clutter).
- **Attributes:**
  - `Qt.WidgetAttribute.WA_TranslucentBackground`
- **Visual Design:**
  - Dark glassmorphism card (`background-color: rgba(18, 18, 24, 0.88)`).
  - Subtle glowing border (`border: 1px solid rgba(255, 255, 255, 0.12)`).
  - Rounded corners (`border-radius: 10px`).
  - Text: High-contrast monospace or clean sans-serif (e.g., `#A0A0B0` for transcript, `#00FFA3` or `#FF5C5C` for detected flaws).
- **Interactions:**
  - Draggable via mouse click-and-drag.
  - Collapse / Minimize toggle button.
  - Optional opacity slider or toggle for hotkey click-through.

---

## 5. Implementation Code Structure

When implementing the application into a single file or modular repository, follow this directory and module structure:

```text
aenf/
├── README.md
├── requirements.txt
├── config.py             # Audio device settings, Ollama endpoint, model name
├── core/
│   ├── __init__.py
│   ├── audio_capture.py  # sounddevice callback + thread-safe queue
│   ├── vad.py            # RMS silence/speech detection
│   ├── transcriber.py    # faster-whisper CPU worker
│   └── llm_client.py     # Ollama REST query worker
└── ui/
    ├── __init__.py
    └── overlay.py        # PyQt6 HUD interface and signal handlers
```

*(Alternatively, for single-file deployment, consolidate all modules into `aenf.py` using Qt's `QThread` or Python `threading.Thread` with thread-safe `pyqtSignal` events).*

---

## 6. Threading & Concurrency Invariants

1. **GUI Thread (Thread 0):** Only handles PyQt rendering, paint events, and window movement. Never perform network requests or inference here.
2. **Audio Recorder Thread:** Continuously reads audio buffers from `sounddevice` and pushes frames into a thread-safe `queue.Queue()`.
3. **STT & LLM Pipeline Thread:** Pops audio buffers, runs `faster-whisper` transcription, sends HTTP requests to Ollama, and dispatches UI updates via `pyqtSignal(str, str)`.

---

## 7. Edge Cases & Safeguards

- **OLLAMA Not Running:** Catch `requests.exceptions.ConnectionError`. Display a clear warning on the HUD (`"Ollama offline. Run: ollama run qwen2.5:3b"`).
- **Audio Device Disconnect:** Catch `sounddevice.PortAudioError` and retry initialization gracefully.
- **Model Hallucination on Silence:** Enforce RMS thresholding before invoking Whisper. Discard audio frames with energy lower than baseline background noise.
- **Context Flooding:** Discard previous uncompleted LLM requests if a new distinct argument arrives, or use a queue with `maxsize=1` (drop older frames to preserve real-time responsiveness).

---

## 8. Verification Checklist for the AI Builder

- [ ] Does STT run exclusively on CPU with INT8 compute?
- [ ] Does the overlay stay on top when focusing other windows (e.g., browser, Discord)?
- [ ] Is total VRAM consumption strictly under 3.0 GB during active inference?
- [ ] Does the system recover cleanly without hanging if Ollama takes $> 5$ seconds to respond?
- [ ] Is speech correctly parsed without blocking the UI frame rate?