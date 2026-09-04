"""
LLM Client — CLI (Claude Code, Codex) and Ollama local providers.
"""

import json
import re
import socket
import subprocess
import time
import urllib.error
import urllib.request
from typing import Optional, Dict, Any, List

from ..config import Config
from .logger import get_logger

logger = get_logger('mirofish.llm_client')

MAX_RETRIES = 3
RETRY_BASE_DELAY = 2.0  # seconds


class LLMClient:
    """LLM Client — supports ollama, claude-cli, and codex-cli."""

    def __init__(self, provider: Optional[str] = None):
        self.provider = (provider or Config.LLM_PROVIDER or "claude-cli").lower()
        if self.provider not in ("claude-cli", "codex-cli", "ollama"):
            raise ValueError(f"Unsupported LLM provider: {self.provider!r}. Use 'ollama', 'claude-cli', or 'codex-cli'.")
        self.ollama_base_url = Config.OLLAMA_BASE_URL
        self.ollama_model = Config.OLLAMA_MODEL
        self.ollama_timeout = Config.OLLAMA_TIMEOUT
        logger.info(f"LLM client initialized: provider={self.provider}" + (f", model={self.ollama_model}" if self.provider == "ollama" else ""))

    def _split_system_message(self, messages: List[Dict[str, str]]):
        """Split system message from conversation messages."""
        system_text = None
        conversation = []

        for msg in messages:
            if msg.get("role") == "system":
                if system_text is None:
                    system_text = msg["content"]
                else:
                    system_text += "\n\n" + msg["content"]
            else:
                conversation.append(msg)

        return system_text, conversation

    def _clean_content(self, content: str) -> str:
        """Remove <think> tags from reasoning models."""
        return re.sub(r'<think>[\s\S]*?</think>', '', content).strip()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        response_format: Optional[Dict] = None
    ) -> str:
        """Send a chat request with automatic retry on transient failures."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                if self.provider == "ollama":
                    return self._chat_ollama(messages, temperature, max_tokens, response_format)
                elif self.provider == "codex-cli":
                    return self._chat_codex_cli(messages, temperature, max_tokens, response_format)
                return self._chat_claude_cli(messages, temperature, max_tokens, response_format)
            except RuntimeError as exc:
                last_error = exc
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    logger.warning(f"LLM call failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay}s: {exc}")
                    time.sleep(delay)
        raise last_error

    def _chat_ollama(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat via Ollama HTTP API (POST /api/generate)."""
        system_text, conversation = self._split_system_message(messages)

        prompt_parts = []
        for msg in conversation:
            role = msg.get("role", "user").upper()
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt = "\n\n".join(prompt_parts) if prompt_parts else (system_text or "")

        payload: Dict[str, Any] = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        if system_text:
            payload["system"] = system_text

        if max_tokens and max_tokens > 0:
            payload["options"]["num_predict"] = max(max_tokens, 4096)

        if response_format and response_format.get("type") == "json_object":
            payload["format"] = "json"

        endpoint = f"{self.ollama_base_url}/api/generate"
        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=req_data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=self.ollama_timeout) as response:
                response_bytes = response.read()
                data = json.loads(response_bytes.decode("utf-8"))

            content = data.get("response", "")
            if not content and not data.get("thinking"):
                raise RuntimeError("Ollama returned an empty response")

            return self._clean_content(content)

        except urllib.error.HTTPError as e:
            err_body = ""
            try:
                err_body = e.read().decode("utf-8")
                err_json = json.loads(err_body)
                err_msg = err_json.get("error", err_body)
            except Exception:
                err_msg = err_body or str(e)

            if e.code == 404 and "not found" in err_msg.lower():
                raise RuntimeError(
                    f"Ollama model '{self.ollama_model}' not found at {self.ollama_base_url}. "
                    f"Run `ollama pull {self.ollama_model}` to install it."
                ) from e
            raise RuntimeError(f"Ollama returned HTTP error {e.code}: {err_msg}") from e

        except (socket.timeout, TimeoutError) as e:
            raise RuntimeError(f"Ollama request timed out after {self.ollama_timeout}s at {self.ollama_base_url}") from e

        except urllib.error.URLError as e:
            if isinstance(e.reason, (socket.timeout, TimeoutError)):
                raise RuntimeError(f"Ollama request timed out after {self.ollama_timeout}s at {self.ollama_base_url}") from e
            raise RuntimeError(
                f"Ollama is not reachable at {self.ollama_base_url}. Start Ollama and try again."
            ) from e

        except (ConnectionRefusedError, OSError) as e:
            raise RuntimeError(
                f"Ollama is not reachable at {self.ollama_base_url}. Start Ollama and try again."
            ) from e

        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to decode response from Ollama: {e}") from e

    def _chat_claude_cli(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat via Claude Code CLI."""
        system_text, conversation = self._split_system_message(messages)

        prompt_parts = []
        if system_text:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{system_text}\n")

        if response_format and response_format.get("type") == "json_object":
            prompt_parts.append("IMPORTANT: Respond with valid JSON only. No markdown, no explanation, just pure JSON.\n")

        for msg in conversation:
            role = msg.get("role", "user").upper()
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt = "\n\n".join(prompt_parts)

        try:
            result = subprocess.run(
                ["claude", "-p", "--output-format", "json", prompt],
                capture_output=True, text=True, timeout=300,
                cwd="/tmp"
            )

            if result.returncode != 0:
                logger.error(f"Claude CLI error: {result.stderr[:200]}")
                raise RuntimeError(f"Claude CLI failed: {result.stderr[:200]}")

            try:
                output = json.loads(result.stdout)
                content = output.get("result", result.stdout)
            except json.JSONDecodeError:
                content = result.stdout.strip()

            return self._clean_content(content)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude CLI timed out after 300s")

    def _chat_codex_cli(
        self,
        messages: List[Dict[str, str]],
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict] = None
    ) -> str:
        """Chat via Codex CLI."""
        system_text, conversation = self._split_system_message(messages)

        prompt_parts = []
        if system_text:
            prompt_parts.append(f"SYSTEM INSTRUCTIONS:\n{system_text}\n")

        if response_format and response_format.get("type") == "json_object":
            prompt_parts.append("IMPORTANT: Respond with valid JSON only. No markdown, no explanation, just pure JSON.\n")

        for msg in conversation:
            role = msg.get("role", "user").upper()
            prompt_parts.append(f"{role}: {msg['content']}")

        prompt = "\n\n".join(prompt_parts)

        try:
            result = subprocess.run(
                ["codex", "exec", "--skip-git-repo-check"],
                input=prompt,
                capture_output=True, text=True, timeout=180,
                cwd="/tmp"
            )

            if result.returncode != 0:
                logger.error(f"Codex CLI error: {result.stderr[:200]}")
                raise RuntimeError(f"Codex CLI failed: {result.stderr[:200]}")

            raw = result.stdout.strip()
            parts = raw.split("\ncodex\n")
            if len(parts) > 1:
                content = parts[-1].strip()
                lines = content.split("\n")
                clean_lines = []
                for line in lines:
                    if line.strip() == "tokens used":
                        break
                    clean_lines.append(line)
                content = "\n".join(clean_lines).strip()
            else:
                content = raw
            return self._clean_content(content)

        except subprocess.TimeoutExpired:
            raise RuntimeError("Codex CLI timed out after 180s")

    @staticmethod
    def _extract_json(content: str) -> Dict[str, Any]:
        """Extract and parse JSON from model output handling markdown code blocks, think tags, and surrounding text."""
        cleaned = re.sub(r'<think>[\s\S]*?</think>', '', content).strip()

        # Check for markdown code blocks (```json ... ``` or ``` ... ```)
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned, flags=re.IGNORECASE)
        if code_block_match:
            candidate = code_block_match.group(1).strip()
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Try direct JSON parsing
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # Search for the outermost JSON object { ... }
        first_brace = cleaned.find('{')
        last_brace = cleaned.rfind('}')
        if first_brace != -1 and last_brace > first_brace:
            candidate = cleaned[first_brace:last_brace + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        # Search for the outermost JSON array [ ... ]
        first_bracket = cleaned.find('[')
        last_bracket = cleaned.rfind(']')
        if first_bracket != -1 and last_bracket > first_bracket:
            candidate = cleaned[first_bracket:last_bracket + 1]
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass

        raise ValueError(f"Invalid JSON returned by LLM: {cleaned[:500]}")

    def chat_json(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Send a chat request and return parsed JSON."""
        response = self.chat(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        return self._extract_json(response)

