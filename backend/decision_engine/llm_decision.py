from openai import OpenAI
import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _rule_based_decision(query_data: str, clauses: str) -> str:
    """Fallback when OPENAI_API_KEY is not set (e.g. Vercel without env vars)."""
    text = f"{query_data}\n{clauses}".lower()
    duration_match = re.search(r"policy duration:\s*(\d+)", query_data.lower())
    months = int(duration_match.group(1)) if duration_match else 12

    rejected = False
    reasons = []

    if "cataract" in text and months < 24:
        rejected = True
        reasons.append(f"Cataract requires 24-month waiting period; policy is {months} months old.")
    if "cosmetic" in text and "reconstruction" not in text:
        rejected = True
        reasons.append("Cosmetic procedures are excluded unless reconstruction after accident/cancer.")
    if "dental" in text and "emergency" not in text and "accident" not in text:
        rejected = True
        reasons.append("Dental treatment is excluded unless emergency due to accident.")

    if rejected:
        return (
            "DECISION: REJECTED\n\n"
            f"REASONING: {' '.join(reasons)}\n\n"
            "COVERAGE AMOUNT: 0\n\n"
            "RELEVANT CLAUSES: Policy waiting period and exclusion clauses\n\n"
            "WAITING PERIOD CHECK: Not met\n\n"
            "EXCLUSION CHECK: Applicable exclusions found"
        )

    amount = 50000 if "cataract" in text else 100000 if "surgery" in text else 25000
    return (
        "DECISION: APPROVED\n\n"
        "REASONING: Claim meets policy waiting periods and no exclusions apply "
        "based on rule-based policy analysis.\n\n"
        f"COVERAGE AMOUNT: {amount}\n\n"
        "RELEVANT CLAUSES: Retrieved policy sections\n\n"
        "WAITING PERIOD CHECK: Met\n\n"
        "EXCLUSION CHECK: No applicable exclusions"
    )


def call_llm(query_data, clauses):
    """
    Call LLM to evaluate insurance claim based on policy clauses.
    """
    print("🔍 DEBUG: Starting LLM call...")
    
    prompt = f"""
    You are an expert insurance claim evaluator. Your task is to analyze the claim request against the provided policy clauses and make a precise decision.

    CLAIM REQUEST:
    {query_data}

    RELEVANT POLICY CLAUSES:
    {clauses}

    DECISION CRITERIA - APPROVE ONLY IF ALL CONDITIONS ARE MET:

    ✅ APPROVE CONDITIONS (ALL must be true):
    1. WAITING PERIOD MET: Policy duration >= required waiting period for the procedure
    2. NO EXCLUSIONS: Procedure is not explicitly excluded in policy clauses
    3. COVERED PROCEDURE: Procedure is listed as covered or not explicitly excluded
    4. POLICY ACTIVE: Policy is in force and not expired
    5. LOCATION COVERED: Treatment location is within policy coverage area

    ❌ REJECT CONDITIONS (Any one triggers rejection):
    1. WAITING PERIOD NOT MET: Policy duration < required waiting period
    2. EXPLICIT EXCLUSION: Procedure is specifically excluded in policy
    3. UNCOVERED PROCEDURE: Procedure is not mentioned as covered
    4. POLICY EXPIRED: Policy is not active or expired
    5. LOCATION NOT COVERED: Treatment location outside coverage area

    SPECIFIC WAITING PERIOD REQUIREMENTS:
    - Cataract surgery: 24 months (policy_duration >= 24)
    - Specified diseases: 24 months (policy_duration >= 24)
    - Pre-existing conditions: 36 months (policy_duration >= 36)
    - General procedures: 30 days (policy_duration >= 1)

    SPECIFIC EXCLUSIONS TO CHECK:
    - Cosmetic surgery (unless reconstruction after accident/cancer)
    - Dental treatment (unless emergency due to accident)
    - Experimental treatments
    - Treatments outside coverage area
    - Refractive eye surgery (unless medically necessary)

    POLICY EXAMPLES FOR REFERENCE:

    EXAMPLE 1 - APPROVED CLAIM:
    Claim: Cataract surgery, policy_duration=24 months
    Policy Clause: "Cataract surgery covered after 24 months waiting period"
    Decision: APPROVED (waiting period met, procedure covered)
    Reasoning: 24 months policy duration meets 24 months waiting period requirement

    EXAMPLE 2 - REJECTED CLAIM (Waiting Period):
    Claim: Cataract surgery, policy_duration=12 months
    Policy Clause: "Cataract surgery covered after 24 months waiting period"
    Decision: REJECTED (waiting period not met)
    Reasoning: Only 12 months policy duration, requires 24 months

    EXAMPLE 3 - REJECTED CLAIM (Exclusion):
    Claim: Cosmetic surgery, policy_duration=36 months
    Policy Clause: "Cosmetic surgery excluded unless reconstruction after accident"
    Decision: REJECTED (explicit exclusion)
    Reasoning: Cosmetic surgery is explicitly excluded unless for reconstruction

    EXAMPLE 4 - APPROVED CLAIM (Emergency):
    Claim: Emergency heart surgery, policy_duration=6 months
    Policy Clause: "Emergency procedures covered without waiting period"
    Decision: APPROVED (emergency exception)
    Reasoning: Emergency procedures are exempt from waiting periods

    EXAMPLE 5 - REJECTED CLAIM (Uncovered):
    Claim: Dental treatment, policy_duration=24 months
    Policy Clause: "Dental treatment excluded unless emergency due to accident"
    Decision: REJECTED (not emergency)
    Reasoning: Dental treatment is excluded unless emergency due to accident

    DECISION LOGIC:
    1. Extract procedure type from claim request
    2. Check if procedure has waiting period requirement
    3. Compare policy_duration with required waiting period
    4. Search policy clauses for explicit exclusions
    5. Check if procedure is listed as covered
    6. Verify policy is active and location is covered
    7. Make decision based on strict compliance

    CRITICAL: Default to REJECT if any condition is unclear or missing.

    Please provide your response in the following format:
    
    DECISION: [APPROVED/REJECTED]
    
    REASONING: [Detailed explanation with specific clause references. For rejections, clearly explain the specific waiting period, exclusion, or condition that was not met.]
    
    COVERAGE AMOUNT: [Specific amount in rupees if approved, 0 if rejected]
    
    RELEVANT CLAUSES: [List the specific clause numbers that support your decision]
    
    POLICY LIMITS: [Any sum insured or policy limits mentioned in the clauses]
    
    WAITING PERIOD CHECK: [State the waiting period requirement and whether it was met]
    
    EXCLUSION CHECK: [State any exclusions found and whether they apply]
    """

    try:
        # Set OpenAI API key from environment variable
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"🔍 DEBUG: API key found: {'Yes' if api_key else 'No'}")
        if api_key:
            print(f"🔍 DEBUG: API key starts with: {api_key[:10]}...")
        
        if not api_key:
            return _rule_based_decision(query_data, clauses)
        
        # Initialize OpenAI client with new API format
        client = OpenAI(api_key=api_key)
        print("🔍 DEBUG: OpenAI client initialized successfully")
        
        print("🔍 DEBUG: Making OpenAI API call...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,  # Increased for better justifications
            temperature=0.1
        )
        
        print("🔍 DEBUG: OpenAI API call successful")
        result = response.choices[0].message.content
        print(f"🔍 DEBUG: Response length: {len(result)} characters")
        
        return result
        
    except Exception as e:
        print(f"❌ Error in LLM call: {str(e)}")
        print(f"❌ Exception type: {type(e)}")
        import traceback
        print(f"❌ Full traceback: {traceback.format_exc()}")
        return f"Error calling LLM: {str(e)}"
