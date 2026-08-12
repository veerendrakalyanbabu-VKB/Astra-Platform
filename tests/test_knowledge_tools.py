import json
from unittest.mock import MagicMock

from astra.core.actions.handlers.calculate import CalculateHandler
from astra.core.actions.handlers.ask_knowledge import AskKnowledgeHandler
from astra.core.knowledge import KnowledgeEngine
from astra.core.tools import ToolManager, register_builtin_tools
from astra.core.intent.intent_engine import IntentEngine


def test_calculate_intent():
    engine = IntentEngine()
    result = engine.process("Calculate 15 * 7")

    assert result.intent == "CALCULATE"
    assert result.entities["expression"] == "15 * 7"


def test_ask_knowledge_intent():
    engine = IntentEngine()
    result = engine.process("What is astra")

    assert result.intent == "ASK_KNOWLEDGE"
    assert result.entities["query"] == "astra"


def test_calculate_handler():
    tools = ToolManager()
    register_builtin_tools(tools)
    handler = CalculateHandler(tools)

    result = handler.execute({"expression": "10 + 5"})

    assert result.success is True
    assert "15" in result.message


def test_ask_knowledge_handler():
    knowledge = KnowledgeEngine()
    handler = AskKnowledgeHandler(knowledge)

    result = handler.execute({"query": "astra"})

    assert result.success is True
    assert "AI-native" in result.message
