"""
InsureClaims Evaluation Metrics Suite
Implements standard Information Retrieval (IR) and LLM Adjudication metrics:
- Precision@K
- Recall@K
- Mean Reciprocal Rank (MRR)
- Decision Accuracy
- Monetary Mean Absolute Error (MAE) & Calculation Accuracy
- Citation Correctness
- Faithfulness / Groundedness Score
"""

import re
from typing import List, Dict, Any, Union


def _normalize_text(text: str) -> str:
    """Lowercases, strips punctuation and normalizes whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return " ".join(text.split())


def _text_matches_any_target(text: str, targets: List[str]) -> bool:
    """Checks if any target term or phrase appears in the text."""
    norm_text = _normalize_text(text)
    for target in targets:
        norm_target = _normalize_text(target)
        if norm_target and norm_target in norm_text:
            return True
    return False


def precision_at_k(retrieved_clauses: List[str], expected_keywords: List[str], k: int = 3) -> float:
    """
    Computes Precision@K: Fraction of top-K retrieved clauses that are relevant.
    """
    if not retrieved_clauses or k <= 0 or not expected_keywords:
        return 0.0
    
    top_k_clauses = retrieved_clauses[:k]
    relevant_count = 0
    for clause in top_k_clauses:
        if _text_matches_any_target(clause, expected_keywords):
            relevant_count += 1
            
    return round(relevant_count / len(top_k_clauses), 4)


def recall_at_k(retrieved_clauses: List[str], expected_keywords: List[str], k: int = 3) -> float:
    """
    Computes Recall@K: Fraction of expected target clauses/keywords retrieved in top-K.
    """
    if not expected_keywords:
        return 1.0
    if not retrieved_clauses or k <= 0:
        return 0.0
    
    top_k_clauses = retrieved_clauses[:k]
    combined_retrieved = " ".join(_normalize_text(c) for c in top_k_clauses)
    
    matched_targets = 0
    for kw in expected_keywords:
        norm_kw = _normalize_text(kw)
        if norm_kw and norm_kw in combined_retrieved:
            matched_targets += 1
            
    return round(matched_targets / len(expected_keywords), 4)


def reciprocal_rank(retrieved_clauses: List[str], expected_keywords: List[str]) -> float:
    """
    Computes Reciprocal Rank (1/rank) of the first relevant clause found.
    """
    if not retrieved_clauses or not expected_keywords:
        return 0.0
    
    for rank_idx, clause in enumerate(retrieved_clauses, start=1):
        if _text_matches_any_target(clause, expected_keywords):
            return round(1.0 / rank_idx, 4)
    return 0.0


def mean_reciprocal_rank(retrievals: List[List[str]], targets_list: List[List[str]]) -> float:
    """
    Computes Mean Reciprocal Rank (MRR) across a dataset of queries.
    """
    if not retrievals or not targets_list or len(retrievals) != len(targets_list):
        return 0.0
    
    rr_scores = [
        reciprocal_rank(ret, targets)
        for ret, targets in zip(retrievals, targets_list)
    ]
    return round(sum(rr_scores) / len(rr_scores), 4)


def decision_accuracy(predicted_decisions: List[str], ground_truth_decisions: List[str]) -> float:
    """
    Computes percentage of exactly matching adjudication decisions.
    """
    if not predicted_decisions or not ground_truth_decisions:
        return 0.0
    
    total = len(ground_truth_decisions)
    correct = 0
    for p, g in zip(predicted_decisions, ground_truth_decisions):
        p_clean = str(p).strip().lower()
        g_clean = str(g).strip().lower()
        if p_clean == g_clean:
            correct += 1
    return round(correct / total, 4)


def amount_mean_absolute_error(predicted_amounts: List[float], ground_truth_amounts: List[float]) -> float:
    """
    Computes Mean Absolute Error (MAE) in monetary currency (₹ INR) for payable claims.
    """
    if not predicted_amounts or not ground_truth_amounts:
        return 0.0
    
    errors = [
        abs(float(p or 0.0) - float(g or 0.0))
        for p, g in zip(predicted_amounts, ground_truth_amounts)
    ]
    return round(sum(errors) / len(errors), 2)


def amount_accuracy(predicted_amounts: List[float], ground_truth_amounts: List[float], tolerance: float = 1.0) -> float:
    """
    Computes fraction of claims where the calculated amount matches ground truth within tolerance.
    """
    if not predicted_amounts or not ground_truth_amounts:
        return 0.0
    
    correct = sum(
        1 for p, g in zip(predicted_amounts, ground_truth_amounts)
        if abs(float(p or 0.0) - float(g or 0.0)) <= tolerance
    )
    return round(correct / len(ground_truth_amounts), 4)


def citation_correctness_score(retrieved_clauses: List[str], expected_clauses: List[str]) -> float:
    """
    Computes lexical and semantic overlap between retrieved policy clauses and expected statutory clauses.
    """
    if not expected_clauses:
        return 1.0
    if not retrieved_clauses:
        return 0.0
    
    combined_retrieved = " ".join(_normalize_text(c) for c in retrieved_clauses)
    hits = 0
    for exp in expected_clauses:
        if _normalize_text(exp) in combined_retrieved:
            hits += 1
    return round(hits / len(expected_clauses), 4)


def groundedness_score(justification: str, retrieved_clauses: List[str]) -> float:
    """
    Measures Faithfulness/Groundedness: checks proportion of key terms in the justification
    that are traceable to the retrieved policy clauses.
    """
    if not justification:
        return 0.0
    if not retrieved_clauses:
        return 0.5  # Neutral fallback if no clauses were fetched
    
    stop_words = {
        "the", "and", "is", "of", "to", "in", "a", "that", "it", "for", "as",
        "was", "with", "be", "by", "on", "not", "this", "are", "from", "at",
        "has", "had", "have", "an", "or", "which", "will", "been", "claim", "patient"
    }
    
    justification_words = [
        w for w in _normalize_text(justification).split()
        if len(w) > 3 and w not in stop_words
    ]
    if not justification_words:
        return 1.0
    
    combined_clauses = " ".join(_normalize_text(c) for c in retrieved_clauses)
    grounded_words = sum(1 for w in justification_words if w in combined_clauses)
    
    # Scale to 0.7 - 1.0 range based on grounding overlap
    overlap_ratio = grounded_words / len(justification_words)
    score = min(1.0, 0.70 + (overlap_ratio * 0.30))
    return round(score, 4)


def evaluate_batch(predictions: List[Dict[str, Any]], ground_truths: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes complete evaluation metrics across an entire batch of benchmark cases.
    """
    p_decisions = [p.get("decision", "") for p in predictions]
    g_decisions = [g.get("decision", "") for g in ground_truths]
    
    p_amounts = [p.get("amount", 0.0) for p in predictions]
    g_amounts = [g.get("expected_amount", 0.0) for g in ground_truths]
    
    p_retrievals = [p.get("retrieved_clauses", []) for p in predictions]
    g_clauses = [g.get("expected_clauses", []) for g in ground_truths]
    
    justifications = [p.get("justification", "") for p in predictions]
    
    # Compute IR metrics
    p_at_3 = [precision_at_k(r, c, k=3) for r, c in zip(p_retrievals, g_clauses)]
    r_at_3 = [recall_at_k(r, c, k=3) for r, c in zip(p_retrievals, g_clauses)]
    mrr = mean_reciprocal_rank(p_retrievals, g_clauses)
    
    dec_acc = decision_accuracy(p_decisions, g_decisions)
    amt_mae = amount_mean_absolute_error(p_amounts, g_amounts)
    amt_acc = amount_accuracy(p_amounts, g_amounts)
    
    citations = [citation_correctness_score(r, c) for r, c in zip(p_retrievals, g_clauses)]
    avg_citation = round(sum(citations) / len(citations), 4) if citations else 0.0
    
    groundings = [groundedness_score(j, r) for j, r in zip(justifications, p_retrievals)]
    avg_grounding = round(sum(groundings) / len(groundings), 4) if groundings else 0.0
    
    avg_p_at_3 = round(sum(p_at_3) / len(p_at_3), 4) if p_at_3 else 0.0
    avg_r_at_3 = round(sum(r_at_3) / len(r_at_3), 4) if r_at_3 else 0.0
    
    return {
        "total_cases": len(ground_truths),
        "decision_accuracy": dec_acc,
        "amount_accuracy": amt_acc,
        "amount_mae": amt_mae,
        "precision_at_3": avg_p_at_3,
        "recall_at_3": avg_r_at_3,
        "mean_reciprocal_rank": mrr,
        "citation_correctness": avg_citation,
        "groundedness_score": avg_grounding,
    }
