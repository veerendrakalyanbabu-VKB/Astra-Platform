from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from astra.core.intent.models import IntentResult
from astra.core.planner.plan import Plan
from astra.core.actions.result import ActionResult


@dataclass
class PipelineResult:
    input: str
    intent: IntentResult
    plan: Optional[Plan] = None
    reasoning: Optional[Dict[str, Any]] = None
    action_result: Optional[ActionResult] = None
    executed: bool = False
    blocked: bool = False
    needs_confirmation: bool = False
    message: str = ""
