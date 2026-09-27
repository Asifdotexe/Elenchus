"""Asynchronous processing pipeline linking Audio, VAD, Transcriber, and LLM."""

import logging
import time
from PyQt6.QtCore import QThread, pyqtSignal

from config import Config
from core.audio_capture import AudioCapture
from core.vad import DynamicVAD
from core.transcriber import Transcriber
from core.llm_client import OllamaClient

logger = logging.getLogger(__name__)


class PipelineWorker(QThread):
    """
    Background QThread running continuous VAD, transcription, and debate reasoning.
    Communicates with HUD via PyQt signals.
    """

    # Signals for UI:
    # status_signal(status_text: str, status_level: "ok" | "busy" | "error")
    status_changed = pyqtSignal(str, str)
    # audio_level_signal(rms: float, is_speaking: bool)
    audio_level = pyqtSignal(float, bool)
    # transcript_signal(text: str)
    transcript_received = pyqtSignal(str)
    # rebuttal_signal(flaw: str, counter: str, latency_seconds: float)
    rebuttal_received = pyqtSignal(str, str, float)

    def __init__(self, config: Config):
        super().__init__()
        self.config = config
        self.running = False
        self.audio_capture = AudioCapture(config)
        self.vad = DynamicVAD(config)
        self.transcriber: Transcriber | None = None
        self.llm_client: OllamaClient | None = None

    def run(self) -> None:
        """Pipeline thread loop."""
        self.running = True
        self.status_changed.emit("Initializing speech models...", "busy")

        # Initialize Whisper and LLM inside worker thread to avoid blocking GUI startup
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

        self.status_changed.emit(f"Listening ({self.llm_client.model})", "ok")
        logger.info("Pipeline worker active and listening.")

        while self.running:
            chunk = self.audio_capture.get_chunk(timeout=0.1)
            if chunk is None:
                continue

            speech_segment, rms, is_speaking = self.vad.process_chunk(chunk)
            self.audio_level.emit(rms, is_speaking)

            if speech_segment is not None:
                start_time = time.monotonic()
                self.status_changed.emit("Transcribing speech...", "busy")

                transcript = self.transcriber.transcribe(speech_segment)
                if not transcript:
                    self.status_changed.emit("Listening...", "ok")
                    continue

                logger.info("Opponent transcript: '%s'", transcript)
                self.transcript_received.emit(transcript)
                self.status_changed.emit("Analyzing rhetorical flaws...", "busy")

                flaw, counter = self.llm_client.analyze(transcript)
                latency = time.monotonic() - start_time

                logger.info("Analysis [Latency %.2fs] -> Flaw: %s | Counter: %s", latency, flaw, counter)
                self.rebuttal_received.emit(flaw, counter, latency)
                self.status_changed.emit("Listening...", "ok")

        self.audio_capture.stop()
        logger.info("Pipeline worker stopped.")

    def stop(self) -> None:
        """Signal worker to terminate and wait."""
        self.running = False
        self.wait(1500)
