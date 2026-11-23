"""
Unit tests for InsureClaims deterministic agent tools.
Tests:
- search_policy
- get_claim_history
- check_waiting_period
- calculate_coverage
- create_audit_entry
"""

import unittest
from backend.agent.tools import (
    search_policy,
    get_claim_history,
    check_waiting_period,
    calculate_coverage,
    create_audit_entry,
)


class TestAgentTools(unittest.TestCase):

    def test_search_policy_retrieves_clauses(self):
        res = search_policy("cataract surgery", top_k=3)
        self.assertIn("clauses", res)
        self.assertGreater(len(res["clauses"]), 0)

    def test_search_policy_handles_empty_query(self):
        res = search_policy("", top_k=3)
        self.assertEqual(res["status"], "NO_QUERY_PROVIDED")
        self.assertEqual(len(res["clauses"]), 0)

    def test_get_claim_history_detection(self):
        res = get_claim_history("test_claimant_1", procedure="cataract")
        self.assertIn("total_prior_claims", res)
        self.assertIn("is_repeated_submission", res)

    def test_check_waiting_period_cataract_deficit(self):
        # Cataract requires 24 months, 14 months should fail
        res = check_waiting_period("cataract surgery", policy_duration_months=14)
        self.assertFalse(res["satisfied"])
        self.assertEqual(res["status"], "NOT_MET")
        self.assertEqual(res["deficit_months"], 10)

    def test_check_waiting_period_cataract_met(self):
        # Cataract requires 24 months, 28 months should pass
        res = check_waiting_period("cataract surgery", policy_duration_months=28)
        self.assertTrue(res["satisfied"])
        self.assertEqual(res["status"], "MET")

    def test_check_waiting_period_accident_emergency_override(self):
        # Accident on day 10 should be exempt
        res = check_waiting_period(
            "fracture fixation",
            policy_duration_months=0,
            policy_duration_days=10,
            is_accident=True,
            is_emergency=True,
        )
        self.assertTrue(res["satisfied"])
        self.assertEqual(res["status"], "EXEMPT")

    def test_check_waiting_period_ped_36_months(self):
        # Pre-existing condition at 20 months should be rejected
        res = check_waiting_period(
            "diabetic nephropathy",
            policy_duration_months=20,
            is_pre_existing=True,
        )
        self.assertFalse(res["satisfied"])
        self.assertEqual(res["status"], "NOT_MET")

    def test_calculate_coverage_sublimit_cap(self):
        # Cataract sub-limit is ₹40,000. Claimed ₹60,000 should cap to ₹40,000
        res = calculate_coverage(
            claimed_amount=60000.0,
            procedure="cataract surgery",
        )
        self.assertEqual(res["eligible_amount"], 40000.0)
        self.assertEqual(res["sub_limit_applied"], 40000.0)

    def test_calculate_coverage_copay_deduction(self):
        # Hospitalization ₹50,000 with 10% co-pay should yield ₹45,000
        res = calculate_coverage(
            claimed_amount=50000.0,
            procedure="general hospitalization",
            co_pay_pct=0.10,
        )
        self.assertEqual(res["eligible_amount"], 45000.0)
        self.assertEqual(res["co_pay_deducted"], 5000.0)

    def test_calculate_coverage_exclusions(self):
        # Cosmetic surgery is excluded
        res_cosmetic = calculate_coverage(
            claimed_amount=80000.0,
            procedure="rhinoplasty cosmetic",
            is_cosmetic=True,
        )
        self.assertEqual(res_cosmetic["eligible_amount"], 0.0)

        # Experimental surgery is excluded
        res_exp = calculate_coverage(
            claimed_amount=200000.0,
            procedure="experimental stem cell",
            is_experimental=True,
        )
        self.assertEqual(res_exp["eligible_amount"], 0.0)

    def test_create_audit_entry_succeeds(self):
        res = create_audit_entry(
            claim_id="test_unit_claim_01",
            decision="approved",
            amount=45000.0,
            confidence_score=0.98,
            justification="Unit test audit verification",
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertIn("audit_id", res)


if __name__ == "__main__":
    unittest.main()
