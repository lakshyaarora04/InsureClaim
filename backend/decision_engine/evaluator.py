import os
from .llm_decision import call_llm
from .reasoning_tree import ReasoningEngine
import json
import re

def check_waiting_periods_and_exclusions(query: dict, chunks: list):
    """
    Improved: Only apply waiting periods to listed procedures, and handle accidents distinctly.
    """
    procedure = query.get('procedure', '').lower()
    policy_duration = query.get('policy_duration_months', 0)
    waiting_period_issues = []
    exclusion_issues = []

    # Accident claims: usually no waiting period, special exclusions
    if "accident" in procedure:
        # Check for exclusions specific to accidents (e.g., self-inflicted, intoxication, etc.)
        # For now, assume accident claims are covered unless a chunk explicitly excludes them
        for chunk in chunks:
            if "accident" in chunk.lower() and ("excluded" in chunk.lower() or "not covered" in chunk.lower()):
                exclusion_issues.append("Accident claims are excluded by policy clause.")
        return waiting_period_issues, exclusion_issues

    # Only apply waiting periods to these procedures
    specified_diseases = [
        "cataract", "hernia", "fistula", "sinus", "haemorrhoids", "piles", 
        "hydrocele", "fibromyoma", "endometriosis", "hysterectomy", 
        "uterine prolapse", "stones", "tumors", "cysts", "gall bladder", 
        "pancreatitis", "cirrhosis", "gout", "rheumatism", "tonsilitis", 
        "varicose veins", "kidney disease", "alzheimer", "joint replacement",
        "vertebral column", "nasal septum", "turbinate", "congenital",
        "refractive error", "bariatric", "parkinson", "genetic"
    ]
    # Only check waiting period if procedure matches
    for disease in specified_diseases:
        if disease in procedure:
            if policy_duration < 24:
                waiting_period_issues.append(f"{disease.title()} procedures require 24 months waiting period, but only {policy_duration} months have passed")
            break

    # Cataract waiting period check - 24 months or more is required
    if "cataract" in procedure and policy_duration < 24:
        waiting_period_issues.append(f"Cataract surgery requires 24 months waiting period, but only {policy_duration} months have passed")

    # Cosmetic surgery exclusion
    if "cosmetic" in procedure:
        exclusion_issues.append("Cosmetic surgery is excluded unless for reconstruction after accident/cancer")
    # Dental treatment exclusion (unless emergency)
    if "dental" in procedure and "emergency" not in procedure:
        exclusion_issues.append("Dental treatment is excluded unless emergency due to accident")

    return waiting_period_issues, exclusion_issues

def evaluate_claim(query: dict, chunks: list):
    """
    Evaluate claim using LLM reasoning based on retrieved policy chunks.
    Now includes reasoning tree for human-readable breakdowns.
    """
    print(f"🔍 DEBUG: Starting LLM evaluation for procedure: {query['procedure']}")
    print(f"🔍 DEBUG: Retrieved {len(chunks)} chunks")
    
    # Initialize reasoning engine
    reasoning_engine = ReasoningEngine()
    
    # Build reasoning tree
    reasoning_tree = reasoning_engine.analyze_claim(query, chunks)
    
    # Format the query for LLM
    query_text = f"""
    Patient Details:
    - Age: {query['age']} years
    - Gender: {query['gender']}
    - Procedure: {query['procedure']}
    - Location: {query['location']}
    - Policy Duration: {query['policy_duration_months']} months
    
    Please evaluate if this claim should be approved or rejected based on the policy clauses below.
    """
    
    # Combine all retrieved chunks
    policy_clauses = "\n\n".join([f"Clause {i+1}: {chunk}" for i, chunk in enumerate(chunks)])
    
    print(f"🔍 DEBUG: About to call LLM with {len(policy_clauses)} characters of policy text")
    
    try:
        # Call LLM for decision
        print("🔍 DEBUG: Calling LLM...")
        llm_response = call_llm(query_text, policy_clauses)
        print(f"🔍 DEBUG: LLM Response received: {len(llm_response)} characters")
        print(f"🔍 DEBUG: LLM Response preview: {llm_response[:200]}...")
        
        # Parse structured LLM response
        decision = "rejected"  # default
        amount = 0  # default
        justification = llm_response
        
        # Try to extract decision from structured response
        if "DECISION:" in llm_response:
            decision_match = re.search(r'DECISION:\s*(APPROVED|REJECTED)', llm_response, re.IGNORECASE)
            if decision_match:
                decision = decision_match.group(1).lower()
                print(f"🔍 DEBUG: Extracted decision from structured response: {decision}")
            else:
                print(f"🔍 DEBUG: Could not extract decision from structured response")
        else:
            print(f"🔍 DEBUG: No DECISION: found in response")
        
        # Fallback check for waiting periods and exclusions
        waiting_issues, exclusion_issues = check_waiting_periods_and_exclusions(query, chunks)
        print(f"🔍 DEBUG: Waiting period issues: {waiting_issues}")
        print(f"🔍 DEBUG: Exclusion issues: {exclusion_issues}")
        
        # Override LLM decision if we find waiting period or exclusion issues
        if waiting_issues or exclusion_issues:
            if decision == "approved":
                print(f"🔍 DEBUG: Overriding LLM approval due to waiting period/exclusion issues")
                decision = "rejected"
                amount = 0
                
                # Update justification
                issues = waiting_issues + exclusion_issues
                justification = f"""DECISION: REJECTED

REASONING: Claim rejected due to policy violations:
{chr(10).join([f"- {issue}" for issue in issues])}

COVERAGE AMOUNT: 0

RELEVANT CLAUSES: Policy waiting period and exclusion clauses

POLICY LIMITS: Not applicable

WAITING PERIOD CHECK: Policy conditions not met"""
        
        # Try to extract amount from structured response - look for various patterns
        if decision == "approved":
            amount_patterns = [
                r'COVERAGE AMOUNT:\s*(\d+)',
                r'AMOUNT:\s*(\d+)',
                r'₹(\d+)',
                r'Rs\.?\s*(\d+)',
                r'INR\s*(\d+)',
                r'(\d+)\s*rupees?',
                r'(\d+)\s*rs',
                r'coverage.*?(\d+)',
                r'amount.*?(\d+)'
            ]
            
            for pattern in amount_patterns:
                amount_match = re.search(pattern, llm_response, re.IGNORECASE)
                if amount_match:
                    try:
                        amount = int(amount_match.group(1))
                        print(f"🔍 DEBUG: Extracted amount from pattern '{pattern}': {amount}")
                        break
                    except ValueError:
                        continue
            
            # If no amount found, use a reasonable default based on procedure
            if amount == 0:
                # Look for sum insured or policy limits in the chunks
                sum_insured_patterns = [
                    r'sum insured.*?(\d+)',
                    r'policy limit.*?(\d+)',
                    r'coverage limit.*?(\d+)',
                    r'maximum.*?(\d+)',
                    r'up to.*?(\d+)'
                ]
                
                for chunk in chunks:
                    for pattern in sum_insured_patterns:
                        match = re.search(pattern, chunk, re.IGNORECASE)
                        if match:
                            try:
                                amount = int(match.group(1))
                                print(f"🔍 DEBUG: Found sum insured amount: {amount}")
                                break
                            except ValueError:
                                continue
                    if amount > 0:
                        break
                
                # If still no amount, use a reasonable default based on procedure
                if amount == 0:
                    if "cataract" in query['procedure'].lower():
                        amount = 50000  # Typical cataract surgery cost
                    elif "surgery" in query['procedure'].lower():
                        amount = 100000  # General surgery
                    else:
                        amount = 25000  # General medical procedure
                    print(f"🔍 DEBUG: Using default amount for {query['procedure']}: {amount}")
        
        # If no structured response, fall back to keyword matching
        # Only use keyword matching if we couldn't extract a structured decision
        if decision == "rejected" and "DECISION:" not in llm_response:
            if "approved" in llm_response.lower() or "approve" in llm_response.lower():
                decision = "approved"
                print(f"🔍 DEBUG: Fallback keyword matching found 'approved'")
        elif decision == "approved" and "DECISION:" not in llm_response:
            if "rejected" in llm_response.lower() or "reject" in llm_response.lower():
                decision = "rejected"
                print(f"🔍 DEBUG: Fallback keyword matching found 'rejected'")
            
        print(f"🔍 DEBUG: Final decision: {decision}, amount: {amount}")
        
        # Get reasoning tree breakdown
        reasoning_breakdown = reasoning_tree.get_human_readable_breakdown()
        reasoning_json = reasoning_tree.get_json_breakdown()
        
        # Ensure we have a proper justification
        if not justification or len(justification.strip()) < 50:
            if decision == "approved":
                justification = f"Claim approved based on policy analysis. Coverage amount: ₹{amount:,}"
            else:
                justification = "Claim rejected based on policy analysis. No relevant coverage found."
        
        return {
            "decision": decision,
            "justification": justification,
            "amount": amount,
            "retrieved_chunks": chunks,
            "reasoning_breakdown": reasoning_breakdown,
            "reasoning_tree": reasoning_json,
            "confidence_score": reasoning_tree.confidence_score
        }
        
    except Exception as e:
        # Fallback to basic logic if LLM fails
        print(f"❌ LLM call failed: {e}")
        print(f"❌ Exception type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        
        # Still provide reasoning tree even if LLM fails
        reasoning_breakdown = reasoning_tree.get_human_readable_breakdown()
        reasoning_json = reasoning_tree.get_json_breakdown()
        
        return {
            "decision": "rejected",
            "justification": f"Error in LLM processing: {str(e)}. No relevant policy clause found.",
            "amount": 0,
            "retrieved_chunks": chunks,
            "reasoning_breakdown": reasoning_breakdown,
            "reasoning_tree": reasoning_json,
            "confidence_score": reasoning_tree.confidence_score
        }
