"""Asynchronous processing pipeline linking Audio, VAD, Transcriber, and LLM."""

import logging
import threading
import time

import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from config import Config
from core.audio_capture import AudioCapture
from core.llm_client import OllamaClient
from core.transcriber import Transcriber
from core.vad import DynamicVAD, compute_rms

logger = logging.getLogger(__name__)


class PipelineWorker(QThread):
    """
    Background QThread running audio ingestion, manual/automatic VAD, transcription, and debate reasoning.
    Communicates with HUD via PyQt signals.
    """

    # Signals for UI:
    status_changed = pyqtSignal(str, str)
    audio_level = pyqtSignal(float, bool)
    transcript_received = pyqtSignal(str)
    rebuttal_received = pyqtSignal(str, str, float)
    recording_state_changed = pyqtSignal(bool)  # True = recording, False = idle

    def __init__(self, config: Config):
        """Initialize pipeline worker thread and sub-components.

        :param config: Application configuration instance.
        """
        super().__init__()
        self.config = config
        self.running = False
        self.manual_mode = config.manual_mode
        self.audio_capture = AudioCapture(config)
        self.vad = DynamicVAD(config)
        self.transcriber: Transcriber | None = None
        self.llm_client: OllamaClient | None = None

        # Manual recording control
        self._lock = threading.Lock()
        self.is_manual_recording = False
        self.manual_buffer: list[np.ndarray] = []
        self._flush_requested = False

    def toggle_manual_capture(self) -> bool:
        """Toggle manual listening on or off.

        :return: True if recording started, False if recording stopped and queued for analysis.
        """
        with self._lock:
            if not self.is_manual_recording:
                # Start recording
                self.manual_buffer = []
                self.is_manual_recording = True
                self.recording_state_changed.emit(True)
                self.status_changed.emit("Listening to opponent...", "busy")
                return True
            else:
                # Stop recording and request immediate analysis
                self.is_manual_recording = False
                self._flush_requested = True
                self.recording_state_changed.emit(False)
                self.status_changed.emit("Cutting & transcribing...", "busy")
                return False

    def set_mode(self, manual: bool) -> None:
        """Switch between Manual Button mode and Auto VAD mode.

        :param manual: True for manual push-to-listen button mode, False for automatic VAD.
        """
        with self._lock:
            self.manual_mode = manual
            self.is_manual_recording = False
            self.manual_buffer = []
            self.recording_state_changed.emit(False)
            mode_str = "Manual (Click to Listen)" if manual else "Auto VAD"
            self.status_changed.emit(f"Mode: {mode_str}", "ok")

    def _process_audio_segment(self, audio_segment: np.ndarray) -> None:
        """Run STT and LLM reasoning on an audio segment.

        :param audio_segment: Audio buffer to transcribe and analyze.
        """
        if audio_segment is None or len(audio_segment) < int(self.config.sample_rate * 0.3):
            self.status_changed.emit("Audio segment too short", "ok")
            return

        start_time = time.monotonic()
        self.status_changed.emit("Transcribing speech...", "busy")

        assert self.transcriber is not None
        assert self.llm_client is not None

        transcript = self.transcriber.transcribe(audio_segment)
        if not transcript:
            self.status_changed.emit("Speech unclear / discarded", "ok")
            return

        logger.info("Opponent transcript: '%s'", transcript)
        self.transcript_received.emit(transcript)
        self.status_changed.emit("Analyzing rhetorical flaws...", "busy")

        flaw, counter = self.llm_client.analyze(transcript)
        latency = time.monotonic() - start_time

        logger.info("Analysis [Latency %.2fs] -> Flaw: %s | Counter: %s", latency, flaw, counter)
        self.rebuttal_received.emit(flaw, counter, latency)
        self.status_changed.emit("Ready", "ok")

    def run(self) -> None:
        """Execute the main pipeline audio ingestion loop."""
        self.running = True
        self.status_changed.emit("Initializing speech models...", "busy")

        try:
            self.transcriber = Transcriber(self.config)
            self.status_changed.emit("Warming up LLM...", "busy")
            self.llm_client = OllamaClient(self.config)
            self.llm_client.warmup()
            self.audio_capture.start()
        except Exception as e:
            logger.exception("Failed initializing pipeline: %s", e)
            self.status_changed.emit(f"Init Error: {e}", "error")
            return

        init_status = (
            "Ready (Manual Mode)" if self.manual_mode else f"Listening ({self.llm_client.model})"
        )
        self.status_changed.emit(init_status, "ok")
        logger.info("Pipeline worker active.")

        while self.running:
            chunk = self.audio_capture.get_chunk(timeout=0.05)
            if chunk is None:
                continue

            rms = compute_rms(chunk)

            if self.manual_mode:
                segment_to_process: np.ndarray | None = None
                with self._lock:
                    if self.is_manual_recording:
                        self.manual_buffer.append(chunk)
                        max_chunks = int(
                            self.config.max_manual_buffer_s / (self.config.chunk_ms / 1000.0)
                        )
                        if len(self.manual_buffer) >= max_chunks:
                            self.is_manual_recording = False
                            self._flush_requested = True
                            self.recording_state_changed.emit(False)
                            self.status_changed.emit(
                                f"Max duration reached ({int(self.config.max_manual_buffer_s)}s). Processing...",
                                "busy",
                            )
                        self.audio_level.emit(rms, True)
                    else:
                        self.audio_level.emit(rms, False)

                    if self._flush_requested:
                        self._flush_requested = False
                        if self.manual_buffer:
                            segment_to_process = np.concatenate(self.manual_buffer, axis=0)
                            self.manual_buffer = []

                if segment_to_process is not None:
                    self._process_audio_segment(segment_to_process)
            else:
                # Continuous Auto VAD mode
                speech_segment, rms, is_speaking = self.vad.process_chunk(chunk)
                self.audio_level.emit(rms, is_speaking)
                if speech_segment is not None:
                    self._process_audio_segment(speech_segment)

        self.audio_capture.stop()
        logger.info("Pipeline worker stopped.")

    def stop(self) -> None:
        """Signal worker to terminate and wait for thread completion."""
        self.running = False
        self.audio_capture.stop()
        self.wait(1500)
        if self.isRunning():
            self.terminate()
            self.wait(500)
