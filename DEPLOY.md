# ASTRA Command OS — Deploy & Ship Guide

## What you have now (demo-ready)

| Piece | Status | URL (local) |
|-------|--------|-------------|
| Command OS Desktop | ✅ Portfolio-ready | http://localhost:8501 |
| Portal (pricing/trials) | ✅ | http://localhost:8503 |
| Neural core + gestures + voice | ✅ | In desktop UI |
| 6-agent squad | ✅ | CORE · NOVA · PILOT · MENTOR · LAUNCH · LEDGER |
| Tests | ✅ | `python -m pytest tests/ -q` |

**You can demo today locally** with `.\go.ps1` — no deploy required for portfolio videos or live demos.

---

## 1. Push to GitHub

### One-time setup

```powershell
cd C:\Astra\astra-platform

git status
git add .
git commit -m "ASTRA v3.6 — living neural core, knowledge learning, GitHub polish"
```

### Use ONE repo: `astra-platform`

Your local project (`C:\Astra\astra-platform`) is the **current** ASTRA Command OS. The GitHub repos `astra-platform` and `astra-os` from June are **old prototypes** — not this version.

**Plan:** Push everything to `astra-platform` and delete `astra-os`.

```powershell
cd C:\Astra\astra-platform

git remote add origin https://github.com/veerendrakalyanbabu-VKB/astra-platform.git
# if remote exists: git remote set-url origin https://github.com/veerendrakalyanbabu-VKB/astra-platform.git

git push -u origin main --force
```

`--force` replaces the old June code with the real Command OS. Safe because the remote is your stale prototype.

### Delete the old `astra-os` repo (manual)

1. https://github.com/veerendrakalyanbabu-VKB/astra-os
2. **Settings** → bottom → **Delete this repository**
3. Type the repo name to confirm

Keep only **astra-platform** as your single ASTRA repo.

### Make the repo look professional

After push, on GitHub:

1. **About** (right sidebar) → add description + website (Streamlit URL after deploy)
2. **Topics** → `ai`, `streamlit`, `python`, `threejs`, `command-line`, `voice-assistant`
3. Pin the repo on your profile
4. Enable **Actions** tab — CI runs `pytest` on every push

Replace `YOUR_USERNAME` in README badge URL after first push.

---

## 2. Deploy options

### Option A — Local demo (recommended for portfolio)

Best for: screen recordings, interviews, hackathon demos.

```powershell
.\go.ps1
```

Share your screen or record with OBS. Gestures, mic, and female voice all work on your machine.

### Option B — Streamlit Community Cloud (free public URL)

Best for: shareable portfolio link.

1. Push repo to GitHub (see above)
2. https://share.streamlit.io → **Create app**
3. Repository: `veerendrakalyanbabu-VKB/astra-platform`
4. Branch: `main`
5. **Main file path:** `app.py`
6. **Secrets** (Settings → Secrets):

```toml
GROQ_API_KEY = "your_groq_key"
ASTRA_LLM_PROVIDER = "groq"
ASTRA_USER_NAME = "YourName"
```

7. Deploy → live URL like `https://astra-platform-xxxx.streamlit.app`

Full walkthrough: **[STREAMLIT_DEPLOY.md](STREAMLIT_DEPLOY.md)**

### Option C — VPS / Railway / Fly.io (production)

Best for: always-on product with custom domain.

- Run `streamlit run desktop/shell.py --server.port 8501 --server.address 0.0.0.0`
- Set env vars from `.env.example`
- Portal on second port 8503 or subdomain
- Stripe live keys for real checkout

Not required for portfolio — do this when you want paying users.

---

## 3. Before you ship publicly

- [ ] Confirm `.env` is **not** in git: `git status` should not list `.env`
- [ ] Rotate any API keys that were ever committed
- [ ] Add `ANTHROPIC_API_KEY` in Streamlit secrets (not in code)
- [ ] Run tests: `python -m pytest tests/ -q`
- [ ] Hard refresh UI after deploy: Ctrl+Shift+R

---

## 4. Optional later (not blocking demo)

| Feature | Priority |
|---------|----------|
| Stripe live checkout | When launching paid tiers |
| Mobile responsive collapse | Nice-to-have |
| TELEMETRY agent tab | v1.1 |
| Docker + one-click deploy | Production scale |

---

## Quick commands

```powershell
.\go.ps1          # Start Command OS
.\stop.ps1        # Stop all ports
.\setup.ps1       # First-time pip install
python -m pytest tests/ -q
```

**You are ready to demo and push to GitHub today.**
