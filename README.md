# ASTRA // AI Command OS

Portfolio-ready AI command operating system — not a chatbot prototype.

**Intent → Agent Factory → Action** with a cinematic neural core, gesture zoom, female voice, and 6-agent industrial squad.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.57+-red)
![License](https://img.shields.io/badge/status-demo--ready-green)

## Highlights

- **Neural core** — Three.js wireframe orb with bloom, string filaments, voice visualizer
- **Gestures** — Pinch zoom, hold commands (MediaPipe + webcam)
- **Voice** — Alexa-style wake word + female browser TTS default
- **Squad** — CORE · NOVA · PILOT · MENTOR · LAUNCH · LEDGER
- **Privacy Fortress** — local-first memory, audit log, encrypted sync option
- **Tiers** — Cosmic (free) · Campus · Startup + portal at `:8503`

## Quick start (Windows)

```powershell
cd astra-platform
.\setup.ps1      # first time only
.\go.ps1         # opens http://localhost:8501
```

Hard refresh after updates: **Ctrl+Shift+R**

## Run modes

| Command | What |
|---------|------|
| `python main.py --desktop` | Command OS (8501) |
| `python main.py --portal` | Pricing portal (8503) |
| `python main.py --mobile` | Mobile companion (8502) |
| `python main.py --tray` | System tray + hotkey |
| `python main.py --serve` | REST API |

## Environment

Copy `.env.example` → `.env` and add keys (optional for basic demo):

```env
ANTHROPIC_API_KEY=sk-ant-...   # Claude responses
OPENAI_API_KEY=sk-...          # alternative LLM
ELEVENLABS_API_KEY=...         # premium TTS (optional)
```

## Tests

```powershell
python -m pytest tests/ -q
```

## Deploy

See **[DEPLOY.md](DEPLOY.md)** for GitHub push + Streamlit Cloud + production checklist.

## Structure

```
astra-platform/
├── desktop/shell.py      # Command OS entry (Streamlit)
├── portal/app.py         # Pricing & trials
├── ui/astra_interface.html # Neural core + gestures (Three.js)
├── src/astra/core/       # Intent, agents, billing, voice
├── go.ps1                # One-command local launch
└── DEPLOY.md             # Ship guide
```

## Version

**v3.5 Cosmic** — Command OS UI, neural core v2, full squad online, female voice default.

---

Built for portfolio demos, hackathons, and AI OS product pitches.
