"""Astra Agent Squad — named digital teammates with mandates."""

SQUAD = {
    "core": {
        "id": "core",
        "name": "CORE",
        "title": "Chief Orchestrator",
        "mandate": "Routes commands, keeps the whole system aligned.",
        "tier": "cosmic",
        "emoji": "◈",
        "color": "#ffaa30",
    },
    "nova": {
        "id": "nova",
        "name": "NOVA",
        "title": "Research & Intel",
        "mandate": "Market research, summaries, competitive intel, explain concepts.",
        "tier": "cosmic",
        "emoji": "🔭",
        "color": "#00d4ff",
    },
    "pilot": {
        "id": "pilot",
        "name": "PILOT",
        "title": "Operations",
        "mandate": "Routines, schedules, workspaces, daily execution.",
        "tier": "cosmic",
        "emoji": "⚡",
        "color": "#6ee7b7",
    },
    "mentor": {
        "id": "mentor",
        "name": "MENTOR",
        "title": "Learning Coach",
        "mandate": "Study plans, explain topics, quiz prep, skill roadmaps for students.",
        "tier": "campus",
        "emoji": "📚",
        "color": "#a78bfa",
    },
    "launch": {
        "id": "launch",
        "name": "LAUNCH",
        "title": "Startup Strategist",
        "mandate": "Pitch decks, GTM ideas, MVP scope, founder ops for startups.",
        "tier": "startup",
        "emoji": "🚀",
        "color": "#f472b6",
    },
    "ledger": {
        "id": "ledger",
        "name": "LEDGER",
        "title": "Finance Analyst",
        "mandate": "Runway math, pricing models, unit economics, budget checks.",
        "tier": "startup",
        "emoji": "📊",
        "color": "#fbbf24",
    },
}


def list_agents(tier_id: str = "cosmic") -> list:
    from astra.core.billing.tiers import tier_includes_agent

    agents = []
    for agent in SQUAD.values():
        llm_tier = tier_includes_agent(tier_id, agent["id"])
        agents.append({
            **agent,
            "online": True,
            "locked": not llm_tier,
            "llm_boost": llm_tier,
        })
    return agents


def get_agent(agent_id: str) -> dict | None:
    return SQUAD.get(agent_id.lower())


def agent_prompt(agent_id: str, query: str) -> str:
    agent = get_agent(agent_id)
    if not agent:
        return query

    return (
        f"You are {agent['name']}, {agent['title']} in Astra Command OS. "
        f"Mandate: {agent['mandate']} "
        f"Answer as this specialist in clear, actionable language. "
        f"User query: {query}"
    )
