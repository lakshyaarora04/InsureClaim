"""
InsureClaims - Agent Tools Module
Provides 5 specialized, auditable tools for the autonomous insurance claim adjudication agent:
1. search_policy: Semantic vector retrieval of policy clauses from FAISS.
2. get_claim_history: Relational database query for claimant history and duplicate submission detection.
3. check_waiting_period: Deterministic validation of waiting period conditions.
4. calculate_coverage: Deterministic financial coverage calculation with sub-limits and co-pay.
5. create_audit_entry: Immutable logging of agent actions, tool calls, and adjudications.
"""

import os
import re
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from backend.database.db_manager import db_manager
from backend.retriever.vector_store import VectorStore
from backend.retriever.embedder import embed_query, embed_claim_query
from backend.utils.document_reader import read_document
from backend.utils.chunker import chunk_text

ROOT_DIR = Path(__file__).resolve().parents[2]
COMPREHENSIVE_POLICY = ROOT_DIR / "documents" / "comprehensive_health_policy.txt"
DEFAULT_POLICY_PATH = COMPREHENSIVE_POLICY if COMPREHENSIVE_POLICY.exists() else (ROOT_DIR / "documents" / "sample_policy.pdf")

# Global reference to active vector stores from backend state
_ACTIVE_VECTOR_STORES: Dict[str, Any] = {}


def register_vector_store(file_id: str, store_data: Dict[str, Any]):
    """Registers a vector store instance for policy retrieval."""
    _ACTIVE_VECTOR_STORES[file_id] = store_data


def get_default_or_active_vector_store(file_id: Optional[str] = None) -> Optional[VectorStore]:
    """Retrieves the active vector store, auto-indexing the default policy if needed."""
    target_id = file_id or ("default" if "default" in _ACTIVE_VECTOR_STORES else (list(_ACTIVE_VECTOR_STORES.keys())[0] if _ACTIVE_VECTOR_STORES else "default"))

    if target_id in _ACTIVE_VECTOR_STORES:
        return _ACTIVE_VECTOR_STORES[target_id].get("vector_store")

    # Initialize default policy document if available
    if DEFAULT_POLICY_PATH.exists():
        try:
            from backend.retriever.embedder import embed_chunks
            text = read_document(str(DEFAULT_POLICY_PATH))
            chunks = chunk_text(text)
            embeddings = embed_chunks(chunks, fit_vectorizer=True)
            store = VectorStore(dimension=embeddings.shape[1] if len(embeddings) > 0 else 1000)
            store.add(embeddings, chunks)
            _ACTIVE_VECTOR_STORES["default"] = {
                "vector_store": store,
                "chunks": chunks,
                "name": "sample_policy.pdf",
            }
            return store
        except Exception as e:
            print(f"⚠️ Error initializing default vector store: {e}")
    return None


# ─── Tool 1: search_policy ──────────────────────────────────────────────────

def search_policy(query: str, top_k: int = 5, file_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Search policy documents for clauses relevant to a clinical procedure or query.
    
    Args:
        query: Insurance inquiry or medical procedure description.
        top_k: Maximum number of clauses to return.
        file_id: Specific uploaded document identifier (optional).
    
    Returns:
        Structured dictionary with retrieved clauses, relevance scores, and metadata.
    """
    if not query or not query.strip():
        return {
            "status": "NO_QUERY_PROVIDED",
            "count": 0,
            "clauses": [],
            "message": "Query string is empty. Please provide a procedure or clause to search.",
        }

    store = get_default_or_active_vector_store(file_id)
    if not store or len(store.text_chunks) == 0:
        return {
            "status": "STORE_NOT_AVAILABLE",
            "count": 0,
            "clauses": [],
            "message": "No policy document is currently indexed in the vector store.",
        }

    try:
        query_vector = embed_query(query)
        # Search FAISS vector index
        raw_results = store.search(query_vector, top_k=top_k, distance_threshold=2.5)

        clauses = []
        for idx, text in enumerate(raw_results):
            # Parse clause headers if present (e.g. "Section 4.1" or "Clause 2")
            section_match = re.search(r"((?:Section|Clause|Article)\s*[\d\.]+[:\s])", text, re.IGNORECASE)
            section_title = section_match.group(1).strip() if section_match else f"Clause {idx + 1}"
            clauses.append({
                "clause_id": idx + 1,
                "section": section_title,
                "text": text,
                "relevance_rank": idx + 1,
            })

        if not clauses:
            return {
                "status": "NO_RELEVANT_CLAUSES_FOUND",
                "count": 0,
                "clauses": [],
                "message": f"No policy clauses found with sufficient similarity for: '{query}'",
            }

        return {
            "status": "SUCCESS",
            "count": len(clauses),
            "clauses": clauses,
            "message": f"Retrieved {len(clauses)} policy clauses for query: '{query}'",
        }
    except Exception as e:
        return {
            "status": "SEARCH_ERROR",
            "count": 0,
            "clauses": [],
            "error": str(e),
            "message": f"Vector retrieval error: {str(e)}",
        }


# ─── Tool 2: get_claim_history ──────────────────────────────────────────────

def get_claim_history(
    claimant_id: Optional[str] = None,
    claim_id: Optional[str] = None,
    procedure: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query the relational database for past claims, prior outcomes, and detect repeated submissions.
    
    Args:
        claimant_id: Unique claimant identifier.
        claim_id: Specific claim ID to look up context.
        procedure: Proposed procedure to cross-check for duplicate submissions.
    
    Returns:
        Structured history, claim frequency, prior rejections, and duplicate warnings.
    """
    history_records: List[Dict[str, Any]] = []

    # 1. Lookup by specific claim_id if provided
    if claim_id:
        context = db_manager.get_complete_claim_context(claim_id)
        if context:
            claimant_id = context.get("claimant_id") or claimant_id
            history_records.append(context)

    # 2. Lookup complete claimant history
    if claimant_id:
        records = db_manager.get_claimant_history_with_joins(claimant_id)
        for r in records:
            if not any(h.get("claim_id") == r.get("claim_id") for h in history_records):
                history_records.append(r)

    # 3. Check for repeated submissions / duplicate claims
    is_repeated_submission = False
    duplicate_warning = None
    if procedure and history_records:
        norm_proc = procedure.lower().strip()
        for past in history_records:
            past_proc = str(past.get("procedure_name", "")).lower()
            if norm_proc in past_proc or past_proc in norm_proc:
                is_repeated_submission = True
                duplicate_warning = (
                    f"Warning: A prior claim for '{past.get('procedure_name')}' was previously "
                    f"submitted (Status: {past.get('claim_status') or past.get('decision')}). "
                    f"Cross-referencing to prevent duplicate payout."
                )
                break

    return {
        "status": "SUCCESS" if history_records else "NO_HISTORY_FOUND",
        "claimant_id": claimant_id,
        "total_prior_claims": len(history_records),
        "history": history_records,
        "is_repeated_submission": is_repeated_submission,
        "duplicate_warning": duplicate_warning,
    }


# ─── Tool 3: check_waiting_period ───────────────────────────────────────────

# Deterministic catalog of statutory & policy waiting periods (in months)
SPECIFIED_DISEASE_WAITING_PERIODS = {
    "cataract": 24,
    "hernia": 24,
    "fistula": 24,
    "piles": 24,
    "haemorrhoids": 24,
    "sinus": 24,
    "sinusitis": 24,
    "stones": 24,
    "gall bladder": 24,
    "kidney stone": 24,
    "joint replacement": 24,
    "knee replacement": 24,
    "hip replacement": 24,
    "tonsil": 24,
    "tonsilitis": 24,
    "hysterectomy": 24,
    "varicose veins": 24,
    "hydrocele": 24,
    "bariatric": 36,
    "pre-existing": 36,
    "congenital": 24,
}


def check_waiting_period(
    procedure: str,
    policy_duration_months: Optional[int] = 12,
    policy_duration_days: Optional[int] = None,
    is_emergency: bool = False,
    is_accident: bool = False,
    is_pre_existing: bool = False,
    retrieved_clauses: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Deterministically evaluates whether the procedure satisfies statutory and policy waiting periods.
    Never invents waiting periods.
    
    Args:
        procedure: Medical procedure or diagnosis name.
        policy_duration_months: Months elapsed since policy inception.
        policy_duration_days: Days elapsed since policy inception (optional).
        is_emergency: Whether treatment was an urgent life-saving intervention.
        is_accident: Whether claim arises from an accidental bodily injury.
        is_pre_existing: Whether claim relates to a pre-existing declared condition.
        retrieved_clauses: Optional text chunks from policy to check custom terms.
    
    Returns:
        Structured evaluation: status (MET, NOT_MET, EXEMPT), required months, and rationale.
    """
    proc_clean = (procedure or "").lower().strip()
    duration = int(policy_duration_months or 0) if policy_duration_months is not None else 0

    # 1. Accident / Life-Threatening Emergency Waiver
    if is_accident or is_emergency or any(k in proc_clean for k in ("accident", "emergency", "perforation", "trauma", "rupture")):
        return {
            "status": "EXEMPT",
            "satisfied": True,
            "required_months": 0,
            "actual_months": duration,
            "exemption_type": "ACCIDENT_OR_EMERGENCY_OVERRIDE",
            "reason": "Emergency life-saving care and accidental injuries are exempt from waiting periods per Section 6.1.",
        }

    # 2. Pre-Existing Disease (PED) Waiting Period (36-48 Months)
    if is_pre_existing or any(k in proc_clean for k in ("pre-existing", "nephropathy", "hypertensive crisis", "asthma exacerbation", "diabetic")):
        req_ped = 36
        if duration < req_ped:
            deficit = req_ped - duration
            return {
                "status": "NOT_MET",
                "satisfied": False,
                "required_months": req_ped,
                "actual_months": duration,
                "deficit_months": deficit,
                "reason": (
                    f"Pre-existing condition requires {req_ped} months of continuous coverage before "
                    f"benefits are payable (Clause 3.1). Policy has been active for {duration} months ({deficit} months remaining)."
                ),
            }

    # 3. Initial 30-Day Waiting Period Check
    if policy_duration_days is not None and policy_duration_days < 30:
        return {
            "status": "NOT_MET",
            "satisfied": False,
            "required_months": 1,
            "actual_days": policy_duration_days,
            "reason": f"Initial 30-day waiting period has not elapsed ({policy_duration_days} days elapsed since inception).",
        }

    # 2. Specified Illness 24-Month Waiting Period
    for disease, req_months in SPECIFIED_DISEASE_WAITING_PERIODS.items():
        if disease in proc_clean:
            if duration >= req_months:
                return {
                    "status": "MET",
                    "satisfied": True,
                    "required_months": req_months,
                    "actual_months": duration,
                    "disease_matched": disease,
                    "reason": f"Waiting period of {req_months} months for {disease.title()} is satisfied ({duration} months elapsed).",
                }
            else:
                deficit = req_months - duration
                return {
                    "status": "NOT_MET",
                    "satisfied": False,
                    "required_months": req_months,
                    "actual_months": duration,
                    "deficit_months": deficit,
                    "disease_matched": disease,
                    "reason": (
                        f"Waiting period NOT met: {disease.title()} requires {req_months} months of continuous "
                        f"coverage, but policy has only been active for {duration} months ({deficit} months remaining)."
                    ),
                }

    # 3. Initial 30-Day (1 Month) General Waiting Period
    if duration < 1:
        return {
            "status": "NOT_MET",
            "satisfied": False,
            "required_months": 1,
            "actual_months": duration,
            "reason": "General 30-day initial waiting period has not elapsed for non-accidental illness.",
        }

    return {
        "status": "MET",
        "satisfied": True,
        "required_months": 1,
        "actual_months": duration,
        "reason": f"Standard policy waiting period is satisfied ({duration} months elapsed).",
    }


# ─── Tool 4: calculate_coverage ─────────────────────────────────────────────

# Standard procedure-level sub-limits
PROCEDURE_SUB_LIMITS = {
    "bilateral cataract": 80000.0,
    "cataract": 40000.0,
    "hernia": 50000.0,
    "knee replacement": 80000.0,
    "joint replacement": 80000.0,
    "hip replacement": 80000.0,
    "accidental dental": 15000.0,
    "dental reconstruction": 15000.0,
    "dialysis": 35000.0,
    "appendectomy": 65000.0,
    "cardiac bypass": 300000.0,
    "heart surgery": 300000.0,
}


def calculate_coverage(
    claimed_amount: float,
    sum_insured: float = 500000.0,
    procedure: str = "",
    co_pay_pct: float = 0.0,
    is_cosmetic: bool = False,
    is_dental_non_accident: bool = False,
    is_experimental: bool = False,
) -> Dict[str, Any]:
    """
    Deterministically computes the eligible claim payout using Python arithmetic.
    Applies procedure sub-limits, exclusions, co-pay deductions, and remaining sum insured caps.
    Never allows an LLM to guess financial calculations.
    
    Args:
        claimed_amount: Amount submitted on invoice in INR.
        sum_insured: Total remaining policy coverage cap.
        procedure: Name of the medical procedure.
        co_pay_pct: Co-payment percentage (e.g., 0.10 for 10% co-pay on senior policies).
        is_cosmetic: Flag if procedure is elective cosmetic surgery.
        is_dental_non_accident: Flag if procedure is non-accidental routine dental.
        is_experimental: Flag if procedure is unproven or experimental therapy.
    
    Returns:
        Structured breakdown with eligible amount, deductions, sub-limit applied, and explanation.
    """
    claimed = max(0.0, float(claimed_amount or 0.0))
    limit = max(0.0, float(sum_insured or 500000.0))
    proc_norm = (procedure or "").lower().strip()

    # 1. Total Exclusions Check
    if is_cosmetic or "cosmetic" in proc_norm or "rhinoplasty" in proc_norm or ("bariatric" in proc_norm and "cosmetic" in proc_norm):
        return {
            "eligible_amount": 0.0,
            "claimed_amount": claimed,
            "sub_limit_applied": 0.0,
            "deductions": claimed,
            "deduction_reasons": ["Strict exclusion for elective cosmetic or aesthetic surgery."],
            "explanation": "Eligible coverage is ₹0 due to policy exclusion on aesthetic/cosmetic procedures.",
        }

    if is_dental_non_accident or ("dental" in proc_norm and not any(k in proc_norm for k in ("accident", "trauma", "jaw"))):
        return {
            "eligible_amount": 0.0,
            "claimed_amount": claimed,
            "sub_limit_applied": 0.0,
            "deductions": claimed,
            "deduction_reasons": ["Strict exclusion for routine, non-accidental dental procedures."],
            "explanation": "Eligible coverage is ₹0 due to policy exclusion on routine outpatient dental treatments.",
        }

    if is_experimental or any(k in proc_norm for k in ("experimental", "stem cell", "unproven", "trial")):
        return {
            "eligible_amount": 0.0,
            "claimed_amount": claimed,
            "sub_limit_applied": 0.0,
            "deductions": claimed,
            "deduction_reasons": ["Strict exclusion for experimental, trial, or unproven clinical procedures."],
            "explanation": "Eligible coverage is ₹0 due to policy exclusion on experimental and unproven treatments.",
        }

    # 2. Procedural Sub-limit Matching
    applicable_sub_limit = None
    for key, sub_val in PROCEDURE_SUB_LIMITS.items():
        if key in proc_norm:
            applicable_sub_limit = sub_val
            break

    # 3. Base Eligible Amount
    base_eligible = claimed
    deduction_reasons = []

    if applicable_sub_limit is not None and claimed > applicable_sub_limit:
        excess = claimed - applicable_sub_limit
        deduction_reasons.append(f"Capped by procedure sub-limit of ₹{applicable_sub_limit:,.0f} (₹{excess:,.0f} excess deducted).")
        base_eligible = applicable_sub_limit

    # 4. Sum Insured Cap
    if base_eligible > limit:
        cap_excess = base_eligible - limit
        deduction_reasons.append(f"Capped by maximum remaining sum insured of ₹{limit:,.0f} (₹{cap_excess:,.0f} excess deducted).")
        base_eligible = limit

    # 5. Co-Payment Deductions
    co_pay_amount = 0.0
    if co_pay_pct > 0.0:
        co_pay_amount = round(base_eligible * co_pay_pct, 2)
        deduction_reasons.append(f"Mandatory {int(co_pay_pct * 100)}% co-pay deduction: ₹{co_pay_amount:,.0f}.")
        base_eligible -= co_pay_amount

    final_eligible = max(0.0, round(base_eligible, 2))
    total_deductions = round(claimed - final_eligible, 2)

    return {
        "eligible_amount": final_eligible,
        "claimed_amount": claimed,
        "sub_limit_applied": applicable_sub_limit,
        "co_pay_deducted": co_pay_amount,
        "total_deductions": total_deductions,
        "deduction_reasons": deduction_reasons,
        "explanation": (
            f"Calculated eligible amount: ₹{final_eligible:,.0f} from claimed ₹{claimed:,.0f}. "
            + (" ".join(deduction_reasons) if deduction_reasons else "Full claimed amount approved under policy caps.")
        ),
    }


# ─── Tool 5: create_audit_entry ─────────────────────────────────────────────

def create_audit_entry(
    claim_id: str,
    decision: str,
    amount: float,
    confidence_score: float = 0.95,
    justification: str = "",
    tools_invoked: Optional[List[Dict[str, Any]]] = None,
    reasoning_tree: Optional[Dict[str, Any]] = None,
    performed_by: str = "AGENT",
) -> Dict[str, Any]:
    """
    Creates an immutable, traceable audit log record storing the agent's complete execution trace.
    
    Args:
        claim_id: Unique claim identifier.
        decision: Final adjudication decision (APPROVED, REJECTED, etc.).
        amount: Approved coverage amount.
        confidence_score: Algorithmic confidence score (0.0 to 1.0).
        justification: Legal/medical policy justification.
        tools_invoked: Chronological list of tool calls with inputs and outputs.
        reasoning_tree: Step-by-step reasoning hierarchy.
        performed_by: Actor identifier ("AGENT", "ADJUSTER", etc.).
    
    Returns:
        Audit record metadata including audit_id and timestamp.
    """
    evaluation_id = uuid.uuid4().hex
    audit_id = uuid.uuid4().hex
    timestamp = datetime.utcnow().isoformat()

    conn = db_manager.get_connection()
    try:
        ph = "%s" if db_manager.is_mysql else "?"
        cursor = conn.cursor()

        tools_invoked = tools_invoked or []

        # Convert reasoning_tree to serializable dict
        serializable_tree = {}
        if hasattr(reasoning_tree, "get_json_breakdown"):
            serializable_tree = reasoning_tree.get_json_breakdown()
        elif hasattr(reasoning_tree, "nodes"):
            serializable_tree = {
                "steps": [
                    {
                        "step": getattr(n.step, "value", str(n.step)),
                        "status": n.status,
                        "details": n.details,
                        "confidence": n.confidence,
                    }
                    for n in getattr(reasoning_tree, "nodes", [])
                ],
                "decision": getattr(reasoning_tree, "final_decision", "PENDING"),
            }
        elif isinstance(reasoning_tree, dict):
            serializable_tree = reasoning_tree

        # Format serialized audit notes containing execution trace
        trace_summary = {
            "evaluation_id": evaluation_id,
            "claim_id": claim_id,
            "decision": decision,
            "amount": amount,
            "confidence_score": confidence_score,
            "tools_count": len(tools_invoked),
            "tools_invoked": tools_invoked,
            "reasoning_tree": serializable_tree,
            "timestamp": timestamp,
        }

        # Ensure referential integrity in normalized 3NF schema
        cursor.execute(f"SELECT id FROM claims WHERE id = {ph}", (claim_id,))
        if not cursor.fetchone():
            stub_claimant = f"clm_{claim_id[:8]}"
            stub_policy = f"pol_{claim_id[:8]}"
            cursor.execute(
                f"""INSERT OR IGNORE INTO claimants (id, full_name, age, gender, contact, city)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (stub_claimant, "Policyholder", 35, "unknown", "", "Mumbai"),
            )
            cursor.execute(
                f"""INSERT OR IGNORE INTO policies (id, claimant_id, policy_number, plan_name, duration_months, max_coverage_amount, status)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (stub_policy, stub_claimant, f"POL-{claim_id[:8].upper()}", "Standard Health Policy", 12, 500000.0, "ACTIVE"),
            )
            cursor.execute(
                f"""INSERT OR IGNORE INTO claims (id, policy_id, procedure_name, hospital_location, claimed_amount, file_id, status)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (claim_id, stub_policy, "Adjudicated Procedure", "Mumbai", float(amount), "default", "ADJUDICATED"),
            )

        # Insert evaluation entry
        cursor.execute(
            f"""INSERT OR REPLACE INTO evaluations 
               (id, claim_id, decision, approved_amount, confidence_score, justification, retrieved_clauses, reasoning_tree)
               VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
            (
                evaluation_id,
                claim_id,
                decision.lower(),
                float(amount),
                float(confidence_score),
                justification,
                json.dumps([t.get("output") for t in tools_invoked if t.get("tool") == "search_policy"]),
                json.dumps(serializable_tree),
            ),
        )

        # Insert audit_logs entry
        cursor.execute(
            f"""INSERT INTO audit_logs 
               (id, evaluation_id, action, performed_by, notes)
               VALUES ({ph}, {ph}, {ph}, {ph}, {ph})""",
            (
                audit_id,
                evaluation_id,
                f"AGENT_DECISION_{decision.upper()}",
                performed_by,
                json.dumps(trace_summary),
            ),
        )

        if hasattr(conn, "commit"):
            conn.commit()

        return {
            "status": "SUCCESS",
            "audit_id": audit_id,
            "evaluation_id": evaluation_id,
            "timestamp": timestamp,
            "message": f"Audit record {audit_id} successfully logged for claim {claim_id}.",
        }
    except Exception as e:
        print(f"⚠️ Error creating audit entry: {e}")
        return {
            "status": "ERROR",
            "error": str(e),
            "audit_id": audit_id,
            "timestamp": timestamp,
        }
    finally:
        conn.close()


# ─── Tool Registry & Schemas for LLM Tool Calling ───────────────────────────

AGENT_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_policy",
            "description": "Searches indexed insurance policy documents using vector search to retrieve applicable clauses, waiting periods, sub-limits, and exclusions for a medical procedure.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The medical procedure or policy condition to search (e.g. 'cataract surgery waiting period', 'cosmetic surgery exclusion').",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of relevant policy clauses to retrieve (default: 5).",
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_claim_history",
            "description": "Queries the relational database for a claimant's previous insurance claims, prior approval/rejection outcomes, and flags duplicate submissions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claimant_id": {
                        "type": "string",
                        "description": "Unique identifier of the claimant.",
                    },
                    "claim_id": {
                        "type": "string",
                        "description": "Specific claim ID to inspect.",
                    },
                    "procedure": {
                        "type": "string",
                        "description": "Current procedure name to cross-check for duplicate submissions.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_waiting_period",
            "description": "Deterministically verifies whether a medical procedure satisfies policy waiting periods (e.g. 24 months for cataract/hernia/joint replacement, 30 days initial, accident exemption).",
            "parameters": {
                "type": "object",
                "properties": {
                    "procedure": {
                        "type": "string",
                        "description": "The medical procedure or surgery name.",
                    },
                    "policy_duration_months": {
                        "type": "integer",
                        "description": "Months elapsed since the policy started.",
                    },
                    "is_emergency": {
                        "type": "boolean",
                        "description": "Whether the treatment is an urgent emergency life-saving procedure.",
                    },
                    "is_accident": {
                        "type": "boolean",
                        "description": "Whether the claim is caused by an accidental injury.",
                    },
                },
                "required": ["procedure", "policy_duration_months"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_coverage",
            "description": "Deterministically calculates the eligible coverage payout using strict Python arithmetic, applying procedural sub-limits, remaining sum insured, co-pay, and exclusions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claimed_amount": {
                        "type": "number",
                        "description": "The monetary amount claimed by the patient in INR.",
                    },
                    "sum_insured": {
                        "type": "number",
                        "description": "The maximum policy coverage limit.",
                    },
                    "procedure": {
                        "type": "string",
                        "description": "Procedure name to evaluate for sub-limits.",
                    },
                    "is_cosmetic": {
                        "type": "boolean",
                        "description": "Whether the procedure is elective aesthetic/cosmetic surgery.",
                    },
                    "is_dental_non_accident": {
                        "type": "boolean",
                        "description": "Whether the procedure is routine non-accidental dental care.",
                    },
                    "co_pay_pct": {
                        "type": "number",
                        "description": "Applicable co-pay fraction (e.g. 0.1 for 10%).",
                    },
                },
                "required": ["claimed_amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_audit_entry",
            "description": "Logs an immutable audit record of the agent's evaluation, tool invocation trace, decision, and justification into the relational database.",
            "parameters": {
                "type": "object",
                "properties": {
                    "claim_id": {
                        "type": "string",
                        "description": "ID of the claim being evaluated.",
                    },
                    "decision": {
                        "type": "string",
                        "description": "Final adjudication decision (APPROVED, REJECTED, INSUFFICIENT_INFORMATION, NEEDS_REVIEW).",
                    },
                    "amount": {
                        "type": "number",
                        "description": "Final approved numerical amount.",
                    },
                    "confidence_score": {
                        "type": "number",
                        "description": "Confidence score between 0.0 and 1.0.",
                    },
                    "justification": {
                        "type": "string",
                        "description": "Detailed explanation citing specific policy clauses.",
                    },
                },
                "required": ["claim_id", "decision", "amount", "justification"],
            },
        },
    },
]
