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

# If not already initialized:
git init
git add .
git commit -m "ASTRA Command OS v3.5 — portfolio release"
```

### Create repo on GitHub

1. Go to https://github.com/new
2. Name: `astra-command-os` (or `astra-platform`)
3. **Private** recommended (until you strip any local paths from docs)
4. Do **not** add README/gitignore (you already have them)
5. Copy the repo URL, e.g. `https://github.com/YOUR_USERNAME/astra-command-os.git`

### Push

```powershell
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/astra-command-os.git
git push -u origin main
```

If prompted, sign in with GitHub (browser or personal access token).

---

## 2. Deploy options

### Option A — Local demo (recommended for portfolio)

Best for: screen recordings, interviews, hackathon demos.

```powershell
.\go.ps1
```

Share your screen or record with OBS. Gestures, mic, and female voice all work on your machine.

### Option B — Streamlit Community Cloud (free public URL)

Best for: shareable link without your laptop running.

**Limits:** No webcam gestures on server; voice uses browser TTS (works); LLM needs secrets in dashboard.

1. Push repo to GitHub (public or private)
2. https://share.streamlit.io → New app
3. Repository: your repo
4. **Main file path:** `desktop/shell.py`
5. **Secrets** (Settings → Secrets), paste:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
# or OPENAI_API_KEY = "sk-..."
```

6. Deploy → you get `https://YOUR-APP.streamlit.app`

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
