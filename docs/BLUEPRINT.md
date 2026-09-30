# Elenchus Technical Blueprint

> Socratic debate analysis and fallacy detection engine for live interactions and recorded speech.

This document tracks milestone releases, core MVP requirements, hardware constraints, and Definition of Done (DoD) criteria for each version of Elenchus using [Semantic Versioning](https://semver.org/).

For permanent system design and threading specifications, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## Version Index

| Version | Milestone Name | Status | Summary |
| :--- | :--- | :--- | :--- |
| **v1.0.0** | **Core Engine & Desktop HUD** | **Active / Implemented** | Low-latency audio ingestion, CPU STT, local LLM fallacy inference, and dark frameless HUD. |

---

## Milestone Template

Use this template to draft future release milestones (`vX.Y.Z`):

```markdown
## vX.Y.Z - [Milestone Name]

### 1. Goals & Scope
- Core purpose, target users, and boundaries of the release.

### 2. MVP Requirements
- List of functional features required for release readiness.

### 3. Constraints & Hardware Budget
- Target memory, compute, and latency limits.

### 4. Definition of Done (DoD)
- Objective verification and acceptance criteria.
```

---

## v1.0.0 - Core Engine & Desktop HUD

### 1. Goals & Scope
- Build a mode-agnostic Socratic fallacy detection core paired with a minimal, dark desktop heads-up display (HUD).
- Enable users to capture spoken claims, detect informal logical fallacies, and view immediate one-sentence counter-arguments.
- Ensure the pipeline runs completely offline on consumer hardware with strict resource isolation.

### 2. MVP Requirements
- **Audio Capture:** Ingest audio from default microphones or virtual loopback devices (e.g., Discord or browser streams) at 16 kHz mono.
- **Voice Activity Detection (VAD):** Dual-mode audio segmentation:
  - *Manual Push-to-Talk (Default):* Start listening on demand and cut immediately on stop.
  - *Continuous Automatic VAD:* Energy-based RMS detection with dynamic noise-floor tracking and silence timeouts.
- **Speech Recognition:** CPU-based speech transcription via `faster-whisper` (`base.en`, INT8 quantization).
- **Rhetorical Pre-Filtering:** Filter out non-arguments (filler phrases, incomplete clauses, coughs) before LLM invocation.
- **Socratic Reasoning Engine:** Local LLM inference via Ollama (`qwen2.5-coder:3b` or `qwen2.5:3b`) identifying the exact fallacy (if any) and a direct one-sentence counter-argument under 30 words.
- **Minimalist HUD Overlay:** PyQt6 frameless, translucent, draggable card pinned on top of active windows with audio level metering, mode toggling, and collapsible views.
- **Developer Tooling & Distribution:** Single-command setup (`setup.ps1` / `setup.sh`), zero-config execution (`uv run elenchus`), and pre-commit test automation.

### 3. Constraints & Hardware Budget

Designed to operate on modest hardware (8 GB system RAM and 4 GB GPU VRAM) without swapping:

| Subsystem | Component / Engine | Hardware Allocation | Memory & Compute Budget |
| :--- | :--- | :--- | :--- |
| **Speech-to-Text** | `faster-whisper` (`base.en`) | CPU (INT8, 4 threads) | 500 MB – 1.0 GB RAM, 0 MB VRAM |
| **Debate Reasoning** | `qwen2.5-coder:3b` via Ollama | GPU (4-bit Q4_K_M) | 2.0 – 2.4 GB VRAM |
| **Audio Capture & VAD** | `sounddevice` + `numpy` RMS | CPU | < 50 MB RAM |
| **HUD Overlay** | PyQt6 frameless composited card | CPU / Window Compositor | < 80 MB RAM |
| **Host System & Desktop** | Windows 10/11 or Linux X11/Wayland | Host OS | Remaining RAM / VRAM headroom |

- **Latency Budget:** Under 3.0 seconds from speech completion to rendered counter-argument on screen.
- **Offline Autonomy:** Zero external network calls during execution. Complete local privacy.

### 4. Definition of Done (DoD) - v1.0.0
- [x] Zero GPU VRAM consumption for speech recognition (verified on CPU INT8).
- [x] Peak GPU VRAM during active inference remains under 2.5 GB.
- [x] Frameless HUD stays pinned above fullscreen-focused third-party applications (Discord, browsers).
- [x] Non-arguments, stutter, and conversational filler are classified accurately without false positive fallacy tags.
- [x] Offline Ollama service failure renders a clean status warning without UI freezes.
- [x] Full test suite (`tests/test_core.py`) passes cleanly across Windows and Linux platforms.
- [x] All repository code passes `prek run --all-files` (Ruff linter and formatter).
- [x] CLI launches reliably via `uv run elenchus`.
