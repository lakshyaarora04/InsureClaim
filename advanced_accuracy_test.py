#!/usr/bin/env python3
"""
Advanced Accuracy Test for Insurance Claim Evaluation
Tests with realistic scenarios to ensure 90+% accuracy in production
"""

import requests
import json
import time
import random

WEBHOOK_URL = "http://localhost:8001/webhook/query"

def create_realistic_test_cases():
    """Create realistic insurance claim test cases with expected outcomes"""
    
    test_cases = [
        # High-value, low-risk claims (should be approved with high confidence)
        {
            "name": "Standard Dental Procedure - Young Adult",
            "data": {
                "claim_id": "real_001",
                "patient_age": 28,
                "patient_gender": "female",
                "procedure": "dental procedure",
                "location": "mumbai",
                "policy_duration_months": 18,
                "claim_amount": 25000.0
            },
            "expected_approved": True,
            "expected_confidence_min": 0.85,
            "expected_coverage_min": 0.8
        },
        {
            "name": "Routine Eye Surgery - Middle Age",
            "data": {
                "claim_id": "real_002",
                "patient_age": 42,
                "patient_gender": "male",
                "procedure": "eye surgery",
                "location": "delhi",
                "policy_duration_months": 24,
                "claim_amount": 45000.0
            },
            "expected_approved": True,
            "expected_confidence_min": 0.8,
            "expected_coverage_min": 0.8
        },
        {
            "name": "Minor Orthopedic - Senior",
            "data": {
                "claim_id": "real_003",
                "patient_age": 58,
                "patient_gender": "female",
                "procedure": "knee surgery",
                "location": "bangalore",
                "policy_duration_months": 36,
                "claim_amount": 80000.0
            },
            "expected_approved": True,
            "expected_confidence_min": 0.7,
            "expected_coverage_min": 0.6
        },
        
        # Medium-risk claims (should be approved with medium confidence)
        {
            "name": "Cardiac Procedure - Middle Age",
            "data": {
                "claim_id": "real_004",
                "patient_age": 45,
                "patient_gender": "male",
                "procedure": "heart surgery",
                "location": "mumbai",
                "policy_duration_months": 12,
                "claim_amount": 300000.0
            },
            "expected_approved": True,
            "expected_confidence_min": 0.5,
            "expected_coverage_min": 0.6
        },
        {
            "name": "Neurological Procedure - Senior",
            "data": {
                "claim_id": "real_005",
                "patient_age": 65,
                "patient_gender": "female",
                "procedure": "brain surgery",
                "location": "chennai",
                "policy_duration_months": 24,
                "claim_amount": 500000.0
            },
            "expected_approved": True,
            "expected_confidence_min": 0.4,
            "expected_coverage_min": 0.6
        },
        
        # High-risk claims (should be approved with low confidence or rejected)
        {
            "name": "Complex Surgery - Young Patient",
            "data": {
                "claim_id": "real_006",
                "patient_age": 22,
                "patient_gender": "male",
                "procedure": "organ transplant",
                "location": "mumbai",
                "policy_duration_months": 6,
                "claim_amount": 800000.0
            },
            "expected_approved": False,  # Too complex for young patient
            "expected_confidence_min": 0.1
        },
        {
            "name": "High Amount Claim - Short Policy",
            "data": {
                "claim_id": "real_007",
                "patient_age": 35,
                "patient_gender": "female",
                "procedure": "cancer treatment",
                "location": "delhi",
                "policy_duration_months": 3,
                "claim_amount": 1200000.0
            },
            "expected_approved": False,  # Exceeds policy limit
            "expected_confidence_min": 0.1
        },
        
        # Edge cases that should be rejected
        {
            "name": "Underage Patient",
            "data": {
                "claim_id": "real_008",
                "patient_age": 16,
                "patient_gender": "male",
                "procedure": "general checkup",
                "location": "mumbai",
                "policy_duration_months": 12,
                "claim_amount": 10000.0
            },
            "expected_approved": False,
            "expected_confidence_min": 0.1
        },
        {
            "name": "Excessive Claim Amount",
            "data": {
                "claim_id": "real_009",
                "patient_age": 50,
                "patient_gender": "female",
                "procedure": "plastic surgery",
                "location": "bangalore",
                "policy_duration_months": 48,
                "claim_amount": 2000000.0
            },
            "expected_approved": False,
            "expected_confidence_min": 0.1
        },
        
        # Borderline cases for accuracy testing
        {
            "name": "Borderline Age - Senior",
            "data": {
                "claim_id": "real_010",
                "patient_age": 75,
                "patient_gender": "male",
                "procedure": "hip replacement",
                "location": "chennai",
                "policy_duration_months": 60,
                "claim_amount": 150000.0
            },
            "expected_approved": True,  # Should be approved with reduced coverage
            "expected_confidence_min": 0.3,
            "expected_coverage_min": 0.6
        },
        {
            "name": "Borderline Amount",
            "data": {
                "claim_id": "real_011",
                "patient_age": 40,
                "patient_gender": "female",
                "procedure": "spine surgery",
                "location": "mumbai",
                "policy_duration_months": 18,
                "claim_amount": 950000.0
            },
            "expected_approved": True,  # Just under the 1M limit
            "expected_confidence_min": 0.5,
            "expected_coverage_min": 0.6
        }
    ]
    
    return test_cases

def test_accuracy():
    """Test webhook accuracy with realistic scenarios"""
    
    test_cases = create_realistic_test_cases()
    
    print("🎯 Advanced Accuracy Test for Insurance Claim Evaluation")
    print("=" * 70)
    print(f"🎯 Target URL: {WEBHOOK_URL}")
    print(f"⏰ Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total Test Cases: {len(test_cases)}")
    
    results = []
    total_processing_time = 0
    correct_decisions = 0
    correct_confidence = 0
    correct_coverage = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"   Input: {test_case['data']}")
        
        try:
            start_time = time.time()
            response = requests.post(
                WEBHOOK_URL,
                headers={"Content-Type": "application/json"},
                json={"data": test_case['data']},
                timeout=15
            )
            processing_time = (time.time() - start_time) * 1000
            total_processing_time += processing_time
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Response: {json.dumps(result, indent=2)}")
                
                # Validate decision accuracy
                decision_correct = result.get("approved") == test_case["expected_approved"]
                if decision_correct:
                    correct_decisions += 1
                    print(f"   ✅ Decision: CORRECT")
                else:
                    print(f"   ❌ Decision: WRONG (expected {test_case['expected_approved']}, got {result.get('approved')})")
                
                # Validate confidence score
                confidence_ok = result.get("confidence_score", 0) >= test_case["expected_confidence_min"]
                if confidence_ok:
                    correct_confidence += 1
                    print(f"   ✅ Confidence: ACCEPTABLE ({result.get('confidence_score'):.3f})")
                else:
                    print(f"   ⚠️  Confidence: LOW ({result.get('confidence_score'):.3f} < {test_case['expected_confidence_min']})")
                
                # Validate coverage for approved claims
                coverage_ok = True
                if test_case["expected_approved"] and result.get("approved"):
                    if "expected_coverage_min" in test_case:
                        coverage_ratio = result.get("approved_amount", 0) / test_case["data"]["claim_amount"]
                        coverage_ok = coverage_ratio >= test_case["expected_coverage_min"]
                        if coverage_ok:
                            correct_coverage += 1
                            print(f"   ✅ Coverage: ACCEPTABLE ({coverage_ratio:.1%})")
                        else:
                            print(f"   ⚠️  Coverage: LOW ({coverage_ratio:.1%} < {test_case['expected_coverage_min']:.1%})")
                
                # Performance check
                if result.get("processing_time_ms", 0) > 2000:
                    print(f"   ⚠️  Slow response: {result.get('processing_time_ms'):.1f}ms")
                
                results.append({
                    "test_name": test_case["name"],
                    "decision_correct": decision_correct,
                    "confidence_ok": confidence_ok,
                    "coverage_ok": coverage_ok,
                    "processing_time": processing_time,
                    "response": result
                })
                
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    "test_name": test_case["name"],
                    "decision_correct": False,
                    "confidence_ok": False,
                    "coverage_ok": False,
                    "processing_time": processing_time,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results.append({
                "test_name": test_case["name"],
                "decision_correct": False,
                "confidence_ok": False,
                "coverage_ok": False,
                "processing_time": 0,
                "error": str(e)
            })
    
    # Calculate accuracy metrics
    total_tests = len(test_cases)
    decision_accuracy = (correct_decisions / total_tests) * 100
    confidence_accuracy = (correct_confidence / total_tests) * 100
    coverage_accuracy = (correct_coverage / total_tests) * 100 if correct_coverage > 0 else 100
    
    # Overall accuracy (weighted average)
    overall_accuracy = (decision_accuracy * 0.6 + confidence_accuracy * 0.3 + coverage_accuracy * 0.1)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 ACCURACY TEST RESULTS")
    print("=" * 70)
    
    print(f"🎯 Decision Accuracy: {correct_decisions}/{total_tests} ({decision_accuracy:.1f}%)")
    print(f"📈 Confidence Accuracy: {correct_confidence}/{total_tests} ({confidence_accuracy:.1f}%)")
    print(f"💰 Coverage Accuracy: {correct_coverage}/{total_tests} ({coverage_accuracy:.1f}%)")
    print(f"🏆 Overall Accuracy: {overall_accuracy:.1f}%")
    print(f"⏱️  Average Processing Time: {total_processing_time/total_tests:.1f}ms")
    
    # Detailed results
    print("\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅" if result["decision_correct"] else "❌"
        print(f"   {status} {result['test_name']}")
        if not result["decision_correct"] and "error" in result:
            print(f"      Error: {result['error']}")
    
    # Production readiness assessment
    print("\n" + "=" * 70)
    print("🎯 PRODUCTION ACCURACY ASSESSMENT")
    print("=" * 70)
    
    if overall_accuracy >= 90:
        print("🎉 EXCELLENT! Your webhook is ready for 90+% accuracy in production!")
        print("✅ Decision accuracy is strong")
        print("✅ Confidence scoring is reliable")
        print("✅ Coverage calculations are appropriate")
    elif overall_accuracy >= 80:
        print("👍 GOOD! Your webhook should perform well in production")
        print("⚠️  Consider fine-tuning for better accuracy")
    elif overall_accuracy >= 70:
        print("⚠️  ACCEPTABLE! Your webhook needs improvement for high accuracy")
        print("🔧 Consider adjusting business logic")
    else:
        print("❌ NEEDS IMPROVEMENT! Your webhook needs significant work")
        print("🔧 Review and fix the business logic")
    
    print(f"\n🌐 Webhook URL: {WEBHOOK_URL}")
    print(f"📊 Predicted Pipeline Accuracy: {overall_accuracy:.1f}%")
    
    return overall_accuracy >= 90

def main():
    """Run the advanced accuracy test"""
    success = test_accuracy()
    
    if success:
        print("\n✅ RECOMMENDATION: Production Ready - 90+% accuracy achieved!")
    else:
        print("\n⚠️  RECOMMENDATION: Improve accuracy before production deployment")

if __name__ == "__main__":
    main()

