# ASTRA Subsystems

## CORE — Chief Orchestrator

**Purpose:** Central coordination and command lifecycle.

**Responsibilities:** Intent classification, pipeline orchestration, memory routing, agent coordination, final responses.

**Status:** AVAILABLE — 56 intents, compound commands, conversation fallback.

**Examples:** `morning brief`, `show squad`, `remember my goal is …`

---

## FORTRESS — Security & Privacy

**Purpose:** Permission gates, audit logging, privacy controls.

**Responsibilities:** Risk analysis, confirmation gates, policy enforcement, audit trail.

**Status:** AVAILABLE — audit enabled by default.

**Examples:** Blocks `format disk`; confirms `delete file`.

---

## NOVA — Research & Intelligence

**Purpose:** Research, knowledge, summarization, LLM-assisted reasoning.

**Status:** AVAILABLE (LLM DEGRADED without API key).

**Examples:** `learn about quantum computing`, `ask nova about AI trends`

---

## PILOT — Operations & Automation

**Purpose:** Routines, schedules, workspaces, Windows automation.

**Status:** AVAILABLE on Windows for OS actions.

**Examples:** `organize my morning routine`, `focus notepad`, `activate coding workspace`

---

## MENTOR — Learning & Guidance

**Purpose:** Teaching, explanations, study guidance.

**Tier:** Campus+

**Examples:** `ask mentor to explain recursion`

---

## LAUNCH — Deployment & Scale

**Purpose:** Profiles, marketplace, trials, deployment metadata.

**Examples:** `list marketplace`, `switch profile`

---

## LEDGER — Finance & Analytics

**Purpose:** ROI tracking, productivity metrics, calculations.

**Examples:** `show roi`, `calculate 15 percent of 200`

---

## Implementation note

Subsystems are **architectural modules and persona layers**, not separate microservices. Routing is defined in `src/astra/core/subsystems/registry.py`.
