"""Ollama LLM client for real-time debate analysis and fallacy detection using stdlib urllib."""

import json
import logging
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

from config import Config

logger = logging.getLogger(__name__)


def ensure_ollama_service(
    url: str = "http://localhost:11434", target_model: str = "qwen2.5-coder:3b"
) -> tuple[bool, str]:
    """Verify Ollama daemon is active; if down and ollama binary is installed, spawn it.

    :param url: Ollama base URL.
    :param target_model: Name of the expected reasoning model.
    :return: Tuple of (is_available_flag, status_or_error_message).
    """
    clean_url = url.rstrip("/")
    try:
        data = _http_json(f"{clean_url}/api/tags", timeout=1.5)
        models = [m.get("name", "") for m in data.get("models", [])]
        has_model = any(
            target_model in m or m.startswith(target_model.split(":")[0]) for m in models
        )
        if has_model:
            return True, f"Ollama connected ({target_model})"
        return True, f"Ollama connected (model {target_model} missing)"
    except Exception:
        pass

    ollama_bin = shutil.which("ollama")
    if not ollama_bin:
        return False, "Ollama not installed. Download from https://ollama.com"

    logger.info("Ollama daemon offline. Launching background 'ollama serve' via %s...", ollama_bin)
    try:
        popen_kwargs: dict = {
            "stdout": subprocess.DEVNULL,
            "stderr": subprocess.DEVNULL,
        }
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        else:
            popen_kwargs["start_new_session"] = True

        subprocess.Popen([ollama_bin, "serve"], **popen_kwargs)

        for _ in range(8):
            time.sleep(0.4)
            try:
                _http_json(f"{clean_url}/api/tags", timeout=1.0)
                logger.info("Ollama daemon successfully started and responding.")
                return True, "Ollama daemon started automatically"
            except Exception:
                pass

        return True, "Ollama daemon launched (starting in background...)"
    except Exception as e:
        logger.warning("Failed to auto-spawn Ollama daemon: %s", e)
        return False, f"Failed to start Ollama: {e}"


def _http_json(url: str, payload: dict | None = None, timeout: float = 10.0) -> dict:
    """Execute JSON HTTP request using standard library urllib.

    :param url: Target endpoint URL.
    :param payload: Optional JSON-serializable request dictionary.
    :param timeout: Request timeout in seconds.
    :raises urllib.error.URLError: If the HTTP request fails or times out.
    :return: Parsed JSON response dictionary.
    """
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def is_substantive_argument(text: str) -> tuple[bool, str]:
    """Check if speech possesses minimal structure to form a debate claim or argument.

    :param text: Candidate statement or transcript to evaluate.
    :return: Tuple of (is_argument_flag, drop_reason_if_false).
    """
    words = text.strip().split()
    if len(words) < 4:
        return False, "Statement too short to contain premise and conclusion."

    last_word = words[-1].lower().rstrip(".,!?")
    trailing_connectors = {
        "because",
        "and",
        "or",
        "so",
        "that",
        "when",
        "if",
        "while",
        "as",
        "the",
        "a",
        "an",
        "at",
        "to",
        "with",
        "for",
        "about",
        "of",
    }
    if last_word in trailing_connectors or text.rstrip().endswith("..."):
        return False, "Trailing fragment. Opponent cut off mid-thought."

    unique_words = set(w.lower().rstrip(".,!?") for w in words)
    filler_words = {
        "oh",
        "ah",
        "um",
        "uh",
        "yeah",
        "yes",
        "no",
        "okay",
        "ok",
        "hey",
        "like",
        "well",
    }
    if unique_words.issubset(filler_words):
        return False, "Conversational filler / interjection."

    return True, ""


class OllamaClient:
    """Interfaces with Ollama REST API for low-latency debate reasoning."""

    def __init__(self, config: Config):
        """Initialize the Ollama client and resolve available model.

        :param config: Application configuration instance with Ollama settings.
        """
        self.config = config
        self.generate_url = f"{config.ollama_url.rstrip('/')}/api/generate"
        self.tags_url = f"{config.ollama_url.rstrip('/')}/api/tags"
        ensure_ollama_service(config.ollama_url, config.ollama_model)
        self.model = self._resolve_model()

    def _resolve_model(self) -> str:
        """Verify model availability in Ollama; fallback gracefully if possible.

        :return: Resolved model name string to use for inference.
        """
        try:
            data = _http_json(self.tags_url, timeout=2.0)
            models = [m.get("name", "") for m in data.get("models", [])]
            for m in models:
                if self.config.ollama_model in m or m.startswith(
                    self.config.ollama_model.split(":")[0]
                ):
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
            logger.warning(
                "Could not query Ollama tags (%s). Using '%s'.",
                e,
                self.config.ollama_model,
            )
        return self.config.ollama_model

    def warmup(self) -> bool:
        """Pre-warm model into VRAM to eliminate cold-start latency.

        :return: True if warmup inference succeeded, False otherwise.
        """
        try:
            logger.info("Warming up Ollama model '%s'...", self.model)
            _http_json(
                self.generate_url,
                payload={
                    "model": self.model,
                    "prompt": "ready",
                    "stream": False,
                    "options": {"num_predict": 1},
                },
                timeout=25.0,
            )
            return True
        except Exception as e:
            logger.warning("Ollama warmup failed: %s", e)
            return False

    def analyze(self, transcript: str) -> tuple[str, str]:
        """Analyze opponent transcript for logical fallacies and generate rebuttal.

        :param transcript: Opponent speech transcript.
        :return: Tuple of (flaw_text, counter_argument).
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
            data = _http_json(
                self.generate_url, payload=payload, timeout=self.config.ollama_timeout_s
            )
            raw_response = data.get("response", "").strip()
            return self._parse_debate_output(raw_response)
        except TimeoutError:
            logger.warning("Ollama request timed out (>%.1fs)", self.config.ollama_timeout_s)
            return (
                "Latency Warning",
                "Ollama took > 8s to respond. Inference dropped to maintain real-time sync.",
            )
        except urllib.error.URLError as e:
            logger.error("Ollama connection failed at %s: %s", self.config.ollama_url, e)
            avail, status_msg = ensure_ollama_service(self.config.ollama_url, self.model)
            return (
                "Ollama Offline",
                status_msg if not avail else f"Reconnecting: {status_msg}",
            )
        except Exception as e:
            logger.error("Error analyzing transcript with Ollama: %s", e)
            return (
                "Inference Error",
                str(e),
            )

    def _parse_debate_output(self, response_text: str) -> tuple[str, str]:
        """Parse structured Flaw and Counter lines from LLM response.

        :param response_text: Raw text generated by the LLM.
        :return: Tuple of (flaw_name, counter_text).
        """
        flaw = "Rhetorical Defect"
        counter = response_text

        flaw_match = re.search(r"[•\-*]?\s*Flaw:\s*([^\n\r]+)", response_text, re.IGNORECASE)
        counter_match = re.search(
            r"[•\-*]?\s*Counter:\s*(.+)", response_text, re.IGNORECASE | re.DOTALL
        )

        if flaw_match:
            flaw = flaw_match.group(1).strip()
        if counter_match:
            counter = counter_match.group(1).strip()

        counter = re.sub(r"^\s*[•\-*]\s*", "", counter).strip()

        return flaw, counter
