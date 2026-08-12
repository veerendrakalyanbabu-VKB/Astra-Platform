from typing import Dict

from astra.core.intent.intents import (
    MORNING_BRIEF,
    ASK_AGENT,
    SET_MODE,
    SHOW_PLANS,
    SHOW_SQUAD,
    ACTIVATE_PLAN,
    REVOLUTION_STATUS,
    RUN_PROTOCOL,
    SHOW_ROI,
    START_TRIAL,
)
from astra.core.actions.handlers.base import ActionHandler
from astra.core.actions.result import ActionResult
from astra.core.billing.tiers import TIERS
from astra.core.agents import squad
from astra.core.agents.agent_replies import local_agent_reply
from astra.core.billing.stripe_billing import PORTAL_BASE, billing_status


class ActivatePlanHandler(ActionHandler):

    def __init__(self, tier_manager):
        self.tiers = tier_manager

    def can_handle(self, action: str) -> bool:
        return action == ACTIVATE_PLAN

    def execute(self, parameters: Dict) -> ActionResult:
        tier_id = parameters.get("tier", "campus")
        result = self.tiers.demo_activate(tier_id)
        return ActionResult(success=result["success"], message=result["message"])


class MorningBriefHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == MORNING_BRIEF

    def execute(self, parameters: Dict) -> ActionResult:
        brief = self.core.morning_brief.generate()
        return ActionResult(
            success=brief["available"],
            message=brief["message"],
            data=brief,
        )


class AskAgentHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == ASK_AGENT

    def execute(self, parameters: Dict) -> ActionResult:
        agent_id = parameters.get("agent", "core")
        query = parameters.get("query", "").strip()

        if not query:
            return ActionResult(success=False, message="What should the agent help with?")

        if not self.core.tiers.tier_includes(agent_id):
            agent = squad.get_agent(agent_id)
            name = agent["name"] if agent else agent_id.upper()
            memory = self.core.memory.list_all()
            offline = local_agent_reply(agent_id, query, memory)
            if offline:
                return ActionResult(
                    success=True,
                    message=(
                        f"{agent['emoji']} {name} (local coach): {offline}\n\n"
                        f"Campus unlocks full {name} with Claude/OpenAI when you're ready."
                    ),
                    data={"agent": agent_id, "source": "local", "tier_limited": True},
                )
            return ActionResult(
                success=False,
                message=(
                    f"{name} needs a quick upgrade for that topic. "
                    f"Try 'ask nova about {query[:40]}' or say 'show plans'."
                ),
            )

        prompt = squad.agent_prompt(agent_id, query)
        memory = self.core.memory.list_all()

        if self.core.llm_responder and self.core.llm_responder.enabled:
            answer = self.core.llm_responder.respond(prompt, memory)
            if answer:
                agent = squad.get_agent(agent_id)
                header = f"{agent['emoji']} {agent['name']}: "
                return ActionResult(success=True, message=header + answer, data={"agent": agent_id})

        offline = local_agent_reply(agent_id, query, memory)
        agent = squad.get_agent(agent_id)
        if offline:
            return ActionResult(
                success=True,
                message=f"{agent['emoji']} {agent['name']}: {offline}",
                data={"agent": agent_id, "source": "local"},
            )

        return ActionResult(
            success=True,
            message=(
                f"{agent['emoji']} {agent['name']} ({agent['title']}): "
                f"I'd help with '{query}'. Add OPENAI_API_KEY for deeper agent responses."
            ),
            data={"agent": agent_id},
        )


class SetModeHandler(ActionHandler):

    def __init__(self, workspace_mode):
        self.modes = workspace_mode

    def can_handle(self, action: str) -> bool:
        return action == SET_MODE

    def execute(self, parameters: Dict) -> ActionResult:
        mode = parameters.get("mode", "personal")
        result = self.modes.set_mode(mode)
        return ActionResult(success=result["success"], message=result["message"])


class ShowPlansHandler(ActionHandler):

    def __init__(self, tier_manager):
        self.tiers = tier_manager

    def can_handle(self, action: str) -> bool:
        return action == SHOW_PLANS

    def execute(self, parameters: Dict) -> ActionResult:
        current = self.tiers.get_tier()
        status = billing_status()
        lines = [
            f"Current plan: {current['name']} — {current['price_label']}",
            "",
            "Available plans:",
        ]

        for tier_id, tier in TIERS.items():
            marker = " ← YOU" if tier_id == current["id"] else ""
            lines.append(f"  {tier['name']:12} {tier['price_label']:22} {tier['tagline']}{marker}")

        lines.extend([
            "",
            f"Upgrade portal: {status['portal_url']}",
            f"Billing mode: {status['mode']}",
            f"Free trial: 30 days on Campus & Startup — say 'start campus trial'",
        ])

        if status["mode"] == "demo":
            lines.append("Demo upgrade: say 'activate campus plan' or 'activate startup plan'")
        else:
            lines.append("Live Stripe checkout available on the portal.")

        return ActionResult(success=True, message="\n".join(lines))


class ShowSquadHandler(ActionHandler):

    def __init__(self, tier_manager):
        self.tiers = tier_manager

    def can_handle(self, action: str) -> bool:
        return action == SHOW_SQUAD

    def execute(self, parameters: Dict) -> ActionResult:
        agents = squad.list_agents(self.tiers.tier_id)
        lines = ["Astra Agent Squad:", ""]

        for agent in agents:
            status = "ONLINE" if agent["online"] else "LOCKED"
            lines.append(
                f"  {agent['emoji']} {agent['name']} — {agent['title']} [{status}]"
            )
            lines.append(f"     {agent['mandate']}")

        lines.append("")
        lines.append("Talk to an agent: ask nova about AI trends | ask mentor to explain loops")
        lines.append("Industrial: run student protocol | run startup protocol | industrial revolution")

        return ActionResult(success=True, message="\n".join(lines))


class RevolutionStatusHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == REVOLUTION_STATUS

    def execute(self, parameters: Dict) -> ActionResult:
        message = self.core.revolution.status_message(self.core)
        return ActionResult(success=True, message=message, data=self.core.revolution.dashboard(self.core))


class RunProtocolHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == RUN_PROTOCOL

    def execute(self, parameters: Dict) -> ActionResult:
        from astra.core.revolution.protocols import IndustrialProtocol

        protocol_id = parameters.get("protocol", "revolution")
        result = IndustrialProtocol(self.core).run(protocol_id)
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result,
        )


class ShowROIHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == SHOW_ROI

    def execute(self, parameters: Dict) -> ActionResult:
        message = self.core.roi.status_message()
        trial = self.core.trial.snapshot()
        if trial.get("on_trial"):
            days = trial.get("days_remaining", 0)
            message += f"\n\nTrial: {days} days left — subscribe before you lose full squad access."
        return ActionResult(
            success=True,
            message=message,
            data=self.core.roi.dashboard(),
        )


class StartTrialHandler(ActionHandler):

    def __init__(self, core):
        self.core = core

    def can_handle(self, action: str) -> bool:
        return action == START_TRIAL

    def execute(self, parameters: Dict) -> ActionResult:
        tier_id = parameters.get("tier", "campus")
        email = self.core.memory.recall("user_email") or ""
        name = self.core.memory.recall("user_name") or ""
        result = self.core.trial.start_trial(tier_id, email=email, name=name)
        return ActionResult(
            success=result["success"],
            message=result["message"],
            data=result,
        )
