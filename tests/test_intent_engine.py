import pytest

from astra.core.intent.intent_engine import IntentEngine
from astra.core.intent.intents import (
    DELETE_FILE,
    GET_TIME,
    HELP,
    LIST_MEMORY,
    OPEN_APP,
    RECALL_MEMORY,
    SAVE_MEMORY,
    UNKNOWN,
)
from astra.core.context import ContextEngine


@pytest.fixture
def intent_engine():
    return IntentEngine()


@pytest.fixture
def context_engine():
    return ContextEngine()


@pytest.fixture
def contextual_intent(context_engine):
    return IntentEngine(context_engine=context_engine)


@pytest.mark.parametrize(
    "text,expected_intent",
    [
        ("Open Chrome", OPEN_APP),
        ("Launch Calculator", OPEN_APP),
        ("Remember my favorite color is blue", SAVE_MEMORY),
        ("What is my favorite color", RECALL_MEMORY),
        ("Show my memory", LIST_MEMORY),
        ("What do you know", LIST_MEMORY),
        ("What so you know", LIST_MEMORY),
        ("What time is it?", GET_TIME),
        ("help", HELP),
        ("Delete old notes", DELETE_FILE),
        ("Do something random", UNKNOWN),
    ],
)
def test_intent_classification(intent_engine, text, expected_intent):
    result = intent_engine.process(text)
    assert result.intent == expected_intent


def test_open_app_entities(intent_engine):
    result = intent_engine.process("Open Chrome")
    assert result.entities["application"] == "chrome"


def test_save_memory_entities(intent_engine):
    result = intent_engine.process("Remember my favorite color is blue")
    assert result.entities["text"] == "my favorite color is blue"


def test_recall_memory_entities(intent_engine):
    result = intent_engine.process("What is my favorite color")
    assert result.entities["query"] == "favorite color"


def test_context_open_again(context_engine, contextual_intent):
    context_engine.update_state("last_application", "notepad")

    result = contextual_intent.process("open it again")

    assert result.intent == OPEN_APP
    assert result.entities["application"] == "notepad"
    assert result.confidence == 0.95
