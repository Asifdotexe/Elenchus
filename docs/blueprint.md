# Version scopes and roadmap

This document defines scope boundaries and milestone deliverables for each version of Elenchus under [Semantic Versioning](https://semver.org/).

Historical release notes, commit logs, and downloadable assets are published on [GitHub Releases](https://github.com/Asifdotexe/elenchus/releases).

---

## Version index

| Version | Milestone | Status | Scope summary |
| :--- | :--- | :--- | :--- |
| **v1.0.0** | Core engine and desktop HUD | Stable | Offline speech recognition, Ollama fallacy reasoning, and floating PyQt6 HUD overlay. |
| **v1.1.0** | Standalone binary distribution | In progress | Zero-dependency standalone executables for Windows, macOS, and Linux with automated release packaging. |
| **v1.2.0** | Extended debate analytics | Planned | Multi-speaker recording sessions up to 30 minutes, full transcript analysis, and personal fallacy trends. |

---

## v1.0.0: Core engine and desktop HUD (stable)

The initial release establishes the local sparring loop. You speak (or route incoming call audio), the engine transcribes the claim on CPU, checks for logical fallacies locally, and displays a concise counter-argument in the overlay.

### Scope boundaries
- Audio input records 16 kHz mono streams from default microphones or system loopback (WASAPI on Windows, PulseAudio or PipeWire on Linux).
- Voice detection supports manual push-to-talk toggling and automated RMS energy detection with silence timeouts.
- Speech transcription runs on CPU via `faster-whisper` using INT8 quantization, using zero GPU memory.
- A heuristic pre-filter drops conversational filler, mid-sentence pauses, and coughs before calling the model.
- Fallacy reasoning runs locally through Ollama using `qwen2.5-coder:3b`, returning classifications and refutations under 30 words.
- The interface is a frameless, translucent PyQt6 desktop overlay with real-time audio meters and status lights.
- Developers can clone and run the project directly using Astral `uv` (`uv run elenchus`).

### Excluded from v1.0.0
This milestone does not include standalone compiled installers without Python, continuous multi-speaker transcripts across long sessions, or remote cloud model synchronization.

Full patch notes and release artifacts are documented on [GitHub Release v1.0.0](https://github.com/Asifdotexe/elenchus/releases).

---

## v1.1.0: Standalone binary distribution (in progress)

The second milestone eliminates developer tool dependencies so anyone can install and run Elenchus with a single double-click or terminal command.

### Scope boundaries
- Standalone executables for Windows (`x86_64`), macOS (`arm64` and `x86_64`), and Linux (`x86_64`) that run without Python preinstalled.
- Automated GitHub Actions workflows that compile release binaries, compute SHA-256 digests, and attach assets to tagged release drafts.
- Single-command web installers for PowerShell and Bash that verify hashes and place the binary on the user path.
- Initial groundwork for native distribution channels (winget, Scoop, Homebrew, and Flatpak).

### Excluded from v1.1.0
Long debate recording sessions remain scheduled for v1.2.0. This release avoids UI overhauls to focus entirely on distribution and packaging reliability.

---

## v1.2.0: Extended debate analytics (planned)

The third milestone expands Elenchus from real-time single-claim sparring into comprehensive debate session analysis.

### Scope boundaries
- Long-format audio ingestion accepting up to 30 minutes of recorded debate audio, generating per-statement fallacy breakdowns.
- Opponent audio isolation to analyze both speakers separately during Discord or browser conference calls.
- Optional integration with macOS's built-in speech engine for lower memory usage on Apple Silicon.
- A local fallacy history tracker that identifies recurring cognitive patterns across multiple sessions.

---

## Release notes and changelog

Granular patch notes, commit logs, and bug fixes are maintained on [GitHub Releases](https://github.com/Asifdotexe/elenchus/releases). This document tracks scope boundaries and planning targets only.
