"""
InsureClaims Benchmark Dataset
Comprehensive canonical dataset of 40 insurance claim test cases spanning 12 distinct adjudication categories.
Used for measuring Retrieval Performance (Precision@K, Recall@K, MRR) and Adjudication Accuracy.
"""

from typing import List, Dict, Any

BENCHMARK_CASES: List[Dict[str, Any]] = [
    # ─── Category 1: Standard Approved Claims Within Limits ──────────────────────
    {
        "id": "TC-001",
        "category": "standard_approved",
        "description": "Acute appendicitis emergency surgery after 14 months policy tenure",
        "query": "A 28-year-old female underwent emergency appendectomy in Delhi after 14 months of policy cover. Claim amount is ₹45,000.",
        "claim_data": {
            "procedure": "appendectomy",
            "policy_duration_months": 14,
            "claim_amount": 45000.0,
            "age": 28,
            "gender": "female",
            "location": "Delhi",
            "is_emergency": True,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 45000.0,
            "expected_clauses": ["appendicitis", "inpatient", "waiting period", "sub-limit"],
            "reason": "Initial 30-day waiting period met, standard acute inpatient treatment within sum insured."
        }
    },
    {
        "id": "TC-002",
        "category": "standard_approved",
        "description": "Gall bladder removal (cholecystectomy) after 26 months policy tenure",
        "query": "A 45-year-old male requires laparoscopic cholecystectomy in Mumbai. Policy has been active for 26 months. Claimed amount ₹55,000.",
        "claim_data": {
            "procedure": "cholecystectomy",
            "policy_duration_months": 26,
            "claim_amount": 55000.0,
            "age": 45,
            "gender": "male",
            "location": "Mumbai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 55000.0,
            "expected_clauses": ["cholecystectomy", "gall bladder", "24 months"],
            "reason": "Exceeds 24-month specific waiting period for gall bladder ailments; within limits."
        }
    },
    {
        "id": "TC-003",
        "category": "standard_approved",
        "description": "Dengue fever inpatient hospitalization after 6 months policy tenure",
        "query": "A 34-year-old male hospitalized for 4 days due to severe dengue fever in Bengaluru. Policy active for 6 months. Claim ₹28,000.",
        "claim_data": {
            "procedure": "dengue hospitalization",
            "policy_duration_months": 6,
            "claim_amount": 28000.0,
            "age": 34,
            "gender": "male",
            "location": "Bengaluru",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 28000.0,
            "expected_clauses": ["hospitalization", "inpatient care", "30 days"],
            "reason": "Inpatient treatment for acute illness past initial 30 days is fully payable."
        }
    },
    {
        "id": "TC-004",
        "category": "standard_approved",
        "description": "Kidney stone lithotripsy procedure after 25 months policy tenure",
        "query": "A 40-year-old female underwent shockwave lithotripsy for renal calculi in Hyderabad. Policy active 25 months. Claim ₹42,000.",
        "claim_data": {
            "procedure": "kidney stone lithotripsy",
            "policy_duration_months": 25,
            "claim_amount": 42000.0,
            "age": 40,
            "gender": "female",
            "location": "Hyderabad",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 42000.0,
            "expected_clauses": ["kidney stone", "renal calculi", "daycare"],
            "reason": "Renal stone treatment covered after 24-month specified waiting period."
        }
    },

    # ─── Category 2: Specific Waiting Period Not Met (24 Months) ────────────────
    {
        "id": "TC-005",
        "category": "specific_waiting_period_not_met",
        "description": "Cataract surgery at 14 months (requires 24 months)",
        "query": "A 52-year-old female claiming ₹35,000 for bilateral cataract surgery in Pune. Policy active for 14 months.",
        "claim_data": {
            "procedure": "cataract surgery",
            "policy_duration_months": 14,
            "claim_amount": 35000.0,
            "age": 52,
            "gender": "female",
            "location": "Pune",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["cataract", "24 months", "waiting period", "exclusion"],
            "reason": "Cataract surgery has a mandatory 24-month waiting period; current tenure is 14 months."
        }
    },
    {
        "id": "TC-006",
        "category": "specific_waiting_period_not_met",
        "description": "Inguinal hernia repair at 16 months (requires 24 months)",
        "query": "A 48-year-old male underwent elective inguinal hernia repair in Chennai. Policy active 16 months. Claim ₹48,000.",
        "claim_data": {
            "procedure": "hernia repair",
            "policy_duration_months": 16,
            "claim_amount": 48000.0,
            "age": 48,
            "gender": "male",
            "location": "Chennai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["hernia", "24 months", "waiting period"],
            "reason": "Hernia repair requires 24 months policy duration; current duration 16 months."
        }
    },
    {
        "id": "TC-007",
        "category": "specific_waiting_period_not_met",
        "description": "Total knee replacement at 18 months for osteoarthritis (requires 24 months)",
        "query": "A 60-year-old male claiming ₹1,20,000 for elective total knee replacement in Kolkata. Policy active 18 months.",
        "claim_data": {
            "procedure": "knee replacement",
            "policy_duration_months": 18,
            "claim_amount": 120000.0,
            "age": 60,
            "gender": "male",
            "location": "Kolkata",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["knee replacement", "osteoarthritis", "joint replacement", "24 months"],
            "reason": "Elective joint replacement requires 24 months continuous coverage."
        }
    },
    {
        "id": "TC-008",
        "category": "specific_waiting_period_not_met",
        "description": "Hydrocele surgery at 10 months (requires 24 months)",
        "query": "A 35-year-old male underwent hydrocelectomy in Ahmedabad. Policy active 10 months. Claim ₹25,000.",
        "claim_data": {
            "procedure": "hydrocele",
            "policy_duration_months": 10,
            "claim_amount": 25000.0,
            "age": 35,
            "gender": "male",
            "location": "Ahmedabad",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["hydrocele", "24 months", "waiting period"],
            "reason": "Hydrocele surgery subject to 24-month specific waiting period."
        }
    },

    # ─── Category 3: Initial 30-Day Waiting Period Not Met ────────────────────────
    {
        "id": "TC-009",
        "category": "initial_waiting_period_not_met",
        "description": "Viral bronchitis hospitalization at 15 days of policy inception",
        "query": "A 29-year-old male admitted for acute bronchitis in Delhi after 15 days of buying policy. Claim ₹22,000.",
        "claim_data": {
            "procedure": "bronchitis hospitalization",
            "policy_duration_months": 0,
            "policy_duration_days": 15,
            "claim_amount": 22000.0,
            "age": 29,
            "gender": "male",
            "location": "Delhi",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["initial 30 days", "waiting period", "inception"],
            "reason": "Illness hospitalized within first 30 days is excluded under initial waiting period."
        }
    },
    {
        "id": "TC-010",
        "category": "initial_waiting_period_not_met",
        "description": "Gastroenteritis admission at 20 days of policy coverage",
        "query": "A 24-year-old female hospitalized for acute gastroenteritis in Mumbai. Policy active for only 20 days. Claim ₹19,000.",
        "claim_data": {
            "procedure": "gastroenteritis",
            "policy_duration_months": 0,
            "policy_duration_days": 20,
            "claim_amount": 19000.0,
            "age": 24,
            "gender": "female",
            "location": "Mumbai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["30 days", "waiting period", "exclusion"],
            "reason": "Non-accidental medical hospitalization within 30 days of policy start is non-payable."
        }
    },
    {
        "id": "TC-011",
        "category": "initial_waiting_period_not_met",
        "description": "Elective ENT tonsillectomy at 25 days of policy",
        "query": "A 31-year-old male scheduled tonsillectomy in Lucknow. Policy active for 25 days. Claim ₹30,000.",
        "claim_data": {
            "procedure": "tonsillectomy",
            "policy_duration_months": 0,
            "policy_duration_days": 25,
            "claim_amount": 30000.0,
            "age": 31,
            "gender": "male",
            "location": "Lucknow",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["30 days", "tonsillectomy", "waiting period"],
            "reason": "Falls inside initial 30 days window and tonsillectomy has 24-month waiting period."
        }
    },

    # ─── Category 4: Pre-Existing Disease (PED) Waiting Period (36-48 Months) ─────
    {
        "id": "TC-012",
        "category": "ped_waiting_period_not_met",
        "description": "Type 2 diabetic nephropathy treatment at 20 months (requires 36/48 months)",
        "query": "A 56-year-old male with pre-existing Type 2 diabetes admitted for diabetic renal management. Policy active 20 months. Claim ₹65,000.",
        "claim_data": {
            "procedure": "diabetic nephropathy",
            "policy_duration_months": 20,
            "claim_amount": 65000.0,
            "age": 56,
            "gender": "male",
            "location": "Jaipur",
            "is_pre_existing": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["pre-existing disease", "PED", "36 months", "48 months"],
            "reason": "Pre-existing diseases require 36/48 months continuous coverage before benefits are payable."
        }
    },
    {
        "id": "TC-013",
        "category": "ped_waiting_period_not_met",
        "description": "Chronic hypertensive encephalopathy at 18 months policy duration",
        "query": "A 62-year-old female with declared hypertension admitted for stroke/hypertensive crisis in Pune. Policy active 18 months. Claim ₹80,000.",
        "claim_data": {
            "procedure": "hypertensive crisis",
            "policy_duration_months": 18,
            "claim_amount": 80000.0,
            "age": 62,
            "gender": "female",
            "location": "Pune",
            "is_pre_existing": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["pre-existing", "hypertension", "waiting period"],
            "reason": "Pre-existing hypertension complications not covered prior to 36 months duration."
        }
    },
    {
        "id": "TC-014",
        "category": "ped_waiting_period_not_met",
        "description": "Chronic bronchial asthma exacerbation at 12 months policy tenure",
        "query": "A 38-year-old male with childhood asthma hospitalized for acute exacerbation in Delhi. Policy active 12 months. Claim ₹35,000.",
        "claim_data": {
            "procedure": "asthma exacerbation",
            "policy_duration_months": 12,
            "claim_amount": 35000.0,
            "age": 38,
            "gender": "male",
            "location": "Delhi",
            "is_pre_existing": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["pre-existing", "asthma", "waiting period"],
            "reason": "Pre-existing declared asthma excluded during the 36-month PED window."
        }
    },

    # ─── Category 5: Emergency & Accident Exceptions to Waiting Periods ───────────
    {
        "id": "TC-015",
        "category": "accident_emergency_exception",
        "description": "Road traffic accident femur fracture surgery at 10 days of policy",
        "query": "A 25-year-old male involved in road traffic accident sustained femur fracture requiring open reduction and internal fixation in Delhi. Policy active only 10 days. Claim ₹75,000.",
        "claim_data": {
            "procedure": "femur fracture fixation",
            "policy_duration_months": 0,
            "policy_duration_days": 10,
            "claim_amount": 75000.0,
            "age": 25,
            "gender": "male",
            "location": "Delhi",
            "is_emergency": True,
            "is_accident": True,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 75000.0,
            "expected_clauses": ["accidental injury", "exception", "initial 30 days", "emergency"],
            "reason": "Accidental injuries are statutory exceptions to initial 30-day waiting periods; claim is payable."
        }
    },
    {
        "id": "TC-016",
        "category": "accident_emergency_exception",
        "description": "Accidental head trauma emergency ICU admission at 14 days of policy",
        "query": "A 33-year-old female admitted to ICU for intracranial hematoma following accidental fall from stairs in Mumbai. Policy active 14 days. Claim ₹95,000.",
        "claim_data": {
            "procedure": "emergency head trauma ICU",
            "policy_duration_months": 0,
            "policy_duration_days": 14,
            "claim_amount": 95000.0,
            "age": 33,
            "gender": "female",
            "location": "Mumbai",
            "is_emergency": True,
            "is_accident": True,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 95000.0,
            "expected_clauses": ["accident", "head trauma", "waiting period waiver"],
            "reason": "Accident emergency treatments are covered from Day 1 without waiting period restrictions."
        }
    },
    {
        "id": "TC-017",
        "category": "accident_emergency_exception",
        "description": "Emergency surgery for acute appendicular perforation at 20 days of policy",
        "query": "A 22-year-old male suffered acute peritonitis from ruptured appendix requiring emergent laparotomy in Bengaluru. Policy active 20 days. Claim ₹60,000.",
        "claim_data": {
            "procedure": "ruptured appendix emergency laparotomy",
            "policy_duration_months": 0,
            "policy_duration_days": 20,
            "claim_amount": 60000.0,
            "age": 22,
            "gender": "male",
            "location": "Bengaluru",
            "is_emergency": True,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 60000.0,
            "expected_clauses": ["emergency", "life-threatening", "waiver"],
            "reason": "Documented life-threatening emergency medical conditions override initial non-accidental waiting restrictions."
        }
    },

    # ─── Category 6: Procedural Sub-Limit Cap Applied ─────────────────────────────
    {
        "id": "TC-018",
        "category": "sublimit_cap_applied",
        "description": "Cataract surgery claim ₹60,000 capped to statutory sub-limit ₹40,000",
        "query": "A 58-year-old male claiming ₹60,000 for unilateral cataract surgery with multifocal lens in Chennai. Policy active 30 months.",
        "claim_data": {
            "procedure": "cataract surgery",
            "policy_duration_months": 30,
            "claim_amount": 60000.0,
            "age": 58,
            "gender": "male",
            "location": "Chennai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 40000.0,
            "expected_clauses": ["cataract sub-limit", "Rs 40,000", "per eye"],
            "reason": "Waiting period satisfied (30 mo > 24 mo), but cataract coverage is subject to ₹40,000 sub-limit cap."
        }
    },
    {
        "id": "TC-019",
        "category": "sublimit_cap_applied",
        "description": "Inguinal hernia claim ₹75,000 capped to procedure sub-limit ₹50,000",
        "query": "A 50-year-old female claiming ₹75,000 for open mesh hernia repair in Mumbai. Policy active 28 months.",
        "claim_data": {
            "procedure": "hernia surgery",
            "policy_duration_months": 28,
            "claim_amount": 75000.0,
            "age": 50,
            "gender": "female",
            "location": "Mumbai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 50000.0,
            "expected_clauses": ["hernia sub-limit", "Rs 50,000", "maximum payable"],
            "reason": "Hernia waiting period satisfied; claimed amount ₹75,000 restricted to ₹50,000 statutory procedure cap."
        }
    },
    {
        "id": "TC-020",
        "category": "sublimit_cap_applied",
        "description": "Knee replacement surgery ₹1,40,000 capped to sub-limit ₹80,000",
        "query": "A 65-year-old male claiming ₹1,40,000 for unilateral total knee replacement in Delhi. Policy active 36 months.",
        "claim_data": {
            "procedure": "knee replacement",
            "policy_duration_months": 36,
            "claim_amount": 140000.0,
            "age": 65,
            "gender": "male",
            "location": "Delhi",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 80000.0,
            "expected_clauses": ["knee replacement", "joint replacement sub-limit", "Rs 80,000"],
            "reason": "24-month waiting period satisfied; payout capped to procedural sub-limit of ₹80,000."
        }
    },
    {
        "id": "TC-021",
        "category": "sublimit_cap_applied",
        "description": "Accidental dental fracture reconstruction ₹25,000 capped to sub-limit ₹15,000",
        "query": "A 27-year-old male suffered accidental jaw/dental trauma requiring tooth splinting in Kolkata. Policy active 12 months. Claim ₹25,000.",
        "claim_data": {
            "procedure": "accidental dental reconstruction",
            "policy_duration_months": 12,
            "claim_amount": 25000.0,
            "age": 27,
            "gender": "male",
            "location": "Kolkata",
            "is_emergency": True,
            "is_accident": True,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 15000.0,
            "expected_clauses": ["dental accident", "sub-limit", "Rs 15,000"],
            "reason": "Accidental dental is covered, but restricted by policy sub-limit of ₹15,000."
        }
    },

    # ─── Category 7: Permanent Policy Exclusions ──────────────────────────────────
    {
        "id": "TC-022",
        "category": "permanent_exclusion",
        "description": "Cosmetic rhinoplasty elective nasal reconstruction",
        "query": "A 26-year-old female claiming ₹85,000 for cosmetic rhinoplasty and septoplasty in Mumbai. Policy active 24 months.",
        "claim_data": {
            "procedure": "cosmetic rhinoplasty",
            "policy_duration_months": 24,
            "claim_amount": 85000.0,
            "age": 26,
            "gender": "female",
            "location": "Mumbai",
            "is_cosmetic": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["cosmetic surgery", "aesthetic treatment", "permanent exclusion"],
            "reason": "Cosmetic, aesthetic, and plastic surgeries performed for appearance enhancement are permanently excluded."
        }
    },
    {
        "id": "TC-023",
        "category": "permanent_exclusion",
        "description": "Routine dental root canal and crown placement (non-accidental)",
        "query": "A 39-year-old male claiming ₹18,000 for root canal treatment and ceramic crown in Pune. Policy active 18 months.",
        "claim_data": {
            "procedure": "routine dental root canal",
            "policy_duration_months": 18,
            "claim_amount": 18000.0,
            "age": 39,
            "gender": "male",
            "location": "Pune",
            "is_dental_non_accident": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["dental treatment", "permanent exclusion", "non-accidental"],
            "reason": "Dental treatments or surgeries not arising from direct accidental trauma are excluded under Clause 4.2."
        }
    },
    {
        "id": "TC-024",
        "category": "permanent_exclusion",
        "description": "Experimental cellular immunotherapy treatment",
        "query": "A 54-year-old female claiming ₹2,50,000 for unapproved experimental stem-cell therapy in Delhi. Policy active 36 months.",
        "claim_data": {
            "procedure": "experimental stem cell therapy",
            "policy_duration_months": 36,
            "claim_amount": 250000.0,
            "age": 54,
            "gender": "female",
            "location": "Delhi",
            "is_experimental": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["experimental treatment", "unproven therapies", "exclusion"],
            "reason": "Treatments with experimental, pharmacological trial, or unproven clinical protocols are strictly excluded."
        }
    },
    {
        "id": "TC-025",
        "category": "permanent_exclusion",
        "description": "Weight loss bariatric surgery for aesthetic obesity management",
        "query": "A 42-year-old male claiming ₹1,80,000 for elective bariatric gastric sleeve surgery in Bengaluru. Policy active 30 months.",
        "claim_data": {
            "procedure": "cosmetic bariatric surgery",
            "policy_duration_months": 30,
            "claim_amount": 180000.0,
            "age": 42,
            "gender": "male",
            "location": "Bengaluru",
            "is_cosmetic": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["obesity treatment", "bariatric", "weight reduction exclusion"],
            "reason": "Elective cosmetic weight reduction surgeries are excluded under general policy exclusions."
        }
    },

    # ─── Category 8: Duplicate Claim Detection ───────────────────────────────────
    {
        "id": "TC-026",
        "category": "duplicate_claim",
        "description": "Resubmission of cataract surgery within 10 days for same patient",
        "query": "A 55-year-old male resubmitting claim for cataract surgery (Claim ID: CLM-DUP-01) for ₹40,000 in Mumbai. Policy active 28 months.",
        "claim_data": {
            "claim_id": "CLM-DUP-01",
            "claimant_id": "CLMNT-001",
            "procedure": "cataract surgery",
            "policy_duration_months": 28,
            "claim_amount": 40000.0,
            "age": 55,
            "gender": "male",
            "location": "Mumbai",
            "force_duplicate_check": True,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["duplicate claim", "fraud prevention", "audit history"],
            "reason": "Duplicate claim detected in relational history for the same procedure and claimant."
        }
    },
    {
        "id": "TC-027",
        "category": "duplicate_claim",
        "description": "Second submission of appendectomy invoice within 14 days",
        "query": "A 28-year-old female re-filing appendicitis claim of ₹45,000 (Claim ID: CLM-DUP-02) in Delhi.",
        "claim_data": {
            "claim_id": "CLM-DUP-02",
            "claimant_id": "CLMNT-002",
            "procedure": "appendectomy",
            "policy_duration_months": 15,
            "claim_amount": 45000.0,
            "age": 28,
            "gender": "female",
            "location": "Delhi",
            "force_duplicate_check": True,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["duplicate claim", "already adjudicated"],
            "reason": "Prior approved claim already processed for identical clinical incident."
        }
    },

    # ─── Category 9: Co-Payment Deductions ────────────────────────────────────────
    {
        "id": "TC-028",
        "category": "copay_deduction",
        "description": "Hospitalization claim ₹50,000 with 10% co-payment clause (Payout: ₹45,000)",
        "query": "A 45-year-old male claiming ₹50,000 for inpatient medical treatment in Hyderabad. Policy active 15 months, co-pay 10%.",
        "claim_data": {
            "procedure": "inpatient medical treatment",
            "policy_duration_months": 15,
            "claim_amount": 50000.0,
            "co_pay_pct": 0.10,
            "age": 45,
            "gender": "male",
            "location": "Hyderabad",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 45000.0,
            "expected_clauses": ["co-pay", "10%", "deduction", "insured share"],
            "reason": "Approved with 10% co-payment deduction (₹5,000 deducted from ₹50,000 = ₹45,000)."
        }
    },
    {
        "id": "TC-029",
        "category": "copay_deduction",
        "description": "Senior citizen cardiac stenting ₹1,00,000 with 20% co-pay (Payout: ₹80,000)",
        "query": "A 68-year-old male with senior citizen policy claiming ₹1,00,000 for angioplasty in Chennai. Policy active 30 months, co-pay 20%.",
        "claim_data": {
            "procedure": "coronary angioplasty",
            "policy_duration_months": 30,
            "claim_amount": 100000.0,
            "co_pay_pct": 0.20,
            "age": 68,
            "gender": "male",
            "location": "Chennai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 80000.0,
            "expected_clauses": ["senior citizen co-pay", "20% co-pay", "deductible"],
            "reason": "20% co-payment applied to ₹1,00,000 approved base, resulting in ₹80,000 payable."
        }
    },
    {
        "id": "TC-030",
        "category": "copay_deduction",
        "description": "Surgery claim ₹80,000 with 15% zone co-payment (Payout: ₹68,000)",
        "query": "A 40-year-old female claiming ₹80,000 for ENT surgery in Mumbai under Tier-2 policy with 15% co-pay.",
        "claim_data": {
            "procedure": "tympanoplasty",
            "policy_duration_months": 26,
            "claim_amount": 80000.0,
            "co_pay_pct": 0.15,
            "age": 40,
            "gender": "female",
            "location": "Mumbai",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 68000.0,
            "expected_clauses": ["zone co-pay", "15% deduction", "eligible amount"],
            "reason": "15% zone co-pay (₹12,000) subtracted from ₹80,000, leaving ₹68,000."
        }
    },

    # ─── Category 10: Sum Insured Exhaustion ──────────────────────────────────────
    {
        "id": "TC-031",
        "category": "sum_insured_exhaustion",
        "description": "Oncology chemotherapy claim ₹4,50,000 with remaining sum insured ₹2,00,000",
        "query": "A 53-year-old female undergoing chemotherapy claiming ₹4,50,000 in Delhi. Remaining policy sum insured is ₹2,00,000. Policy active 24 months.",
        "claim_data": {
            "procedure": "chemotherapy oncology",
            "policy_duration_months": 24,
            "claim_amount": 450000.0,
            "sum_insured": 200000.0,
            "age": 53,
            "gender": "female",
            "location": "Delhi",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 200000.0,
            "expected_clauses": ["sum insured exhaustion", "maximum limit", "coverage cap"],
            "reason": "Eligible for reimbursement up to the remaining sum insured balance of ₹2,00,000."
        }
    },
    {
        "id": "TC-032",
        "category": "sum_insured_exhaustion",
        "description": "Major polytrauma ICU claim ₹6,00,000 against ₹5,00,000 sum insured limit",
        "query": "A 36-year-old male claiming ₹6,00,000 for emergency multi-system trauma ICU in Bengaluru. Policy sum insured ₹5,00,000.",
        "claim_data": {
            "procedure": "polytrauma ICU care",
            "policy_duration_months": 18,
            "claim_amount": 600000.0,
            "sum_insured": 500000.0,
            "age": 36,
            "gender": "male",
            "location": "Bengaluru",
            "is_emergency": True,
            "is_accident": True,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 500000.0,
            "expected_clauses": ["sum insured", "maximum benefit", "policy limit"],
            "reason": "Capped strictly at total policy sum insured of ₹5,00,000."
        }
    },

    # ─── Category 11: Insufficient Information ────────────────────────────────────
    {
        "id": "TC-033",
        "category": "insufficient_information",
        "description": "Vague claim inquiry with missing procedure and clinical details",
        "query": "Patient was admitted to hospital for tests and needs reimbursement soon.",
        "claim_data": {
            "procedure": "",
            "policy_duration_months": 12,
            "claim_amount": 15000.0,
        },
        "ground_truth": {
            "decision": "insufficient_information",
            "expected_amount": 0.0,
            "expected_clauses": ["procedure required", "missing information", "diagnosis"],
            "reason": "Procedure/diagnosis missing; cannot evaluate medical necessity or waiting periods."
        }
    },
    {
        "id": "TC-034",
        "category": "insufficient_information",
        "description": "Claim amount and duration missing from patient inquiry",
        "query": "A 40-year-old patient who had a medical procedure in Pune. Please review.",
        "claim_data": {
            "procedure": "unspecified medical procedure",
            "policy_duration_months": None,
            "claim_amount": None,
        },
        "ground_truth": {
            "decision": "insufficient_information",
            "expected_amount": 0.0,
            "expected_clauses": ["missing policy duration", "missing claim amount"],
            "reason": "Missing both policy duration and claimed amount prevents deterministic calculation."
        }
    },
    {
        "id": "TC-035",
        "category": "insufficient_information",
        "description": "Single-word inquiry without context or policy identifiers",
        "query": "Surgery",
        "claim_data": {
            "procedure": "Surgery",
            "policy_duration_months": None,
            "claim_amount": 0.0,
        },
        "ground_truth": {
            "decision": "insufficient_information",
            "expected_amount": 0.0,
            "expected_clauses": ["insufficient data", "incomplete inquiry"],
            "reason": "Incomplete query lacking clinical context, tenure, and expense figures."
        }
    },

    # ─── Category 12: Contradictory / Ambiguous Terms Needing Human Review ────────
    {
        "id": "TC-036",
        "category": "needs_human_review",
        "description": "Therapeutic vs cosmetic bariatric surgery for morbid obesity with obstructive sleep apnea",
        "query": "A 46-year-old male claiming ₹2,20,000 for bariatric surgery with BMI 44 and severe sleep apnea in Delhi. Policy has conflicting cosmetic vs therapeutic endorsement riders.",
        "claim_data": {
            "procedure": "morbid obesity bariatric surgery",
            "policy_duration_months": 36,
            "claim_amount": 220000.0,
            "age": 46,
            "has_conflicting_rider": True,
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "needs_review",
            "expected_amount": 0.0,
            "expected_clauses": ["ambiguous endorsement", "therapeutic rider", "medical board review"],
            "reason": "Contradictory policy endorsements between cosmetic exclusion and therapeutic endorsement require human senior adjuster review."
        }
    },
    {
        "id": "TC-037",
        "category": "needs_human_review",
        "description": "Off-label biological cancer drug infusion with partial FDA/DCGI clearance",
        "query": "A 51-year-old female claiming ₹3,10,000 for off-label targeted immunotherapy for refractory sarcoma in Mumbai. Policy clauses show contradictory experimental exclusions.",
        "claim_data": {
            "procedure": "off-label targeted immunotherapy",
            "policy_duration_months": 40,
            "claim_amount": 310000.0,
            "has_conflicting_rider": True,
        },
        "ground_truth": {
            "decision": "needs_review",
            "expected_amount": 0.0,
            "expected_clauses": ["off-label drug", "medical necessity dispute", "peer review"],
            "reason": "Contradictory clauses on off-label life-saving medication require clinical committee review."
        }
    },

    # ─── Additional Validations & Edge Cases (Completing 40 Cases) ────────────────
    {
        "id": "TC-038",
        "category": "standard_approved",
        "description": "Daycare laparoscopic appendectomy after 18 months policy",
        "query": "A 23-year-old female claiming ₹38,000 for daycare laparoscopic appendectomy in Chennai. Policy active 18 months.",
        "claim_data": {
            "procedure": "laparoscopic appendectomy",
            "policy_duration_months": 18,
            "claim_amount": 38000.0,
            "age": 23,
            "gender": "female",
            "location": "Chennai",
            "is_emergency": True,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 38000.0,
            "expected_clauses": ["daycare procedure", "appendectomy", "payable"],
            "reason": "Standard daycare approved procedure past waiting period."
        }
    },
    {
        "id": "TC-039",
        "category": "specific_waiting_period_not_met",
        "description": "Sinusitis FESS surgery at 15 months (requires 24 months)",
        "query": "A 37-year-old male claiming ₹45,000 for Functional Endoscopic Sinus Surgery (FESS) in Kolkata. Policy active 15 months.",
        "claim_data": {
            "procedure": "sinusitis FESS",
            "policy_duration_months": 15,
            "claim_amount": 45000.0,
            "age": 37,
            "gender": "male",
            "location": "Kolkata",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "rejected",
            "expected_amount": 0.0,
            "expected_clauses": ["sinusitis", "24 months", "waiting period"],
            "reason": "Sinus disorders have 24 months specific waiting period."
        }
    },
    {
        "id": "TC-040",
        "category": "sublimit_cap_applied",
        "description": "Bilateral cataract surgery ₹90,000 capped to dual sub-limit ₹80,000",
        "query": "A 64-year-old female claiming ₹90,000 for bilateral cataract extraction in Pune. Policy active 36 months.",
        "claim_data": {
            "procedure": "bilateral cataract surgery",
            "policy_duration_months": 36,
            "claim_amount": 90000.0,
            "sum_insured": 300000.0,
            "age": 64,
            "gender": "female",
            "location": "Pune",
            "is_emergency": False,
            "is_accident": False,
        },
        "ground_truth": {
            "decision": "approved",
            "expected_amount": 80000.0,
            "expected_clauses": ["cataract sub-limit", "Rs 40,000 per eye", "bilateral 80,000"],
            "reason": "Both eyes operated; capped at ₹40,000 per eye = ₹80,000 total eligible amount."
        }
    },
]

def get_benchmark_cases(category: str = None) -> List[Dict[str, Any]]:
    """Returns all benchmark cases or filters by category."""
    if not category or category == "all":
        return BENCHMARK_CASES
    return [c for c in BENCHMARK_CASES if c.get("category") == category]

def get_benchmark_categories() -> List[str]:
    """Returns unique benchmark category names."""
    return list(dict.fromkeys(c["category"] for c in BENCHMARK_CASES))
