"""
InsureClaims - Relational Database Manager & Multi-Join Retrieval Engine
Provides normalized data persistence, connection routing (MySQL with SQLite fallback),
and complex multi-join relational queries for insurance claims.
"""

import os
import sqlite3
import uuid
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_SQLITE_PATH = (
    "/tmp/insureclaims.db" if os.environ.get("VERCEL") else str(ROOT_DIR / "insureclaims.db")
)
SCHEMA_FILE = Path(__file__).resolve().parent / "schema.sql"


class DatabaseManager:
    """
    Manages normalized relational storage and multi-join query execution.
    Supports MySQL via DATABASE_URL/MYSQL_HOST or embedded SQLite.
    """

    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or os.environ.get("DATABASE_URL")
        self.is_mysql = bool(self.db_url and ("mysql" in self.db_url.lower()))
        self.sqlite_path = os.environ.get("DB_PATH", DEFAULT_SQLITE_PATH)
        self._init_schema()

    def get_connection(self):
        """Get an active database connection with row dictionary factories."""
        if self.is_mysql:
            try:
                import pymysql
                # Parse mysql://user:pass@host:port/dbname
                import urllib.parse
                parsed = urllib.parse.urlparse(self.db_url)
                conn = pymysql.connect(
                    host=parsed.hostname or "localhost",
                    user=parsed.username or "root",
                    password=parsed.password or "",
                    database=parsed.path.lstrip("/"),
                    port=parsed.port or 3306,
                    cursorclass=pymysql.cursors.DictCursor,
                    autocommit=True
                )
                return conn
            except Exception as e:
                print(f"⚠️ MySQL connection failed: {e}. Falling back to SQLite.")

        # SQLite connection
        conn = sqlite3.connect(self.sqlite_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_schema(self):
        """Execute DDL statements to set up normalized 3NF tables."""
        conn = self.get_connection()
        try:
            with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
                ddl = f.read()

            cursor = conn.cursor()
            # Split and execute individual statements
            statements = [s.strip() for s in ddl.split(";") if s.strip()]
            for stmt in statements:
                try:
                    cursor.execute(stmt)
                except Exception as ex:
                    # Ignore table already exists or index exists errors
                    pass
            if hasattr(conn, "commit"):
                conn.commit()
        finally:
            conn.close()

    # ─── Multi-Join Relational Queries ──────────────────────────────────────────

    def get_complete_claim_context(self, claim_id: str) -> Optional[Dict[str, Any]]:
        """
        Multi-join query spanning 4 normalized tables:
        CLAIMS -> POLICIES -> CLAIMANTS -> EVALUATIONS.
        Retrieves complete structured context for a specific claim.
        """
        query = """
        SELECT 
            c.id AS claim_id,
            c.procedure_name,
            c.claimed_amount,
            c.hospital_location,
            c.status AS claim_status,
            c.file_id,
            c.created_at AS claim_created_at,
            p.id AS policy_id,
            p.policy_number,
            p.plan_name,
            p.duration_months AS policy_duration_months,
            p.max_coverage_amount,
            cl.id AS claimant_id,
            cl.full_name AS claimant_name,
            cl.age AS claimant_age,
            cl.gender AS claimant_gender,
            cl.city AS claimant_city,
            e.id AS evaluation_id,
            e.decision,
            e.approved_amount,
            e.confidence_score,
            e.justification,
            e.reasoning_tree
        FROM claims c
        INNER JOIN policies p ON c.policy_id = p.id
        INNER JOIN claimants cl ON p.claimant_id = cl.id
        LEFT JOIN evaluations e ON e.claim_id = c.id
        WHERE c.id = ?;
        """
        conn = self.get_connection()
        try:
            param = (claim_id,)
            if self.is_mysql:
                query = query.replace("?", "%s")
            cursor = conn.cursor()
            cursor.execute(query, param)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
        finally:
            conn.close()

    def get_claimant_history_with_joins(self, claimant_id: str) -> List[Dict[str, Any]]:
        """
        Multi-join query retrieving full claims, policies, and decision history
        for a claimant to evaluate risk profiles and prior pre-existing claims.
        """
        query = """
        SELECT 
            cl.id AS claimant_id,
            cl.full_name,
            cl.age,
            p.policy_number,
            p.plan_name,
            p.duration_months,
            c.id AS claim_id,
            c.procedure_name,
            c.claimed_amount,
            c.hospital_location,
            c.status AS claim_status,
            e.decision,
            e.approved_amount,
            e.confidence_score,
            e.created_at AS evaluation_date
        FROM claimants cl
        INNER JOIN policies p ON cl.id = p.claimant_id
        INNER JOIN claims c ON p.id = c.policy_id
        LEFT JOIN evaluations e ON c.id = e.claim_id
        WHERE cl.id = ?
        ORDER BY c.created_at DESC;
        """
        conn = self.get_connection()
        try:
            param = (claimant_id,)
            if self.is_mysql:
                query = query.replace("?", "%s")
            cursor = conn.cursor()
            cursor.execute(query, param)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def save_complete_claim_record(
        self,
        claimant_data: Dict[str, Any],
        policy_data: Dict[str, Any],
        claim_data: Dict[str, Any],
        evaluation_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """
        Transactional multi-table insertion enforcing referential integrity:
        1. Insert/Update Claimants
        2. Insert/Update Policies (FK -> claimant)
        3. Insert Claims (FK -> policy)
        4. Insert Evaluations (FK -> claim)
        5. Insert Audit Log (FK -> evaluation)
        """
        conn = self.get_connection()
        claimant_id = claimant_data.get("id") or uuid.uuid4().hex
        policy_id = policy_data.get("id") or uuid.uuid4().hex
        claim_id = claim_data.get("id") or uuid.uuid4().hex
        evaluation_id = evaluation_data.get("id") or uuid.uuid4().hex
        audit_id = uuid.uuid4().hex

        try:
            cursor = conn.cursor()
            ph = "%s" if self.is_mysql else "?"

            # 1. Claimant
            cursor.execute(
                f"""INSERT OR IGNORE INTO claimants (id, full_name, age, gender, contact, city)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (
                    claimant_id,
                    claimant_data.get("name", "Policy Holder"),
                    claimant_data.get("age", 35),
                    claimant_data.get("gender", "male"),
                    claimant_data.get("contact", ""),
                    claimant_data.get("city", claim_data.get("location", "Mumbai")),
                ),
            )

            # 2. Policy
            cursor.execute(
                f"""INSERT OR IGNORE INTO policies (id, claimant_id, policy_number, plan_name, duration_months, max_coverage_amount, status)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (
                    policy_id,
                    claimant_id,
                    policy_data.get("policy_number", f"POL-{uuid.uuid4().hex[:8].upper()}"),
                    policy_data.get("plan_name", "Comprehensive Health Plan"),
                    policy_data.get("duration_months", claim_data.get("policy_duration_months", 12)),
                    policy_data.get("max_coverage_amount", 500000.0),
                    "ACTIVE",
                ),
            )

            # 3. Claim
            decision = evaluation_data.get("decision", "pending")
            claim_status = "APPROVED" if decision.lower() == "approved" else "REJECTED"
            cursor.execute(
                f"""INSERT INTO claims (id, policy_id, procedure_name, hospital_location, claimed_amount, file_id, status)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (
                    claim_id,
                    policy_id,
                    claim_data.get("procedure", "General Medical Claim"),
                    claim_data.get("location", "Mumbai"),
                    float(claim_data.get("claim_amount", 50000.0) or 50000.0),
                    claim_data.get("file_id", "default"),
                    claim_status,
                ),
            )

            # 4. Evaluation
            reasoning_str = (
                json.dumps(evaluation_data.get("reasoning_tree", {}))
                if isinstance(evaluation_data.get("reasoning_tree"), dict)
                else str(evaluation_data.get("reasoning_tree", ""))
            )
            clauses_str = json.dumps(evaluation_data.get("retrieved_chunks", []))
            cursor.execute(
                f"""INSERT INTO evaluations (id, claim_id, decision, approved_amount, confidence_score, justification, retrieved_clauses, reasoning_tree)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})""",
                (
                    evaluation_id,
                    claim_id,
                    decision.lower(),
                    float(evaluation_data.get("amount", 0.0) or 0.0),
                    float(evaluation_data.get("confidence_score", 0.9)),
                    evaluation_data.get("justification", ""),
                    clauses_str,
                    reasoning_str,
                ),
            )

            # 5. Audit Log
            cursor.execute(
                f"""INSERT INTO audit_logs (id, evaluation_id, action, performed_by, notes)
                    VALUES ({ph}, {ph}, {ph}, {ph}, {ph})""",
                (
                    audit_id,
                    evaluation_id,
                    "CLAIM_EVALUATED",
                    "INSURECLAIMS_RAG_ENGINE",
                    f"Decision: {decision.upper()}, Amount: ₹{evaluation_data.get('amount', 0)}",
                ),
            )

            if hasattr(conn, "commit"):
                conn.commit()

            return {
                "claimant_id": claimant_id,
                "policy_id": policy_id,
                "claim_id": claim_id,
                "evaluation_id": evaluation_id,
                "audit_id": audit_id,
            }
        finally:
            conn.close()


# Singleton instance
db_manager = DatabaseManager()
