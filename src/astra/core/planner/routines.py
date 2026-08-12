"""Built-in and custom multi-step goal routines."""

from astra.core.intent.intents import (
    GET_TIME,
    LIST_MEMORY,
    OPEN_APP,
    OPEN_FOLDER,
    SYSTEM_INFO,
)
from astra.core.planner.plan import PlanStep


BUILTIN_ROUTINES = {
    "morning": {
        "title": "Morning Routine",
        "description": "Check time, open browser, review memory",
        "steps": [
            PlanStep(GET_TIME, {}),
            PlanStep(OPEN_APP, {"application": "chrome"}),
            PlanStep(LIST_MEMORY, {}),
        ],
    },
    "work": {
        "title": "Work Start",
        "description": "System check, open code editor, show time",
        "steps": [
            PlanStep(SYSTEM_INFO, {}),
            PlanStep(OPEN_APP, {"application": "code"}),
            PlanStep(GET_TIME, {}),
        ],
    },
    "focus": {
        "title": "Focus Mode",
        "description": "Time check, open notepad, review memory",
        "steps": [
            PlanStep(GET_TIME, {}),
            PlanStep(OPEN_APP, {"application": "notepad"}),
            PlanStep(LIST_MEMORY, {}),
        ],
    },
    "downloads": {
        "title": "Downloads Check",
        "description": "Open Downloads folder and show system info",
        "steps": [
            PlanStep(OPEN_FOLDER, {"folder": "downloads"}),
            PlanStep(SYSTEM_INFO, {}),
        ],
    },
}


ROUTINE_ALIASES = {
    "morning routine": "morning",
    "morning": "morning",
    "start my day": "morning",
    "organize my morning routine": "morning",
    "run my morning routine": "morning",
    "work start": "work",
    "start work": "work",
    "work routine": "work",
    "focus mode": "focus",
    "focus routine": "focus",
    "focus": "focus",
    "downloads": "downloads",
    "check downloads": "downloads",
}


def resolve_routine(name: str, routine_store=None):
    normalized = name.lower().strip().replace(" ", "_")

    if routine_store:
        custom = routine_store.get_routine(normalized)
        if custom:
            return normalized, custom

        for key in routine_store.routines:
            if key == normalized or normalized.endswith(key) or key in normalized:
                custom = routine_store.get_routine(key)
                if custom:
                    return key, custom

    if normalized in ROUTINE_ALIASES:
        key = ROUTINE_ALIASES[normalized]
        return key, BUILTIN_ROUTINES[key]

    for alias, key in ROUTINE_ALIASES.items():
        if alias in normalized or normalized in alias:
            return key, BUILTIN_ROUTINES[key]

    if normalized in BUILTIN_ROUTINES:
        return normalized, BUILTIN_ROUTINES[normalized]

    return None, None


def list_routines(routine_store=None) -> list:
    routines = [
        {
            "key": key,
            "title": routine["title"],
            "description": routine["description"],
            "steps": len(routine["steps"]),
            "custom": False,
        }
        for key, routine in BUILTIN_ROUTINES.items()
    ]

    if routine_store:
        routines.extend(routine_store.list_all())

    return routines
