# InsureClaims Evaluation Benchmark Report

- **Generated**: 2026-11-22T07:22:39.315403
- **Benchmark Suite**: 40 Canonical Adjudication Test Cases (12 Categories)
- **Execution Duration**: 0.22s

---

## 1. Global Performance Metrics

| Metric | Measured Value | Target Baseline | Status |
|:---|:---:|:---:|:---:|
| **Adjudication Decision Accuracy** | **100.0%** | ≥ 92.0% | ✅ PASS |
| **Monetary Calculation Accuracy** | **100.0%** | ≥ 95.0% | ✅ PASS |
| **Calculation MAE (INR)** | **₹0.00** | ≤ ₹2,500 | ✅ PASS |
| **Retrieval Precision@3** | **47.5%** | ≥ 75.0% | ⚠️ CHECK |
| **Retrieval Recall@3** | **44.4%** | ≥ 80.0% | ⚠️ CHECK |
| **Mean Reciprocal Rank (MRR)** | **0.5729** | ≥ 0.7000 | ⚠️ CHECK |
| **Citation Correctness** | **46.0%** | ≥ 85.0% | ⚠️ CHECK |
| **Groundedness / Faithfulness** | **83.2%** | ≥ 88.0% | ⚠️ CHECK |

---

## 2. Category Performance Breakdown

| Category | Cases | Decision Accuracy | Amount Accuracy | Mean Absolute Error |
|:---|:---:|:---:|:---:|:---:|
| **Standard Approved** | 5 | 100.0% | 100.0% | ₹0 |
| **Specific Waiting Period Not Met** | 5 | 100.0% | 100.0% | ₹0 |
| **Initial Waiting Period Not Met** | 3 | 100.0% | 100.0% | ₹0 |
| **Ped Waiting Period Not Met** | 3 | 100.0% | 100.0% | ₹0 |
| **Accident Emergency Exception** | 3 | 100.0% | 100.0% | ₹0 |
| **Sublimit Cap Applied** | 5 | 100.0% | 100.0% | ₹0 |
| **Permanent Exclusion** | 4 | 100.0% | 100.0% | ₹0 |
| **Duplicate Claim** | 2 | 100.0% | 100.0% | ₹0 |
| **Copay Deduction** | 3 | 100.0% | 100.0% | ₹0 |
| **Sum Insured Exhaustion** | 2 | 100.0% | 100.0% | ₹0 |
| **Insufficient Information** | 3 | 100.0% | 100.0% | ₹0 |
| **Needs Human Review** | 2 | 100.0% | 100.0% | ₹0 |

---

## 3. Notable Edge Case Validations

1. **Sub-Limit Enforcement**: Correctly caps cataract, hernia, and knee replacement procedures to statutory limits regardless of hospital invoice totals.
2. **Accident & Emergency Exceptions**: Immediate waivers executed on Day 1 for traumatic accidents overriding standard 30-day waiting periods.
3. **Pre-Existing Disease (PED) Waiting Windows**: 36-month waiting period strictly checked before granting chronic illness coverage.
4. **Duplicate Submission Protection**: Relational lookup in 3NF database detects prior submissions for identical clinical episodes.
5. **Deterministic Co-Payment Math**: Computes exact percent co-pays without LLM hallucination risk.
