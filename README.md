# ASTRA // AI Command OS

> **Intent → Agent Factory → Action** — a cinematic AI operating system with a living neural core, not a chatbot wrapper.

[![CI](https://github.com/veerendrakalyanbabu-VKB/astra-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/veerendrakalyanbabu-VKB/astra-platform/actions/workflows/ci.yml)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.57+-red)
![License MIT](https://img.shields.io/badge/license-MIT-green)
[![Live Demo](https://img.shields.io/badge/Live_Demo-astra--platform--os.streamlit.app-gold?style=for-the-badge)](https://astra-platform-os.streamlit.app/)
[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://astra-platform-os.streamlit.app/)

---

## What is ASTRA?

ASTRA is a **local-first AI command center** — black/gold/cyan mission-control UI, Three.js neural core, gesture control, voice, and a 6-agent industrial squad.

| Layer | What it does |
|-------|----------------|
| **Neural Core** | Living 3D orb — pulses when listening, thinking, executing |
| **Knowledge Graph** | Teach topics — `learn about Kubernetes` grows the core |
| **Memory** | Personal facts — `remember my goal is …` |
| **Agent Squad** | CORE · NOVA · PILOT · MENTOR · LAUNCH · LEDGER |
| **LLM Bridge** | Groq / Claude / GPT when API key present — offline fallbacks without |

---

## Screenshots & demo

**Live:** [https://astra-platform-os.streamlit.app/](https://astra-platform-os.streamlit.app/)

```powershell
cd astra-platform
.\go.ps1    # → http://localhost:8501
```

Hard refresh after updates: **Ctrl+Shift+R**

---

## Quick start (Windows)

```powershell
cd astra-platform
.\setup.ps1      # first time only
.\go.ps1         # Command OS desktop
```

| Mode | Command | Port |
|------|---------|------|
| Command OS | `python main.py --desktop` | 8501 |
| Portal | `python main.py --portal` | 8503 |
| Mobile | `python main.py --mobile` | 8502 |
| API | `python main.py --serve` | 8080 |

---

## Teach ASTRA (self-learning knowledge graph)

ASTRA **learns topics you teach** — stored locally in `data/knowledge.json`. More topics = denser neural core visualization.

```text
learn about quantum computing          # LLM researches + saves (needs API key)
learn that pods are smallest units in Kubernetes   # direct teach
show knowledge                         # list everything she knows
explain kubernetes                     # retrieves learned knowledge
```

Without an LLM key, use **direct teach** (`learn that …`). With `ANTHROPIC_API_KEY`, she can **research and learn** autonomously.

---

## Environment

Copy `.env.example` → `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...   # Claude (recommended)
OPENAI_API_KEY=sk-...          # alternative
```

---

## Architecture

```
User intent
    → Intent Engine (rules + optional LLM classifier)
    → Pipeline Orchestrator
        → Handler (memory / knowledge / agents / OS actions)
        → LLM fallback with memory + learned topics in context
    → Neural core UI reflects memory + knowledge density
```

**Key paths**

| Path | Role |
|------|------|
| `desktop/shell.py` | Streamlit Command OS entry |
| `ui/astra_interface.html` | Neural core, gestures, voice UI |
| `src/astra/core/knowledge/` | Knowledge graph + LLM responder |
| `src/astra/core/agents/` | Industrial squad |
| `go.ps1` | One-command launch |

---

## Tests

```powershell
python -m pytest tests/ -q
```

---

## Deploy

| Option | Best for |
|--------|----------|
| **Local** `.\go.ps1` | Portfolio demos, gestures, voice |
| **Streamlit Cloud** | Public shareable URL |
| **VPS / Railway** | Always-on production |

Full guide: **[DEPLOY.md](DEPLOY.md)**

Streamlit Cloud: main file `app.py`, add `GROQ_API_KEY` in Secrets.

See **[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)** for click-by-click deploy.

---

## Tech stack

Python · Streamlit · Three.js · MediaPipe · Web Speech API · Claude/GPT (optional) · Stripe (portal)

---

## License

MIT — see [LICENSE](LICENSE).

---

**v3.6** — Living neural core v2, knowledge graph learning, V2 UI polish, GitHub-ready.
