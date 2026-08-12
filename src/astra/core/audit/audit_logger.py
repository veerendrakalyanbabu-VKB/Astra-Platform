from datetime import datetime
from pathlib import Path


class AuditLogger:
    """
    Security audit trail for privileged and blocked actions.
    """

    def __init__(self, audit_path: Path = None, enabled: bool = True):
        self.enabled = enabled
        self.audit_path = audit_path or Path("logs/audit.log")
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, event: str, action: str, decision: str, details: str = "") -> None:
        if not self.enabled:
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{timestamp}] {event} | action={action} | decision={decision}"

        if details:
            line += f" | {details}"

        with open(self.audit_path, "a", encoding="utf-8") as file:
            file.write(line + "\n")

    def log_execute(self, action: str, success: bool) -> None:
        self.record(
            "EXECUTE",
            action,
            "SUCCESS" if success else "FAILED",
        )

    def log_block(self, action: str, reason: str) -> None:
        self.record("BLOCK", action, "BLOCKED", reason)

    def log_confirm(self, action: str, approved: bool) -> None:
        self.record(
            "CONFIRM",
            action,
            "APPROVED" if approved else "DENIED",
        )
