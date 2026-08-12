import time
from collections import defaultdict


class MetricsCollector:
    """
    Lightweight in-process metrics for observability.
    """

    def __init__(self):
        self.counters = defaultdict(int)
        self.timings = defaultdict(list)

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] += value

    def record_timing(self, name: str, duration_ms: float) -> None:
        self.timings[name].append(duration_ms)

    def snapshot(self) -> dict:
        timing_summary = {}

        for name, values in self.timings.items():
            if values:
                timing_summary[name] = {
                    "count": len(values),
                    "avg_ms": round(sum(values) / len(values), 2),
                    "max_ms": round(max(values), 2),
                }

        return {
            "counters": dict(self.counters),
            "timings": timing_summary,
        }

    def reset(self) -> None:
        self.counters.clear()
        self.timings.clear()


class TimedOperation:
    """Context manager for timing pipeline stages."""

    def __init__(self, metrics: MetricsCollector, name: str):
        self.metrics = metrics
        self.name = name
        self.start = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed_ms = (time.perf_counter() - self.start) * 1000
        self.metrics.record_timing(self.name, elapsed_ms)
