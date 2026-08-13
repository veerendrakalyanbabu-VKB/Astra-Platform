"""Subsystem registry — truthful metadata for UI, routing, and capability center."""

from typing import Any, Dict, List, Optional

from astra.core.agents.squad import SQUAD, get_agent

# Intent → primary subsystem routing (FORTRESS wraps security decisions globally)
INTENT_ROUTING: Dict[str, str] = {
    "ASK_AGENT": "CORE",
    "ASK_KNOWLEDGE": "NOVA",
    "LEARN_TOPIC": "NOVA",
    "LIST_KNOWLEDGE": "NOVA",
    "MORNING_BRIEF": "CORE",
    "SHOW_SQUAD": "CORE",
    "REVOLUTION_STATUS": "CORE",
    "RUN_PROTOCOL": "CORE",
    "HELP": "MENTOR",
    "WHO_AM_I": "MENTOR",
    "CREATE_ROUTINE": "PILOT",
    "LIST_ROUTINES": "PILOT",
    "DELETE_ROUTINE": "PILOT",
    "SCHEDULE_ROUTINE": "PILOT",
    "LIST_SCHEDULES": "PILOT",
    "ACTIVATE_WORKSPACE": "PILOT",
    "RUN_GOAL": "PILOT",
    "FOCUS_TIMER": "PILOT",
    "OPEN_APP": "PILOT",
    "FOCUS_WINDOW": "PILOT",
    "SET_VOLUME": "PILOT",
    "MINIMIZE_ALL": "PILOT",
    "LIST_WINDOWS": "PILOT",
    "COPY_CLIPBOARD": "PILOT",
    "GET_CLIPBOARD": "PILOT",
    "SYSTEM_INFO": "PILOT",
    "OPEN_FOLDER": "PILOT",
    "SAVE_MEMORY": "CORE",
    "RECALL_MEMORY": "CORE",
    "LIST_MEMORY": "CORE",
    "SYNC_MEMORY": "CORE",
    "GET_TIME": "CORE",
    "CALCULATE": "LEDGER",
    "SHOW_ROI": "LEDGER",
    "SHOW_PLANS": "LAUNCH",
    "ACTIVATE_PLAN": "LAUNCH",
    "START_TRIAL": "LAUNCH",
    "LIST_MARKETPLACE": "LAUNCH",
    "INSTALL_PLUGIN": "LAUNCH",
    "LIST_PROFILES": "LAUNCH",
    "CREATE_PROFILE": "LAUNCH",
    "SWITCH_PROFILE": "LAUNCH",
    "SET_MODE": "LAUNCH",
    "SHOW_WEATHER": "NOVA",
    "SHOW_CALENDAR": "NOVA",
    "CONNECT_CALENDAR": "NOVA",
    "DETECT_LOCATION": "NOVA",
    "SET_CITY": "NOVA",
    "SHOW_VOICE_SETTINGS": "CORE",
    "SET_ASSISTANT_NAME": "CORE",
    "SET_WAKE_PHRASE": "CORE",
    "TOGGLE_WAKE_WORD": "CORE",
    "DELETE_FILE": "FORTRESS",
    "SHUTDOWN_PC": "FORTRESS",
    "FORMAT_DISK": "FORTRESS",
    "UNKNOWN": "CORE",
}

FORTRESS_META = {
    "id": "fortress",
    "name": "FORTRESS",
    "title": "Security & Privacy",
    "purpose": "Permission gates, audit logging, and privacy controls.",
    "what_it_does": (
        "Evaluates risk on every plan, blocks critical actions, requires confirmation "
        "for high-risk operations, and records audit events."
    ),
    "how_it_works": (
        "ReasoningEngine analyzes plan risk → SafetyEngine applies policies → "
        "PermissionManager holds pending confirmations → AuditLogger records outcomes."
    ),
    "inputs": ["Execution plans", "User confirmations", "Policy rules"],
    "outputs": ["ALLOW / CONFIRM / BLOCK decisions", "Audit log entries"],
    "capabilities": [
        "Risk classification (LOW / HIGH / CRITICAL)",
        "Confirmation gates",
        "Policy enforcement",
        "Audit trail",
        "Privacy snapshot",
    ],
    "dependencies": ["reasoning", "safety", "permissions", "audit"],
    "permissions": "Overrides all subsystems for dangerous actions",
    "status_label": "AVAILABLE",
    "color": "#6ee7b7",
    "emoji": "🛡",
    "tier": "cosmic",
    "examples": [
        "Blocks FORMAT_DISK without override",
        "Requires yes/no for DELETE_FILE",
        "Records every privileged execution",
    ],
}

CORE_META = {
    "id": "core",
    "name": "CORE",
    "title": "Chief Orchestrator",
    "purpose": "Central coordination and command lifecycle management.",
    "what_it_does": (
        "Receives commands, classifies intent, builds plans, coordinates subsystems, "
        "and returns structured results."
    ),
    "how_it_works": (
        "IntentEngine → SmartPlanner → ReasoningEngine → Executor → PipelineResult."
    ),
    "inputs": ["User commands", "Session context", "Memory"],
    "outputs": ["Responses", "Command records", "State updates"],
    "capabilities": [
        "Intent classification (56 intents)",
        "Compound commands",
        "Agent routing (ASK_AGENT)",
        "Memory orchestration",
        "Conversation fallback",
    ],
    "dependencies": ["intent", "pipeline", "context", "memory"],
    "permissions": "Routes all commands",
    "status_label": "AVAILABLE",
    "color": "#ffaa30",
    "emoji": "◈",
    "tier": "cosmic",
    "examples": [
        "morning brief",
        "show squad",
        "remember my goal is …",
        "ask core about system status",
    ],
}


def route_intent(intent: str, entities: Optional[dict] = None) -> str:
    entities = entities or {}
    if intent == "ASK_AGENT":
        agent = (entities.get("agent") or "").lower()
        agent_data = get_agent(agent)
        if agent_data:
            return agent_data["name"]
        return "CORE"
    return INTENT_ROUTING.get(intent, "CORE")


def _agent_to_subsystem(agent_key: str) -> Dict[str, Any]:
    agent = SQUAD.get(agent_key, {})
    return {
        "id": agent.get("id", agent_key),
        "name": agent.get("name", agent_key.upper()),
        "title": agent.get("title", ""),
        "purpose": agent.get("mandate", ""),
        "what_it_does": agent.get("mandate", ""),
        "how_it_works": (
            f"Persona layer: ASK_AGENT routes to {agent.get('name', '')} with "
            "specialized prompt template and tier gating."
        ),
        "inputs": ["Natural language queries", "Optional LLM context"],
        "outputs": ["Specialist responses"],
        "capabilities": [agent.get("mandate", "")],
        "dependencies": ["llm_responder", "knowledge", "memory"],
        "permissions": f"Tier: {agent.get('tier', 'cosmic')}",
        "status_label": "AVAILABLE",
        "color": agent.get("color", "#ffaa30"),
        "emoji": agent.get("emoji", "◈"),
        "tier": agent.get("tier", "cosmic"),
        "examples": [f"ask {agent.get('name', '').lower()} about …"],
    }


def list_subsystems(tier_id: str = "cosmic") -> List[Dict[str, Any]]:
    from astra.core.billing.tiers import tier_includes_agent

    subs = [CORE_META, FORTRESS_META]
    for key in ("nova", "pilot", "mentor", "launch", "ledger"):
        meta = _agent_to_subsystem(key)
        locked = not tier_includes_agent(tier_id, key)
        meta["locked"] = locked
        meta["status_label"] = "LOCKED" if locked else "AVAILABLE"
        subs.append(meta)
    return subs


def list_capabilities(core) -> List[Dict[str, Any]]:
    """Capabilities derived from registered intents and subsystem status."""
    llm_active = False
    llm_label = "Standby"
    if core and hasattr(core, "config"):
        llm_cfg = core.config.get("llm_config") or {}
        llm_active = llm_cfg.get("llm_active", False)
        llm_label = llm_cfg.get("llm_label", "Standby")

    caps: List[Dict[str, Any]] = [
        {
            "name": "Intent Command Engine",
            "category": "System",
            "description": "56 classified intents with pipeline orchestration.",
            "status": "AVAILABLE",
            "subsystem": "CORE",
            "example": "what time is it",
            "permissions": "SAFE",
        },
        {
            "name": "Knowledge Graph",
            "category": "Intelligence",
            "description": "Teach and retrieve topics stored locally.",
            "status": "AVAILABLE",
            "subsystem": "NOVA",
            "example": "learn that pods are smallest K8s units",
            "permissions": "CONTROLLED",
        },
        {
            "name": "LLM Research",
            "category": "Intelligence",
            "description": "LLM-assisted research and conversation.",
            "status": "AVAILABLE" if llm_active else "DEGRADED",
            "subsystem": "NOVA",
            "example": "learn about quantum computing",
            "permissions": "CONTROLLED",
            "detail": llm_label if not llm_active else "",
        },
        {
            "name": "Routines & Schedules",
            "category": "Automation",
            "description": "Multi-step routines and time-based schedules.",
            "status": "AVAILABLE",
            "subsystem": "PILOT",
            "example": "create routine morning: get time, open chrome",
            "permissions": "CONTROLLED",
        },
        {
            "name": "Windows Automation",
            "category": "Automation",
            "description": "Launch apps, focus windows, volume, clipboard (Windows).",
            "status": "AVAILABLE",
            "subsystem": "PILOT",
            "example": "focus notepad",
            "permissions": "CONTROLLED",
        },
        {
            "name": "Memory Vault",
            "category": "Memory",
            "description": "Local JSON memory store per profile.",
            "status": "AVAILABLE",
            "subsystem": "CORE",
            "example": "remember my meeting is at 3pm",
            "permissions": "CONTROLLED",
        },
        {
            "name": "ROI Tracking",
            "category": "Analytics",
            "description": "Estimates time saved from completed commands.",
            "status": "AVAILABLE",
            "subsystem": "LEDGER",
            "example": "show roi",
            "permissions": "SAFE",
        },
        {
            "name": "Permission Gates",
            "category": "Security",
            "description": "Confirmation required for high-risk OS actions.",
            "status": "AVAILABLE",
            "subsystem": "FORTRESS",
            "example": "delete file (requires confirmation)",
            "permissions": "HIGH RISK",
        },
        {
            "name": "Cloud Sync",
            "category": "Integrations",
            "description": "Optional encrypted bundle export/import.",
            "status": "BETA",
            "subsystem": "LAUNCH",
            "example": "sync my memory",
            "permissions": "CONTROLLED",
        },
        {
            "name": "Plugin Marketplace",
            "category": "Integrations",
            "description": "Install catalog plugins (weather, timer, quotes).",
            "status": "BETA",
            "subsystem": "LAUNCH",
            "example": "list marketplace",
            "permissions": "CONTROLLED",
        },
    ]
    return caps
