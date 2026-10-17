# Elenchus (ἔλεγχος)

> Real-time Socratic debate analysis and fallacy detection engine for live conversations and recorded speech.

Elenchus runs on your local machine. It listens to desktop audio or microphone input, transcribes spoken statements with `faster-whisper`, spots logical fallacies with a local LLM through Ollama, and displays short refutations in a translucent desktop HUD.

<a href="../" class="elenchus-home-link">
  <span>← Return to Main Website & Live Simulator</span>
</a>

---

## Highlights

- **Offline and private**: Audio transcription and reasoning run locally in volatile memory with zero external network requests.
- **Low latency**: Local CPU speech recognition paired with quantized language models for real-time turnarounds during live speech.
- **Desktop HUD**: Frameless, translucent desktop overlay that stays visible above active windows without stealing input focus.
- **Rhetorical pre-filtering**: Discards conversational filler, background noise, and incomplete utterances before fallacy evaluation.
- **Cross-platform**: Prebuilt standalone packages and quick-start scripts across Windows, macOS, and Linux.

---

## Documentation sections

- [Design philosophy and origins](philosophy.md)
- [Installation and distribution](installation.md)
- [System architecture](architecture.md)
- [Runtime specifications](specifications.md)
- [User guide and HUD controls](user-guide.md)
- [Version scopes and roadmap](blueprint.md)
