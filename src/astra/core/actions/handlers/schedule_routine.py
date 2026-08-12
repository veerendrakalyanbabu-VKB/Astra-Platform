from typing import Dict

from astra.core.intent.intents import SCHEDULE_ROUTINE, LIST_SCHEDULES
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


class ScheduleRoutineHandler(ActionHandler):

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def can_handle(self, action: str) -> bool:
        return action == SCHEDULE_ROUTINE

    def execute(self, parameters: Dict) -> ActionResult:
        routine = parameters.get("routine", "").strip()
        time_str = parameters.get("time", "08:00")
        command = parameters.get("command", "").strip()

        if not routine:
            return ActionResult(
                success=False,
                message=(
                    "Usage: schedule morning brief at 8am | "
                    "schedule startup protocol at 7:30am"
                ),
                error="MISSING_ROUTINE",
            )

        entry = self.scheduler.add(routine, time_str, command or None)

        return ActionResult(
            success=True,
            message=(
                f"Scheduled daily at {entry['time']}: {entry['command']}. "
                "Say 'list schedules' to review."
            ),
            data=entry,
        )


class ListSchedulesHandler(ActionHandler):

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def can_handle(self, action: str) -> bool:
        return action == LIST_SCHEDULES

    def execute(self, parameters: Dict) -> ActionResult:
        schedules = self.scheduler.list_all()

        if not schedules:
            return ActionResult(
                success=True,
                message=(
                    "No schedules yet. Try:\n"
                    "  schedule morning brief at 8am\n"
                    "  schedule startup protocol at 7am"
                ),
            )

        lines = ["Scheduled automations:", ""]
        for entry in schedules:
            status = "ON" if entry.get("enabled", True) else "OFF"
            lines.append(
                f"  {entry['time']} [{status}] → {entry.get('command', entry['routine'])}"
            )

        return ActionResult(success=True, message="\n".join(lines))
