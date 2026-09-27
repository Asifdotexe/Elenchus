"""Ollama LLM REST client for real-time debate analysis and fallacy detection."""

import logging
import re
import requests
from config import Config

logger = logging.getLogger(__name__)


class OllamaClient:
    """Interfaces with Ollama REST API for low-latency debate reasoning."""

    def __init__(self, config: Config):
        self.config = config
        self.generate_url = f"{config.ollama_url.rstrip('/')}/api/generate"
        self.tags_url = f"{config.ollama_url.rstrip('/')}/api/tags"
        self.model = self._resolve_model()

    def _resolve_model(self) -> str:
        """Verify model availability in Ollama; fallback gracefully if possible."""
        try:
            resp = requests.get(self.tags_url, timeout=2.0)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                # Exact or prefix match
                for m in models:
                    if self.config.ollama_model in m or m.startswith(self.config.ollama_model.split(":")[0]):
                        logger.info("Found matching Ollama model: %s", m)
                        return m
                # If preferred not found, use first available 3b/small model if any
                if models:
                    logger.warning(
                        "Configured model '%s' not found. Available: %s. Using '%s'.",
                        self.config.ollama_model,
                        models,
                        models[0],
                    )
                    return models[0]
        except Exception as e:
            logger.warning("Could not query Ollama tags (%s). Using '%s'.", e, self.config.ollama_model)
        return self.config.ollama_model

    def warmup(self) -> bool:
        """Pre-warm model into VRAM to eliminate cold-start latency."""
        try:
            logger.info("Warming up Ollama model '%s'...", self.model)
            resp = requests.post(
                self.generate_url,
                json={"model": self.model, "prompt": "ready", "stream": False, "options": {"num_predict": 1}},
                timeout=25.0,
            )
            return resp.status_code == 200
        except Exception as e:
            logger.warning("Ollama warmup failed: %s", e)
            return False


    def analyze(self, transcript: str) -> tuple[str, str]:
        """
        Analyze opponent transcript for logical fallacies and generate rebuttal.
        Returns:
            (flaw_text, counter_argument)
        """
        payload = {
            "model": self.model,
            "prompt": transcript,
            "system": self.config.system_prompt,
            "stream": False,
            "options": {
                "temperature": self.config.ollama_temperature,
                "num_predict": self.config.ollama_num_predict,
            },
        }

        try:
            resp = requests.post(
                self.generate_url,
                json=payload,
                timeout=self.config.ollama_timeout_s,
            )
            resp.raise_for_status()
            data = resp.json()
            raw_response = data.get("response", "").strip()
            return self._parse_debate_output(raw_response)
        except requests.exceptions.ConnectionError:
            logger.error("Ollama connection failed at %s", self.config.ollama_url)
            return (
                "Ollama Offline",
                f"Start Ollama service. Command: ollama run {self.model}",
            )
        except requests.exceptions.Timeout:
            logger.warning("Ollama request timed out (>%.1fs)", self.config.ollama_timeout_s)
            return (
                "Latency Warning",
                "Ollama took > 8s to respond. Inference dropped to maintain real-time sync.",
            )
        except Exception as e:
            logger.error("Error analyzing transcript with Ollama: %s", e)
            return (
                "Inference Error",
                str(e),
            )

    def _parse_debate_output(self, response_text: str) -> tuple[str, str]:
        """Parse structured Flaw and Counter lines from LLM response."""
        flaw = "Rhetorical Defect"
        counter = response_text

        flaw_match = re.search(r"[•\-*]?\s*Flaw:\s*([^\n\r]+)", response_text, re.IGNORECASE)
        counter_match = re.search(r"[•\-*]?\s*Counter:\s*(.+)", response_text, re.IGNORECASE | re.DOTALL)

        if flaw_match:
            flaw = flaw_match.group(1).strip()
        if counter_match:
            counter = counter_match.group(1).strip()

        # Clean trailing extra lines or bullets
        counter = re.sub(r"^\s*[•\-*]\s*", "", counter).strip()

        return flaw, counter
