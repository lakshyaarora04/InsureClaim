"""
InsureClaims - Autonomous AI Agent Orchestrator
Executes multi-turn tool calling with dynamic tool selection using OpenAI/Groq/Gemini function calling,
integrated with the deterministic policy, financial, and relational database tools.
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional

from backend.agent.tools import (
    AGENT_TOOLS,
    search_policy,
    get_claim_history,
    check_waiting_period,
    calculate_coverage,
    create_audit_entry,
)
from backend.decision_engine.reasoning_tree import ReasoningEngine

AGENT_SYSTEM_PROMPT = """You are an autonomous Insurance Claim Adjudication Agent for InsureClaims.
Your mission is to evaluate insurance claims with strict legal rigor, procedural precision, and policy compliance.

You have access to 5 deterministic, verifiable tools:
1. `search_policy(query, top_k)`: Searches vector policy index for relevant policy clauses.
2. `get_claim_history(claimant_id, claim_id, procedure)`: Queries relational database for past claims and detects duplicate submissions.
3. `check_waiting_period(procedure, policy_duration_months, is_emergency, is_accident)`: Deterministically verifies whether statutory waiting periods are satisfied.
4. `calculate_coverage(claimed_amount, sum_insured, procedure, is_cosmetic, is_dental_non_accident, co_pay_pct)`: Deterministically calculates monetary payout enforcing sub-limits.
5. `create_audit_entry(claim_id, decision, amount, confidence_score, justification)`: Records audit trail of adjudication.

ORCHESTRATION RULES:
1. TOOL SELECTION: Select tools dynamically based on user inquiry. Do not blindly invoke all tools.
2. FACTUAL GROUNDING: Never invent policy terms or waiting periods. All adjudications must be grounded in tool outputs.
3. INSUFFICIENT INFO: If critical claim details (procedure, duration, or claim amount) are missing, render decision "INSUFFICIENT_INFORMATION".
4. CONTRADICTIONS: If retrieved policy clauses present contradictory terms or ambiguous coverage, render decision "NEEDS_REVIEW".
5. FINANCIAL ACCURACY: Always use `calculate_coverage` for the final approved amount. Never guess monetary math.
6. FINAL OUTPUT: Provide a comprehensive, structured response detailing decision, approved amount, and cited clauses.
"""


class InsuranceClaimAgent:
    """
    Autonomous AI Agent for claim evaluation supporting dynamic multi-turn tool calling.
    """

    def __init__(self):
        self.reasoning_engine = ReasoningEngine()
        self.tool_map = {
            "search_policy": search_policy,
            "get_claim_history": get_claim_history,
            "check_waiting_period": check_waiting_period,
            "calculate_coverage": calculate_coverage,
            "create_audit_entry": create_audit_entry,
        }

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a single tool and captures execution metrics."""
        tool_fn = self.tool_map.get(tool_name)
        if not tool_fn:
            return {
                "status": "TOOL_NOT_FOUND",
                "error": f"Tool '{tool_name}' is not registered in agent catalog.",
            }

        start_time = time.perf_counter()
        try:
            output = tool_fn(**arguments)
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "SUCCESS",
                "output": output,
                "duration_ms": elapsed_ms,
            }
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {
                "status": "ERROR",
                "error": str(e),
                "duration_ms": elapsed_ms,
            }

    def run_deterministic_workflow(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic, rule-guided execution of the agent tools.
        Used when no API key is available or during offline execution.
        Transparently labels the execution mode as 'deterministic_fallback'.
        """
        start_overall = time.perf_counter()
        tools_invoked: List[Dict[str, Any]] = []

        procedure = (claim_data.get("procedure") or "").strip()
        duration_val = claim_data.get("policy_duration_months")
        duration_days = claim_data.get("policy_duration_days")
        amount_val = claim_data.get("claim_amount")
        query_text = (claim_data.get("query_text") or claim_data.get("query") or "").strip()

        # Check 1: Insufficient Information Guard
        is_missing_procedure = (not procedure) or (procedure.lower() in ("surgery", "unspecified medical procedure", "unspecified"))
        is_missing_duration = (duration_val is None and duration_days is None)
        is_missing_amount = (amount_val is None or float(amount_val or 0.0) <= 0.0)

        if is_missing_procedure or (is_missing_duration and is_missing_amount):
            return {
                "decision": "insufficient_information",
                "amount": 0.0,
                "confidence_score": 0.90,
                "claim_id": claim_data.get("claim_id") or uuid.uuid4().hex,
                "claimant_id": claim_data.get("claimant_id"),
                "procedure": procedure or "Unspecified",
                "justification": "Claim submission lacks mandatory clinical diagnosis, policy duration, or invoice amount needed for adjudication.",
                "waiting_period_analysis": "Cannot evaluate waiting period without policy inception tenure and procedure diagnosis.",
                "coverage_breakdown": {},
                "retrieved_clauses": [],
                "reasoning_tree": {"steps": []},
                "tools_invoked": [],
                "agent_mode": "deterministic_fallback",
                "total_duration_ms": 1.0,
            }

        # Check 2: Contradictory / Ambiguous Endorsement Guard
        if claim_data.get("has_conflicting_rider"):
            return {
                "decision": "needs_review",
                "amount": 0.0,
                "confidence_score": 0.70,
                "claim_id": claim_data.get("claim_id") or uuid.uuid4().hex,
                "claimant_id": claim_data.get("claimant_id"),
                "procedure": procedure,
                "justification": "Claim involves contradictory policy endorsements and clinical necessity contentions. Escalated for Senior Adjuster manual adjudication.",
                "waiting_period_analysis": "Ambiguous rider terms supersede standard clause schedule.",
                "coverage_breakdown": {},
                "retrieved_clauses": [],
                "reasoning_tree": {"steps": []},
                "tools_invoked": [],
                "agent_mode": "deterministic_fallback",
                "total_duration_ms": 1.0,
            }

        policy_duration = int(duration_val) if duration_val is not None else 12
        claimed_amount = float(amount_val or 50000.0)
        claim_id = claim_data.get("claim_id") or uuid.uuid4().hex
        claimant_id = claim_data.get("claimant_id")
        file_id = claim_data.get("file_id")

        # Step 1: Query relational claim history
        step1_res = self._execute_tool("get_claim_history", {
            "claimant_id": claimant_id,
            "claim_id": claim_id,
            "procedure": procedure,
        })
        tools_invoked.append({
            "step": 1,
            "tool": "get_claim_history",
            "input": {"claimant_id": claimant_id, "procedure": procedure},
            "output": step1_res.get("output"),
            "duration_ms": step1_res.get("duration_ms", 1.0),
            "status": step1_res.get("status"),
        })

        is_duplicate = (step1_res.get("output") or {}).get("is_duplicate", False) or bool(claim_data.get("force_duplicate_check"))

        # Step 2: Search policy clauses from FAISS vector store
        step2_res = self._execute_tool("search_policy", {
            "query": f"{procedure} coverage waiting period exclusions",
            "top_k": 4,
            "file_id": file_id,
        })
        tools_invoked.append({
            "step": 2,
            "tool": "search_policy",
            "input": {"query": procedure, "top_k": 4},
            "output": step2_res.get("output"),
            "duration_ms": step2_res.get("duration_ms", 2.0),
            "status": step2_res.get("status"),
        })

        retrieved_clauses = [c.get("text", "") for c in (step2_res.get("output") or {}).get("clauses", [])]

        # Step 3: Check waiting period
        is_accident = bool(claim_data.get("is_accident")) or any(k in procedure.lower() or k in query_text.lower() for k in ("accident", "fracture", "road", "trauma"))
        is_emergency = bool(claim_data.get("is_emergency")) or any(k in procedure.lower() or k in query_text.lower() for k in ("emergency", "perforation", "rupture", "acute peritonitis", "icu"))
        is_pre_existing = bool(claim_data.get("is_pre_existing"))

        step3_res = self._execute_tool("check_waiting_period", {
            "procedure": procedure,
            "policy_duration_months": policy_duration,
            "policy_duration_days": duration_days,
            "is_accident": is_accident,
            "is_emergency": is_emergency,
            "is_pre_existing": is_pre_existing,
            "retrieved_clauses": retrieved_clauses,
        })
        tools_invoked.append({
            "step": 3,
            "tool": "check_waiting_period",
            "input": {"procedure": procedure, "policy_duration_months": policy_duration},
            "output": step3_res.get("output"),
            "duration_ms": step3_res.get("duration_ms", 0.5),
            "status": step3_res.get("status"),
        })

        wp_output = step3_res.get("output", {})
        waiting_period_satisfied = wp_output.get("satisfied", True)

        # Step 4: Check exclusions & calculate coverage
        is_cosmetic = bool(claim_data.get("is_cosmetic")) or ("cosmetic" in procedure.lower()) or ("rhinoplasty" in procedure.lower())
        is_dental = bool(claim_data.get("is_dental_non_accident")) or ("dental" in procedure.lower() and not is_accident)
        is_experimental = bool(claim_data.get("is_experimental")) or ("experimental" in procedure.lower()) or ("stem cell" in procedure.lower())
        co_pay_pct = float(claim_data.get("co_pay_pct", 0.0) or 0.0)
        sum_insured = float(claim_data.get("sum_insured") or claim_data.get("max_coverage_amount") or 500000.0)

        step4_res = self._execute_tool("calculate_coverage", {
            "claimed_amount": claimed_amount,
            "sum_insured": sum_insured,
            "procedure": procedure,
            "co_pay_pct": co_pay_pct,
            "is_cosmetic": is_cosmetic,
            "is_dental_non_accident": is_dental,
            "is_experimental": is_experimental,
        })
        tools_invoked.append({
            "step": 4,
            "tool": "calculate_coverage",
            "input": {"claimed_amount": claimed_amount, "procedure": procedure},
            "output": step4_res.get("output"),
            "duration_ms": step4_res.get("duration_ms", 0.5),
            "status": step4_res.get("status"),
        })

        cov_output = step4_res.get("output", {})
        eligible_amount = cov_output.get("eligible_amount", 0.0)

        # Adjudication synthesis
        if is_duplicate:
            decision = "rejected"
            amount = 0.0
            confidence = 0.98
            justification = "Claim rejected: Duplicate submission detected in relational history for identical procedure and claimant."
        elif not waiting_period_satisfied:
            decision = "rejected"
            amount = 0.0
            confidence = 0.95
            justification = f"Claim rejected: {wp_output.get('reason', 'Waiting period requirement not met.')}"
        elif is_cosmetic or is_dental or is_experimental:
            decision = "rejected"
            amount = 0.0
            confidence = 0.95
            justification = f"Claim rejected: {cov_output.get('explanation', 'Procedure excluded from policy coverage.')}"
        elif eligible_amount > 0:
            decision = "approved"
            amount = eligible_amount
            confidence = 0.95
            justification = (
                f"Claim approved: {procedure} is covered under policy terms. "
                f"{wp_output.get('reason', '')} "
                f"{cov_output.get('explanation', '')}"
            )
        else:
            decision = "rejected"
            amount = 0.0
            confidence = 0.85
            justification = "Claim rejected: Zero eligible coverage after applying sub-limits, deductibles, or policy exclusions."

        # Step 5: Audit log
        tree_obj = self.reasoning_engine.analyze_claim(claim_data, retrieved_clauses)
        if hasattr(tree_obj, "get_json_breakdown"):
            tree_data = tree_obj.get_json_breakdown()
            steps = [
                {
                    "title": n.get("step", ""),
                    "status": n.get("status", False),
                    "description": n.get("details", ""),
                    "confidence": n.get("confidence", 0.8),
                }
                for n in tree_data.get("reasoning_tree", [])
            ]
            serializable_tree = {"steps": steps, "tree": tree_data}
        elif hasattr(tree_obj, "nodes"):
            steps = [
                {
                    "title": getattr(n.step, "value", str(n.step)),
                    "status": n.status,
                    "description": n.details,
                    "confidence": n.confidence,
                }
                for n in getattr(tree_obj, "nodes", [])
            ]
            serializable_tree = {"steps": steps}
        else:
            serializable_tree = tree_obj if isinstance(tree_obj, dict) else {}

        step5_res = self._execute_tool("create_audit_entry", {
            "claim_id": claim_id,
            "decision": decision,
            "amount": amount,
            "confidence_score": confidence,
            "justification": justification,
            "tools_invoked": tools_invoked,
            "reasoning_tree": serializable_tree,
            "performed_by": "AGENT_DETERMINISTIC_FALLBACK",
        })
        tools_invoked.append({
            "step": 5,
            "tool": "create_audit_entry",
            "input": {"claim_id": claim_id, "decision": decision, "amount": amount},
            "output": step5_res.get("output"),
            "duration_ms": step5_res.get("duration_ms", 1.5),
            "status": step5_res.get("status"),
        })

        total_ms = round((time.perf_counter() - start_overall) * 1000, 2)

        return {
            "decision": decision,
            "amount": amount,
            "confidence_score": confidence,
            "claim_id": claim_id,
            "claimant_id": claimant_id,
            "procedure": procedure,
            "justification": justification,
            "waiting_period_analysis": wp_output.get("reason", ""),
            "coverage_breakdown": cov_output,
            "retrieved_clauses": retrieved_clauses,
            "reasoning_tree": serializable_tree,
            "tools_invoked": tools_invoked,
            "agent_mode": "deterministic_fallback",
            "total_duration_ms": total_ms,
        }

    def adjudicate_claim(self, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adjudicate a claim using autonomous tool calling when API key is configured,
        or graceful deterministic fallback when offline.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return self.run_deterministic_workflow(claim_data)

        # Autonomous LLM Multi-Turn Tool Calling
        start_overall = time.perf_counter()
        tools_invoked: List[Dict[str, Any]] = []

        try:
            from openai import OpenAI
            base_url = os.getenv("OPENAI_BASE_URL")
            client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
            model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

            procedure = claim_data.get("procedure", "treatment")
            duration = claim_data.get("policy_duration_months", 12)
            amount = claim_data.get("claim_amount", 50000.0)
            claimant_id = claim_data.get("claimant_id", "clm_user")
            claim_id = claim_data.get("claim_id") or uuid.uuid4().hex

            user_prompt = (
                f"Patient Claim Submission:\n"
                f"- Procedure: {procedure}\n"
                f"- Policy Duration: {duration} months\n"
                f"- Claimed Amount: ₹{amount}\n"
                f"- Claimant ID: {claimant_id}\n"
                f"- Claim ID: {claim_id}\n"
                f"- Location: {claim_data.get('location', 'Mumbai')}\n\n"
                f"Adjudicate this claim by invoking appropriate tools. "
                f"Ground your decision in policy clauses and calculate the exact eligible amount."
            )

            messages = [
                {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]

            step_counter = 1
            max_turns = 5

            for turn in range(max_turns):
                response = client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    tools=AGENT_TOOLS,
                    tool_choice="auto",
                    temperature=0.1,
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                # If model finished without calling more tools
                if not tool_calls:
                    messages.append(response_message)
                    break

                messages.append(response_message)

                for tc in tool_calls:
                    fn_name = tc.function.name
                    try:
                        fn_args = json.loads(tc.function.arguments)
                    except Exception:
                        fn_args = {}

                    # Execute the tool
                    exec_result = self._execute_tool(fn_name, fn_args)
                    tools_invoked.append({
                        "step": step_counter,
                        "tool": fn_name,
                        "input": fn_args,
                        "output": exec_result.get("output"),
                        "duration_ms": exec_result.get("duration_ms", 1.0),
                        "status": exec_result.get("status"),
                    })
                    step_counter += 1

                    # Append tool message back to LLM context
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "name": fn_name,
                        "content": json.dumps(exec_result.get("output") or exec_result),
                    })

            # Final synthesis pass
            final_content = messages[-1]["content"] if isinstance(messages[-1], dict) else getattr(messages[-1], "content", "")
            
            # Extract decision & amount from tools or LLM text
            calc_tool = next((t for t in reversed(tools_invoked) if t["tool"] == "calculate_coverage"), None)
            wp_tool = next((t for t in reversed(tools_invoked) if t["tool"] == "check_waiting_period"), None)
            search_tool = next((t for t in reversed(tools_invoked) if t["tool"] == "search_policy"), None)

            retrieved_clauses = [
                c.get("text", "") for c in (search_tool.get("output") or {}).get("clauses", [])
            ] if search_tool else []

            # Deterministic override guard: financial amounts and waiting periods must be grounded
            final_amount = 0.0
            if calc_tool and calc_tool.get("output"):
                final_amount = float(calc_tool["output"].get("eligible_amount", 0.0))

            if wp_tool and wp_tool.get("output") and not wp_tool["output"].get("satisfied"):
                decision = "rejected"
                final_amount = 0.0
            elif final_amount > 0:
                decision = "approved"
            else:
                decision = "rejected" if "reject" in str(final_content).lower() else "needs_review"

            total_ms = round((time.perf_counter() - start_overall) * 1000, 2)
            reasoning_tree = self.reasoning_engine.analyze_claim(claim_data, retrieved_clauses)

            # Auto-audit if not already done
            if not any(t["tool"] == "create_audit_entry" for t in tools_invoked):
                audit_res = self._execute_tool("create_audit_entry", {
                    "claim_id": claim_id,
                    "decision": decision,
                    "amount": final_amount,
                    "confidence_score": 0.95,
                    "justification": str(final_content),
                    "tools_invoked": tools_invoked,
                    "reasoning_tree": reasoning_tree,
                    "performed_by": f"AUTONOMOUS_AGENT_{model_name.upper()}",
                })
                tools_invoked.append({
                    "step": step_counter,
                    "tool": "create_audit_entry",
                    "input": {"claim_id": claim_id, "decision": decision, "amount": final_amount},
                    "output": audit_res.get("output"),
                    "duration_ms": audit_res.get("duration_ms", 1.0),
                    "status": audit_res.get("status"),
                })

            return {
                "decision": decision,
                "amount": final_amount,
                "confidence_score": 0.95,
                "claim_id": claim_id,
                "claimant_id": claimant_id,
                "procedure": procedure,
                "justification": str(final_content),
                "waiting_period_analysis": wp_tool.get("output", {}).get("reason", "") if wp_tool else "",
                "coverage_breakdown": calc_tool.get("output", {}) if calc_tool else {},
                "retrieved_clauses": retrieved_clauses,
                "reasoning_tree": reasoning_tree,
                "tools_invoked": tools_invoked,
                "agent_mode": "autonomous_tool_calling",
                "total_duration_ms": total_ms,
            }

        except Exception as e:
            print(f"⚠️ Autonomous agent encountered exception: {e}. Executing deterministic fallback.")
            return self.run_deterministic_workflow(claim_data)


# Singleton agent instance
claim_agent = InsuranceClaimAgent()
