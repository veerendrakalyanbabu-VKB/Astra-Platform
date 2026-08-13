"""Astra immersive command center — full HTML interface."""

import json
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components

UI_DIR = Path(__file__).resolve().parent
INTERFACE_HTML = UI_DIR / "astra_interface.html"
CORE_HTML = UI_DIR / "ultron_core.html"

GESTURE_COMMANDS = {
    "palm": ("help", "PALM · SYSTEM HELP"),
    "point": ("what time is it", "POINT · TEMPORAL QUERY"),
    "pinch": ("show my memory", "PINCH · ZOOM · HOLD=MEMORY"),
    "fist": ("sync my memory", "FIST · CLOUD SYNC"),
    "wave": ("inspire me", "WAVE · INSPIRATION"),
    "spread": ("organize my morning routine", "SPREAD · MORNING PROTOCOL"),
    "circle": ("activate coding workspace", "CIRCLE · CODE WORKSPACE"),
}

QUICK_DOCK = [
    ("GO", "industrial revolution"),
    ("BRIEF", "morning brief"),
    ("WEATHER", "show weather"),
    ("LOC", "detect my location"),
    ("SQUAD", "show squad"),
    ("FOCUS", "focus timer 25"),
    ("STUDENT", "student mode"),
]

HUD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;600;700&family=Share+Tech+Mono&family=IBM+Plex+Sans:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', system-ui, sans-serif; }
.stApp {
    background: #07080c !important;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -10%, rgba(212,160,67,0.05), transparent),
        radial-gradient(ellipse 50% 40% at 100% 100%, rgba(94,200,219,0.03), transparent) !important;
}
[data-testid="stAppViewContainer"] { background: #07080c !important; }
header[data-testid="stHeader"], #MainMenu, footer, .stDeployButton {
    visibility:hidden!important; display:none!important; height:0!important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
section.main > div { padding: 0 !important; }
iframe { border:none!important; width:100%!important; }
div[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
div[data-testid="stHtml"] { min-height: calc(100vh - 8px); height: calc(100vh - 8px); }
div[data-testid="stHtml"] iframe { min-height: calc(100vh - 8px) !important; height: calc(100vh - 8px) !important; border: none !important; }
[data-testid="stChatInput"], [data-testid="stBottomBlockContainer"] { display: none !important; }
</style>
"""


@lru_cache(maxsize=1)
def _interface_html_template() -> str:
    return INTERFACE_HTML.read_text(encoding="utf-8")


def _render_html(html: str, height: int = 860) -> None:
    """Full Command OS iframe — Three.js, MediaPipe, wake word, parent navigation."""
    components.html(html, height=height, scrolling=False)


def render_astra_interface(
    status: dict,
    messages: list,
    suggestions: list = None,
    dashboard: dict = None,
    layout: str = "desktop",
    height: int = 860,
    command_records: list = None,
    health: dict = None,
    boot_status: dict = None,
    subsystems: list = None,
    capabilities: list = None,
):
    html = _interface_html_template()
    payload = {
        "user": status.get("user", "User"),
        "version": status.get("version", "3.4.0"),
        "llm": status.get("llm", "Standby"),
        "llm_label": status.get("llm_label", status.get("llm", "Standby")),
        "llm_provider": status.get("llm_provider", "none"),
        "encryption": status.get("encryption", "Off"),
        "profile": status.get("profile", "cosmic"),
        "memory_count": status.get("memory_count", 0),
        "knowledge_count": status.get("knowledge_count", 0),
        "knowledge_learned": status.get("knowledge_learned", 0),
        "learning_rate": status.get("learning_rate", "0%"),
        "requests": status.get("requests", 0),
        "cloud_sync": status.get("cloud_sync", "Local"),
        "privacy": status.get("privacy", {}),
        "voice_settings": status.get("voice_settings", {}),
        "location": status.get("location", {}),
    }
    html = (
        html.replace("__LAYOUT__", layout)
        .replace("__LAYOUT_LABEL__", layout.upper())
        .replace("__STATUS_JSON__", json.dumps(payload))
        .replace("__DASHBOARD_JSON__", json.dumps(dashboard or {}))
        .replace("__MESSAGES_JSON__", json.dumps(messages[-16:]))
        .replace("__SUGGESTIONS_JSON__", json.dumps(suggestions or []))
        .replace("__QUICK_DOCK_JSON__", json.dumps(QUICK_DOCK))
        .replace("__COMMAND_RECORDS_JSON__", json.dumps((command_records or [])[-20:]))
        .replace("__HEALTH_JSON__", json.dumps(health or {}))
        .replace("__BOOT_STATUS_JSON__", json.dumps(boot_status or {}))
        .replace("__SUBSYSTEMS_JSON__", json.dumps(subsystems or []))
        .replace("__CAPABILITIES_JSON__", json.dumps(capabilities or []))
        .replace("__LLM_ACTIVE__", "true" if status.get("llm") == "Active" else "false")
        .replace("__VOICE_SETTINGS_JSON__", json.dumps(status.get("voice_settings", {})))
    )
    _render_html(html, height=height)


def render_ultron_core(
    llm_active: bool,
    memory_count: int = 0,
    enable_gestures: bool = True,
    enable_voice: bool = True,
    height: int = 420,
) -> None:
    html = CORE_HTML.read_text(encoding="utf-8")
    html = (
        html.replace("__LLM_ACTIVE__", "true" if llm_active else "false")
        .replace("__MEMORY_COUNT__", str(memory_count))
        .replace("__GESTURES__", "true" if enable_gestures else "false")
        .replace("__VOICE__", "true" if enable_voice else "false")
        .replace("__STATUS__", "ACTIVE" if llm_active else "STANDBY")
    )
    _render_html(html, height=height)


def pop_ultron_event() -> Tuple[Optional[str], Optional[str]]:
    cmd = st.query_params.get("astra_cmd")
    source = st.query_params.get("astra_src")
    if cmd:
        st.query_params.clear()
        return cmd, source or "ultron"
    return None, None


def handle_ultron_events(bridge, run_command_fn) -> bool:
    cmd, source = pop_ultron_event()
    if not cmd:
        return False
    if source and source.startswith("gesture:"):
        gesture = source.split(":", 1)[-1]
        label = GESTURE_COMMANDS.get(gesture, (cmd, cmd))[1]
        st.toast(label, icon="🖐️")
    elif source == "voice":
        st.toast("Voice transmitted", icon="🎙️")
    else:
        st.toast("Command received", icon="◈")
    run_command_fn(bridge, cmd)
    return True
