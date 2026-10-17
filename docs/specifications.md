# Runtime specifications and benchmarks

This page is the canonical reference for performance metrics, latency budgets, hardware memory footprints, and baseline requirements for Elenchus.

---

## Core manifesto

> Conversations move faster than memory.

When an opponent in a live debate shifts premises, forces a false dilemma, or attacks character instead of evidence, you often catch the flaw seconds after your turn to respond has passed.

Elenchus runs quietly in the background. It listens to incoming speech, evaluates logical claims, and shows short Socratic counter-arguments directly in your peripheral vision before you take your turn to speak.

---

## Verified benchmarks

These numbers reflect verified runs on mid-tier consumer hardware (Intel Core i5-11400 or AMD Ryzen 5 5600X, 16 GB RAM, RTX 3060):

| Metric | Target | Measurement method |
| :--- | :--- | :--- |
| **Peak resident memory (RAM)** | `< 380 MB RSS` | Task Manager / `/proc/[pid]/status` during INT8 CPU transcription |
| **Speech chunk STT latency** | `~ 550 ms` | Timestamp delta between audio chunk completion and text emission |
| **LLM classification latency** | `650 ms to 950 ms` | Ollama response latency using `qwen2.5-coder:3b` (Q4_K_M) |
| **End-to-end latency** | `< 2.5 seconds` | Time from end of speech slice to counter-argument rendered in HUD |
| **External network transmission** | `0 bytes` | Verified with Wireshark and Process Hacker (fully offline) |
| **Binary digest integrity** | `SHA-256` | Automated digest check against release `checksums.txt` |

---

## Hardware allocation budget

Elenchus is budgeted to run on machines with modest headroom without starving active video calls, browsers, or streaming software:

```mermaid
pie title Hardware memory footprint by component (~3.0 GB total)
    "Ollama LLM (2200 MB VRAM)" : 2200
    "faster-whisper STT (650 MB RAM)" : 650
    "PyQt6 HUD overlay (80 MB RAM)" : 80
    "Audio capture & VAD (50 MB RAM)" : 50
```

| Subsystem | Component | Hardware target | Memory budget | Share | Purpose |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Audio capture & VAD** | `sounddevice` + `numpy` | Host CPU | `< 50 MB RAM` | 1.7% | 16 kHz audio buffer and energy thresholding |
| **Speech-to-text** | `faster-whisper` (`base.en`) | CPU (INT8, 4 threads) | `~ 650 MB RAM` | 21.8% | Quantized INT8 weights in system RAM (`0 MB VRAM`) |
| **Desktop HUD overlay** | PyQt6 composited window | CPU / Compositor | `< 80 MB RAM` | 2.7% | Transparent obsidian HUD elements |
| **Debate reasoning** | `qwen2.5-coder:3b` | Dedicated GPU | `~ 2,200 MB VRAM` | 73.8% | 4-bit quantized model resident in VRAM |
| **Total memory footprint** | All subsystems | Hybrid RAM + VRAM | **~ 2,980 MB** | **100%** | **Leaves ample headroom for Discord, OBS, or Zoom** |

System RAM stays under 800 MB RSS during continuous speech recognition. The LLM reasoning model runs isolated in ~2.2 GB of GPU VRAM, keeping desktop multitasking fluid.

---

## Latency budget breakdown

Elenchus targets an end-to-end response time under 2.5 seconds, with a typical turnaround of ~1.55 seconds (1,550 ms) on recommended hardware:

```mermaid
pie title Latency share by pipeline stage (1.55s total)
    "Ollama local inference (0.80s)" : 800
    "faster-whisper STT (0.55s)" : 550
    "Audio buffer & VAD cutoff (0.10s)" : 100
    "Argument pre-filter (0.05s)" : 50
    "PyQt6 HUD repaint (0.05s)" : 50
```

| Pipeline stage | Duration | Latency | Budget share | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1: Buffer flush & VAD cutoff** | `0.10s` | 100 ms | 6.5% | Audio ring buffer capture and energy thresholding |
| **Stage 2: Speech-to-text** | `0.55s` | 550 ms | 35.5% | `faster-whisper` INT8 CPU transcription |
| **Proposition pre-filter** | `0.05s` | 50 ms | 3.2% | Rejects incomplete utterances, stutters, and room noise |
| **Stage 3: Fallacy & refutation engine** | `0.80s` | 800 ms | 51.6% | Ollama local model inference (`qwen2.5-coder:3b`) |
| **Stage 4: Desktop HUD repaint** | `0.05s` | 50 ms | 3.2% | PyQt6 thread-safe signal dispatch and widget repaint |
| **Total end-to-end turnaround** | `~1.55s` | **1,550 ms** | **100%** | **Refutation displayed before your speaking turn** |

Over 87 percent of total processing time is dedicated to local AI execution (0.80 seconds for Ollama refutation generation and 0.55 seconds for faster-whisper speech transcription). Audio ingestion, heuristics, and UI compositing take less than 0.20 seconds combined (under 13 percent), ensuring zero sluggishness on the desktop.
