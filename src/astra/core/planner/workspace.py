"""Workspace layout presets."""

from astra.core.planner.plan import PlanStep
from astra.core.intent.intents import (
    GET_TIME,
    LIST_MEMORY,
    MINIMIZE_ALL,
    OPEN_APP,
    SET_VOLUME,
    SYSTEM_INFO,
)


WORKSPACES = {
    "coding": {
        "title": "Coding Workspace",
        "description": "Minimize distractions, open VS Code, show time",
        "steps": [
            PlanStep(MINIMIZE_ALL, {}),
            PlanStep(OPEN_APP, {"application": "code"}),
            PlanStep(GET_TIME, {}),
        ],
    },
    "focus": {
        "title": "Focus Workspace",
        "description": "Clean desktop, notepad, memory review",
        "steps": [
            PlanStep(MINIMIZE_ALL, {}),
            PlanStep(OPEN_APP, {"application": "notepad"}),
            PlanStep(LIST_MEMORY, {}),
        ],
    },
    "chill": {
        "title": "Chill Workspace",
        "description": "Low volume, browser, system info",
        "steps": [
            PlanStep(SET_VOLUME, {"level": 30}),
            PlanStep(OPEN_APP, {"application": "chrome"}),
            PlanStep(SYSTEM_INFO, {}),
        ],
    },
}


def resolve_workspace(name: str):
    normalized = name.lower().strip().replace(" workspace", "")

    for key, workspace in WORKSPACES.items():
        if key in normalized or normalized == key:
            return key, workspace

    return None, None


def list_workspaces() -> list:
    return [
        {
            "key": key,
            "title": workspace["title"],
            "description": workspace["description"],
            "steps": len(workspace["steps"]),
        }
        for key, workspace in WORKSPACES.items()
    ]
