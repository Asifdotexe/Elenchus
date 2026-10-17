<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/branding/kit/elenchus-symbol-white.svg">
    <source media="(prefers-color-scheme: light)" srcset="assets/branding/kit/elenchus-symbol-black.svg">
    <img alt="Elenchus (ἔλεγχος)" src="assets/branding/kit/elenchus-symbol-white.svg" width="140" height="140">
  </picture>

  <h1>Elenchus (ἔλεγχος)</h1>

  <p>
    <strong>Real-time Socratic debate analysis and fallacy detection engine.</strong><br>
    <em>100% offline. Local Whisper speech-to-text and Ollama reasoning rendered over your desktop.</em>
  </p>

  <p>
    <a href="https://github.com/Asifdotexe/elenchus/actions/workflows/ci.yml"><img src="https://github.com/Asifdotexe/elenchus/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
    <a href="https://asifdotexe.github.io/elenchus/docs/"><img src="https://img.shields.io/badge/docs-mkdocs-101010?style=flat&logo=materialformkdocs&logoColor=white" alt="Documentation"></a>
    <a href="https://asifdotexe.github.io/elenchus/"><img src="https://img.shields.io/badge/website-live-101010?style=flat&logo=safari&logoColor=white" alt="Website"></a>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.12-101010?style=flat&logo=python&logoColor=white" alt="Python 3.12"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-101010?style=flat" alt="MIT License"></a>
  </p>

  <p>
    <a href="https://asifdotexe.github.io/elenchus/"><strong>Website</strong></a> &nbsp;•&nbsp;
    <a href="https://asifdotexe.github.io/elenchus/docs/"><strong>Documentation</strong></a> &nbsp;•&nbsp;
    <a href="https://asifdotexe.github.io/elenchus/#simulator"><strong>Interactive HUD Demo</strong></a> &nbsp;•&nbsp;
    <a href="https://asifdotexe.github.io/elenchus/docs/installation/"><strong>Installation Guide</strong></a> &nbsp;•&nbsp;
    <a href="assets/branding/BRAND_GUIDELINES.md"><strong>Brand Guidelines</strong></a>
  </p>
</div>

---

> **/ɪˈlɛŋ.kəs/** (Ancient Greek: **ἔλεγχος**, *elenchos*): The Socratic method of dialectical inquiry. Examining claims to test logical consistency, expose fallacies, and surface direct counter-arguments.

**Elenchus** is a privacy-first, offline debate assistant designed for live conversations, panel discussions, and recorded speech. It continuously monitors audio, extracts discrete claims, isolates rhetorical fallacies, and delivers concise, one-sentence Socratic rebuttals on a translucent, always-on-top desktop Heads-Up Display (HUD).

Engineered to run entirely on consumer hardware (8 GB RAM, 4 GB GPU VRAM) with zero data leaving your machine.

---

## Quick Install

### Standalone Executable (No Python Required)

**Windows (PowerShell):**
```powershell
irm https://github.com/Asifdotexe/elenchus/releases/latest/download/install.ps1 | iex
```

**macOS / Linux:**
```bash
curl -fsSL https://github.com/Asifdotexe/elenchus/releases/latest/download/install.sh | bash
```

Once installed, run `elenchus` from any terminal.

> For developer source builds (Astral `uv`), package manager status (Winget, Scoop, Homebrew, AUR), and cryptographic SHA-256 checksums, visit the [Installation & Packaging Guide](https://asifdotexe.github.io/elenchus/docs/installation/).

---

## Documentation

Full architectural specifications, hardware benchmarks, user guides, and release roadmaps are maintained at **[asifdotexe.github.io/elenchus/docs/](https://asifdotexe.github.io/elenchus/docs/)**.

| Section | Description |
| :--- | :--- |
| **[Philosophy & Principles](https://asifdotexe.github.io/elenchus/docs/philosophy/)** | Socratic dialectic ethos, real-time debate ergonomics, and privacy-first local AI. |
| **[System Architecture](https://asifdotexe.github.io/elenchus/docs/architecture/)** | Asynchronous IPC pipeline, threading topology, and security boundary isolation. |
| **[Specifications & Benchmarks](https://asifdotexe.github.io/elenchus/docs/specifications/)** | Hardware resource allocation budgets (VRAM/RAM) and 1.55s end-to-end latency breakdown. |
| **[Installation & Packaging](https://asifdotexe.github.io/elenchus/docs/installation/)** | Native binaries, Astral `uv` setup, package manager roadmap, and airgapped flags. |
| **[User Guide & CLI Reference](https://asifdotexe.github.io/elenchus/docs/user-guide/)** | HUD overlay controls, push-to-talk shortcuts, audio loopback configuration, and CLI commands. |
| **[Milestone Blueprint](https://asifdotexe.github.io/elenchus/docs/blueprint/)** | Version scopes, historical development milestones, and release scope tracking. |

---

## Development

```bash
# Clone repository
git clone https://github.com/Asifdotexe/elenchus.git
cd elenchus

# Run automated unit tests
uv run python -m unittest tests/test_core.py

# Run ruff code linter & formatter
uv run ruff check .
uv run ruff format --check
```

See the [User Guide](https://asifdotexe.github.io/elenchus/docs/user-guide/) for complete development environment setup and dependency configuration.

---

## Security & Airgap Guarantee

- **Zero Cloud Transmission**: Speech audio and model inference run 100% locally on localhost.
- **Prompt Injection Defense**: Speech transcripts are strictly isolated within structural `<opponent_statement>` boundaries.
- **RichText Injection Immunity**: HUD labels enforce `Qt.TextFormat.PlainText` preventing HTML execution.
- **Cryptographic Verification**: Release scripts verify SHA-256 digests prior to installation.

See [Security Posture](https://asifdotexe.github.io/elenchus/docs/architecture/#6-security-posture-airgap-verification) for technical verification commands.

---

## License

Elenchus is open-source software licensed under the [MIT License](LICENSE).
