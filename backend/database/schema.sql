-- ==============================================================================
-- InsureClaims: Normalized Relational Schema (3NF)
-- Compatible with MySQL and SQLite engines
-- ==============================================================================

-- 1. Claimants Table
CREATE TABLE IF NOT EXISTS claimants (
    id VARCHAR(36) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    contact VARCHAR(50),
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Policies Table (Foreign Key -> claimants)
CREATE TABLE IF NOT EXISTS policies (
    id VARCHAR(36) PRIMARY KEY,
    claimant_id VARCHAR(36) NOT NULL,
    policy_number VARCHAR(50) UNIQUE NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    duration_months INT NOT NULL,
    max_coverage_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claimant_id) REFERENCES claimants(id) ON DELETE CASCADE
);

-- 3. Claims Table (Foreign Key -> policies)
CREATE TABLE IF NOT EXISTS claims (
    id VARCHAR(36) PRIMARY KEY,
    policy_id VARCHAR(36) NOT NULL,
    procedure_name VARCHAR(150) NOT NULL,
    hospital_location VARCHAR(100),
    claimed_amount DECIMAL(12, 2) NOT NULL,
    file_id VARCHAR(64),
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (policy_id) REFERENCES policies(id) ON DELETE CASCADE
);

-- 4. Evaluations Table (Foreign Key -> claims)
CREATE TABLE IF NOT EXISTS evaluations (
    id VARCHAR(36) PRIMARY KEY,
    claim_id VARCHAR(36) NOT NULL,
    decision VARCHAR(20) NOT NULL,
    approved_amount DECIMAL(12, 2) NOT NULL,
    confidence_score DECIMAL(5, 4) NOT NULL,
    justification TEXT,
    retrieved_clauses TEXT,
    reasoning_tree TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE
);

-- 5. Audit Logs Table (Foreign Key -> evaluations)
CREATE TABLE IF NOT EXISTS audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    evaluation_id VARCHAR(36) NOT NULL,
    action VARCHAR(50) NOT NULL,
    performed_by VARCHAR(50) DEFAULT 'SYSTEM',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
);

-- Indexes for high-performance join operations
CREATE INDEX IF NOT EXISTS idx_policies_claimant ON policies(claimant_id);
CREATE INDEX IF NOT EXISTS idx_claims_policy ON claims(policy_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_claim ON evaluations(claim_id);
CREATE INDEX IF NOT EXISTS idx_audit_eval ON audit_logs(evaluation_id);
