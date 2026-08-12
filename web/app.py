import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def render():
    import streamlit as st
    from astra.core.astra_core import AstraCore

    st.set_page_config(
        page_title="Astra Platform",
        page_icon="🌌",
        layout="wide",
    )

    @st.cache_resource
    def get_core():
        core = AstraCore()
        core.initialize()
        return core

    core = get_core()

    if "pending" not in st.session_state:
        st.session_state.pending = False
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("Astra Platform")
    st.caption(f"Version {core.VERSION} — AI-Native Computing")

    tab_chat, tab_memory, tab_metrics, tab_system = st.tabs(
        ["Chat", "Memory", "Metrics", "System"]
    )

    with tab_chat:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        prompt = st.chat_input("Tell Astra what you need...")

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})

            if core.permissions.has_pending():
                confirmation = core.permissions.parse_confirmation(prompt)

                if confirmation is True:
                    result = core.pipeline.execute_approved_plan(prompt)
                    st.session_state.pending = False
                elif confirmation is False:
                    result = core.pipeline.cancel_pending(prompt)
                    st.session_state.pending = False
                else:
                    result = None
                    reply = "Please answer yes or no to confirm the pending action."
                    st.session_state.messages.append({"role": "assistant", "content": reply})
                    st.rerun()
            else:
                result = core.process(prompt)

                if result.needs_confirmation:
                    st.session_state.pending = True

            if result:
                reply = result.message or "Done."
                st.session_state.messages.append({"role": "assistant", "content": reply})

            st.rerun()

    with tab_memory:
        memory = core.memory.list_all()
        st.json(memory)

    with tab_metrics:
        col1, col2, col3 = st.columns(3)
        stats = core.learning.stats()
        col1.metric("Pipeline Requests", core.metrics.snapshot()["counters"].get("pipeline.requests", 0))
        col2.metric("Learning Records", stats["total"])
        col3.metric("Success Rate", f"{stats['success_rate'] * 100:.0f}%")
        st.subheader("Counters")
        st.json(core.metrics.snapshot())

    with tab_system:
        st.subheader("Voice")
        st.json(core.voice.status() if core.voice else {})
        st.subheader("Plugins")
        st.write(core.plugins.loaded_plugins or ["None loaded"])
        st.subheader("Knowledge Topics")
        st.write(core.knowledge.list_topics())
        st.subheader("Tools")
        st.json(core.tools.list_tools())


if __name__ == "__main__":
    render()
