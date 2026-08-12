from typing import Dict

from astra.core.intent.intents import HELP
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult


HELP_TEXT = """I can help you with:

  === COSMIC (FREE FOREVER) ===
  Daily       morning brief · show weather · detect my location
  Agents      ask nova about trends · ask pilot to plan my day
              ask mentor to explain loops (local coach on Cosmic)
  Goals       organize my morning routine · plan my study session
  Routines    create routine myday: get time, open notepad | list routines
  Schedule    schedule morning brief at 8am | list schedules
  Workspaces  activate coding workspace | focus workspace | student mode
  Apps        open chrome | launch calculator | start notepad
  Windows     system info | focus notepad | set volume 50 | minimize all
  Memory      remember my favorite color is blue | show my memory
  Learn       learn about Kubernetes | learn that pods are smallest units in K8s
              show knowledge | what have you learned
  Command OS  show squad | industrial revolution | revolution status
  Voice       python main.py --voice | python main.py --wake (Alexa-style)
  Integrations show weather | show calendar | set city to Paris | focus timer 25

  === CAMPUS+ (OPTIONAL, WHEN YOU CAN) ===
  Portal      python main.py --portal  (30-day free trial · no card)
  Trial       start campus trial | start startup trial | show plans

  System      help | exit

Cosmic: 75 action commands/day · weather, voice, 3 agents · resets at midnight.
High-risk actions ask for confirmation. Critical actions are blocked."""


class HelpHandler(ActionHandler):

    def can_handle(self, action: str) -> bool:
        return action == HELP

    def execute(self, parameters: Dict) -> ActionResult:
        return ActionResult(
            success=True,
            message=HELP_TEXT,
        )
