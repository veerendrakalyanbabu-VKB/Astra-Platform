"""Morning brief — daily command summary like APEX Command OS."""

from datetime import datetime

from astra.core.agents import squad


class MorningBriefEngine:

    def __init__(self, core):
        self.core = core

    def generate(self) -> dict:
        full_brief = self.core.tiers.has_feature("morning_brief")
        lines = self._build_lines(full_brief=full_brief)
        label = "Morning Brief" if full_brief else "Daily Brief"
        message = f"☀ {label}\n" + "\n".join(f"  • {line}" for line in lines)

        return {
            "available": True,
            "message": message,
            "lines": lines,
            "label": label,
            "tier": "full" if full_brief else "cosmic",
            "generated_at": datetime.now().isoformat(),
        }

    def _build_lines(self, full_brief: bool = True) -> list:
        core = self.core
        lines = []
        learning = core.learning.stats()
        metrics = core.metrics.snapshot()
        mode = core.workspace_mode.get_info()
        user = core.memory.recall("user_name") or "Operator"
        tier = core.tiers.get_tier()
        usage = core.usage.snapshot(core.tiers.tier_id) if hasattr(core, "usage") else {}

        lines.append(f"Good morning, {user}. {mode['label']} mode · {tier['name']} plan.")

        if hasattr(core, "location") and core.location:
            loc = core.location.format_location_line()
            if loc and "Unknown" not in loc:
                lines.append(f"Location: {loc}.")

        success = learning.get("success_rate", 0)
        lines.append(f"Command success rate: {success * 100:.0f}%.")

        mem = core.memory.list_all()
        mem_count = len(mem)
        lines.append(f"Memory blocks: {mem_count}.")

        goals = [f"{k}: {v}" for k, v in mem.items() if "goal" in k or "project" in k][:2]
        if goals:
            lines.append(f"Tracked goals: {'; '.join(goals)}.")

        requests = metrics["counters"].get("pipeline.requests", 0)
        if requests:
            lines.append(f"Session commands: {requests}.")

        if usage.get("limited") and usage.get("remaining") is not None:
            lines.append(f"Commands left today: {usage['remaining']} of {usage['limit']}.")

        schedules = core.scheduler.list_all()
        if schedules:
            next_item = schedules[0]
            lines.append(
                f"Next routine: {next_item['routine']} at {next_item['time']}."
            )

        if hasattr(core, "weather") and core.weather:
            weather = core.weather.current()
            if weather.get("available") and weather.get("lines"):
                lines.append(weather["lines"][0])

        if full_brief and hasattr(core, "calendar") and core.calendar:
            cal = core.calendar.today_events(limit=3)
            if cal.get("lines"):
                for item in cal["lines"][:2]:
                    lines.append(f"Calendar: {item}")

        routines = core.routine_store.list_all() if core.routine_store else []
        if routines and not schedules:
            names = [r.get("key", r.get("title", "routine")) for r in routines[:3]]
            lines.append(f"Routines ready: {', '.join(names)}.")

        for suggestion in core.proactive.suggest()[:2]:
            lines.append(f"Suggested: {suggestion.get('command', suggestion)}")

        online = [a["name"] for a in squad.list_agents(core.tiers.tier_id) if a["online"]]
        lines.append(f"Squad online: {', '.join(online)}.")

        if not full_brief:
            locked = [a["name"] for a in squad.list_agents(core.tiers.tier_id) if a["locked"]]
            if locked:
                lines.append(
                    f"Local coaching available — ask {', '.join(locked[:2])} anytime. "
                    "Campus adds LLM depth + calendar sync."
                )
        else:
            locked = [a["name"] for a in squad.list_agents(core.tiers.tier_id) if a["locked"]]
            if locked:
                lines.append(f"Upgrade to unlock: {', '.join(locked)}.")

        if mode.get("id") == "student":
            if full_brief:
                lines.append("Focus today: ask mentor for a study sprint or exam plan.")
            else:
                lines.append("Focus today: ask nova to explain a topic or pilot to plan your study blocks.")
        elif mode.get("id") == "startup":
            if full_brief:
                lines.append("Focus today: ask launch for GTM wedge or ask ledger for runway check.")
            else:
                lines.append("Focus today: ask nova for market trends or pilot for your founder checklist.")

        return lines
