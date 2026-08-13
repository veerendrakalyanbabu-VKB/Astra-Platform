"""Structured command lifecycle record for UI and audit transparency."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class CommandRecord:
    """One command execution through the ASTRA pipeline."""

    id: str
    timestamp: str
    command: str
    intent: str
    subsystem: str
    route: str
    plan: List[str] = field(default_factory=list)
    risk_level: str = "LOW"
    permission_state: str = "NOT_REQUIRED"
    execution_state: str = "PENDING"
    duration_ms: int = 0
    result_summary: str = ""
    verification: str = "NOT_RUN"
    audit_status: str = "RECORDED"
    confidence: Optional[float] = None
    why: str = ""
    source: str = "command"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def new_id() -> str:
        return uuid.uuid4().hex[:12].upper()


def build_command_record(result, duration_ms: int = 0, source: str = "command") -> Dict[str, Any]:
    """Build a CommandRecord dict from a PipelineResult."""
    from astra.core.subsystems.registry import route_intent

    intent_name = result.intent.intent if result.intent else "UNKNOWN"
    entities = result.intent.entities if result.intent else {}
    subsystem = route_intent(intent_name, entities)

    plan_steps: List[str] = []
    if result.plan:
        if result.plan.is_multi_step:
            plan_steps = [step.action for step in result.plan.steps]
        elif result.plan.action:
            plan_steps = [result.plan.action]

    risk = "LOW"
    permission = "NOT_REQUIRED"
    if result.reasoning:
        risk = result.reasoning.get("analysis", {}).get("risk", "LOW")
        decision = result.reasoning.get("decision", {}).get("decision", "EXECUTE")
        if decision == "CONFIRM":
            permission = "PENDING"
        elif decision == "BLOCK":
            permission = "DENIED"
        else:
            permission = "APPROVED"

    if result.needs_confirmation:
        permission = "PENDING"
    if result.blocked:
        permission = "DENIED"

    execution_state = "COMPLETED"
    if result.blocked:
        execution_state = "BLOCKED"
    elif result.needs_confirmation:
        execution_state = "AWAITING_CONFIRMATION"
    elif not result.executed:
        execution_state = "FAILED"

    verification = "NOT_RUN"
    if result.executed and result.action_result:
        verification = "PASSED" if result.action_result.success else "FAILED"
    elif result.executed and not result.action_result:
        verification = "PASSED"

    confidence = None
    if result.intent and hasattr(result.intent, "confidence"):
        confidence = result.intent.confidence

    why = _explain_result(result, subsystem, intent_name)

    record = CommandRecord(
        id=CommandRecord.new_id(),
        timestamp=datetime.now().isoformat(timespec="seconds"),
        command=result.input or "",
        intent=intent_name,
        subsystem=subsystem,
        route=f"{subsystem} → {intent_name}",
        plan=plan_steps,
        risk_level=risk,
        permission_state=permission,
        execution_state=execution_state,
        duration_ms=duration_ms,
        result_summary=(result.message or "")[:500],
        verification=verification,
        audit_status="RECORDED",
        confidence=confidence,
        why=why,
        source=source,
    )
    return record.to_dict()


def _explain_result(result, subsystem: str, intent_name: str) -> str:
    if result.blocked:
        return (
            f"FORTRESS blocked {intent_name} due to risk policy. "
            f"{result.message or 'Action not permitted.'}"
        )
    if result.needs_confirmation:
        return (
            f"High-risk action {intent_name} requires explicit yes/no confirmation "
            "before FORTRESS releases execution."
        )
    if result.executed:
        return (
            f"ASTRA CORE routed intent {intent_name} to {subsystem}, "
            f"executed the planned action, and returned the result."
        )
    if intent_name == "UNKNOWN":
        return (
            "No matching capability found. ASTRA attempted conversational fallback "
            "or suggested alternative commands."
        )
    return f"Command processed via {subsystem} for intent {intent_name}."
