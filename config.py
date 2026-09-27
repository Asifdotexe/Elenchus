"""Configuration settings for aenf (all ears no foul)."""

import os
from dataclasses import dataclass

@dataclass
class Config:
    # Audio capture
    sample_rate: int = 16000
    channels: int = 1
    chunk_ms: int = 100  # slice size for audio callback (100 ms)
    audio_device: int | str | None = None  # None = default input

    # Voice Activity Detection (RMS energy-based dynamic chunking)
    vad_rms_threshold: float = 0.012  # baseline RMS threshold for speech
    vad_silence_duration_s: float = 0.7  # silence required to commit buffer (600-800 ms)
    vad_min_speech_duration_s: float = 0.6  # minimum speech to trigger Whisper
    vad_max_speech_duration_s: float = 5.0  # max buffer duration before forced commit

    # Speech to Text (faster-whisper on CPU)
    whisper_model: str = "base.en"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"
    whisper_beam_size: int = 1
    min_transcript_len: int = 15

    # Known Whisper hallucination phrases to drop
    hallucination_phrases: tuple = (
        "thank you for watching",
        "thanks for watching",
        "thank you",
        "subscribe to my channel",
        "[music]",
        "(music)",
        "[applause]",
        "[silence]",
        "you",
        "bye",
    )

    # Ollama LLM Reasoning
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("AENF_MODEL", "qwen2.5-coder:3b")
    ollama_temperature: float = 0.25
    ollama_num_predict: int = 80
    ollama_timeout_s: float = 12.0

    system_prompt: str = (
        "You are an expert, real-time debate analysis engine named aenf.\n"
        "Your job is to identify logical fallacies, faulty premises, or rhetorical tricks "
        "in the user's opponent's speech, or recognize when no actual argument has been made.\n\n"
        "CRITICAL RULES:\n"
        "1. ARGUMENT THRESHOLD: A logical fallacy ONLY exists in an argument that has premises and an inferred conclusion.\n"
        "2. INCOMPLETE / NON-ARGUMENT: If the statement is incomplete, an interjection, conversational filler, "
        "casual remark, simple question, or lacks both a premise and conclusion, DO NOT invent a fallacy.\n"
        "   Output strictly:\n"
        "   • Flaw: None (Incomplete / Non-Argument)\n"
        "   • Counter: Statement lacks premises or conclusion to evaluate.\n"
        "3. VALID STATEMENT: If the statement is coherent and has no fallacy:\n"
        "   • Flaw: None (Valid claim)\n"
        "   • Counter: <1-sentence counter-perspective or fact-check>\n"
        "4. WHEN FALLACY EXISTS:\n"
        "   • Flaw: <Exact Fallacy Name>\n"
        "   • Counter: <Direct, impactful 1-sentence counter-argument>\n"
        "5. Maximum 30 words total. No pleasantries."
    )

    # Operation mode: manual button trigger (True) vs continuous VAD (False)
    manual_mode: bool = True

    # UI appearance
    window_width: int = 420
    window_height: int = 280
    opacity: float = 0.94


DEFAULT_CONFIG = Config()
