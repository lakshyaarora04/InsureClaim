"""
Reasoning Tree System for Insurance Claim Evaluation
Provides human-readable breakdowns of decision logic
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class DecisionStep(Enum):
    PROCEDURE_MATCHED = "Procedure matched"
    LOCATION_VERIFIED = "Location verified"
    WAITING_PERIOD_MET = "Waiting period met"
    WAITING_PERIOD_NOT_MET = "Waiting period not met"
    EXCLUSION_FOUND = "Exclusion found"
    NO_EXCLUSION = "No exclusion found"
    POLICY_ACTIVE = "Policy active"
    COVERAGE_VERIFIED = "Coverage verified"
    AMOUNT_CALCULATED = "Amount calculated"

@dataclass
class ReasoningNode:
    step: DecisionStep
    status: bool  # True for passed, False for failed
    details: str
    clause_references: List[str]
    confidence: float  # 0.0 to 1.0

class ReasoningTree:
    """
    Builds a human-readable reasoning tree for insurance claim decisions
    """
    
    def __init__(self):
        self.nodes: List[ReasoningNode] = []
        self.final_decision: str = "PENDING"
        self.confidence_score: float = 0.0
    
    def add_step(self, step: DecisionStep, status: bool, details: str, 
                 clause_refs: List[str] = None, confidence: float = 0.8):
        """Add a reasoning step to the tree"""
        if clause_refs is None:
            clause_refs = []
        
        node = ReasoningNode(
            step=step,
            status=status,
            details=details,
            clause_references=clause_refs,
            confidence=confidence
        )
        self.nodes.append(node)
    
    def get_human_readable_breakdown(self) -> str:
        """Generate human-readable reasoning breakdown"""
        if not self.nodes:
            return "No reasoning steps available"
        
        breakdown = []
        breakdown.append("🔍 DECISION REASONING BREAKDOWN:")
        breakdown.append("=" * 50)
        
        for i, node in enumerate(self.nodes, 1):
            status_icon = "✅" if node.status else "❌"
            breakdown.append(f"{i}. {status_icon} {node.step.value}")
            breakdown.append(f"   Details: {node.details}")
            if node.clause_references:
                breakdown.append(f"   Clauses: {', '.join(node.clause_references)}")
            breakdown.append(f"   Confidence: {node.confidence:.1%}")
            breakdown.append("")
        
        # Add final decision
        breakdown.append(f"🎯 FINAL DECISION: {self.final_decision.upper()}")
        breakdown.append(f"📊 OVERALL CONFIDENCE: {self.confidence_score:.1%}")
        
        return "\n".join(breakdown)
    
    def get_json_breakdown(self) -> Dict[str, Any]:
        """Get structured JSON breakdown for API responses"""
        return {
            "reasoning_tree": [
                {
                    "step": node.step.value,
                    "status": node.status,
                    "details": node.details,
                    "clause_references": node.clause_references,
                    "confidence": node.confidence
                }
                for node in self.nodes
            ],
            "final_decision": self.final_decision,
            "overall_confidence": self.confidence_score
        }
    
    def calculate_overall_confidence(self):
        """Calculate overall confidence based on individual steps"""
        if not self.nodes:
            self.confidence_score = 0.0
            return
        
        # Weight different steps differently
        step_weights = {
            DecisionStep.PROCEDURE_MATCHED: 0.25,
            DecisionStep.WAITING_PERIOD_MET: 0.30,
            DecisionStep.NO_EXCLUSION: 0.25,
            DecisionStep.COVERAGE_VERIFIED: 0.20
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for node in self.nodes:
            weight = step_weights.get(node.step, 0.1)
            total_weight += weight
            weighted_sum += node.confidence * weight
        
        if total_weight > 0:
            self.confidence_score = weighted_sum / total_weight
        else:
            self.confidence_score = sum(node.confidence for node in self.nodes) / len(self.nodes)

class ReasoningEngine:
    """
    Main reasoning engine that builds decision trees
    """
    
    def __init__(self):
        self.tree = ReasoningTree()
    
    def analyze_claim(self, query_data: Dict[str, Any], 
                     policy_clauses: List[str]) -> ReasoningTree:
        """
        Analyze a claim and build a reasoning tree
        """
        self.tree = ReasoningTree()
        
        # Step 1: Check if procedure is covered
        self._check_procedure_coverage(query_data, policy_clauses)
        
        # Step 2: Check waiting period
        self._check_waiting_period(query_data, policy_clauses)
        
        # Step 3: Check exclusions
        self._check_exclusions(query_data, policy_clauses)
        
        # Step 4: Check policy status
        self._check_policy_status(query_data, policy_clauses)
        
        # Step 5: Calculate final decision
        self._calculate_final_decision()
        
        return self.tree
    
    def _check_procedure_coverage(self, query_data: Dict[str, Any], 
                                 policy_clauses: List[str]):
        """Check if the procedure is covered by the policy"""
        procedure = query_data.get('procedure', '').lower()
        
        # Search for procedure coverage in clauses
        coverage_found = False
        relevant_clauses = []
        
        for i, clause in enumerate(policy_clauses):
            if procedure in clause.lower():
                coverage_found = True
                relevant_clauses.append(f"Clause {i+1}")
        
        if coverage_found:
            self.tree.add_step(
                DecisionStep.PROCEDURE_MATCHED,
                True,
                f"Procedure '{procedure}' found in policy coverage",
                relevant_clauses,
                0.9
            )
        else:
            self.tree.add_step(
                DecisionStep.PROCEDURE_MATCHED,
                False,
                f"Procedure '{procedure}' not explicitly covered in policy",
                [],
                0.7
            )
    
    def _check_waiting_period(self, query_data: Dict[str, Any], 
                             policy_clauses: List[str]):
        """Check if waiting period requirements are met"""
        procedure = (query_data.get('procedure') or '').lower()
        policy_duration = int(query_data.get('policy_duration_months') or 0)
        
        # Define waiting periods for different procedures
        waiting_periods = {
            'cataract': 24,
            'cataract surgery': 24,
            'heart surgery': 24,
            'knee replacement': 24,
            'dental': 0,  # Dental has different rules
            'cosmetic': 0  # Cosmetic is usually excluded
        }
        
        required_waiting_period = 0
        for proc, period in waiting_periods.items():
            if proc in procedure:
                required_waiting_period = period
                break
        
        if required_waiting_period == 0:
            # No specific waiting period found
            self.tree.add_step(
                DecisionStep.WAITING_PERIOD_MET,
                True,
                f"No specific waiting period found for '{procedure}'",
                [],
                0.8
            )
        elif policy_duration >= required_waiting_period:
            self.tree.add_step(
                DecisionStep.WAITING_PERIOD_MET,
                True,
                f"Policy duration {policy_duration} months >= required {required_waiting_period} months",
                [],
                0.95
            )
        else:
            self.tree.add_step(
                DecisionStep.WAITING_PERIOD_NOT_MET,
                False,
                f"Policy duration {policy_duration} months < required {required_waiting_period} months",
                [],
                0.95
            )
    
    def _check_exclusions(self, query_data: Dict[str, Any], 
                         policy_clauses: List[str]):
        """Check if the procedure is excluded"""
        procedure = query_data.get('procedure', '').lower()
        
        # Define common exclusions
        exclusions = {
            'cosmetic': 'Cosmetic surgery is excluded unless reconstruction after accident',
            'dental': 'Dental treatment is excluded unless emergency due to accident',
            'experimental': 'Experimental treatments are excluded',
            'refractive': 'Refractive eye surgery is excluded unless medically necessary'
        }
        
        exclusion_found = False
        exclusion_reason = ""
        
        for exclusion_type, reason in exclusions.items():
            if exclusion_type in procedure:
                exclusion_found = True
                exclusion_reason = reason
                break
        
        if exclusion_found:
            self.tree.add_step(
                DecisionStep.EXCLUSION_FOUND,
                False,
                exclusion_reason,
                [],
                0.9
            )
        else:
            self.tree.add_step(
                DecisionStep.NO_EXCLUSION,
                True,
                f"No exclusions found for '{procedure}'",
                [],
                0.8
            )
    
    def _check_policy_status(self, query_data: Dict[str, Any], 
                           policy_clauses: List[str]):
        """Check if policy is active and valid"""
        policy_duration = int(query_data.get('policy_duration_months') or 0)
        
        if policy_duration > 0:
            self.tree.add_step(
                DecisionStep.POLICY_ACTIVE,
                True,
                f"Policy is active with {policy_duration} months duration",
                [],
                0.9
            )
        else:
            self.tree.add_step(
                DecisionStep.POLICY_ACTIVE,
                False,
                "Policy duration is invalid or zero",
                [],
                0.9
            )
    
    def _calculate_final_decision(self):
        """Calculate final decision based on reasoning tree"""
        # Count passed and failed steps
        passed_steps = sum(1 for node in self.tree.nodes if node.status)
        total_steps = len(self.tree.nodes)
        
        # Calculate confidence
        self.tree.calculate_overall_confidence()
        
        # Make decision based on passed steps
        if passed_steps == total_steps:
            self.tree.final_decision = "APPROVED"
        else:
            self.tree.final_decision = "REJECTED"
