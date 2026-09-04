"""Tests for Ollama LLM Client integration and JSON parsing."""

import io
import json
import socket
import urllib.error
import urllib.request
from unittest.mock import MagicMock, patch

import pytest

from app.config import Config
from app.utils.llm_client import LLMClient
from app.utils.oasis_llm import create_oasis_model, CLIModel


def test_config_validation_accepts_ollama(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Config, "LLM_PROVIDER", "ollama")
    assert Config.validate() == []

    monkeypatch.setattr(Config, "LLM_PROVIDER", "claude-cli")
    assert Config.validate() == []

    monkeypatch.setattr(Config, "LLM_PROVIDER", "codex-cli")
    assert Config.validate() == []

    monkeypatch.setattr(Config, "LLM_PROVIDER", "unsupported-provider")
    errors = Config.validate()
    assert len(errors) == 1
    assert "LLM_PROVIDER must be 'claude-cli', 'codex-cli', or 'ollama'" in errors[0]


def test_llm_client_initialization(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Config, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(Config, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(Config, "OLLAMA_MODEL", "qwen3:8b")

    client = LLMClient()
    assert client.provider == "ollama"
    assert client.ollama_base_url == "http://localhost:11434"
    assert client.ollama_model == "qwen3:8b"

    with pytest.raises(ValueError, match="Unsupported LLM provider"):
        LLMClient(provider="invalid-backend")


def test_ollama_chat_success(monkeypatch: pytest.MonkeyPatch):
    client = LLMClient(provider="ollama")

    fake_response_data = {
        "model": "qwen3:8b",
        "response": "Hello world from Qwen3!",
        "thinking": "Thinking about greeting...",
        "done": True
    }
    fake_body = json.dumps(fake_response_data).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_body
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        result = client.chat(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello"},
            ],
            temperature=0.5,
        )

        assert result == "Hello world from Qwen3!"
        assert mock_urlopen.called
        req = mock_urlopen.call_args[0][0]
        assert isinstance(req, urllib.request.Request)
        assert req.full_url == "http://localhost:11434/api/generate"
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["model"] == "qwen3:8b"
        assert payload["system"] == "You are a helpful assistant."
        assert "USER: Say hello" in payload["prompt"]
        assert payload["options"]["temperature"] == 0.5


def test_ollama_chat_cleans_think_tags():
    client = LLMClient(provider="ollama")

    fake_response_data = {
        "model": "qwen3:8b",
        "response": "<think>Let me formulate the answer.</think>Final answer content.",
        "done": True
    }
    fake_body = json.dumps(fake_response_data).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_body
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = client.chat(messages=[{"role": "user", "content": "Test"}])
        assert result == "Final answer content."


def test_ollama_chat_json_success():
    client = LLMClient(provider="ollama")

    expected_dict = {"entities": ["Alice", "Bob"], "confidence": 0.95}
    fake_response_data = {
        "model": "qwen3:8b",
        "response": json.dumps(expected_dict),
        "done": True
    }
    fake_body = json.dumps(fake_response_data).encode("utf-8")

    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_body
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        result = client.chat_json(
            messages=[{"role": "user", "content": "Extract entities"}],
            temperature=0.2,
        )

        assert result == expected_dict
        req = mock_urlopen.call_args[0][0]
        payload = json.loads(req.data.decode("utf-8"))
        assert payload["format"] == "json"


def test_extract_json_edge_cases():
    client = LLMClient(provider="ollama")

    # 1. Pure markdown code block
    md_json = "```json\n{\"key\": \"value\", \"num\": 42}\n```"
    assert client._extract_json(md_json) == {"key": "value", "num": 42}

    # 2. Markdown without language tag
    md_no_lang = "```\n{\"key\": \"value2\"}\n```"
    assert client._extract_json(md_no_lang) == {"key": "value2"}

    # 3. Explanatory text surrounding JSON
    surrounded = "Here is the requested output:\n```json\n{\"prediction\": \"high\", \"signals\": [1, 2]}\n```\nHope that helps!"
    assert client._extract_json(surrounded) == {"prediction": "high", "signals": [1, 2]}

    # 4. Embedded JSON object without markdown fences
    raw_embedded = "Based on our analysis, the verdict is {\"status\": \"passed\", \"score\": 0.88} as expected."
    assert client._extract_json(raw_embedded) == {"status": "passed", "score": 0.88}

    # 5. Embedded JSON array
    array_embedded = "The top items are [\"item1\", \"item2\", \"item3\"] in order."
    assert client._extract_json(array_embedded) == ["item1", "item2", "item3"]

    # 6. With <think> tag
    think_json = "<think>Calculating JSON...</think>```json\n{\"ok\": true}\n```"
    assert client._extract_json(think_json) == {"ok": True}

    # 7. Invalid JSON throws ValueError
    with pytest.raises(ValueError, match="Invalid JSON returned by LLM"):
        client._extract_json("No json here at all")


def test_ollama_error_handling_not_reachable():
    client = LLMClient(provider="ollama")

    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")):
        with pytest.raises(RuntimeError, match="Ollama is not reachable at"):
            client.chat(messages=[{"role": "user", "content": "hi"}])


def test_ollama_error_handling_model_not_found():
    client = LLMClient(provider="ollama")

    err_json = json.dumps({"error": "model 'qwen3:8b' not found"}).encode("utf-8")
    http_err = urllib.error.HTTPError(
        url="http://localhost:11434/api/generate",
        code=404,
        msg="Not Found",
        hdrs=MagicMock(),
        fp=io.BytesIO(err_json)
    )

    with patch("urllib.request.urlopen", side_effect=http_err):
        with pytest.raises(RuntimeError, match="Run `ollama pull qwen3:8b`"):
            client.chat(messages=[{"role": "user", "content": "hi"}])


def test_ollama_error_handling_timeout():
    client = LLMClient(provider="ollama")

    with patch("urllib.request.urlopen", side_effect=TimeoutError("Request timed out")):
        with pytest.raises(RuntimeError, match="timed out"):
            client.chat(messages=[{"role": "user", "content": "hi"}])


def test_ollama_error_handling_empty_response():
    client = LLMClient(provider="ollama")

    mock_resp = MagicMock()
    mock_resp.read.return_value = json.dumps({"response": "", "done": True}).encode("utf-8")
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(RuntimeError, match="Ollama returned an empty response"):
            client.chat(messages=[{"role": "user", "content": "hi"}])


def test_create_oasis_model_with_ollama(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(Config, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(Config, "OLLAMA_MODEL", "qwen3:8b")

    model = create_oasis_model({"llm_provider": "ollama"})
    assert isinstance(model, CLIModel)
    assert model.provider == "ollama"
    assert model.model_type == "qwen3:8b"
    assert model._llm.provider == "ollama"


@pytest.mark.integration
def test_live_ollama_connectivity_and_chat():
    """Live test against local Ollama instance if available."""
    try:
        req = urllib.request.Request("http://localhost:11434/api/tags")
        with urllib.request.urlopen(req, timeout=2) as res:
            if res.status != 200:
                pytest.skip("Ollama is not responding with 200 on /api/tags")
    except Exception:
        pytest.skip("Local Ollama server is not running")

    client = LLMClient(provider="ollama")
    response = client.chat(
        messages=[{"role": "user", "content": "Reply with only the single word PONG."}],
        temperature=0.1,
    )
    assert "pong" in response.lower()

    json_response = client.chat_json(
        messages=[
            {"role": "system", "content": "Return JSON with test_status: 'ok'."},
            {"role": "user", "content": "Generate JSON status."},
        ],
        temperature=0.1,
    )
    assert isinstance(json_response, dict)
    assert "test_status" in json_response or "status" in json_response
