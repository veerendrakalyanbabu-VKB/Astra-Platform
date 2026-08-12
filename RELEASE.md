# Astra Platform 2.1.0 — Profiles + Marketplace + Mobile

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What's New in v2.1

### Multi-User Profiles
- Per-user isolated storage under `data/users/{profile}/`
- Commands: `list profiles`, `create profile guest`, `switch profile guest`, `who am i`
- Memory, routines, schedules, learning, and sync scoped per profile

### Plugin Marketplace
- Catalog at `marketplace/catalog.json`
- Packages: **weather**, **quotes**, **timer**
- `list marketplace` and `install plugin weather`
- Hot-install without restart

### Mobile Companion
- `python main.py --mobile` → http://localhost:8502
- Chat, quick actions, profile switcher, marketplace install
- Remote API: `--serve --host 0.0.0.0` for phone access

---

# Astra Platform 2.0.0 — OS Layer Release

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What's New in v2.0

### v1.4 — Desktop Shell Polish
- Tabbed Desktop Shell: Chat, Routines, Sync, Plan
- Visual routine builder and step-by-step progress
- Sync status panel and proactive suggestions sidebar

### v1.5 — Sync Server
- Standalone sync server: `python main.py --sync-server`
- POST/GET memory bundles on port 8790
- Works with `ASTRA_SYNC_URL` + encrypted bundles

### v1.6 — Smart Planning
- `SmartPlanner` with keyword + LLM goal decomposition
- `plan my work morning` creates multi-step plans
- `schedule myday at 8am` for daily routines
- `ProactiveEngine` time-aware suggestions

### v2.0 — Astra OS Layer
- System tray: `python main.py --tray`
- Global hotkey **Ctrl+Shift+A** → quick command dialog
- Workspace presets: `activate coding workspace`
- Background scheduler for due routines

---

# Astra Platform 1.3.0 — Custom Routines + Encrypted Sync + Windows Automation

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What's New in v1.3

### Custom Routines
- Define your own: `create routine myday: get time, open notepad, show memory`
- Run them: `run myday`
- Manage: `list routines` | `delete routine myday`
- Stored in `data/routines.json`

### Encrypted Cloud Sync
- Set `ASTRA_SYNC_KEY` in `.env` to encrypt sync bundles
- PBKDF2 + HMAC authenticated encryption (stdlib only)
- Works with existing `ASTRA_SYNC_URL` remote sync

### Deeper Windows Automation
- `focus notepad` — bring app window to foreground
- `set volume 50` — adjust system volume
- `minimize all` — show desktop
- `list windows` — show open window titles

---

# Astra Platform 1.2.0 — Goal Planning + Cloud Sync + Windows Layer

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What's New in v1.2

### Multi-Step Goal Planning
- Built-in routines: **morning**, **work**, **focus**, **downloads**
- Say: `organize my morning routine`, `run focus mode`, `start work`
- `GoalPlanner` decomposes goals into ordered pipeline steps
- Orchestrator executes multi-step plans with progress reporting

### Cloud Sync
- Local-first memory sync with device IDs and version metadata
- Command: `sync my memory`
- Export bundle: `data/sync/latest_bundle.json`
- Optional remote: set `ASTRA_SYNC_URL` in `.env`
- API: `GET /v1/sync/pull`, `POST /v1/sync/push`, `POST /v1/sync/run`

### Native Windows Layer
- Centralized `WindowsLayer` for OS operations
- `system info` — OS, user, machine details
- `open folder downloads` — open Downloads, Documents, Desktop
- `copy hello to clipboard` / `show clipboard`
- App launching refactored through Windows layer

---

# Astra Platform 1.1.0 — Desktop Shell

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What's New in v1.1

### Desktop Shell
- Streamlit-based desktop UI (`python main.py --desktop`)
- Command bar with quick actions (Time, Memory, Help, Chrome, etc.)
- Live status sidebar (LLM, plugins, memory, learning rate)
- Memory panel and session context
- `CommandBridge` connects UI to the full Astra Core pipeline

---

# Astra Platform 1.0.0 — Genesis Release

**Release Date:** August 11, 2026  
**Status:** SHIPPED

---

## What Astra Is

An AI-native computing platform that organizes computing around **human intent**, not applications.

```
User → Intent → Astra Core → Execute → Learn
```

---

## What's Included in v1.0

### Astra Core
- Intent Engine (rules + NLU + optional LLM)
- Planner & Reasoning Engine
- Permission Manager & Safety Engine
- Memory, Context, Session persistence
- Action Engine with real handlers
- Knowledge Engine & Tool Manager
- Plugin system
- Learning Engine & Audit Logger
- Event Bus & Metrics

### Interfaces
- Interactive REPL (`python main.py`)
- One-shot commands (`--cmd`)
- Streamlit Web UI (`--web`)
- REST API (`--serve`)
- Voice mode (`--voice`)
- Windows launcher (`astra.bat`)

### Actions
- Open apps (Chrome, Notepad, Calculator, etc.)
- Save / recall / list memory
- Get time, calculate, ask knowledge
- Compound commands (`open X and remember Y`)
- Safety gates (confirm / block)

### Quality
- 57+ automated tests
- Policy-based safety
- Session restore across restarts
- `.env` configuration
- Full audit trail

---

## Quick Verify

```powershell
python main.py --status
python main.py --demo
python -m pytest tests/ -q
```

All should pass.

---

## What's Next (Post v2.1)

- Shared family profiles
- Signed plugin packages
- Native iOS/Android app

---

*Astra Platform v2.1.0 — Your platform, your profiles, your plugins, anywhere.*
