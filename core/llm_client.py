"""Ollama LLM client for real-time debate analysis and fallacy detection using stdlib urllib."""

import json
import logging
import re
import socket
import urllib.error
import urllib.request
from config import Config

logger = logging.getLogger(__name__)


def _http_json(url: str, payload: dict | None = None, timeout: float = 10.0) -> dict:
    """Execute JSON HTTP request using standard library urllib."""
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def is_substantive_argument(text: str) -> tuple[bool, str]:
    """Check if speech possesses minimal structure to form a debate claim/argument."""
    words = text.strip().split()
    if len(words) < 4:
        return False, "Statement too short to contain premise and conclusion."

    last_word = words[-1].lower().rstrip(".,!?")
    trailing_connectors = {
        "because", "and", "or", "so", "that", "when", "if", "while",
        "as", "the", "a", "an", "at", "to", "with", "for", "about", "of",
    }
    if last_word in trailing_connectors or text.rstrip().endswith("..."):
        return False, "Trailing fragment. Opponent cut off mid-thought."

    unique_words = set(w.lower().rstrip(".,!?") for w in words)
    filler_words = {"oh", "ah", "um", "uh", "yeah", "yes", "no", "okay", "ok", "hey", "like", "well"}
    if unique_words.issubset(filler_words):
        return False, "Conversational filler / interjection."

    return True, ""


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
            data = _http_json(self.tags_url, timeout=2.0)
            models = [m.get("name", "") for m in data.get("models", [])]
            for m in models:
                if self.config.ollama_model in m or m.startswith(self.config.ollama_model.split(":")[0]):
                    logger.info("Found matching Ollama model: %s", m)
                    return m
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
            _http_json(
                self.generate_url,
                payload={"model": self.model, "prompt": "ready", "stream": False, "options": {"num_predict": 1}},
                timeout=25.0,
            )
            return True
        except Exception as e:
            logger.warning("Ollama warmup failed: %s", e)
            return False

    def analyze(self, transcript: str) -> tuple[str, str]:
        """
        Analyze opponent transcript for logical fallacies and generate rebuttal.
        Returns:
            (flaw_text, counter_argument)
        """
        is_arg, reason = is_substantive_argument(transcript)
        if not is_arg:
            logger.info("Dropping non-argument: '%s' (%s)", transcript, reason)
            return (
                "None (Incomplete / Non-Argument)",
                f"Cannot evaluate: {reason}",
            )

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
            data = _http_json(self.generate_url, payload=payload, timeout=self.config.ollama_timeout_s)
            raw_response = data.get("response", "").strip()
            return self._parse_debate_output(raw_response)
        except (TimeoutError, socket.timeout):
            logger.warning("Ollama request timed out (>%.1fs)", self.config.ollama_timeout_s)
            return (
                "Latency Warning",
                "Ollama took > 8s to respond. Inference dropped to maintain real-time sync.",
            )
        except urllib.error.URLError as e:
            logger.error("Ollama connection failed at %s: %s", self.config.ollama_url, e)
            return (
                "Ollama Offline",
                f"Start Ollama service. Command: ollama run {self.model}",
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

        counter = re.sub(r"^\s*[•\-*]\s*", "", counter).strip()

        return flaw, counter
