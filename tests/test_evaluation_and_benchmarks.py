"""
Unit tests for the Evaluation Benchmark Dataset and Retrieval Metrics suite.
Tests:
- Benchmark dataset structural integrity (40 canonical cases, 12 categories)
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Decision Accuracy
- Amount MAE
- Groundedness Score
"""

import unittest
from backend.evaluation.benchmark_dataset import BENCHMARK_CASES, get_benchmark_categories
from backend.evaluation.metrics import (
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    mean_reciprocal_rank,
    decision_accuracy,
    amount_mean_absolute_error,
    amount_accuracy,
    groundedness_score,
)


class TestEvaluationAndBenchmarks(unittest.TestCase):

    def test_benchmark_dataset_size_and_categories(self):
        self.assertEqual(len(BENCHMARK_CASES), 40)
        categories = get_benchmark_categories()
        self.assertGreaterEqual(len(categories), 12)
        # Ensure unique IDs
        ids = [c["id"] for c in BENCHMARK_CASES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_precision_at_k(self):
        retrieved = ["cataract surgery is covered under Section 3.1", "hernia repair", "appendectomy"]
        expected = ["cataract", "waiting period"]
        # Top 1 matches, top 2 does not -> 1/2 = 0.5
        p2 = precision_at_k(retrieved, expected, k=2)
        self.assertEqual(p2, 0.5)

    def test_recall_at_k(self):
        retrieved = ["cataract surgery is covered under Section 3.1 with 24 months waiting period"]
        expected = ["cataract", "waiting period"]
        r = recall_at_k(retrieved, expected, k=1)
        self.assertEqual(r, 1.0)

    def test_reciprocal_rank(self):
        retrieved = ["unrelated clause", "cataract surgery is covered", "another clause"]
        expected = ["cataract"]
        # Match is at rank 2 -> RR is 0.5
        rr = reciprocal_rank(retrieved, expected)
        self.assertEqual(rr, 0.5)

    def test_decision_accuracy(self):
        preds = ["approved", "rejected", "approved", "rejected"]
        truths = ["approved", "rejected", "rejected", "rejected"]
        acc = decision_accuracy(preds, truths)
        self.assertEqual(acc, 0.75)

    def test_amount_mae(self):
        preds = [40000.0, 0.0, 50000.0]
        truths = [40000.0, 0.0, 52000.0]
        mae = amount_mean_absolute_error(preds, truths)
        self.assertAlmostEqual(mae, 666.67, places=2)

    def test_groundedness_score(self):
        justification = "Claim approved: cataract is covered after 24 months under Section 3."
        clauses = ["Section 3: Cataract surgery is covered after 24 months."]
        score = groundedness_score(justification, clauses)
        self.assertGreaterEqual(score, 0.8)


if __name__ == "__main__":
    unittest.main()
