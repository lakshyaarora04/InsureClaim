"""
InsureClaims - Synthetic Data Generation & Edge-Case Testing Engine
Generates synthetic insurance policies and claim scenarios covering tricky edge-cases
(waiting period boundaries, exclusion exceptions, demographic boundaries, multi-format documents)
to test and validate the RAG pipeline.
"""

import json
import random
from typing import List, Dict, Any
from backend.validation.claim_validator import ClaimValidationRequest


# Canonical edge case scenarios for testing RAG correctness
EDGE_CASE_SCENARIOS = [
    {
        "id": "SYNTH_EDGE_001",
        "name": "Cataract Surgery - 1 Month Before 24m Waiting Period",
        "description": "Tests strict waiting period enforcement right at the boundary.",
        "payload": {
            "age": 52,
            "gender": "female",
            "procedure": "cataract surgery",
            "location": "Pune",
            "policy_duration_months": 23,
            "claim_amount": 40000.0,
        },
        "expected_decision": "rejected",
        "expected_reason_contains": "waiting period",
    },
    {
        "id": "SYNTH_EDGE_002",
        "name": "Cataract Surgery - 1 Month After 24m Waiting Period",
        "description": "Tests approval when waiting period is satisfied.",
        "payload": {
            "age": 52,
            "gender": "female",
            "procedure": "cataract surgery",
            "location": "Pune",
            "policy_duration_months": 25,
            "claim_amount": 45000.0,
        },
        "expected_decision": "approved",
        "expected_reason_contains": "waiting period",
    },
    {
        "id": "SYNTH_EDGE_003",
        "name": "Elective Cosmetic Surgery",
        "description": "Tests explicit policy exclusion for aesthetic procedures.",
        "payload": {
            "age": 29,
            "gender": "female",
            "procedure": "elective cosmetic rhinoplasty",
            "location": "Mumbai",
            "policy_duration_months": 36,
            "claim_amount": 120000.0,
        },
        "expected_decision": "rejected",
        "expected_reason_contains": "cosmetic",
    },
    {
        "id": "SYNTH_EDGE_004",
        "name": "Reconstructive Surgery Following Road Accident",
        "description": "Tests exception to cosmetic exclusion when trauma-related.",
        "payload": {
            "age": 34,
            "gender": "male",
            "procedure": "facial reconstructive surgery after road accident",
            "location": "Delhi",
            "policy_duration_months": 8,
            "claim_amount": 180000.0,
        },
        "expected_decision": "approved",
        "expected_reason_contains": "accident",
    },
    {
        "id": "SYNTH_EDGE_005",
        "name": "Emergency Cardiac Intervention During Initial Months",
        "description": "Tests emergency life-saving exception bypassing standard waiting periods.",
        "payload": {
            "age": 58,
            "gender": "male",
            "procedure": "emergency heart surgery cardiac arrest",
            "location": "Bangalore",
            "policy_duration_months": 4,
            "claim_amount": 280000.0,
        },
        "expected_decision": "approved",
        "expected_reason_contains": "emergency",
    },
    {
        "id": "SYNTH_EDGE_006",
        "name": "Routine Dental Cleaning & Veneers",
        "description": "Tests dental treatment exclusion in non-emergency situations.",
        "payload": {
            "age": 27,
            "gender": "female",
            "procedure": "dental treatment veneers and scaling",
            "location": "Chennai",
            "policy_duration_months": 18,
            "claim_amount": 35000.0,
        },
        "expected_decision": "rejected",
        "expected_reason_contains": "dental",
    },
    {
        "id": "SYNTH_EDGE_007",
        "name": "Emergency Dental Surgery Due to Accidental Trauma",
        "description": "Tests accident override for dental treatments.",
        "payload": {
            "age": 31,
            "gender": "male",
            "procedure": "dental jaw reconstruction emergency due to accident",
            "location": "Hyderabad",
            "policy_duration_months": 12,
            "claim_amount": 75000.0,
        },
        "expected_decision": "approved",
        "expected_reason_contains": "dental",
    },
    {
        "id": "SYNTH_EDGE_008",
        "name": "Joint Replacement at 14 Months",
        "description": "Tests 24-month waiting period on major orthopedic surgery.",
        "payload": {
            "age": 66,
            "gender": "male",
            "procedure": "knee joint replacement surgery",
            "location": "Kolkata",
            "policy_duration_months": 14,
            "claim_amount": 150000.0,
        },
        "expected_decision": "rejected",
        "expected_reason_contains": "waiting period",
    },
]


class SyntheticDataGenerator:
    """
    Engine to synthesize test datasets and edge-case policy documents.
    """

    def get_edge_case_claims(self) -> List[Dict[str, Any]]:
        """Return the curated suite of edge-case claims validated by Pydantic."""
        validated_cases = []
        for case in EDGE_CASE_SCENARIOS:
            # Validate payload schema
            validated_req = ClaimValidationRequest(**case["payload"])
            validated_cases.append({
                **case,
                "validated_payload": validated_req.model_dump(),
            })
        return validated_cases

    def generate_random_claims(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate stochastic synthetic claim payloads with randomized parameters."""
        procedures = [
            ("cataract surgery", 40000, 24),
            ("appendectomy surgery", 55000, 1),
            ("cardiac bypass surgery", 250000, 24),
            ("elective cosmetic surgery", 80000, 0),
            ("emergency accident trauma", 95000, 0),
            ("knee replacement surgery", 140000, 24),
            ("dental checkup and root canal", 20000, 0),
        ]
        cities = ["Mumbai", "Delhi", "Bangalore", "Pune", "Chennai", "Hyderabad"]

        results = []
        for i in range(count):
            proc, base_amt, wait_req = random.choice(procedures)
            duration = random.randint(1, 48)
            req = ClaimValidationRequest(
                age=random.randint(18, 80),
                gender=random.choice(["male", "female"]),
                procedure=proc,
                location=random.choice(cities),
                policy_duration_months=duration,
                claim_amount=float(base_amt + random.randint(-5000, 15000)),
            )
            results.append(req.model_dump())
        return results

    def generate_synthetic_policy_document(self, format_type: str = "txt") -> str:
        """
        Generate edge-case synthetic policy clauses in various document formats:
        'txt', 'html', or 'json'.
        """
        policy_data = {
            "policy_name": "InsureClaims Synthetic Comprehensive Policy v2024",
            "section_waiting_periods": (
                "Section 4.1: A mandatory 24-month waiting period applies to all specified procedures "
                "including Cataract surgery, Hernia, Hydrocele, Piles, Sinusitis, Joint Replacements, "
                "and Kidney stones. A 30-day initial waiting period applies to all non-accidental hospitalizations."
            ),
            "section_exclusions": (
                "Section 5.1: Excluded Treatments: All cosmetic, aesthetic, or reconstructive plastic surgeries "
                "are strictly excluded, unless required as direct treatment for severe burn or accidental injuries. "
                "Dental treatments are excluded unless emergency inpatient treatment necessitated by accidental injury."
            ),
            "section_emergency": (
                "Section 6.1: Emergency Exception: Immediate coverage is granted for life-threatening emergencies, "
                "cardiac arrest interventions, and accidental trauma irrespective of standard waiting periods."
            ),
        }

        if format_type == "json":
            return json.dumps(policy_data, indent=2)
        elif format_type == "html":
            return f"""
            <html>
                <head><title>{policy_data['policy_name']}</title></head>
                <body>
                    <h1>{policy_data['policy_name']}</h1>
                    <h2>Waiting Periods</h2>
                    <p>{policy_data['section_waiting_periods']}</p>
                    <h2>Exclusions</h2>
                    <p>{policy_data['section_exclusions']}</p>
                    <h2>Emergency Provisions</h2>
                    <p>{policy_data['section_emergency']}</p>
                </body>
            </html>
            """
        else:
            return (
                f"{policy_data['policy_name']}\n\n"
                f"{policy_data['section_waiting_periods']}\n\n"
                f"{policy_data['section_exclusions']}\n\n"
                f"{policy_data['section_emergency']}\n"
            )


synthetic_generator = SyntheticDataGenerator()
