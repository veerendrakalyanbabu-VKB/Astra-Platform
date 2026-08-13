"""Tests for subsystem registry."""

from astra.core.subsystems.registry import route_intent, list_subsystems, INTENT_ROUTING


def test_route_intent_known():
    assert route_intent("GET_TIME") == "CORE"
    assert route_intent("CREATE_ROUTINE") == "PILOT"
    assert route_intent("SHOW_ROI") == "LEDGER"
    assert route_intent("DELETE_FILE") == "FORTRESS"


def test_route_ask_agent():
    assert route_intent("ASK_AGENT", {"agent": "pilot"}) == "PILOT"
    assert route_intent("ASK_AGENT", {"agent": "unknown"}) == "CORE"


def test_list_subsystems_includes_fortress():
    subs = list_subsystems("cosmic")
    names = [s["name"] for s in subs]
    assert "CORE" in names
    assert "FORTRESS" in names
    assert "NOVA" in names


def test_intent_routing_coverage():
    assert len(INTENT_ROUTING) >= 50
