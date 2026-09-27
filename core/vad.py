"""Voice Activity Detection and dynamic speech segmentation using energy RMS."""

import time
import numpy as np
from config import Config


def compute_rms(audio_chunk: np.ndarray) -> float:
    """Calculate Root Mean Square (RMS) energy of an audio chunk."""
    if audio_chunk.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(audio_chunk, dtype=np.float32))))


class DynamicVAD:
    """Buffers stream slices and yields completed speech segments using sample-accurate timing."""

    def __init__(self, config: Config):
        self.config = config
        self.sample_rate = config.sample_rate
        self.rms_threshold = config.vad_rms_threshold
        self.silence_duration_s = config.vad_silence_duration_s
        self.min_speech_duration_s = config.vad_min_speech_duration_s
        self.max_speech_duration_s = config.vad_max_speech_duration_s

        # Rolling pre-roll buffer (~300ms) to avoid clipping start of utterances
        self.preroll_chunks: list[np.ndarray] = []
        self.max_preroll_chunks = max(1, int(0.3 / (config.chunk_ms / 1000.0)))

        # Active speech buffer
        self.active_buffer: list[np.ndarray] = []
        self.is_speaking = False
        self.consecutive_silence_s = 0.0
        self.total_speech_s = 0.0

    def process_chunk(self, chunk: np.ndarray) -> tuple[np.ndarray | None, float, bool]:
        """
        Process incoming audio chunk (float32 array).
        Returns:
            (completed_speech_segment or None, current_rms, is_speaking)
        """
        rms = compute_rms(chunk)
        chunk_s = len(chunk) / float(self.sample_rate) if self.sample_rate > 0 else 0.0
        completed_segment: np.ndarray | None = None

        is_voice = rms >= self.rms_threshold

        if is_voice:
            if not self.is_speaking:
                # Speech triggered
                self.is_speaking = True
                self.consecutive_silence_s = 0.0
                self.total_speech_s = 0.0
                # Prepend pre-roll buffer
                self.active_buffer = list(self.preroll_chunks)
            self.active_buffer.append(chunk)
            self.total_speech_s += chunk_s
            self.consecutive_silence_s = 0.0
        else:
            if self.is_speaking:
                # In speech, but current slice is quiet
                self.active_buffer.append(chunk)
                self.consecutive_silence_s += chunk_s
                self.total_speech_s += chunk_s

                # Check if silence exceeded threshold or max length reached
                if self.consecutive_silence_s >= self.silence_duration_s or self.total_speech_s >= self.max_speech_duration_s:
                    if self.total_speech_s >= self.min_speech_duration_s and self.active_buffer:
                        completed_segment = np.concatenate(self.active_buffer, axis=0)
                    # Reset state
                    self.is_speaking = False
                    self.active_buffer = []
                    self.consecutive_silence_s = 0.0
                    self.total_speech_s = 0.0
            else:
                # In idle silence: maintain rolling pre-roll buffer
                self.preroll_chunks.append(chunk)
                if len(self.preroll_chunks) > self.max_preroll_chunks:
                    self.preroll_chunks.pop(0)

        # Force flush if speech exceeds maximum allowed duration
        if self.is_speaking and self.total_speech_s >= self.max_speech_duration_s:
            if self.active_buffer:
                completed_segment = np.concatenate(self.active_buffer, axis=0)
            self.is_speaking = False
            self.active_buffer = []
            self.consecutive_silence_s = 0.0
            self.total_speech_s = 0.0

        return completed_segment, rms, self.is_speaking
