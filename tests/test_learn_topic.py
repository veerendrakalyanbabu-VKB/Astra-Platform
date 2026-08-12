"""Tests for topic learning / knowledge graph growth."""

import json
from pathlib import Path

import pytest

from astra.core.knowledge.knowledge_engine import KnowledgeEngine
from astra.core.actions.handlers.learn_topic import LearnTopicHandler
from astra.core.actions.handlers.list_knowledge import ListKnowledgeHandler


@pytest.fixture
def knowledge_path(tmp_path):
    return tmp_path / "knowledge.json"


@pytest.fixture
def engine(knowledge_path):
    return KnowledgeEngine(knowledge_path)


def test_add_entry_persists(engine, knowledge_path):
    engine.add_entry("kubernetes", "Pods are the smallest deployable units.", keywords=["k8s", "pods"])
    assert engine.topic_count() >= 7  # 6 defaults + 1
    data = json.loads(knowledge_path.read_text(encoding="utf-8"))
    assert any(e["topic"] == "kubernetes" for e in data["entries"])


def test_add_entry_updates_existing(engine):
    engine.add_entry("docker", "Containers package apps.")
    engine.add_entry("docker", "Containers package apps with images.")
    results = engine.search("docker containers")
    assert results[0]["content"].startswith("Containers package apps with")


def test_learn_topic_direct(engine):
    handler = LearnTopicHandler(engine, llm_responder=None)
    result = handler.execute({
        "topic": "",
        "content": "Neural networks use layers of weighted nodes.",
        "raw": "learn that neural networks use layers of weighted nodes",
    })
    assert result.success
    assert "neural" in result.message.lower() or "neural" in engine.best_match("neural networks").lower()


def test_list_knowledge(engine):
    engine.add_entry("rust_lang", "Rust is memory-safe systems language.", source="learned")
    handler = ListKnowledgeHandler(engine)
    result = handler.execute({})
    assert result.success
    assert "rust_lang" in result.message


def test_stats(engine):
    engine.add_entry("topic_a", "Content A", source="learned")
    stats = engine.stats()
    assert stats["total"] >= 7
    assert stats["learned"] >= 1
