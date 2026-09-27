"""Speech-to-Text transcriber using faster-whisper on CPU (INT8)."""

import logging
import re
import numpy as np
from faster_whisper import WhisperModel

from config import Config

logger = logging.getLogger(__name__)


class Transcriber:
    """CPU-only INT8 faster-whisper transcriber."""

    def __init__(self, config: Config):
        self.config = config
        logger.info(
            "Loading faster-whisper model '%s' on %s (%s)...",
            config.whisper_model,
            config.whisper_device,
            config.whisper_compute_type,
        )
        self.model = WhisperModel(
            config.whisper_model,
            device=config.whisper_device,
            compute_type=config.whisper_compute_type,
            cpu_threads=4,
        )
        self.last_transcript = ""

    def transcribe(self, audio: np.ndarray) -> str | None:
        """
        Transcribe speech audio segment (float32, 16kHz).
        Returns validated transcript or None if invalid/hallucinated.
        """
        if audio is None or len(audio) < int(self.config.sample_rate * 0.3):
            return None

        try:
            segments, info = self.model.transcribe(
                audio,
                beam_size=self.config.whisper_beam_size,
                language="en",
                vad_filter=False,  # We already did custom energy VAD
            )
            raw_text = " ".join(seg.text for seg in segments).strip()
            return self._validate_and_clean(raw_text)
        except Exception as e:
            logger.error("Whisper transcription error: %s", e)
            return None

    def _validate_and_clean(self, text: str) -> str | None:
        """Validate transcript length, strip hallucinations and formatting artifacts."""
        if not text:
            return None

        # Clean multiple spaces and whitespace
        cleaned = re.sub(r"\s+", " ", text).strip()
        lower = cleaned.lower()

        # Check minimum character length
        if len(cleaned) < self.config.min_transcript_len:
            logger.debug("Discarding short transcript (<%d chars): '%s'", self.config.min_transcript_len, cleaned)
            return None

        # Discard known hallucination phrases
        for phrase in self.config.hallucination_phrases:
            if lower == phrase or lower.startswith(phrase + ".") or lower.startswith(phrase + "!"):
                logger.debug("Discarding hallucination: '%s'", cleaned)
                return None

        # Check deduplication against immediately prior transcript
        if cleaned == self.last_transcript:
            logger.debug("Discarding duplicate transcript: '%s'", cleaned)
            return None

        self.last_transcript = cleaned
        return cleaned
