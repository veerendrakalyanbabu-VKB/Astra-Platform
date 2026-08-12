from astra.core.planner.scheduler import RoutineScheduler


def test_scheduler_add_and_list(tmp_path):
    scheduler = RoutineScheduler(tmp_path)
    scheduler.schedule_file = tmp_path / "data" / "schedules.json"
    scheduler.schedule_file.parent.mkdir(parents=True, exist_ok=True)

    entry = scheduler.add("myday", "8am")

    assert entry["time"] == "08:00"
    assert len(scheduler.list_all()) == 1


def test_scheduler_parse_time(tmp_path):
    scheduler = RoutineScheduler(tmp_path)

    assert scheduler._parse_time("8:30 am") == "08:30"
    assert scheduler._parse_time("2pm") == "14:00"
