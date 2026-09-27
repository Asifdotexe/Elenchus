"""Main entry point for aenf (all ears no foul) desktop HUD."""

import argparse
import logging
import signal
import sys
from PyQt6.QtWidgets import QApplication

from config import DEFAULT_CONFIG, Config
from core.audio_capture import list_audio_devices
from core.pipeline import PipelineWorker
from ui.overlay import AenfOverlay


def setup_logging(verbose: bool = False) -> None:
    """Configure console logging level and format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] [%(levelname)s] (%(name)s) %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    """Parse command line options."""
    parser = argparse.ArgumentParser(
        prog="aenf",
        description="Real-time heads-up display overlay for debate flaw detection and instant counter-arguments.",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List all audio input devices and exit.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default=None,
        help="Audio input device index or partial name.",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=DEFAULT_CONFIG.ollama_model,
        help=f"Ollama model name (default: {DEFAULT_CONFIG.ollama_model}).",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default=DEFAULT_CONFIG.whisper_model,
        help=f"faster-whisper model (default: {DEFAULT_CONFIG.whisper_model}).",
    )
    parser.add_argument(
        "--rms",
        type=float,
        default=DEFAULT_CONFIG.vad_rms_threshold,
        help=f"VAD RMS energy threshold (default: {DEFAULT_CONFIG.vad_rms_threshold}).",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=DEFAULT_CONFIG.opacity,
        help=f"Window opacity between 0.2 and 1.0 (default: {DEFAULT_CONFIG.opacity}).",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable detailed debug logging.",
    )
    return parser.parse_args()


def print_devices() -> None:
    """Print available audio input devices formatted neatly."""
    devs = list_audio_devices()
    print("\n--- Available Audio Input Devices ---")
    for d in devs:
        print(f"[{d['index']:2d}] {d['name']} ({d['channels']} in, rate: {d['default_samplerate']}Hz)")
    print("-------------------------------------\n")


def build_config(args: argparse.Namespace) -> Config:
    """Build Config dataclass instance from CLI args."""
    cfg = Config()
    if args.device is not None:
        try:
            cfg.audio_device = int(args.device)
        except ValueError:
            cfg.audio_device = args.device
    cfg.ollama_model = args.model
    cfg.whisper_model = args.whisper_model
    cfg.vad_rms_threshold = args.rms
    cfg.opacity = max(0.2, min(1.0, args.opacity))
    return cfg


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    if args.list_devices:
        print_devices()
        sys.exit(0)

    config = build_config(args)

    # Enable Ctrl+C in terminal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    app.setApplicationName("aenf")

    pipeline = PipelineWorker(config)
    overlay = AenfOverlay(config, pipeline)

    # Position overlay at top-right corner of screen by default
    screen = app.primaryScreen()
    if screen:
        screen_geometry = screen.availableGeometry()
        x = screen_geometry.width() - config.window_width - 40
        y = 60
        overlay.move(x, y)

    overlay.show()
    pipeline.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
