#!/usr/bin/env python3
"""
InsureClaims Performance & Latency Benchmarking Runner
Measures:
- Cold Start vs Warm Latency
- Percentiles (P50, P90, P95, P99)
- Stage-by-Stage Latency Breakdown (Search, Rules, Financial Calc, Audit)
- Throughput (Queries/sec)
Outputs: reports/benchmark_report.json
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from backend.utils.timing import calculate_latency_stats, TimingCollector, time_block
from backend.agent.orchestrator import claim_agent
from backend.agent.tools import (
    search_policy,
    get_claim_history,
    check_waiting_period,
    calculate_coverage,
    create_audit_entry,
)

SAMPLE_BENCHMARK_QUERIES = [
    {
        "procedure": "cataract surgery",
        "policy_duration_months": 30,
        "claim_amount": 55000.0,
        "is_emergency": False,
        "is_accident": False,
    },
    {
        "procedure": "emergency appendectomy",
        "policy_duration_months": 14,
        "claim_amount": 42000.0,
        "is_emergency": True,
        "is_accident": False,
    },
    {
        "procedure": "knee replacement",
        "policy_duration_months": 18,
        "claim_amount": 120000.0,
        "is_emergency": False,
        "is_accident": False,
    },
    {
        "procedure": "accidental fracture surgery",
        "policy_duration_months": 1,
        "claim_amount": 75000.0,
        "is_emergency": True,
        "is_accident": True,
    },
    {
        "procedure": "hernia repair",
        "policy_duration_months": 28,
        "claim_amount": 65000.0,
        "is_emergency": False,
        "is_accident": False,
    },
]


def run_latency_benchmarks(iterations: int = 15, output_dir: Path = None) -> dict:
    if output_dir is None:
        output_dir = ROOT_DIR / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n================================================================================")
    print(f"⚡ Running InsureClaims Performance & Latency Benchmarks ({iterations} iterations)")
    print(f"================================================================================\n")

    overall_latencies = []
    stage_collector = TimingCollector()

    for i in range(iterations):
        sample = SAMPLE_BENCHMARK_QUERIES[i % len(SAMPLE_BENCHMARK_QUERIES)]
        is_cold = (i == 0)
        marker = "❄️ [COLD]" if is_cold else f"🔥 [WARM #{i:02d}]"

        start_iter = time.perf_counter()

        # Step 1: Policy Vector Search
        with time_block("vector_search", stage_collector):
            search_res = search_policy(sample["procedure"], top_k=3)

        # Step 2: Relational Claim History
        with time_block("claim_history_lookup", stage_collector):
            hist_res = get_claim_history(claimant_id=f"bench_user_{i}", procedure=sample["procedure"])

        # Step 3: Waiting Period Rules
        with time_block("waiting_period_rules", stage_collector):
            wp_res = check_waiting_period(
                procedure=sample["procedure"],
                policy_duration_months=sample["policy_duration_months"],
                is_emergency=sample.get("is_emergency", False),
                is_accident=sample.get("is_accident", False),
            )

        # Step 4: Deterministic Coverage Calculation
        with time_block("coverage_calculation", stage_collector):
            calc_res = calculate_coverage(
                claimed_amount=sample["claim_amount"],
                sum_insured=500000.0,
                procedure=sample["procedure"],
            )

        # Step 5: Relational DB Audit
        with time_block("audit_persistence", stage_collector):
            audit_res = create_audit_entry(
                claim_id=f"bench_claim_{i}",
                decision="approved" if wp_res.get("satisfied") else "rejected",
                amount=calc_res.get("eligible_amount", 0.0),
                confidence_score=0.98,
                justification="Automated benchmarking run",
            )

        iter_elapsed_ms = round((time.perf_counter() - start_iter) * 1000, 2)
        overall_latencies.append(iter_elapsed_ms)
        print(f"{marker} Iteration {i+1:02d}: {iter_elapsed_ms:.2f} ms")

    # Aggregate Statistics
    overall_stats = calculate_latency_stats(overall_latencies)
    stage_breakdown = stage_collector.get_summary()

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "iterations": iterations,
        "overall_latency_ms": overall_stats,
        "stage_latency_breakdown_ms": stage_breakdown,
        "throughput_qps": round(1000.0 / overall_stats["mean_ms"], 2) if overall_stats["mean_ms"] > 0 else 0.0,
    }

    # Save to reports/benchmark_report.json
    out_file = output_dir / "benchmark_report.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n📈 Saved Benchmark Report to: {out_file}")
    print(f"   • Cold Latency: {overall_stats['cold_latency_ms']} ms")
    print(f"   • Warm Average: {overall_stats['warm_avg_ms']} ms")
    print(f"   • P50 (Median): {overall_stats['p50_ms']} ms")
    print(f"   • P95 Latency:  {overall_stats['p95_ms']} ms")
    print(f"   • Throughput:   {report['throughput_qps']} queries/sec\n")

    return report


if __name__ == "__main__":
    run_latency_benchmarks()
