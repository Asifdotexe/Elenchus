"""Audio capture engine using sounddevice InputStream with thread-safe queue."""

import logging
import queue
import time
from typing import Any
import numpy as np
import sounddevice as sd

from config import Config

logger = logging.getLogger(__name__)


def list_audio_devices() -> list[dict[str, Any]]:
    """Return all available audio input devices."""
    devices = sd.query_devices()
    input_devs = []
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            input_devs.append({
                "index": idx,
                "name": dev.get("name"),
                "hostapi": dev.get("hostapi"),
                "channels": dev.get("max_input_channels"),
                "default_samplerate": dev.get("default_samplerate"),
            })
    return input_devs


class AudioCapture:
    """Manages audio stream capture into a thread-safe queue."""

    def __init__(self, config: Config):
        self.config = config
        self.queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=100)
        self.stream: sd.InputStream | None = None
        self.running = False
        self.blocksize = int(self.config.sample_rate * (self.config.chunk_ms / 1000.0))

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info: Any, status: sd.CallbackFlags) -> None:
        """Callback executed in PortAudio thread for incoming audio blocks."""
        if status:
            logger.warning("Audio callback status warning: %s", status)
        if not self.running:
            return

        # indata is shape (frames, channels), float32
        chunk = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
        try:
            self.queue.put_nowait(chunk)
        except queue.Full:
            # Drop older audio chunk to maintain real-time responsiveness
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(chunk)
            except Exception:
                pass

    def start(self) -> None:
        """Initialize and start the sounddevice InputStream."""
        self.running = True
        device = self.config.audio_device
        logger.info("Opening audio stream on device %s (rate=%d, blocksize=%d)", device, self.config.sample_rate, self.blocksize)

        try:
            self.stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                blocksize=self.blocksize,
                device=device,
                channels=self.config.channels,
                dtype="float32",
                callback=self._audio_callback,
            )
            self.stream.start()
        except sd.PortAudioError as e:
            logger.error("PortAudio error during stream startup: %s. Attempting fallback to default device.", e)
            # Fallback to system default input device
            self.stream = sd.InputStream(
                samplerate=self.config.sample_rate,
                blocksize=self.blocksize,
                device=None,
                channels=self.config.channels,
                dtype="float32",
                callback=self._audio_callback,
            )
            self.stream.start()

    def get_chunk(self, timeout: float = 0.2) -> np.ndarray | None:
        """Fetch next audio chunk from queue."""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def stop(self) -> None:
        """Stop and close the audio stream."""
        self.running = False
        if self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                logger.debug("Error stopping audio stream: %s", e)
            self.stream = None
