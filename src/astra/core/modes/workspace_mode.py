"""Workspace modes: personal, startup, student."""

MODES = {
    "personal": {
        "id": "personal",
        "label": "Personal",
        "description": "Everyday productivity and memory.",
        "suggestions": [
            "what time is it",
            "show my memory",
            "organize my morning routine",
        ],
    },
    "student": {
        "id": "student",
        "label": "Campus",
        "description": "Study sessions, explainers, and exam prep with MENTOR.",
        "suggestions": [
            "ask mentor to explain recursion",
            "plan my study session",
            "quiz me on python basics",
            "help me write a project outline",
        ],
    },
    "startup": {
        "id": "startup",
        "label": "Startup",
        "description": "Founder ops, pitch, GTM, and runway with LAUNCH + LEDGER.",
        "suggestions": [
            "ask launch for a one-line pitch",
            "ask ledger about runway math",
            "plan my work morning",
            "morning brief",
        ],
    },
}


class WorkspaceMode:

    KEY = "workspace_mode"

    def __init__(self, memory_manager, tier_manager):
        self.memory = memory_manager
        self.tiers = tier_manager

    def get_mode(self) -> str:
        return self.memory.recall(self.KEY) or "personal"

    def set_mode(self, mode: str) -> dict:
        mode = mode.lower().strip()

        if mode not in MODES:
            return {
                "success": False,
                "message": f"Unknown mode. Choose: {', '.join(MODES)}",
            }

        if mode == "startup" and not self.tiers.has_feature("startup_mode"):
            return {
                "success": False,
                "message": "Startup mode requires the Startup plan. Say 'show plans' to upgrade.",
            }

        if mode == "student" and not self.tiers.has_feature("student_mode"):
            return {
                "success": False,
                "message": "Student mode requires Campus plan or higher.",
            }

        self.memory.remember(self.KEY, mode)
        label = MODES[mode]["label"]
        return {
            "success": True,
            "message": f"Mode set to {label}. Your squad is tuned for this workflow.",
        }

    def get_info(self) -> dict:
        mode_id = self.get_mode()
        mode = MODES.get(mode_id, MODES["personal"])
        return {
            "mode": mode_id,
            **mode,
            "suggestions": mode["suggestions"],
        }
