"""
Integration tests for FastAPI endpoints.
Tests:
- GET /api/agent/tools
- POST /api/agent/adjudicate
- GET /api/evaluation/benchmark
- GET /api/benchmarks/latest
- GET /api/stats
- POST /api/analyze
"""

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.api.routes import router


class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app = FastAPI()
        app.include_router(router)
        cls.client = TestClient(app)

    def test_get_agent_tools(self):
        res = self.client.get("/api/agent/tools")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["total_tools"], 5)
        tool_names = [t["function"]["name"] for t in data["tools"]]
        self.assertIn("search_policy", tool_names)
        self.assertIn("calculate_coverage", tool_names)

    def test_post_agent_adjudicate(self):
        payload = {
            "procedure": "cataract surgery",
            "policy_duration_months": 30,
            "claim_amount": 55000.0,
        }
        res = self.client.post("/api/agent/adjudicate", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["decision"], "approved")
        self.assertEqual(data["amount"], 40000.0)
        self.assertIn("tools_invoked", data)

    def test_get_evaluation_benchmark(self):
        res = self.client.get("/api/evaluation/benchmark")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["total_cases"], 40)
        self.assertGreaterEqual(len(data["categories"]), 12)

    def test_get_benchmarks_latest(self):
        res = self.client.get("/api/benchmarks/latest")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("overall_latency_ms", data)
        self.assertIn("p50_ms", data["overall_latency_ms"])

    def test_get_system_stats(self):
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")

    def test_post_analyze(self):
        res = self.client.post("/api/analyze", json={"query": "A 45-year-old male needs cataract surgery in Pune. Policy is 24 months old."})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("decision", data)
        self.assertIn("amount", data)
        self.assertIn("report_id", data)


if __name__ == "__main__":
    unittest.main()
