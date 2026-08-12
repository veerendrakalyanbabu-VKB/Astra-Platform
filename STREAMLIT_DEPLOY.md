# Deploy ASTRA on Streamlit Cloud (step-by-step)

## 1. GitHub must be pushed

Repo: https://github.com/veerendrakalyanbabu-VKB/astra-platform

## 2. Create app on Streamlit Cloud

1. Open https://share.streamlit.io
2. Click **Create app**
3. Fill in:
   - **Repository:** `veerendrakalyanbabu-VKB/astra-platform`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Click **Advanced settings** → Python 3.11 if available
5. **Deploy**

## 3. Add Secrets (required for Groq brain)

App → **Settings** → **Secrets** → paste:

```toml
GROQ_API_KEY = "your_groq_key_here"
ASTRA_LLM_PROVIDER = "groq"
ASTRA_USER_NAME = "Veerendra"
```

Save → app will reboot.

## 4. Your live URL

Format: `https://astra-platform-veerendrakalyanbabu-vkb.streamlit.app`

(Add custom subdomain in Settings if you want.)

## 5. What works on Cloud vs Local

| Feature | Cloud | Local `.\go.ps1` |
|---------|-------|------------------|
| Neural core UI | Yes | Yes |
| Groq / LLM chat | Yes (secrets) | Yes (.env) |
| Voice (browser TTS) | Yes | Yes |
| Gestures / webcam | No | Yes |
| Pinch zoom | Partial (trackpad) | Yes |

## 6. Troubleshooting

- **Build fails:** Check Logs tab — usually missing dep; `requirements.txt` has streamlit + stripe
- **LLM Standby:** Secrets missing or wrong key name — use `GROQ_API_KEY` exactly
- **Blank page:** Hard refresh Ctrl+Shift+R
- **Old UI:** Redeploy from Manage app → Reboot app
