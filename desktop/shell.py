import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ui.ultron import HUD_CSS, handle_ultron_events, render_astra_interface

def _run_command(bridge, command: str) -> None:
    import streamlit as st

    response = bridge.run(command)
    st.session_state.shell_messages.append({"role": "user", "content": command})
    reply = response.message or "Done."
    st.session_state.shell_messages.append({
        "role": "astra",
        "content": reply,
    })
    st.session_state.pending_voice = reply
    if response.command_record:
        if "command_records" not in st.session_state:
            st.session_state.command_records = []
        st.session_state.command_records.append(response.command_record)
    st.session_state.dash_dirty = True


def _run_due_schedules(bridge) -> bool:
    import streamlit as st

    tick_key = f"sched_tick_{__import__('datetime').datetime.now().strftime('%Y-%m-%d-%H:%M')}"
    if st.session_state.get("last_sched_tick") == tick_key:
        return False

    st.session_state.last_sched_tick = tick_key
    ran = False

    def on_due(command, entry):
        return bridge.run(command)

    for item in bridge.core.scheduler.run_due(on_due):
        ran = True
        label = item.get("command", item.get("routine", "task"))
        msg = item["result"].message or "Done."
        st.session_state.shell_messages.append({
            "role": "astra",
            "content": f"[Scheduled {item.get('time')}] {label}\n{msg}",
        })
        st.session_state.dash_dirty = True

    return ran


def _cached_ui_data(bridge):
    import streamlit as st

    if st.session_state.get("dash_dirty", True) or "status_cache" not in st.session_state:
        st.session_state.status_cache = bridge.get_status()
        st.session_state.dashboard_cache = bridge.get_command_dashboard()
        st.session_state.health_cache = bridge.get_health()
        st.session_state.boot_cache = bridge.get_boot_status()
        st.session_state.subsystems_cache = bridge.get_subsystems()
        st.session_state.capabilities_cache = bridge.get_capabilities()
        st.session_state.dash_dirty = False

    return (
        st.session_state.status_cache,
        st.session_state.dashboard_cache,
        st.session_state.get("health_cache", {}),
        st.session_state.get("boot_cache", {}),
        st.session_state.get("subsystems_cache", []),
        st.session_state.get("capabilities_cache", []),
    )


def render():
    import streamlit as st
    from astra.core.astra_core import AstraCore
    from astra.shell.command_bridge import CommandBridge

    st.set_page_config(
        page_title="ASTRA",
        page_icon="🔶",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    st.markdown(
        HUD_CSS,
        unsafe_allow_html=True,
    )

    @st.cache_resource
    def get_bridge():
        core = AstraCore(project_root=PROJECT_ROOT)
        core.initialize()
        return CommandBridge(core)

    bridge = get_bridge()

    if "shell_messages" not in st.session_state:
        st.session_state.shell_messages = []
        st.session_state.command_records = []
        st.session_state.dash_dirty = True
        st.session_state.intro_shown = False
        st.session_state.welcome_voice_done = False

    if handle_ultron_events(bridge, _run_command):
        st.rerun()

    if _run_due_schedules(bridge):
        st.rerun()

    status, dashboard, health, boot_status_data, subsystems, capabilities = _cached_ui_data(bridge)

    show_intro = not st.session_state.get("intro_shown", False)
    speak_welcome = not st.session_state.get("welcome_voice_done", False)
    if show_intro:
        st.session_state.intro_shown = True
    if speak_welcome:
        st.session_state.welcome_voice_done = True

    pending_voice = st.session_state.pop("pending_voice", "") or ""

    render_astra_interface(
        status=status,
        messages=st.session_state.shell_messages,
        suggestions=bridge.get_suggestions(),
        dashboard=dashboard,
        layout="desktop",
        height=940,
        command_records=st.session_state.get("command_records", []),
        health=health,
        boot_status=boot_status_data,
        subsystems=subsystems,
        capabilities=capabilities,
        pending_voice=pending_voice,
        show_intro=show_intro,
        speak_welcome=speak_welcome,
    )


if __name__ == "__main__":
    render()
