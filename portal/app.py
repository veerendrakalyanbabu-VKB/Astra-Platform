"""Astra Portal — landing, 30-day trial, checkout, and lead capture."""

import json
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = PROJECT_ROOT / "src"
LEADS_FILE = PROJECT_ROOT / "data" / "leads.json"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

PORTAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');
.stApp { background:#000 !important; color:#f5e6d3; font-family:'Share Tech Mono',monospace; }
header, footer, #MainMenu, .stDeployButton { visibility:hidden!important; height:0!important; }
.hero { text-align:center; padding:2rem 1rem 1rem; }
.hero h1 { font-family:Orbitron,sans-serif; font-size:2rem; letter-spacing:.25em; color:#ffaa30; text-shadow:0 0 30px rgba(255,170,48,.4); }
.hero p { color:rgba(0,212,255,.75); letter-spacing:.08em; font-size:.85rem; max-width:640px; margin:.75rem auto; }
.trial-banner { text-align:center; padding:1rem; margin:1rem 0; border:1px solid rgba(110,231,183,.35); background:rgba(110,231,183,.06); }
.trial-banner strong { color:#6ee7b7; font-family:Orbitron,sans-serif; letter-spacing:.12em; }
.act { padding:1.5rem 1rem; border-top:1px solid rgba(255,170,48,.12); }
.act h2 { font-family:Orbitron,sans-serif; font-size:1rem; letter-spacing:.15em; color:#ffaa30; margin-bottom:.5rem; }
.act p { font-size:.8rem; color:rgba(245,230,211,.7); line-height:1.6; }
.price-card { border:1px solid rgba(255,170,48,.2); padding:1rem; background:rgba(255,170,48,.03); min-height:180px; }
.price-card.featured { border-color:rgba(255,170,48,.5); box-shadow:0 0 24px rgba(255,170,48,.12); }
.price-name { font-family:Orbitron,sans-serif; color:#ffcc66; letter-spacing:.1em; }
.price-amt { font-size:1.4rem; color:#ffaa30; margin:.35rem 0; }
.trial-badge { display:inline-block; font-size:.6rem; color:#6ee7b7; border:1px solid rgba(110,231,183,.4); padding:2px 8px; margin-bottom:6px; }
.success-box { border:1px solid rgba(110,231,183,.4); padding:1rem; background:rgba(110,231,183,.06); margin:1rem 0; }
.warn-box { border:1px solid rgba(255,170,48,.4); padding:1rem; background:rgba(255,170,48,.06); margin:1rem 0; }
</style>
"""


def _save_lead(name: str, email: str, use_case: str, plan: str, source: str = "portal") -> None:
    LEADS_FILE.parent.mkdir(parents=True, exist_ok=True)
    leads = []

    if LEADS_FILE.exists():
        try:
            leads = json.loads(LEADS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            leads = []

    leads.append({
        "name": name,
        "email": email,
        "use_case": use_case,
        "plan": plan,
        "source": source,
        "at": datetime.now().isoformat(),
    })
    LEADS_FILE.write_text(json.dumps(leads, indent=2), encoding="utf-8")


def _activate_tier(tier_id: str, email: str = "", source: str = "portal", name: str = "") -> dict:
    from astra.core.billing.tiers import TierManager

    manager = TierManager(PROJECT_ROOT)
    return manager.activate_paid(tier_id, source=source, email=email, name=name)


def _start_trial(tier_id: str, email: str = "", name: str = "") -> dict:
    from astra.core.billing.tiers import TierManager
    from astra.core.billing.trial_manager import TrialManager

    tiers = TierManager(PROJECT_ROOT)
    trial = TrialManager(PROJECT_ROOT, tiers)
    result = trial.start_trial(tier_id, email=email, name=name)
    if result.get("success") and email:
        _save_lead(name or "Trial user", email, "Free trial", tier_id.title(), source="free_trial")
    return result


def render():
    import streamlit as st
    from astra.core.billing.roi_engine import TRIAL_DAYS
    from astra.core.billing.tiers import TIERS, TierManager
    from astra.core.billing.trial_manager import TrialManager
    from astra.core.billing.stripe_billing import (
        billing_status,
        checkout_available,
        create_checkout_session,
    )

    st.set_page_config(page_title="Astra Command OS", page_icon="🔶", layout="wide")
    st.markdown(PORTAL_CSS, unsafe_allow_html=True)

    params = st.query_params
    billing = billing_status()
    tier_mgr = TierManager(PROJECT_ROOT)
    trial_mgr = TrialManager(PROJECT_ROOT, tier_mgr)
    trial_mgr.refresh()
    tier_mgr.reload()
    current = tier_mgr.get_tier()
    trial_snap = trial_mgr.snapshot()

    if params.get("checkout") == "success":
        tier_id = params.get("tier", "campus")
        if tier_id in TIERS:
            result = _activate_tier(tier_id, source="stripe_checkout")
            st.markdown(
                f'<div class="success-box"><strong>Plan activated:</strong> {result["message"]}</div>',
                unsafe_allow_html=True,
            )
            st.balloons()

    if params.get("trial") == "started":
        st.markdown(
            '<div class="success-box"><strong>Trial active!</strong> '
            'Run <code>python main.py --desktop</code> → say '
            '<code>morning brief</code> or <code>industrial revolution</code></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        f"""
        <div class="hero">
            <h1>A S T R A</h1>
            <p>The Industrial Revolution of computing. One command layer. Named agents that execute — not chatbots that talk.</p>
        </div>
        <div class="trial-banner">
            <strong>30-DAY FREE TRIAL</strong> · Full Campus or Startup squad · No credit card required · Cancel anytime
        </div>
        """,
        unsafe_allow_html=True,
    )

    status_line = f"Plan: **{current['name']}** · Billing: **{billing['mode']}**"
    if trial_snap.get("on_trial"):
        status_line += f" · **Trial: {trial_snap['days_remaining']} days left**"
        if trial_snap.get("expiring_soon"):
            st.markdown(
                f'<div class="warn-box">Trial ending in {trial_snap["days_remaining"]} days. '
                "Subscribe below to keep MENTOR, morning brief, and unlimited commands.</div>",
                unsafe_allow_html=True,
            )
    st.caption(status_line + " · Desktop: `python main.py --desktop` · Mobile: `:8502`")

    st.link_button("Open Command OS", "http://localhost:8501")

    st.markdown("### Start your free trial")
    t1, t2 = st.columns(2)

    with t1:
        st.markdown(f"#### 📚 Campus — {TIERS['campus']['price_label']}")
        st.caption("MENTOR · morning brief · unlimited commands · cloud sync")
        with st.form("trial_campus"):
            name = st.text_input("Name", key="campus_name")
            email = st.text_input("Email", key="campus_email", placeholder="you@school.edu")
            if st.form_submit_button(f"Start {TRIAL_DAYS}-day Campus trial", type="primary"):
                if email:
                    result = _start_trial("campus", email=email, name=name)
                    if result["success"]:
                        st.success(result["message"])
                        st.query_params["trial"] = "started"
                        st.rerun()
                    else:
                        st.warning(result["message"])
                else:
                    st.error("Email required to start trial")

    with t2:
        st.markdown(f"#### 🚀 Startup — {TIERS['startup']['price_label']}")
        st.caption("Full squad · LAUNCH · LEDGER · industrial protocols")
        with st.form("trial_startup"):
            name = st.text_input("Name", key="startup_name")
            email = st.text_input("Email", key="startup_email", placeholder="founder@startup.com")
            if st.form_submit_button(f"Start {TRIAL_DAYS}-day Startup trial", type="primary"):
                if email:
                    result = _start_trial("startup", email=email, name=name)
                    if result["success"]:
                        st.success(result["message"])
                        st.query_params["trial"] = "started"
                        st.rerun()
                    else:
                        st.warning(result["message"])
                else:
                    st.error("Email required to start trial")

    st.markdown("---")
    st.markdown("### Subscribe after trial")

    cols = st.columns(4)
    tier_order = ["cosmic", "campus", "startup", "enterprise"]

    for col, tier_id in zip(cols, tier_order):
        tier = TIERS[tier_id]
        featured = tier_id == "startup"
        with col:
            trial_badge = ""
            if tier_id in ("campus", "startup"):
                trial_badge = f'<div class="trial-badge">{TRIAL_DAYS}-DAY FREE TRIAL</div>'
            st.markdown(
                f"""<div class="price-card {"featured" if featured else ""}">
                {trial_badge}
                <div class="price-name">{tier["name"].upper()}</div>
                <div class="price-amt">{tier["price_label"]}</div>
                <p style="font-size:.72rem;color:rgba(255,170,48,.55)">{tier["tagline"]}</p>
                </div>""",
                unsafe_allow_html=True,
            )

            if tier_id == "cosmic":
                st.caption("Always free")
            elif tier_id == "enterprise":
                st.link_button("Contact sales", "mailto:hello@astra.dev?subject=Enterprise")
            elif checkout_available(tier_id):
                pay_email = st.text_input("Email", key=f"pay_email_{tier_id}")
                if st.button(f"Subscribe — {tier['price_label']}", key=f"pay_{tier_id}"):
                    session = create_checkout_session(tier_id, customer_email=pay_email)
                    if session and session.get("url"):
                        st.link_button("Continue to Stripe ↗", session["url"])
            else:
                if st.button(f"Activate {tier['name']} (demo pay)", key=f"demo_{tier_id}"):
                    result = _activate_tier(tier_id, source="demo_checkout")
                    st.success(result["message"])

    st.markdown("---")
    st.markdown("### Why users pay")
    w1, w2, w3 = st.columns(3)
    with w1:
        st.markdown("**ROI proof** — `show roi` tracks hours saved ($25/hr value)")
    with w2:
        st.markdown("**Agent factory** — MENTOR, LAUNCH, LEDGER run real workflows")
    with w3:
        st.markdown("**Industrial protocols** — one command, full squad execution")

    st.markdown("---")
    with st.form("lead_form"):
        st.markdown("### Enterprise / waitlist")
        name = st.text_input("Name")
        email = st.text_input("Email")
        use_case = st.selectbox("I am a…", ["Startup founder", "Student", "Developer", "Agency", "Enterprise"])
        plan = st.selectbox("Interested plan", ["Campus", "Startup", "Enterprise"])
        if st.form_submit_button("Request access"):
            if name and email:
                _save_lead(name, email, use_case, plan)
                st.success("Received. Start your free trial above for instant access.")
            else:
                st.error("Name and email required.")


if __name__ == "__main__":
    render()
