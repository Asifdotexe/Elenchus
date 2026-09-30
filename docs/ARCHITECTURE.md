# Elenchus System Architecture

This document specifies the permanent system design decisions, data flow pipeline, threading model, and resilience strategies for Elenchus.

---

## 1. High-Level Architecture

Elenchus separates concerns into discrete, decoupled layers: audio ingestion, voice activity detection, speech recognition, rhetorical filtering, reasoning inference, and presentation.

```text
[Audio Input: Mic or Loopback Stream]
              │
              ▼
[Sample Buffer & RMS VAD]  ◄── Audio Activity Signal (PyQt)
              │ (discrete speech slice)
              ▼
[faster-whisper CPU Worker]
              │ (normalized transcript string)
              ▼
[Argument Pre-Filter] ─────► (bypasses LLM if incomplete or conversational filler)
              │ (substantive claim)
              ▼
[Ollama Local REST API] ───► Fallacy + Direct Socratic Counter-Argument
              │
              ▼
[Pipeline Coordinator]
              │ (thread-safe signal dispatch)
              ▼
[Elenchus HUD Overlay]
```

---

## 2. Subsystem Responsibilities

| Subsystem | Component / Module | Responsibility |
| :--- | :--- | :--- |
| **Audio Ingestion** | `core.audio_capture` | Captures raw float32 audio blocks from physical microphones or virtual loopback devices (e.g., Discord or browser streams). |
| **Voice Activity Detection** | `core.vad` | Computes sample-accurate RMS energy, dynamically tracks noise floor, and handles both push-to-talk slices and auto silence cutting. |
| **Speech-to-Text** | `core.transcriber` | Executes CPU-based INT8 transcription with beam size 1 using `faster-whisper`, dropping repeated phrases and hallucinated filler. |
| **Argument Pre-Filter** | `core.llm_client` | Evaluates whether a transcript constitutes a complete proposition before invoking the language model, preventing false-positive fallacy flags on interjections. |
| **Reasoning Engine** | `core.llm_client` | Queries the local Ollama instance (`qwen2.5-coder:3b` or `qwen2.5:3b`) with concise Socratic refutation prompts. |
| **Pipeline Coordination** | `core.pipeline` | Background `QThread` orchestrating the worker pipeline without blocking GUI responsiveness. |
| **Desktop HUD Overlay** | `ui.overlay` | Draggable, frameless, translucent PyQt6 heads-up display with Lucide vector icons and Monochart audio metering. |

---

## 3. Concurrency & Thread Isolation

To guarantee responsive UI rendering and stutter-free audio capture under heavy CPU/GPU load, Elenchus maintains three isolated execution contexts:

1. **Thread 0 (UI Thread):**
   - Owns the Qt event loop, paint events, window dragging, and user mouse/key interactions.
   - Never blocks on network calls, disk I/O, or model inference.
   - Receives state updates exclusively through thread-safe Qt signals (`result_ready`, `audio_level`, `status_changed`).

2. **Audio Recorder Thread:**
   - High-priority stream callback initiated by `sounddevice`.
   - Continuously pulls audio blocks from the hardware buffer and enqueues them into a thread-safe queue.
   - Performs no heavy computation in the callback path to prevent buffer overflows or dropouts.

3. **Pipeline Coordinator (`QThread`):**
   - Consumes raw audio blocks from the queue.
   - Runs sample-accurate RMS calculations and VAD state transitions.
   - Executes CPU transcription in `faster-whisper`.
   - Dispatches HTTP requests to the Ollama daemon on `localhost:11434`.
   - Emits structured results to the UI thread.

---

## 4. Fault Tolerance & Resilience

- **Sample Rate Auto-Negotiation:**
  Audio hardware often defaults to 44.1 kHz or 48 kHz (especially under Windows WASAPI). The ingestion layer queries the device's native sample rate and resamples in memory to 16 kHz using linear interpolation, preventing pitch distortion and sample rate mismatches.

- **Ollama Service Resilience:**
  If the Ollama daemon is offline or crashes, network exceptions are caught gracefully. The HUD displays an actionable status warning without crashing the application or freezing the interface.

- **Inference Latency Guard:**
  Inference requests that exceed 10 seconds are aborted with a timeout notice to ensure the application maintains real-time pacing.

- **Clean Teardown:**
  When the application window is closed, `closeEvent` explicitly stops worker threads, releases PortAudio device descriptors, terminates child tasks, and exits the event loop cleanly to avoid orphaned background processes.
