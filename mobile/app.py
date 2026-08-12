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

    st.session_state.mobile_messages.append({"role": "user", "content": command})

    st.session_state.mobile_messages.append({

        "role": "astra",

        "content": response.message or "Done.",

    })





def _run_due_schedules(bridge) -> bool:

    import streamlit as st



    tick_key = f"sched_tick_{__import__('datetime').datetime.now().strftime('%Y-%m-%d-%H:%M')}"

    if st.session_state.get("last_sched_tick") == tick_key:

        return False



    st.session_state.last_sched_tick = tick_key



    def on_due(command, entry):

        return bridge.run(command)



    ran = False

    for item in bridge.core.scheduler.run_due(on_due):

        ran = True

        msg = item["result"].message or "Done."

        st.session_state.mobile_messages.append({

            "role": "astra",

            "content": f"[Scheduled] {msg}",

        })

    return ran





def render():

    import streamlit as st

    from astra.core.astra_core import AstraCore

    from astra.shell.command_bridge import CommandBridge



    st.set_page_config(

        page_title="ASTRA",

        page_icon="🔶",

        layout="centered",

        initial_sidebar_state="collapsed",

    )



    st.markdown(HUD_CSS, unsafe_allow_html=True)



    @st.cache_resource

    def get_bridge():

        core = AstraCore(project_root=PROJECT_ROOT)

        core.initialize()

        return CommandBridge(core)



    bridge = get_bridge()

    status = bridge.get_status()



    if "mobile_messages" not in st.session_state:

        st.session_state.mobile_messages = []



    if handle_ultron_events(bridge, _run_command):

        st.rerun()



    if _run_due_schedules(bridge):

        st.rerun()



    render_astra_interface(

        status=status,

        messages=st.session_state.mobile_messages,

        suggestions=bridge.get_suggestions(),

        dashboard=bridge.get_command_dashboard(),

        layout="mobile",

        height=880,

    )



    if prompt := st.chat_input("Command…"):

        _run_command(bridge, prompt.strip())

        st.rerun()





if __name__ == "__main__":

    render()


