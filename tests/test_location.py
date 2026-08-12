import json
from io import BytesIO
from unittest.mock import patch

import pytest

from astra.core.integrations.integrations_store import IntegrationsStore
from astra.core.integrations.location_engine import LocationEngine
from astra.core.intent.intent_engine import IntentEngine
from astra.core.intent.intents import DETECT_LOCATION, SET_CITY


@pytest.fixture
def store(tmp_path):
    return IntegrationsStore(tmp_path)


@pytest.fixture
def engine(store):
    return LocationEngine(store)


def _mock_ipwho_response(city="Hyderabad", region="Telangana", country="India"):
    body = json.dumps(
        {
            "success": True,
            "city": city,
            "region": region,
            "country": country,
            "latitude": 17.385,
            "longitude": 78.4867,
        }
    ).encode("utf-8")

    def fake_urlopen(url, timeout=8):
        return BytesIO(body)

    return fake_urlopen


def test_detect_applies_city_from_ip(store, engine):
    with patch.dict("os.environ", {"ASTRA_AUTO_LOCATION": "true"}, clear=False):
        with patch("urllib.request.urlopen", side_effect=_mock_ipwho_response()):
            result = engine.detect(force=True)

    assert result["success"] is True
    assert result["city"] == "Hyderabad"
    assert store.get("city") == "Hyderabad"
    assert store.get("location_source") == "ip"
    assert store.get("region") == "Telangana"
    assert store.get("country") == "India"


def test_detect_respects_auto_location_off(store, engine):
    with patch.dict("os.environ", {"ASTRA_AUTO_LOCATION": "false"}, clear=False):
        result = engine.detect()

    assert result["success"] is False
    assert "Auto-location is off" in result["message"]


def test_detect_uses_cache_when_fresh(store, engine):
    store._data["city"] = "Paris"
    store._data["location_source"] = "ip"
    store._data["location_detected_at"] = __import__("datetime").datetime.now().isoformat()
    store._save(store._data)

    with patch.dict("os.environ", {"ASTRA_AUTO_LOCATION": "true"}, clear=False):
        with patch("urllib.request.urlopen") as mock_open:
            result = engine.detect()

    assert result["success"] is True
    assert "cached" in result["message"].lower()
    mock_open.assert_not_called()


def test_ensure_location_detects_when_empty(store, engine):
    with patch.dict("os.environ", {"ASTRA_AUTO_LOCATION": "true"}, clear=False):
        with patch("urllib.request.urlopen", side_effect=_mock_ipwho_response(city="Austin")):
            ok = engine.ensure_location()

    assert ok is True
    assert store.get("city") == "Austin"


def test_format_location_line_manual(store):
    store.set_city("London")
    engine = LocationEngine(store)

    line = engine.format_location_line()

    assert "London" in line
    assert "manual" in line


def test_format_location_line_auto(store, engine):
    with patch.dict("os.environ", {"ASTRA_AUTO_LOCATION": "true"}, clear=False):
        with patch("urllib.request.urlopen", side_effect=_mock_ipwho_response()):
            engine.detect(force=True)

    line = engine.format_location_line()

    assert "Hyderabad" in line
    assert "auto" in line


def test_intent_detect_location():
    intent = IntentEngine().process("detect my location")
    assert intent.intent == DETECT_LOCATION


def test_intent_set_city():
    intent = IntentEngine().process("set city to Paris")
    assert intent.intent == SET_CITY
    assert intent.entities.get("city") == "paris"
