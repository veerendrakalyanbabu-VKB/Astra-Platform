"""Multi-agent industrial protocols — squad chains for student & startup revolutions."""

from astra.core.agents import squad
from astra.core.agents.agent_replies import local_agent_reply


PROTOCOLS = {
    "student": {
        "name": "Student Revolution",
        "symbol": "📚",
        "agents": ("pilot", "mentor", "nova"),
        "focus": "Daily execution → deep learning → research synthesis",
        "queries": {
            "pilot": "organize my study day with focus blocks",
            "mentor": "build a 7-day exam prep plan",
            "nova": "summarize how to learn faster with active recall",
        },
    },
    "startup": {
        "name": "Startup Revolution",
        "symbol": "🚀",
        "agents": ("pilot", "launch", "ledger"),
        "focus": "Ops → GTM → runway in one industrial pass",
        "queries": {
            "pilot": "morning founder execution checklist",
            "launch": "14-day MVP launch wedge",
            "ledger": "runway check with simple unit economics",
        },
    },
    "revolution": {
        "name": "Full Industrial Revolution",
        "symbol": "◈",
        "agents": ("core", "pilot", "mentor", "launch", "ledger", "nova"),
        "focus": "Complete agent factory — maximum orchestration",
        "queries": {
            "core": "route my highest-leverage action today",
            "pilot": "daily command sequence",
            "mentor": "skill acceleration plan",
            "launch": "go-to-market priority this week",
            "ledger": "financial discipline check",
            "nova": "market intelligence snapshot",
        },
    },
}


class IndustrialProtocol:

    def __init__(self, core):
        self.core = core

    def run(self, protocol_id: str) -> dict:
        protocol = PROTOCOLS.get(protocol_id)
        if not protocol:
            return {
                "success": False,
                "message": f"Unknown protocol. Try: {', '.join(PROTOCOLS)}",
            }

        lines = [
            f"{protocol['symbol']} {protocol['name'].upper()}",
            f"Focus: {protocol['focus']}",
            "",
        ]
        memory = self.core.memory.list_all()
        blocked = []

        for agent_id in protocol["agents"]:
            agent = squad.get_agent(agent_id)
            if not agent:
                continue

            if not self.core.tiers.tier_includes(agent_id):
                query = protocol["queries"].get(agent_id, "status report")
                reply = local_agent_reply(agent_id, query, memory)
                if reply:
                    lines.append(f"  {agent['emoji']} {agent['name']} (local): {reply}")
                else:
                    blocked.append(agent["name"])
                    lines.append(f"  🔒 {agent['emoji']} {agent['name']} — say 'show plans' to unlock")
                continue

            query = protocol["queries"].get(agent_id, "status report")
            reply = None

            if self.core.llm_responder and self.core.llm_responder.enabled:
                prompt = squad.agent_prompt(agent_id, query)
                reply = self.core.llm_responder.respond(prompt, memory)

            if not reply:
                reply = local_agent_reply(agent_id, query, memory) or f"Ready on '{query}'."

            lines.append(f"  {agent['emoji']} {agent['name']}: {reply}")

        lines.append("")
        if blocked:
            lines.append(f"Cosmic ran local coaches for locked agents. Campus adds LLM + full squad sync.")
        else:
            lines.append("Industrial chain complete. Human intent → agent factory → action.")

        if hasattr(self.core, "revolution"):
            self.core.revolution.record_protocol()

        return {
            "success": True,
            "message": "\n".join(lines),
            "protocol": protocol_id,
            "blocked": blocked,
        }

    def list_protocols(self) -> str:
        lines = ["Industrial Protocols:", ""]
        for key, proto in PROTOCOLS.items():
            lines.append(f"  {proto['symbol']} run {key} protocol — {proto['focus']}")
        lines.append("")
        lines.append("Say: run student protocol | run startup protocol | run revolution protocol")
        return "\n".join(lines)
