"""
InsureClaims Evaluation Package
Provides benchmark datasets and quantitative retrieval and adjudication metrics.
"""

from backend.evaluation.benchmark_dataset import (
    BENCHMARK_CASES,
    get_benchmark_cases,
    get_benchmark_categories,
)
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
    evaluate_batch,
)

__all__ = [
    "BENCHMARK_CASES",
    "get_benchmark_cases",
    "get_benchmark_categories",
    "precision_at_k",
    "recall_at_k",
    "reciprocal_rank",
    "mean_reciprocal_rank",
    "decision_accuracy",
    "amount_mean_absolute_error",
    "amount_accuracy",
    "citation_correctness_score",
    "groundedness_score",
    "evaluate_batch",
]
