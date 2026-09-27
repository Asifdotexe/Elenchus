"""Audio capture engine using sounddevice InputStream with thread-safe queue."""

import logging
import queue
from typing import Any

import numpy as np
import sounddevice as sd

from config import Config

logger = logging.getLogger(__name__)


def list_audio_devices() -> list[dict[str, Any]]:
    """Return all available audio input devices with categories and host APIs.

    :return: List of device dictionaries containing index, name, hostapi, category, channels, and default samplerate.
    """
    devices = sd.query_devices()
    hostapis = {i: h.get("name", "") for i, h in enumerate(sd.query_hostapis())}
    input_devs = []
    for idx, dev in enumerate(devices):
        if dev.get("max_input_channels", 0) > 0:
            name = dev.get("name", "")
            h_name = hostapis.get(dev.get("hostapi"), "")
            name_lower = name.lower()

            if any(
                term in name_lower
                for term in ["cable", "stereo mix", "wave", "loopback", "what u hear"]
            ):
                category = "LOOPBACK (System/Discord audio)"
            elif any(term in name_lower for term in ["mic", "headset", "array"]):
                category = "MIC (Your physical voice)"
            else:
                category = "INPUT"

            input_devs.append(
                {
                    "index": idx,
                    "name": name,
                    "hostapi": h_name,
                    "category": category,
                    "channels": dev.get("max_input_channels"),
                    "default_samplerate": dev.get("default_samplerate"),
                }
            )
    return input_devs


class AudioCapture:
    """Manages audio stream capture into a thread-safe queue with auto-resampling."""

    def __init__(self, config: Config):
        """Initialize the audio capture manager.

        :param config: Application configuration instance with audio settings.
        """
        self.config = config
        self.queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=100)
        self.stream: sd.InputStream | None = None
        self.running = False
        self.target_rate = self.config.sample_rate  # 16000
        self.target_blocksize = int(self.target_rate * (self.config.chunk_ms / 1000.0))
        self.actual_sample_rate = self.target_rate

    def _audio_callback(
        self, indata: np.ndarray, frames: int, time_info: Any, status: sd.CallbackFlags
    ) -> None:
        """Process incoming audio blocks from the PortAudio thread and push into queue.

        :param indata: Buffer containing input audio samples.
        :param frames: Number of frames in buffer.
        :param time_info: Dictionary-like object containing ADC and DAC timestamps.
        :param status: PortAudio callback status flags indicating underflow or overflow.
        """
        if status:
            logger.warning("Audio callback status warning: %s", status)
        if not self.running:
            return

        chunk = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()

        # Resample to 16kHz if device requires different native sample rate (e.g. 48kHz on WASAPI)
        if self.actual_sample_rate != self.target_rate and len(chunk) > 0:
            orig_len = len(chunk)
            chunk = np.interp(
                np.linspace(0.0, 1.0, self.target_blocksize, endpoint=False),
                np.linspace(0.0, 1.0, orig_len, endpoint=False),
                chunk,
            ).astype(np.float32)

        try:
            self.queue.put_nowait(chunk)
        except queue.Full:
            try:
                self.queue.get_nowait()
                self.queue.put_nowait(chunk)
            except Exception:
                pass

    def start(self) -> None:
        """Initialize and start the PortAudio InputStream with native device samplerate support.

        :raises sd.PortAudioError: If stream fails to open on primary and fallback devices.
        """
        self.running = True
        device = self.config.audio_device

        # Determine native sample rate for selected device
        try:
            dev_info = sd.query_devices(device if device is not None else sd.default.device[0])
            self.actual_sample_rate = int(dev_info.get("default_samplerate", self.target_rate))
        except Exception:
            self.actual_sample_rate = self.target_rate

        blocksize = int(self.actual_sample_rate * (self.config.chunk_ms / 1000.0))
        logger.info(
            "Opening audio stream on device %s (native_rate=%d, target_rate=%d, blocksize=%d)",
            device,
            self.actual_sample_rate,
            self.target_rate,
            blocksize,
        )

        try:
            self.stream = sd.InputStream(
                samplerate=self.actual_sample_rate,
                blocksize=blocksize,
                device=device,
                channels=self.config.channels,
                dtype="float32",
                callback=self._audio_callback,
            )
            self.stream.start()
        except sd.PortAudioError as e:
            logger.error(
                "PortAudio error on device %s: %s. Attempting fallback to default device.",
                device,
                e,
            )
            self.actual_sample_rate = self.target_rate
            self.stream = sd.InputStream(
                samplerate=self.target_rate,
                blocksize=self.target_blocksize,
                device=None,
                channels=self.config.channels,
                dtype="float32",
                callback=self._audio_callback,
            )
            self.stream.start()

    def get_chunk(self, timeout: float = 0.2) -> np.ndarray | None:
        """Fetch next audio chunk from queue.

        :param timeout: Maximum time in seconds to wait before returning None.
        :return: Float32 audio chunk array, or None if queue is empty.
        """
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
