"""Parse natural-language routine steps into pipeline actions."""

import re

from astra.core.intent.intents import (
    GET_CLIPBOARD,
    GET_TIME,
    FOCUS_WINDOW,
    LIST_MEMORY,
    LIST_WINDOWS,
    MINIMIZE_ALL,
    OPEN_APP,
    OPEN_FOLDER,
    SET_VOLUME,
    SYSTEM_INFO,
)
from astra.core.planner.plan import PlanStep


STEP_RULES = [
    (re.compile(r"^(get time|what time|show time|time)$"), GET_TIME, {}),
    (re.compile(r"^(show memory|list memory|my memory|memory)$"), LIST_MEMORY, {}),
    (re.compile(r"^(system info|computer info)$"), SYSTEM_INFO, {}),
    (re.compile(r"^(show clipboard|get clipboard|clipboard)$"), GET_CLIPBOARD, {}),
    (re.compile(r"^(minimize all|minimize windows|show desktop)$"), MINIMIZE_ALL, {}),
    (re.compile(r"^(list windows|show windows|windows)$"), LIST_WINDOWS, {}),
    (
        re.compile(r"^open (chrome|notepad|calc|calculator|code|vscode)$"),
        OPEN_APP,
        lambda match: {"application": "calc" if match.group(1) == "calculator" else match.group(1)},
    ),
    (
        re.compile(r"^open folder (downloads|documents|desktop|home)$"),
        OPEN_FOLDER,
        lambda match: {"folder": match.group(1)},
    ),
    (
        re.compile(r"^focus (chrome|notepad|calc|calculator|code|vscode|.+)$"),
        FOCUS_WINDOW,
        lambda match: {"application": match.group(1)},
    ),
    (
        re.compile(r"^(set volume|volume) (\d+)$"),
        SET_VOLUME,
        lambda match: {"level": int(match.group(2))},
    ),
]


def parse_steps(steps_text: str) -> list:
    parts = [part.strip().lower() for part in steps_text.split(",") if part.strip()]
    steps = []
    errors = []

    for part in parts:
        matched = False

        for pattern, action, params in STEP_RULES:
            match = pattern.match(part)

            if match:
                parameters = params(match) if callable(params) else dict(params)
                steps.append(PlanStep(action, parameters))
                matched = True
                break

        if not matched:
            errors.append(part)

    return steps, errors
