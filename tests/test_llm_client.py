import os

from astra.core.llm.llm_client import resolve_llm_config, LLMClient


def test_resolve_prefers_anthropic_when_both_keys(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.delenv("ASTRA_LLM_PROVIDER", raising=False)

    cfg = resolve_llm_config()
    assert cfg["provider"] == "anthropic"
    assert cfg["llm_active"] is True
    assert cfg["llm_label"] == "Claude Active"


def test_resolve_openai_when_forced(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.setenv("ASTRA_LLM_PROVIDER", "openai")

    cfg = resolve_llm_config()
    assert cfg["provider"] == "openai"
    assert cfg["llm_label"] == "GPT Active"


def test_llm_client_disabled_without_keys(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    client = LLMClient()
    assert client.enabled is False
    assert client.chat("sys", "hi") is None
