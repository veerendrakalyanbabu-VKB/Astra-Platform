# ASTRA Commands

## Command model

Each executed command produces a **CommandRecord** with:

- `id`, `timestamp`, `command`, `intent`, `subsystem`, `route`
- `plan`, `risk_level`, `permission_state`, `execution_state`
- `duration_ms`, `result_summary`, `verification`, `audit_status`, `why`

View full details in the UI **Command Inspector** (click any log block).

## Pipeline flow

```text
User input
    → IntentEngine (56 intents)
    → SmartPlanner (Plan)
    → ReasoningEngine (EXECUTE | CONFIRM | BLOCK)
    → SafetyEngine (policy override)
    → Executor → Handler
    → PipelineResult → CommandRecord
```

## Intent categories

| Category | Examples | Subsystem |
|----------|----------|-----------|
| System | `what time is it`, `system info`, `help` | CORE / PILOT |
| Memory | `remember …`, `show my memory` | CORE |
| Knowledge | `learn about …`, `explain kubernetes` | NOVA |
| Agents | `ask nova about …` | NOVA / PILOT / etc. |
| Automation | `create routine …`, `run morning` | PILOT |
| Windows OS | `focus notepad`, `set volume 50` | PILOT |
| Analytics | `show roi`, `industrial revolution` | LEDGER / CORE |
| Security | `delete file` (CONFIRM), `format disk` (BLOCK) | FORTRESS |

## Confirmation flow

High-risk actions set `needs_confirmation`. User must reply **yes** or **no**. Pending state is held in `PermissionManager`.

## Compound commands

Split on `and then`:

```text
what time is it and then show my memory
```

## Errors

Failed commands return structured records with `execution_state: FAILED` and human-readable `why` explaining subsystem, intent, and recommended next step.

## Extensibility

1. Add intent constant in `intents.py`
2. Add classifier patterns in `classifier.py`
3. Register handler in `actions/handlers/`
4. Add routing in `subsystems/registry.py` if needed
