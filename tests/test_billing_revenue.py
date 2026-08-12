import pytest

from astra.core.billing.usage import UsageTracker, COSMIC_DAILY_LIMIT
from astra.core.billing.tiers import TierManager
from astra.core.agents.agent_replies import local_agent_reply
from astra.core.billing.stripe_billing import billing_status


def test_usage_limit_cosmic(tmp_path):
    tracker = UsageTracker(tmp_path)
    tiers = TierManager(tmp_path)

    allowed, _ = tracker.check_allowed(tiers.tier_id, "OPEN_APP")
    assert allowed is True

    for _ in range(COSMIC_DAILY_LIMIT):
        tracker.record(tiers.tier_id, "OPEN_APP")

    allowed, msg = tracker.check_allowed(tiers.tier_id, "OPEN_APP")
    assert allowed is False
    assert "limit" in msg.lower()


def test_usage_exempt_help(tmp_path):
    tracker = UsageTracker(tmp_path)
    tiers = TierManager(tmp_path)

    for _ in range(COSMIC_DAILY_LIMIT + 5):
        tracker.record(tiers.tier_id, "HELP")

    allowed, _ = tracker.check_allowed(tiers.tier_id, "HELP")
    assert allowed is True


def test_paid_tier_unlimited(tmp_path):
    tracker = UsageTracker(tmp_path)
    tiers = TierManager(tmp_path)
    tiers.demo_activate("startup")

    snap = tracker.snapshot(tiers.tier_id)
    assert snap["limited"] is False


def test_activate_paid_metadata(tmp_path):
    tiers = TierManager(tmp_path)
    result = tiers.activate_paid("campus", source="demo_checkout", email="test@edu.com")

    assert result["success"] is True
    assert tiers.tier_id == "campus"


def test_local_mentor_reply():
    reply = local_agent_reply("mentor", "help me study for my exam", {})
    assert reply
    assert "day" in reply.lower() or "focus" in reply.lower()


def test_local_launch_reply():
    reply = local_agent_reply("launch", "help with my pitch deck", {})
    assert "pitch" in reply.lower() or "slide" in reply.lower()


def test_billing_status_demo_mode():
    status = billing_status()
    assert status["mode"] in ("demo", "live")
    assert "portal_url" in status
