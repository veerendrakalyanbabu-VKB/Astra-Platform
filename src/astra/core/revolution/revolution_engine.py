"""Industrial Revolution engine — tracks humanity's shift from apps to intent."""

import json
from datetime import datetime
from pathlib import Path

MANIFESTO = (
    "We are not building another chatbot. We are building the Industrial Revolution "
    "of computing — where human intent flows through agent factories, not app silos. "
    "One operator. One command layer. Infinite execution."
)

STAGES = (
    {"id": "awakening", "name": "Awakening", "min_commands": 0, "symbol": "◈"},
    {"id": "automation", "name": "Automation", "min_commands": 12, "symbol": "⚡"},
    {"id": "orchestration", "name": "Orchestration", "min_commands": 48, "symbol": "🔭"},
    {"id": "revolution", "name": "Revolution", "min_commands": 150, "symbol": "🚀"},
)


class RevolutionEngine:

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "data" / "revolution.json"
        self.state = self._load()

    def _load(self) -> dict:
        default = {
            "total_commands": 0,
            "successful_commands": 0,
            "agent_invocations": 0,
            "protocols_run": 0,
            "started_at": datetime.now().isoformat(),
        }
        if not self.state_file.exists():
            return default

        try:
            data = json.loads(self.state_file.read_text(encoding="utf-8"))
            return {**default, **data}
        except (json.JSONDecodeError, OSError):
            return default

    def _save(self) -> None:
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2), encoding="utf-8")

    def record_command(self, success: bool, intent: str = "") -> None:
        self.state["total_commands"] = self.state.get("total_commands", 0) + 1
        if success:
            self.state["successful_commands"] = self.state.get("successful_commands", 0) + 1
        if intent == "ASK_AGENT":
            self.state["agent_invocations"] = self.state.get("agent_invocations", 0) + 1
        self._save()

    def record_protocol(self) -> None:
        self.state["protocols_run"] = self.state.get("protocols_run", 0) + 1
        self._save()

    def stage(self) -> dict:
        total = self.state.get("total_commands", 0)
        current = STAGES[0]

        for stage in STAGES:
            if total >= stage["min_commands"]:
                current = stage

        next_stage = None
        for stage in STAGES:
            if stage["min_commands"] > total:
                next_stage = stage
                break

        progress = 100
        if next_stage:
            span = next_stage["min_commands"] - current["min_commands"]
            if span > 0:
                progress = int(((total - current["min_commands"]) / span) * 100)

        return {
            **current,
            "progress": min(progress, 100),
            "total_commands": total,
            "next": next_stage["name"] if next_stage else "Peak",
        }

    def automation_index(self, learning_stats: dict = None) -> int:
        total = max(self.state.get("total_commands", 0), 1)
        success = self.state.get("successful_commands", 0)
        base = (success / total) * 100

        if learning_stats:
            base = (base + learning_stats.get("success_rate", 0) * 100) / 2

        agents = min(self.state.get("agent_invocations", 0) * 2, 20)
        protocols = min(self.state.get("protocols_run", 0) * 5, 15)

        return int(min(99, base * 0.65 + agents + protocols))

    def dashboard(self, core) -> dict:
        learning = core.learning.stats() if core.learning else {}
        metrics = core.metrics.snapshot() if core.metrics else {"counters": {}}
        stage = self.stage()
        index = self.automation_index(learning)

        online = sum(
            1 for a in core.tiers.get_tier().get("agents", [])
            if isinstance(a, str)
        )

        return {
            "manifesto": MANIFESTO,
            "stage": stage,
            "automation_index": index,
            "automation_label": self._index_label(index),
            "total_commands": self.state.get("total_commands", 0),
            "protocols_run": self.state.get("protocols_run", 0),
            "agent_invocations": self.state.get("agent_invocations", 0),
            "intents_per_session": metrics["counters"].get("pipeline.requests", 0),
            "agents_online": online,
            "tagline": "Intent → Agents → Action",
        }

    def status_message(self, core) -> str:
        dash = self.dashboard(core)
        stage = dash["stage"]
        lines = [
            "◈ ASTRA INDUSTRIAL REVOLUTION",
            "",
            MANIFESTO,
            "",
            f"Stage: {stage['symbol']} {stage['name']} ({stage['progress']}% to {stage['next']})",
            f"Automation Index: {dash['automation_index']}/100 — {dash['automation_label']}",
            f"Commands executed: {dash['total_commands']} · Protocols: {dash['protocols_run']}",
            f"Agent invocations: {dash['agent_invocations']}",
            "",
            "Run: run student protocol | run startup protocol | run revolution protocol",
        ]
        return "\n".join(lines)

    def _index_label(self, index: int) -> str:
        if index >= 85:
            return "Full industrial orchestration"
        if index >= 65:
            return "Multi-agent factory online"
        if index >= 40:
            return "Automation accelerating"
        if index >= 20:
            return "Intent layer awakening"
        return "Manual era ending"
