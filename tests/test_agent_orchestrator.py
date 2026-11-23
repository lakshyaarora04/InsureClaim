"""
Unit and Integration tests for InsureClaims Agent Orchestrator.
Tests:
- InsuranceClaimAgent initialization
- Deterministic fallback adjudication workflow
- Tool trace tracking and execution status
- Insufficient information handling
- Ambiguous/conflicting rider detection
"""

import unittest
from backend.agent.orchestrator import InsuranceClaimAgent, claim_agent


class TestAgentOrchestrator(unittest.TestCase):

    def setUp(self):
        self.agent = InsuranceClaimAgent()

    def test_agent_initialization(self):
        self.assertIsNotNone(self.agent)
        self.assertIn("search_policy", self.agent.tool_map)
        self.assertIn("calculate_coverage", self.agent.tool_map)
        self.assertEqual(len(self.agent.tool_map), 5)

    def test_deterministic_workflow_cataract_sublimit(self):
        claim_data = {
            "procedure": "cataract surgery",
            "policy_duration_months": 30,
            "claim_amount": 60000.0,
            "is_emergency": False,
            "is_accident": False,
        }
        res = self.agent.adjudicate_claim(claim_data)
        self.assertEqual(res["decision"], "approved")
        self.assertEqual(res["amount"], 40000.0)  # Capped at ₹40,000 sub-limit
        self.assertIn("tools_invoked", res)
        self.assertGreaterEqual(len(res["tools_invoked"]), 4)

    def test_deterministic_workflow_waiting_period_rejection(self):
        claim_data = {
            "procedure": "hernia repair",
            "policy_duration_months": 16,  # requires 24 months
            "claim_amount": 48000.0,
        }
        res = self.agent.adjudicate_claim(claim_data)
        self.assertEqual(res["decision"], "rejected")
        self.assertEqual(res["amount"], 0.0)
        self.assertIn("Waiting period", res["justification"])

    def test_insufficient_information_guard(self):
        claim_data = {
            "procedure": "",
            "policy_duration_months": None,
            "claim_amount": None,
        }
        res = self.agent.adjudicate_claim(claim_data)
        self.assertEqual(res["decision"], "insufficient_information")
        self.assertEqual(res["amount"], 0.0)

    def test_conflicting_rider_human_review(self):
        claim_data = {
            "procedure": "bariatric surgery",
            "policy_duration_months": 36,
            "claim_amount": 220000.0,
            "has_conflicting_rider": True,
        }
        res = self.agent.adjudicate_claim(claim_data)
        self.assertEqual(res["decision"], "needs_review")
        self.assertEqual(res["amount"], 0.0)


if __name__ == "__main__":
    unittest.main()
