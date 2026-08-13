# Changelog

## [3.6.0] - 2026-08-13

### Added

- Structured **CommandRecord** lifecycle (intent, route, plan, permissions, audit)
- **Command Inspector** UI — click log entries for full execution detail
- **Capability Center** — truthful list of implemented features with status labels
- **Subsystem registry** with FORTRESS + routing for 56 intents
- **System health** panel with real uptime, metrics, service status
- **Truthful boot sequence** driven by actual initialization state
- Architecture panel with interactive subsystem nodes
- Documentation: `docs/ARCHITECTURE.md`, `docs/COMMANDS.md`, `docs/SUBSYSTEMS.md`
- Tests for command records and subsystem routing

### Changed

- Command log renders structured blocks instead of generic chat bubbles
- Version unified to 3.6.0 in `astra_core.py`

## [3.5.0] - prior

- Neural core UI, Groq LLM integration, knowledge learning, Streamlit Cloud deploy
