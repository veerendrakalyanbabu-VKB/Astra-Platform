import json
from datetime import datetime
from pathlib import Path


class SessionManager:
    """
    Persists and restores session context across restarts.
    """

    def __init__(self, session_path: Path = None):
        self.session_path = session_path or Path("data/session.json")

    def save(self, context_engine) -> None:
        self.session_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "saved_at": datetime.now().isoformat(),
            "conversation": context_engine.conversation.all(),
            "history": context_engine.history.all(),
            "state": context_engine.state.all(),
        }

        with open(self.session_path, "w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def restore(self, context_engine) -> bool:
        if not self.session_path.exists():
            return False

        with open(self.session_path, "r", encoding="utf-8") as file:
            payload = json.load(file)

        for message in payload.get("conversation", []):
            context_engine.conversation.add(
                message["speaker"],
                message["text"],
            )

        for command in payload.get("history", []):
            context_engine.history.add(command)

        for key, value in payload.get("state", {}).items():
            context_engine.state.set(key, value)

        return True

    def clear(self) -> None:
        if self.session_path.exists():
            self.session_path.unlink()

    def reconfigure(self, session_path: Path) -> None:
        self.session_path = Path(session_path)
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
