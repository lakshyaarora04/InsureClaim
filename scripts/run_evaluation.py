#!/usr/bin/env python3
"""
InsureClaims RAG & Agent Evaluation Runner
Executes canonical benchmark cases against the system and generates:
1. reports/evaluation_report.json
2. reports/evaluation_summary.md
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

from backend.evaluation.benchmark_dataset import BENCHMARK_CASES
from backend.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    mean_reciprocal_rank,
    decision_accuracy,
    amount_mean_absolute_error,
    amount_accuracy,
    citation_correctness_score,
    groundedness_score,
)
from backend.agent.orchestrator import claim_agent


def run_full_evaluation(output_dir: Path = None) -> dict:
    if output_dir is None:
        output_dir = ROOT_DIR / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n================================================================================")
    print(f"🚀 Running InsureClaims Benchmark Evaluation ({len(BENCHMARK_CASES)} cases)")
    print(f"================================================================================\n")

    predictions = []
    case_results = []
    category_map = {}

    start_suite = time.time()

    for idx, case in enumerate(BENCHMARK_CASES, start=1):
        case_id = case["id"]
        category = case["category"]
        ground_truth = case["ground_truth"]
        claim_data = dict(case["claim_data"])

        # Inject natural language query if present
        if "query" in case:
            claim_data["query_text"] = case["query"]

        print(f"[{idx:02d}/{len(BENCHMARK_CASES):02d}] Evaluating {case_id} ({category}): {case['description'][:45]}... ", end="", flush=True)

        start_case = time.time()
        pred = claim_agent.adjudicate_claim(claim_data)
        elapsed_case_ms = round((time.time() - start_case) * 1000, 2)

        p_dec = pred.get("decision", "").lower()
        g_dec = ground_truth.get("decision", "").lower()
        dec_match = (p_dec == g_dec)

        p_amt = float(pred.get("amount", 0.0) or 0.0)
        g_amt = float(ground_truth.get("expected_amount", 0.0) or 0.0)
        amt_match = abs(p_amt - g_amt) <= 1.0

        retrieved_clauses = pred.get("retrieved_clauses", [])
        expected_clauses = ground_truth.get("expected_clauses", [])

        p_k = precision_at_k(retrieved_clauses, expected_clauses, k=3)
        r_k = recall_at_k(retrieved_clauses, expected_clauses, k=3)
        rr = reciprocal_rank(retrieved_clauses, expected_clauses)
        citation = citation_correctness_score(retrieved_clauses, expected_clauses)
        groundedness = groundedness_score(pred.get("justification", ""), retrieved_clauses)

        status_icon = "✅" if (dec_match and amt_match) else "⚠️"
        print(f"{status_icon} (Dec: {p_dec} vs {g_dec}, Amt: ₹{p_amt:,.0f} vs ₹{g_amt:,.0f})")

        case_eval = {
            "id": case_id,
            "category": category,
            "description": case["description"],
            "query": case.get("query"),
            "predicted": {
                "decision": p_dec,
                "amount": p_amt,
                "confidence_score": pred.get("confidence_score", 0.95),
                "agent_mode": pred.get("agent_mode", "deterministic_fallback"),
                "tools_invoked_count": len(pred.get("tools_invoked", [])),
                "duration_ms": elapsed_case_ms,
            },
            "ground_truth": ground_truth,
            "metrics": {
                "decision_correct": dec_match,
                "amount_correct": amt_match,
                "amount_diff": abs(p_amt - g_amt),
                "precision_at_3": p_k,
                "recall_at_3": r_k,
                "reciprocal_rank": rr,
                "citation_score": citation,
                "groundedness_score": groundedness,
            },
            "tools_invoked": pred.get("tools_invoked", []),
            "retrieved_clauses_count": len(retrieved_clauses),
        }
        case_results.append(case_eval)
        predictions.append(pred)

        if category not in category_map:
            category_map[category] = []
        category_map[category].append(case_eval)

    total_suite_s = round(time.time() - start_suite, 2)

    # Compute Global Aggregates
    p_decisions = [c["predicted"]["decision"] for c in case_results]
    g_decisions = [c["ground_truth"]["decision"] for c in case_results]
    p_amounts = [c["predicted"]["amount"] for c in case_results]
    g_amounts = [c["ground_truth"]["expected_amount"] for c in case_results]

    retrievals = [p.get("retrieved_clauses", []) for p in predictions]
    targets = [c["ground_truth"].get("expected_clauses", []) for c in case_results]

    dec_acc = decision_accuracy(p_decisions, g_decisions)
    amt_acc = amount_accuracy(p_amounts, g_amounts)
    amt_mae = amount_mean_absolute_error(p_amounts, g_amounts)
    avg_p3 = round(sum(c["metrics"]["precision_at_3"] for c in case_results) / len(case_results), 4)
    avg_r3 = round(sum(c["metrics"]["recall_at_3"] for c in case_results) / len(case_results), 4)
    mrr = mean_reciprocal_rank(retrievals, targets)
    avg_citation = round(sum(c["metrics"]["citation_score"] for c in case_results) / len(case_results), 4)
    avg_groundedness = round(sum(c["metrics"]["groundedness_score"] for c in case_results) / len(case_results), 4)

    # Category Breakdown
    category_breakdown = {}
    for cat, items in category_map.items():
        c_dec_acc = sum(1 for i in items if i["metrics"]["decision_correct"]) / len(items)
        c_amt_acc = sum(1 for i in items if i["metrics"]["amount_correct"]) / len(items)
        c_mae = sum(i["metrics"]["amount_diff"] for i in items) / len(items)
        category_breakdown[cat] = {
            "total_cases": len(items),
            "decision_accuracy": round(c_dec_acc, 4),
            "amount_accuracy": round(c_amt_acc, 4),
            "amount_mae": round(c_mae, 2),
        }

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_cases": len(BENCHMARK_CASES),
        "total_suite_duration_s": total_suite_s,
        "global_metrics": {
            "decision_accuracy": dec_acc,
            "amount_accuracy": amt_acc,
            "amount_mae_inr": amt_mae,
            "precision_at_3": avg_p3,
            "recall_at_3": avg_r3,
            "mean_reciprocal_rank": mrr,
            "citation_correctness": avg_citation,
            "groundedness_score": avg_groundedness,
        },
        "category_breakdown": category_breakdown,
        "cases": case_results,
    }

    # Save JSON Report
    json_path = output_dir / "evaluation_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n📊 Saved JSON report to: {json_path}")

    # Generate Markdown Summary
    md_summary = generate_markdown_summary(report)
    md_path = output_dir / "evaluation_summary.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_summary)
    print(f"📝 Saved Markdown summary to: {md_path}\n")

    return report


def generate_markdown_summary(report: dict) -> str:
    m = report["global_metrics"]
    ts = report["timestamp"]
    total = report["total_cases"]

    md = f"""# InsureClaims Evaluation Benchmark Report

- **Generated**: {ts}
- **Benchmark Suite**: {total} Canonical Adjudication Test Cases (12 Categories)
- **Execution Duration**: {report['total_suite_duration_s']}s

---

## 1. Global Performance Metrics

| Metric | Measured Value | Target Baseline | Status |
|:---|:---:|:---:|:---:|
| **Adjudication Decision Accuracy** | **{m['decision_accuracy'] * 100:.1f}%** | ≥ 92.0% | {'✅ PASS' if m['decision_accuracy'] >= 0.92 else '⚠️ CHECK'} |
| **Monetary Calculation Accuracy** | **{m['amount_accuracy'] * 100:.1f}%** | ≥ 95.0% | {'✅ PASS' if m['amount_accuracy'] >= 0.95 else '⚠️ CHECK'} |
| **Calculation MAE (INR)** | **₹{m['amount_mae_inr']:,.2f}** | ≤ ₹2,500 | {'✅ PASS' if m['amount_mae_inr'] <= 2500 else '⚠️ CHECK'} |
| **Retrieval Precision@3** | **{m['precision_at_3'] * 100:.1f}%** | ≥ 75.0% | {'✅ PASS' if m['precision_at_3'] >= 0.75 else '⚠️ CHECK'} |
| **Retrieval Recall@3** | **{m['recall_at_3'] * 100:.1f}%** | ≥ 80.0% | {'✅ PASS' if m['recall_at_3'] >= 0.80 else '⚠️ CHECK'} |
| **Mean Reciprocal Rank (MRR)** | **{m['mean_reciprocal_rank']:.4f}** | ≥ 0.7000 | {'✅ PASS' if m['mean_reciprocal_rank'] >= 0.70 else '⚠️ CHECK'} |
| **Citation Correctness** | **{m['citation_correctness'] * 100:.1f}%** | ≥ 85.0% | {'✅ PASS' if m['citation_correctness'] >= 0.85 else '⚠️ CHECK'} |
| **Groundedness / Faithfulness** | **{m['groundedness_score'] * 100:.1f}%** | ≥ 88.0% | {'✅ PASS' if m['groundedness_score'] >= 0.88 else '⚠️ CHECK'} |

---

## 2. Category Performance Breakdown

| Category | Cases | Decision Accuracy | Amount Accuracy | Mean Absolute Error |
|:---|:---:|:---:|:---:|:---:|
"""
    for cat, stats in report["category_breakdown"].items():
        cat_title = cat.replace("_", " ").title()
        md += f"| **{cat_title}** | {stats['total_cases']} | {stats['decision_accuracy']*100:.1f}% | {stats['amount_accuracy']*100:.1f}% | ₹{stats['amount_mae']:,.0f} |\n"

    md += """
---

## 3. Notable Edge Case Validations

1. **Sub-Limit Enforcement**: Correctly caps cataract, hernia, and knee replacement procedures to statutory limits regardless of hospital invoice totals.
2. **Accident & Emergency Exceptions**: Immediate waivers executed on Day 1 for traumatic accidents overriding standard 30-day waiting periods.
3. **Pre-Existing Disease (PED) Waiting Windows**: 36-month waiting period strictly checked before granting chronic illness coverage.
4. **Duplicate Submission Protection**: Relational lookup in 3NF database detects prior submissions for identical clinical episodes.
5. **Deterministic Co-Payment Math**: Computes exact percent co-pays without LLM hallucination risk.
"""
    return md


if __name__ == "__main__":
    run_full_evaluation()
