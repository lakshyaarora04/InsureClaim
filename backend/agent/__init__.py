"""
InsureClaims Agent Package
Provides autonomous multi-turn tool calling and deterministic fallback orchestration.
"""

from backend.agent.orchestrator import InsuranceClaimAgent, claim_agent
from backend.agent.tools import (
    AGENT_TOOLS,
    search_policy,
    get_claim_history,
    check_waiting_period,
    calculate_coverage,
    create_audit_entry,
)

__all__ = [
    "InsuranceClaimAgent",
    "claim_agent",
    "AGENT_TOOLS",
    "search_policy",
    "get_claim_history",
    "check_waiting_period",
    "calculate_coverage",
    "create_audit_entry",
]
