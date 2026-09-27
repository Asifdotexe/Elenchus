"""Main entry point for aenf (all ears no foul) desktop HUD."""

import argparse
import logging
import signal
import sys

from PyQt6.QtWidgets import QApplication

from config import Config
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
    cfg = Config()
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
        default=cfg.ollama_model,
        help=f"Ollama model name (default: {cfg.ollama_model}).",
    )
    parser.add_argument(
        "--whisper-model",
        type=str,
        default=cfg.whisper_model,
        help=f"faster-whisper model (default: {cfg.whisper_model}).",
    )
    parser.add_argument(
        "--rms",
        type=float,
        default=cfg.vad_rms_threshold,
        help=f"VAD RMS energy threshold (default: {cfg.vad_rms_threshold}).",
    )
    parser.add_argument(
        "--opacity",
        type=float,
        default=cfg.opacity,
        help=f"Window opacity between 0.2 and 1.0 (default: {cfg.opacity}).",
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Enable continuous auto VAD silence-cut mode instead of manual button mode.",
    )
    parser.add_argument(
        "--test-device",
        type=int,
        nargs="?",
        const=-1,
        default=None,
        help="Test live audio input level with an ASCII volume meter for 5 seconds.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable detailed debug logging.",
    )
    return parser.parse_args()


def print_devices() -> None:
    """Print available audio input devices cleanly categorized."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    devs = list_audio_devices()
    mics = [d for d in devs if "MIC" in d["category"]]
    loopbacks = [d for d in devs if "LOOPBACK" in d["category"]]
    others = [d for d in devs if d not in mics and d not in loopbacks]

    print("\n================== AUDIO DEVICE DIRECTORY ==================")
    print(">> YOUR MICROPHONE (Physical Voice / Room):")
    for d in mics:
        rec = " [RECOMMENDED]" if "WASAPI" in d["hostapi"] else ""
        print(f"   [{d['index']:2d}] {d['name']} ({d['hostapi']}){rec}")

    print("\n>> SYSTEM AUDIO / DISCORD LOOPBACK (Opponent Speech):")
    if loopbacks:
        for d in loopbacks:
            print(f"   [{d['index']:2d}] {d['name']} ({d['hostapi']})")
    else:
        print(
            "   (No virtual loopback detected. Install VB-Audio Cable to record Discord directly)"
        )

    if others:
        print("\n>> OTHER INPUTS:")
        for d in others:
            print(f"   [{d['index']:2d}] {d['name']} ({d['hostapi']})")
    print("============================================================\n")
    print("TIP: Run 'uv run aenf --test-device <ID>' to see live volume meter before launching!\n")


def test_audio_device(device_idx: int | None = None) -> None:
    """Listen to device for 5 seconds and display live ASCII volume meter."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    import time

    import numpy as np
    import sounddevice as sd

    from config import Config

    cfg = Config()
    target = None if (device_idx is None or device_idx < 0) else device_idx
    print(f"\n--- Testing Device [{target if target is not None else 'DEFAULT'}] for 5 seconds ---")
    print("Speak into mic or play Discord/YouTube audio now...")
    try:
        dev_info = sd.query_devices(target if target is not None else sd.default.device[0])
        native_rate = int(dev_info.get("default_samplerate", cfg.sample_rate))
        blocksize = int(native_rate * 0.1)
        with sd.InputStream(
            device=target, channels=1, samplerate=native_rate, blocksize=blocksize
        ) as stream:
            for _ in range(50):
                data, _ = stream.read(blocksize)
                rms = float(np.sqrt(np.mean(data**2)))
                pct = min(100, int((rms / 0.08) * 100))
                bars = int(pct / 5)
                meter = "#" * bars + "-" * (20 - bars)
                status = "SOUND DETECTED" if rms >= cfg.vad_rms_threshold else "QUIET"
                print(f"\r  [{meter}] {pct:3d}% | {status}  ", end="", flush=True)
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"\nError capturing device: {e}")
    print("\n--- Test Complete ---\n")


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
    if args.auto:
        cfg.manual_mode = False
    return cfg


def main() -> None:
    args = parse_args()
    setup_logging(args.verbose)

    if args.list_devices:
        print_devices()
        sys.exit(0)

    if args.test_device is not None:
        test_audio_device(args.test_device)
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

    app.setQuitOnLastWindowClosed(True)
    overlay.show()
    pipeline.start()

    exit_code = app.exec()
    pipeline.stop()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
