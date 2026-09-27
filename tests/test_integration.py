"""Integration test verifying end-to-end transcription and Ollama inference."""

import time
import unittest
import numpy as np

from config import Config
from core.transcriber import Transcriber
from core.llm_client import OllamaClient


class TestIntegration(unittest.TestCase):
    def test_transcriber_cpu_int8(self):
        config = Config()
        transcriber = Transcriber(config)
        self.assertIsNotNone(transcriber.model)

        # Transcribe 1.0 second of silence -> should return None (filtered)
        silence = np.zeros(16000, dtype=np.float32)
        res = transcriber.transcribe(silence)
        self.assertIsNone(res)

    def test_ollama_reasoning_integration(self):
        config = Config()
        client = OllamaClient(config)
        self.assertTrue(len(client.model) > 0)
        client.warmup()

        statement = "We should ban all renewable energy because solar panels produce toxic waste when discarded."
        start = time.monotonic()
        flaw, counter = client.analyze(statement)
        elapsed = time.monotonic() - start

        print(f"\n[Integration Result] Time: {elapsed:.2f}s")
        print(f"Flaw: {flaw}")
        print(f"Counter: {counter}")

        self.assertTrue(len(flaw) > 0)
        self.assertTrue(len(counter) > 0)
        self.assertNotEqual(flaw, "Ollama Offline")


if __name__ == "__main__":
    unittest.main()
