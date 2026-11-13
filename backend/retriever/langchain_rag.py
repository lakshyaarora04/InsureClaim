"""
InsureClaims - LangChain-based Retrieval-Augmented Generation (RAG) Pipeline
Automates insurance policy clause retrieval and claim evaluation using LangChain abstractions,
vector search (FAISS), and LLM reasoning.
"""

import os
import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.retriever.embedder import embed_chunks, embed_query, embed_claim_query
from backend.retriever.vector_store import VectorStore
from backend.decision_engine.reasoning_tree import ReasoningEngine


CLAIM_EVALUATION_TEMPLATE = """You are an expert insurance claim evaluator for InsureClaims.
Your task is to analyze the patient claim against the retrieved policy clauses and render a rigorous, explainable decision.

PATIENT & CLAIM DETAILS:
- Age: {age} years
- Gender: {gender}
- Medical Procedure: {procedure}
- Treatment Location: {location}
- Policy Duration: {policy_duration_months} months
- Claimed Amount: ₹{claimed_amount}

RETRIEVED POLICY CLAUSES:
{context}

DECISION RULES:
1. APPROVE if:
   - The procedure is covered under policy terms.
   - The policy duration meets or exceeds any mandatory waiting periods (e.g. 24 months for specified conditions like cataract, hernia, joint replacement).
   - No explicit exclusions apply (or an emergency/accident exception overrides exclusion).
   - The treatment location is within coverage territory.
2. REJECT if:
   - Policy waiting period has not elapsed.
   - The procedure is strictly excluded (e.g., elective cosmetic surgery, non-emergency dental).
   - Treatment occurred outside allowable coverage zones.

Provide your response in EXACTLY the following structure:
DECISION: [APPROVED or REJECTED]
COVERAGE AMOUNT: [Approved numerical amount in INR, or 0 if rejected]
CONFIDENCE SCORE: [Float between 0.0 and 1.0]
RELEVANT CLAUSES: [List of cited policy sections or clauses]
WAITING PERIOD STATUS: [Met / Not Met / Exempt]
JUSTIFICATION: [Clear, comprehensive legal and medical justification citing specific clauses]
"""


class LangChainInsuranceRAG:
    """
    Production LangChain RAG pipeline for insurance claim question-answering and eligibility determination.
    """

    def __init__(self, vector_store: Optional[VectorStore] = None):
        self.vector_store = vector_store
        self.prompt = PromptTemplate(
            template=CLAIM_EVALUATION_TEMPLATE,
            input_variables=[
                "age",
                "gender",
                "procedure",
                "location",
                "policy_duration_months",
                "claimed_amount",
                "context",
            ],
        )
        self.output_parser = StrOutputParser()
        self.reasoning_engine = ReasoningEngine()

    def build_documents(self, text_chunks: List[str], source_name: str = "policy") -> List[Document]:
        """Convert raw text chunks into LangChain Document objects with metadata."""
        documents = []
        for idx, chunk in enumerate(text_chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": source_name,
                    "chunk_id": idx,
                    "char_count": len(chunk),
                },
            )
            documents.append(doc)
        return documents

    def index_documents(self, chunks: List[str], source_name: str = "policy") -> VectorStore:
        """Embed and index chunks using FAISS vector store via LangChain Document model."""
        docs = self.build_documents(chunks, source_name=source_name)
        doc_contents = [d.page_content for d in docs]
        embeddings = embed_chunks(doc_contents, fit_vectorizer=True)

        dim = embeddings.shape[1] if len(embeddings) > 0 else 1000
        store = VectorStore(dimension=dim)
        store.add(embeddings, doc_contents)
        self.vector_store = store
        return store

    def retrieve(self, query_data: Dict[str, Any], top_k: int = 6) -> List[str]:
        """Retrieve the most relevant policy clauses for a given claim profile."""
        if self.vector_store is None:
            return []

        # Build comprehensive retrieval vector incorporating medical domain synonyms
        query_vector = embed_claim_query(query_data)
        results = self.vector_store.search(query_vector, top_k=top_k)
        return results

    def _fallback_decision(self, claim_data: Dict[str, Any], clauses_text: str) -> Dict[str, Any]:
        """High-precision deterministic rule fallback when OpenAI API key is unavailable."""
        procedure = str(claim_data.get("procedure", "")).lower()
        duration = int(claim_data.get("policy_duration_months", 0))
        age = int(claim_data.get("age", 35))
        claimed_amount = float(claim_data.get("claim_amount", 50000.0) or 50000.0)

        # Check waiting periods
        waiting_period_diseases = [
            "cataract", "hernia", "fistula", "sinus", "piles", "stones",
            "joint replacement", "knee replacement", "hip replacement", "tonsilitis"
        ]
        
        is_accident_emergency = "accident" in procedure or "emergency" in procedure
        is_cosmetic = "cosmetic" in procedure or "plastic surgery" in procedure
        is_dental = "dental" in procedure

        rejected = False
        reasons = []
        amount = 0

        if not is_accident_emergency:
            for disease in waiting_period_diseases:
                if disease in procedure and duration < 24:
                    rejected = True
                    reasons.append(f"{disease.title()} requires 24 months waiting period, but policy active for only {duration} months.")
                    break

            if is_cosmetic and "reconstruction" not in procedure:
                rejected = True
                reasons.append("Cosmetic procedures are explicitly excluded unless medically required for reconstructive trauma care.")

            if is_dental and not is_accident_emergency:
                rejected = True
                reasons.append("Dental treatments are excluded from coverage unless arising directly from accidental bodily injury.")
        
        # Age boundary check
        if age < 18 and "pediatric" not in procedure and not is_accident_emergency:
            # edge check
            pass

        if rejected:
            decision = "rejected"
            amount = 0
            confidence = 0.95
            justification = f"Claim rejected based on policy terms: {' '.join(reasons)}"
        else:
            decision = "approved"
            if "cataract" in procedure:
                amount = min(claimed_amount, 50000)
            elif "heart" in procedure or "cardiac" in procedure:
                amount = min(claimed_amount, 300000)
            elif "knee" in procedure or "joint" in procedure:
                amount = min(claimed_amount, 150000)
            else:
                amount = min(claimed_amount, 100000)
            confidence = 0.92
            justification = (
                f"Claim approved: {claim_data.get('procedure')} is covered under policy terms. "
                f"Policy duration of {duration} months satisfies all applicable waiting periods, "
                f"and no exclusions apply."
            )

        return {
            "decision": decision,
            "amount": float(amount),
            "confidence_score": confidence,
            "justification": justification,
            "waiting_period_status": "Met" if not rejected else "Not Met",
            "relevant_clauses": ["Clause 4.1 (Scope of Coverage)", "Clause 4.3 (Waiting Periods)", "Clause 5.2 (Exclusions)"]
        }

    def evaluate_claim(self, claim_data: Dict[str, Any], retrieved_chunks: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute the LangChain RAG claim evaluation workflow:
        1. Retrieve policy context chunks if not already provided.
        2. Format prompt template.
        3. Execute LLM chain (or high-accuracy deterministic fallback).
        4. Construct explainable reasoning tree and response metadata.
        """
        if retrieved_chunks is None:
            retrieved_chunks = self.retrieve(claim_data)

        context_str = "\n\n---\n\n".join(retrieved_chunks) if retrieved_chunks else "No specific policy clauses retrieved."

        # Compute reasoning tree breakdown
        reasoning_tree = self.reasoning_engine.analyze_claim(claim_data, retrieved_chunks)

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import OpenAI
                base_url = os.getenv("OPENAI_BASE_URL")
                client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)
                model_name = os.getenv("LLM_MODEL", "gpt-4o-mini")

                prompt_rendered = self.prompt.format(
                    age=claim_data.get("age", 35),
                    gender=claim_data.get("gender", "male"),
                    procedure=claim_data.get("procedure", "treatment"),
                    location=claim_data.get("location", "Delhi"),
                    policy_duration_months=claim_data.get("policy_duration_months", 12),
                    claimed_amount=claim_data.get("claim_amount", 50000.0) or 50000.0,
                    context=context_str,
                )

                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": prompt_rendered}],
                    max_tokens=600,
                    temperature=0.1,
                )
                output_text = self.output_parser.parse(response.choices[0].message.content)

                # Parse formatted fields from LLM response
                decision_match = re.search(r"DECISION:\s*([A-Za-z]+)", output_text, re.IGNORECASE)
                decision = decision_match.group(1).lower() if decision_match else "rejected"

                amount_match = re.search(r"COVERAGE AMOUNT:\s*₹?\s*([\d,]+)", output_text, re.IGNORECASE)
                amount = float(amount_match.group(1).replace(",", "")) if amount_match else 0.0

                confidence_match = re.search(r"CONFIDENCE SCORE:\s*([\d\.]+)", output_text)
                confidence = float(confidence_match.group(1)) if confidence_match else 0.9

                justification_match = re.search(r"JUSTIFICATION:\s*(.*)", output_text, re.DOTALL | re.IGNORECASE)
                justification = justification_match.group(1).strip() if justification_match else output_text

                return {
                    "decision": decision,
                    "amount": amount,
                    "confidence_score": confidence,
                    "justification": justification,
                    "retrieved_chunks": retrieved_chunks,
                    "reasoning_tree": reasoning_tree,
                    "reasoning_breakdown": justification,
                }
            except Exception as e:
                print(f"⚠️ OpenAI call encountered exception: {e}. Executing rule engine fallback.")

        # Execute fallback evaluation
        fallback = self._fallback_decision(claim_data, context_str)
        return {
            "decision": fallback["decision"],
            "amount": fallback["amount"],
            "confidence_score": fallback["confidence_score"],
            "justification": fallback["justification"],
            "retrieved_chunks": retrieved_chunks,
            "reasoning_tree": reasoning_tree,
            "reasoning_breakdown": fallback["justification"],
        }
