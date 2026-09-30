"""Unit tests for Elenchus core components."""

import unittest
from unittest.mock import patch

import numpy as np

from config import Config
from core.llm_client import OllamaClient
from core.transcriber import Transcriber
from core.vad import DynamicVAD, compute_rms


class TestVAD(unittest.TestCase):
    def setUp(self):
        self.config = Config(
            sample_rate=16000,
            chunk_ms=100,
            vad_rms_threshold=0.02,
            vad_silence_duration_s=0.3,
            vad_min_speech_duration_s=0.2,
            vad_max_speech_duration_s=1.0,
        )
        self.vad = DynamicVAD(self.config)

    def test_compute_rms_silence(self):
        silence = np.zeros(1600, dtype=np.float32)
        rms = compute_rms(silence)
        self.assertAlmostEqual(rms, 0.0)

    def test_compute_rms_signal(self):
        sine = (np.sin(np.linspace(0, 100, 1600)) * 0.1).astype(np.float32)
        rms = compute_rms(sine)
        self.assertGreater(rms, 0.05)

    def test_vad_speech_segment_detection(self):
        # 1600 samples = 100ms
        speech_chunk = np.ones(1600, dtype=np.float32) * 0.05
        silence_chunk = np.zeros(1600, dtype=np.float32)

        # Feed 3 speech chunks (300ms speech)
        for _ in range(3):
            seg, rms, is_speaking = self.vad.process_chunk(speech_chunk)
            self.assertIsNone(seg)
            self.assertTrue(is_speaking)

        # Feed 4 silence chunks (400ms silence > 300ms threshold)
        completed = None
        for _ in range(4):
            seg, rms, is_speaking = self.vad.process_chunk(silence_chunk)
            if seg is not None:
                completed = seg

        self.assertIsNotNone(completed)
        self.assertGreaterEqual(len(completed), 1600 * 3)


class TestTranscriberValidation(unittest.TestCase):
    def setUp(self):
        self.config = Config(min_transcript_len=15)
        # Avoid loading full model in mock validation test
        self.transcriber = Transcriber.__new__(Transcriber)
        self.transcriber.config = self.config
        self.transcriber.last_transcript = ""

    def test_validate_too_short(self):
        result = self.transcriber._validate_and_clean("yes")
        self.assertIsNone(result)

    def test_validate_hallucination(self):
        result = self.transcriber._validate_and_clean("Thank you for watching.")
        self.assertIsNone(result)

        music_result = self.transcriber._validate_and_clean("[Music]")
        self.assertIsNone(music_result)

    def test_validate_valid_speech(self):
        text = "Nuclear energy is fundamentally unsafe for modern cities."
        result = self.transcriber._validate_and_clean(text)
        self.assertEqual(result, text)

    def test_validate_deduplication(self):
        text = "Renewable sources cannot meet baseline energy demands."
        r1 = self.transcriber._validate_and_clean(text)
        self.assertEqual(r1, text)
        # Second identical transcript is dropped
        r2 = self.transcriber._validate_and_clean(text)
        self.assertIsNone(r2)


class TestOllamaClientParsing(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        self.client = OllamaClient.__new__(OllamaClient)
        self.client.config = self.config

    def test_parse_standard_bullet_format(self):
        raw = (
            "• Flaw: False Equivalence\n"
            "• Counter: Nuclear energy has far lower mortality rates per kilowatt-hour than coal or gas."
        )
        flaw, counter = self.client._parse_debate_output(raw)
        self.assertEqual(flaw, "False Equivalence")
        self.assertEqual(
            counter,
            "Nuclear energy has far lower mortality rates per kilowatt-hour than coal or gas.",
        )

    def test_parse_colon_format(self):
        raw = (
            "Flaw: Straw Man Argument\n"
            "Counter: The proposal never called for abolishing private healthcare, only expanding public coverage."
        )
        flaw, counter = self.client._parse_debate_output(raw)
        self.assertEqual(flaw, "Straw Man Argument")
        self.assertEqual(
            counter,
            "The proposal never called for abolishing private healthcare, only expanding public coverage.",
        )


class TestArgumentFilter(unittest.TestCase):
    def test_filter_incomplete_and_filler(self):
        from core.llm_client import is_substantive_argument

        # Repetitive interjections
        valid, _ = is_substantive_argument("Oh, oh, oh, oh.")
        self.assertFalse(valid)

        # Trailing cutoff
        valid, _ = is_substantive_argument("Because when you look at the other day...")
        self.assertFalse(valid)

        # Too short
        valid, _ = is_substantive_argument("I think so")
        self.assertFalse(valid)

        # Substantive claim
        valid, _ = is_substantive_argument(
            "We should ban electric vehicles because battery recycling is not yet feasible."
        )
        self.assertTrue(valid)


class TestConfigRebrand(unittest.TestCase):
    def test_default_model(self):
        cfg = Config()
        self.assertEqual(cfg.ollama_model, "qwen2.5-coder:3b")

    def test_elenchus_model_env_precedence(self):
        import os

        old_elenchus = os.environ.get("ELENCHUS_MODEL")
        try:
            os.environ["ELENCHUS_MODEL"] = "custom-elenchus:latest"
            cfg = Config()
            self.assertEqual(cfg.ollama_model, "custom-elenchus:latest")
        finally:
            if old_elenchus is not None:
                os.environ["ELENCHUS_MODEL"] = old_elenchus
            else:
                os.environ.pop("ELENCHUS_MODEL", None)


class TestUIIcons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_get_icon_known_and_unknown(self):
        from ui.icons import get_icon

        icon = get_icon("mic")
        self.assertFalse(icon.isNull())

        fallback_icon = get_icon("nonexistent_icon_key")
        self.assertTrue(fallback_icon.isNull())

    def test_get_pixmap(self):
        from ui.icons import get_pixmap

        pixmap = get_pixmap("activity", size=14)
        self.assertFalse(pixmap.isNull())
        self.assertEqual(pixmap.width(), 14)
        self.assertEqual(pixmap.height(), 14)


class TestMonochartMeter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_set_level_clamping(self):
        from ui.waveform import MonochartMeter

        meter = MonochartMeter()
        meter.set_level(0.0, False)
        self.assertEqual(meter.level, 0.0)
        self.assertFalse(meter.is_speaking)

        meter.set_level(0.1, True)
        self.assertEqual(meter.level, 1.0)
        self.assertTrue(meter.is_speaking)


class TestElenchusOverlay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PyQt6.QtWidgets import QApplication

        cls.app = QApplication.instance() or QApplication([])

    def test_overlay_creation(self):
        from core.pipeline import PipelineWorker
        from ui.overlay import ElenchusOverlay

        cfg = Config()
        pipeline = PipelineWorker(cfg)
        overlay = ElenchusOverlay(cfg, pipeline)
        self.assertEqual(overlay.title_label.text(), "elenchus")
        overlay.close()


class TestEnsureOllamaService(unittest.TestCase):
    def test_ensure_ollama_not_installed_mock(self):
        from core.llm_client import ensure_ollama_service

        with patch("core.llm_client._http_json", side_effect=Exception("Connection refused")):
            with patch("shutil.which", return_value=None):
                avail, msg = ensure_ollama_service(url="http://localhost:11434")
                self.assertFalse(avail)
                self.assertIn("Ollama not installed", msg)

    def test_ensure_ollama_running_mock(self):
        from core.llm_client import ensure_ollama_service

        fake_tags = {"models": [{"name": "qwen2.5-coder:3b"}]}
        with patch("core.llm_client._http_json", return_value=fake_tags):
            avail, msg = ensure_ollama_service(
                url="http://localhost:11434", target_model="qwen2.5-coder:3b"
            )
            self.assertTrue(avail)
            self.assertIn("Ollama connected", msg)


if __name__ == "__main__":
    unittest.main()
