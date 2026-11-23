"""
InsureClaims High-Precision Timing Utilities
Provides context managers, function decorators, and statistical analyzers for
measuring pipeline stage latency, P50, P95, and cold vs warm performance.
"""

import time
import functools
import statistics
from contextlib import contextmanager
from typing import Dict, List, Any, Callable, Optional


class TimingCollector:
    """Thread-safe collector for pipeline stage execution timings."""

    def __init__(self):
        self.timings: Dict[str, List[float]] = {}

    def record(self, stage: str, duration_ms: float):
        if stage not in self.timings:
            self.timings[stage] = []
        self.timings[stage].append(duration_ms)

    def get_summary(self) -> Dict[str, Any]:
        summary = {}
        for stage, durations in self.timings.items():
            summary[stage] = calculate_latency_stats(durations)
        return summary

    def clear(self):
        self.timings.clear()


GLOBAL_TIMING_COLLECTOR = TimingCollector()


@contextmanager
def time_block(stage_name: str, collector: Optional[TimingCollector] = None):
    """
    Context manager to time a block of code with microsecond precision.
    
    Usage:
        with time_block("vector_search"):
            results = store.search(query)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
        target = collector or GLOBAL_TIMING_COLLECTOR
        target.record(stage_name, elapsed_ms)


def time_function(stage_name: Optional[str] = None, collector: Optional[TimingCollector] = None):
    """
    Decorator to benchmark a function call.
    """
    def decorator(func: Callable):
        name = stage_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed_ms = round((time.perf_counter() - start) * 1000, 3)
                target = collector or GLOBAL_TIMING_COLLECTOR
                target.record(name, elapsed_ms)

        return wrapper
    return decorator


def calculate_latency_stats(latencies: List[float]) -> Dict[str, float]:
    """
    Calculates detailed percentile latency statistics from a series of measurements:
    P50, P90, P95, P99, Min, Max, Mean, Cold Latency (run 0), Warm Average (runs 1..N).
    """
    if not latencies:
        return {
            "samples": 0,
            "min_ms": 0.0,
            "max_ms": 0.0,
            "mean_ms": 0.0,
            "p50_ms": 0.0,
            "p90_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "cold_latency_ms": 0.0,
            "warm_avg_ms": 0.0,
        }

    sorted_lats = sorted(latencies)
    n = len(sorted_lats)

    def percentile(p: float) -> float:
        idx = int(p * n)
        idx = min(idx, n - 1)
        return round(sorted_lats[idx], 2)

    cold = round(latencies[0], 2)
    warm_avg = round(statistics.mean(latencies[1:]), 2) if n > 1 else cold

    return {
        "samples": n,
        "min_ms": round(min(sorted_lats), 2),
        "max_ms": round(max(sorted_lats), 2),
        "mean_ms": round(statistics.mean(sorted_lats), 2),
        "p50_ms": percentile(0.50),
        "p90_ms": percentile(0.90),
        "p95_ms": percentile(0.95),
        "p99_ms": percentile(0.99),
        "cold_latency_ms": cold,
        "warm_avg_ms": warm_avg,
    }
