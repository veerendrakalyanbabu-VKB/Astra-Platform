# Contributing to ASTRA

## Setup

```powershell
cd astra-platform
.\setup.ps1
copy .env.example .env
.\go.ps1
```

## Development principles

1. **Preserve working functionality** — audit before large refactors
2. **No fake metrics** — UI must reflect real system state
3. **Truthful security claims** — only claim encryption/audit if implemented
4. **Minimize scope** — focused diffs, match existing style
5. **Test command pipeline** — run `pytest` before PR

## Running tests

```powershell
python -m pytest tests/ -q
```

## Code layout

- Core logic: `src/astra/core/`
- UI bridge: `ui/ultron.py`, `ui/astra_interface.html`
- Desktop shell: `desktop/shell.py`

## Adding a command

See [docs/COMMANDS.md](docs/COMMANDS.md).

## Commit style

- `feat(core): …`
- `feat(ui): …`
- `feat(logs): …`
- `docs: …`
- `test: …`

## Pull requests

- Describe what works and what is partial
- Include test results
- No secrets in commits
