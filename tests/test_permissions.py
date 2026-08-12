import pytest

from astra.core.permissions import PermissionManager
from astra.core.planner.plan import Plan


def test_permission_pending_flow():
    manager = PermissionManager()
    plan = Plan(action="DELETE_FILE", parameters={"target": "notes.txt"})

    assert manager.has_pending() is False

    manager.request_confirmation(plan, {"analysis": {"risk": "HIGH"}})

    assert manager.has_pending() is True
    assert "DELETE_FILE" in manager.describe_pending()


def test_permission_approve():
    manager = PermissionManager()
    plan = Plan(action="DELETE_FILE", parameters={"target": "notes.txt"})
    manager.request_confirmation(plan, {})

    approved = manager.approve()

    assert approved.action == "DELETE_FILE"
    assert manager.has_pending() is False


def test_permission_deny():
    manager = PermissionManager()
    plan = Plan(action="DELETE_FILE", parameters={"target": "notes.txt"})
    manager.request_confirmation(plan, {})

    manager.deny()

    assert manager.has_pending() is False


@pytest.mark.parametrize(
    "text,expected",
    [
        ("yes", True),
        ("y", True),
        ("go ahead", True),
        ("no", False),
        ("cancel", False),
        ("maybe", None),
    ],
)
def test_confirmation_parsing(text, expected):
    manager = PermissionManager()
    assert manager.parse_confirmation(text) is expected
