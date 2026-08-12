from astra.core.planner.workspace import resolve_workspace, list_workspaces


def test_resolve_coding_workspace():
    key, workspace = resolve_workspace("coding workspace")

    assert key == "coding"
    assert len(workspace["steps"]) == 3


def test_list_workspaces():
    workspaces = list_workspaces()

    assert len(workspaces) == 3
    keys = {item["key"] for item in workspaces}
    assert "coding" in keys
    assert "focus" in keys
    assert "chill" in keys
