import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from astra.core.billing.roi_engine import ROIEngine
from astra.core.billing.trial_manager import TrialManager
from astra.core.billing.tiers import TierManager


@pytest.fixture
def tier_manager(tmp_path):
    return TierManager(tmp_path)


@pytest.fixture
def trial_manager(tmp_path, tier_manager):
    return TrialManager(tmp_path, tier_manager)


def test_start_trial_unlocks_campus(trial_manager, tier_manager):
    result = trial_manager.start_trial("campus", email="student@edu.com", name="Cosmic")
    assert result["success"] is True
    tier_manager.reload()
    assert tier_manager.tier_id == "campus"
    assert tier_manager.has_feature("morning_brief") is True


def test_trial_snapshot_days_remaining(trial_manager):
    trial_manager.start_trial("startup", email="founder@co.com")
    snap = trial_manager.snapshot()
    assert snap["on_trial"] is True
    assert snap["days_remaining"] == 30


def test_trial_cannot_restart(trial_manager):
    trial_manager.start_trial("campus", email="a@b.com")
    result = trial_manager.start_trial("startup", email="a@b.com")
    assert result["success"] is True
    assert "already active" in result["message"].lower() or "days left" in result["message"].lower()


def test_trial_expiry_downgrades_to_cosmic(tmp_path, trial_manager, tier_manager):
    trial_manager.start_trial("campus", email="x@y.com")
    tier_file = tmp_path / "data" / "tier.json"
    data = json.loads(tier_file.read_text(encoding="utf-8"))
    data["trial_ends"] = (datetime.now() - timedelta(days=1)).isoformat()
    tier_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    notice = trial_manager.refresh()
    tier_manager.reload()

    assert notice is not None
    assert notice["expired"] is True
    assert tier_manager.tier_id == "cosmic"
    assert tier_manager.has_feature("morning_brief") is False


def test_roi_records_minutes(tmp_path):
    roi = ROIEngine(tmp_path)
    roi.record(True, "RUN_PROTOCOL")
    roi.record(True, "ASK_AGENT")
    dash = roi.dashboard()
    assert dash["hours_saved_total"] > 0
    assert dash["tasks_automated_total"] == 2
    assert "value_saved_week_usd" in dash


def test_roi_status_message(tmp_path):
    roi = ROIEngine(tmp_path)
    roi.record(True, "MORNING_BRIEF")
    msg = roi.status_message()
    assert "ROI REPORT" in msg
    assert "$" in msg


def test_show_roi_intent():
    from astra.core.intent.intent_engine import IntentEngine
    from astra.core.intent.intents import SHOW_ROI, START_TRIAL

    engine = IntentEngine(llm_enabled=False)
    assert engine.process("show roi").intent == SHOW_ROI
    assert engine.process("start campus trial").intent == START_TRIAL
    assert engine.process("start campus trial").entities["tier"] == "campus"


def test_trial_in_get_tier(trial_manager, tier_manager):
    trial_manager.start_trial("campus", email="t@t.com")
    tier_manager.reload()
    tier = tier_manager.get_tier()
    assert tier["trial"]["active"] is True
    assert tier["trial"]["days_remaining"] == 30
