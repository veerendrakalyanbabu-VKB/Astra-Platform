"""Offline specialist replies when LLM is unavailable."""

from typing import Dict, Optional


def local_agent_reply(agent_id: str, query: str, memory: Dict[str, str] = None) -> Optional[str]:
    agent_id = (agent_id or "core").lower()
    q = (query or "").lower().strip()
    memory = memory or {}

    handlers = {
        "mentor": _mentor_reply,
        "launch": _launch_reply,
        "ledger": _ledger_reply,
        "nova": _nova_reply,
        "pilot": _pilot_reply,
        "core": _core_reply,
    }

    handler = handlers.get(agent_id)
    if not handler:
        return None

    return handler(q, memory)


def _mentor_reply(q: str, memory: Dict[str, str]) -> str:
    if any(w in q for w in ("exam", "test", "quiz", "midterm", "final")):
        return (
            "Build a 7-day cram plan: Day 1–2 review notes, Day 3 practice problems, "
            "Day 4 mock test, Day 5 fix weak spots, Day 6 flashcards, Day 7 light review + sleep. "
            "Use 50-min focus blocks with 10-min breaks."
        )

    if any(w in q for w in ("study", "learn", "course", "class", "homework")):
        subject = _pick_subject(q)
        return (
            f"For {subject or 'this topic'}: preview → lecture notes → active recall → "
            "teach-back in 3 sentences. Schedule 2×25 min today and one review block tomorrow."
        )

    if "roadmap" in q or "plan" in q:
        return (
            "Skill roadmap: (1) define outcome in one sentence, (2) list 5 core concepts, "
            "(3) one project per week for 4 weeks, (4) weekly self-quiz. "
            "Say 'remember my study goal is …' so I track it."
        )

    return (
        "Tell me your subject, deadline, and what you've covered so far. "
        "I'll build a study sprint or explain the concept step-by-step."
    )


def _launch_reply(q: str, memory: Dict[str, str]) -> str:
    if any(w in q for w in ("pitch", "deck", "investor")):
        return (
            "Pitch skeleton: Problem → Why now → Solution → Traction → Market → "
            "Business model → Team → Ask. Keep 10 slides, 3-min story. "
            "Lead with one customer quote or metric."
        )

    if any(w in q for w in ("mvp", "launch", "ship", "build")):
        return (
            "MVP in 14 days: Week 1 — one painful workflow, 5 user interviews, wireframe. "
            "Week 2 — build only the core loop, onboard 3 beta users, measure one metric."
        )

    if any(w in q for w in ("gtm", "marketing", "growth", "customers")):
        return (
            "GTM wedge: pick one ICP, one channel, one message. "
            "Example: CS students on campus → Discord + demo reel → 'Command OS for founders'. "
            "Run 10 outbound touches before adding a second channel."
        )

    return (
        "Share your idea, stage, and deadline. I'll outline MVP scope, "
        "first 10 customers, or a one-page GTM plan."
    )


def _ledger_reply(q: str, memory: Dict[str, str]) -> str:
    if any(w in q for w in ("runway", "burn", "cash")):
        return (
            "Runway = cash ÷ monthly burn. If burn is $2k/mo and cash is $20k → 10 months. "
            "Remember numbers with 'remember my monthly burn is 2000' and 'remember my cash is 20000'."
        )

    if any(w in q for w in ("price", "pricing", "charge")):
        return (
            "Pricing sanity check: (1) value metric tied to customer outcome, "
            "(2) 3 tiers with clear upgrade path, (3) anchor high, default middle. "
            "Campus $9 / Startup $29 is a good student→founder ladder."
        )

    if any(w in q for w in ("budget", "cost", "expense")):
        return (
            "Monthly budget buckets: infra 15%, tools 10%, marketing 20%, "
            "ops 55%. Track top 3 costs weekly; cut anything not tied to revenue or retention."
        )

    return (
        "Give me monthly burn, cash on hand, or a pricing question — "
        "I'll model runway, unit economics, or a simple budget."
    )


def _nova_reply(q: str, memory: Dict[str, str]) -> str:
    if any(w in q for w in ("trend", "ai", "market", "research")):
        return (
            "AI command-layer trend: users want agents that act (open apps, run routines), "
            "not just chat. Position Astra as Command OS — squad + brief + device control."
        )

    return (
        "Ask for a summary, competitor angle, or concept explain. "
        "Example: 'ask nova summarize agent OS market'."
    )


def _pilot_reply(q: str, memory: Dict[str, str]) -> str:
    if any(w in q for w in ("morning", "routine", "schedule", "day")):
        return (
            "Morning stack: 'organize my morning routine' → time check → priority list → "
            "focus workspace. Schedule with 'schedule myday at 8am'."
        )

    return (
        "I run execution: routines, schedules, workspaces. "
        "Try 'activate coding workspace' or 'list routines'."
    )


def _core_reply(q: str, memory: Dict[str, str]) -> str:
    user = memory.get("user_name", "Operator")
    return (
        f"{user}, I'm routing your command. For squad work say 'ask mentor …' or "
        "'ask launch …'. For plans say 'show plans'. For daily sync say 'morning brief' (paid tiers)."
    )


def _pick_subject(q: str) -> str:
    subjects = (
        "python", "javascript", "math", "calculus", "physics", "biology",
        "history", "economics", "chemistry", "data structures",
    )
    for subject in subjects:
        if subject in q:
            return subject
    return ""
