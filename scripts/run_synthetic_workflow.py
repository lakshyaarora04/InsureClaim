#!/usr/bin/env python3
"""
InsureClaims - Automated Synthetic Data Generation & Edge-Case Validation Workflow
Tests the end-to-end pipeline:
1. Synthetic document generation across diverse formats (JSON, HTML, TXT)
2. Ingestion & LangChain RAG document indexing
3. Validation of boundary edge cases against Pydantic models
4. Automated decision evaluation against expected ground truth
5. Transactional persistence into the normalized 3NF database
"""

import sys
import os
import json
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.data_generator.synthetic_generator import synthetic_generator
from backend.retriever.langchain_rag import LangChainInsuranceRAG
from backend.utils.chunker import chunk_text
from backend.database.db_manager import db_manager


def run_synthetic_workflow():
    print("=" * 80)
    print("🚀 STARTING INSURECLAIMS SYNTHETIC DATA & EDGE-CASE VALIDATION WORKFLOW")
    print("=" * 80)

    # 1. Generate synthetic policy in multi-format representations
    print("\n📄 STEP 1: Generating synthetic policy in multiple document formats...")
    txt_policy = synthetic_generator.generate_synthetic_policy_document("txt")
    html_policy = synthetic_generator.generate_synthetic_policy_document("html")
    json_policy = synthetic_generator.generate_synthetic_policy_document("json")

    print(f"  ✅ Generated TXT policy ({len(txt_policy)} chars)")
    print(f"  ✅ Generated HTML policy ({len(html_policy)} chars)")
    print(f"  ✅ Generated JSON policy ({len(json_policy)} chars)")

    # 2. Index into LangChain RAG pipeline
    print("\n🧠 STEP 2: Indexing policy clauses into LangChain RAG pipeline...")
    chunks = chunk_text(txt_policy)
    rag_engine = LangChainInsuranceRAG()
    vector_store = rag_engine.index_documents(chunks, source_name="synthetic_policy.txt")
    print(f"  ✅ Successfully indexed {len(chunks)} chunks into LangChain FAISS vector store")

    # 3. Retrieve and test curated edge-case claims
    print("\n🧪 STEP 3: Evaluating edge-case claims against LangChain RAG engine...")
    edge_cases = synthetic_generator.get_edge_case_claims()
    passed = 0
    total = len(edge_cases)

    for case in edge_cases:
        cid = case["id"]
        cname = case["name"]
        payload = case["validated_payload"]
        expected = case["expected_decision"]

        print(f"\n  ▶ Testing [{cid}]: {cname}")
        print(f"    Payload: {payload['age']}yo {payload['gender']} | Procedure: {payload['procedure']} | Duration: {payload['policy_duration_months']}m")

        # Evaluate via LangChain RAG pipeline
        result = rag_engine.evaluate_claim(payload)
        actual = result["decision"]
        amount = result["amount"]
        confidence = result["confidence_score"]

        is_match = (actual.lower() == expected.lower())
        if is_match:
            passed += 1
            status_symbol = "✅ PASS"
        else:
            status_symbol = "❌ FAIL"

        print(f"    {status_symbol} -> Expected: {expected.upper()} | Got: {actual.upper()} (₹{amount:,.0f}, Conf: {confidence:.2f})")
        print(f"    Justification: {result['justification'][:120]}...")

        # 4. Save to Normalized Relational Database
        db_manager.save_complete_claim_record(
            claimant_data={"name": f"Synthetic Claimant {cid}", "age": payload["age"], "gender": payload["gender"], "city": payload["location"]},
            policy_data={"plan_name": "Synthetic Comprehensive", "duration_months": payload["policy_duration_months"]},
            claim_data={"procedure": payload["procedure"], "location": payload["location"], "claim_amount": payload["claim_amount"]},
            evaluation_data=result,
        )

    # 5. Multi-Join Query Verification
    print("\n🔍 STEP 4: Verifying multi-join retrieval from normalized database...")
    # Fetch all records for one of the claims
    sample_context = db_manager.get_complete_claim_context(case["id"])
    print(f"  ✅ Multi-join relational query executed successfully across 4 tables.")

    accuracy = (passed / total) * 100
    print("\n" + "=" * 80)
    print(f"🏁 WORKFLOW SUMMARY: {passed}/{total} Edge Cases Passed ({accuracy:.1f}% Accuracy)")
    print("=" * 80)
    return accuracy >= 85.0


if __name__ == "__main__":
    success = run_synthetic_workflow()
    sys.exit(0 if success else 1)
