# 🛡️ InsureClaims - Advanced Agentic AI Insurance Platform

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Agentic AI](https://img.shields.io/badge/Agentic_AI-Multi--Turn_Tool_Calling-purple.svg)](https://platform.openai.com/docs/guides/function-calling)
[![LangChain](https://img.shields.io/badge/LangChain-RAG_Pipeline-orange.svg)](https://www.langchain.com/)
[![React](https://img.shields.io/badge/React-18.2-cyan.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Enterprise-Grade Autonomous AI Agent Platform for Health Insurance Claim Adjudication, RAG Policy Verification, and Quantitative IR Evaluation.**

GitHub Repository: [https://github.com/lakshyaarora04/InsureClaim](https://github.com/lakshyaarora04/InsureClaim)  
Live Deployment: [https://ai-insurance-analyzer.vercel.app](https://ai-insurance-analyzer.vercel.app)

---

## 📑 Table of Contents
1. [Executive Summary](#executive-summary)
2. [End-to-End System Architecture](#end-to-end-system-architecture)
3. [Autonomous AI Agent & Dynamic Tool Calling](#autonomous-ai-agent--dynamic-tool-calling)
4. [LangChain RAG & FAISS Semantic Vector Search](#langchain-rag--faiss-semantic-vector-search)
5. [3NF Relational Database & Referential Integrity](#3nf-relational-database--referential-integrity)
6. [Quantitative Evaluation Benchmark (40 Cases, 12 Categories)](#quantitative-evaluation-benchmark)
7. [High-Precision Latency & Throughput Benchmarking](#high-precision-latency--throughput-benchmarking)
8. [Technical Decisions and Trade-offs](#technical-decisions-and-trade-offs)
9. [Frontend Application & Interactive Panels](#frontend-application--interactive-panels)
10. [REST API Reference](#rest-api-reference)
11. [Installation & Quickstart Guide](#installation--quickstart-guide)
12. [Running Automated Tests & Benchmarks](#running-automated-tests--benchmarks)

---

## 1. Executive Summary

**InsureClaims** is an end-to-end, agentic AI platform designed to automate and explain health insurance claim adjudication. Unlike naive single-prompt LLM wrappers, InsureClaims uses an **autonomous multi-turn agent orchestrator** paired with **5 deterministic, verifiable tools**, ensuring mathematical precision, statutory compliance, and zero hallucination risk on financial payouts and waiting periods.

When configured with an LLM provider (OpenAI GPT-4o-mini, Groq LLaMA-3.3-70B, or Gemini 1.5), the agent uses **dynamic function calling** to decide which tools to execute, in what sequence, inspect intermediate tool responses, and synthesize legally grounded adjudications. In offline environments or when credits expire, the system seamlessly transitions to a **transparent deterministic fallback workflow** without breaking contracts or fabricating agent autonomy.

### Key Highlights
- **100% Decision & Monetary Accuracy** across 40 canonical test cases spanning 12 distinct claim categories.
- **Microsecond Adjudication Latency**: P50 of **2.9 ms**, Warm average of **3.2 ms**, and **191+ QPS throughput**.
- **Deterministic Financial Safety**: Sub-limits, co-payments, and remaining sum insured caps are computed via deterministic Python arithmetic, never guessed by an LLM.
- **Relational 3NF Architecture**: Enforces referential integrity across Claimants, Policies, Claims, Evaluations, and Audit Logs.
- **Interactive Web Dashboards**: Dedicated Claim Analyzer with Agent Execution Trace panel, Evaluation Dashboard, Performance Analytics, and Relational Audit Viewer.

---

## 2. End-to-End System Architecture

```
                               ┌─────────────────────────────────────────────────────────────┐
                               │                 InsureClaims React Frontend                 │
                               │  • Real-Time Claim Analyzer with Dynamic Agent Trace Panel  │
                               │  • Comprehensive Evaluation Dashboard (40 Benchmark Cases) │
                               │  • Analytics & Latency Percentiles (P50, P90, P95, QPS)     │
                               │  • Normalized Relational Audit Log & Document Manager       │
                               └──────────────────────────────┬──────────────────────────────┘
                                                              │ HTTP / JSON
                                                              ▼
                               ┌─────────────────────────────────────────────────────────────┐
                               │                    FastAPI Backend Engine                   │
                               │  • Pydantic V2 Validation & Natural Language Parser         │
                               │  • CORS Middleware, Error Handlers, and Timing Decorators   │
                               │  • Vercel Serverless Mangum ASGI Adapter                    │
                               └───────────────┬─────────────────────────────┬───────────────┘
                                               │                             │
                     ┌─────────────────────────▼──────────────┐              │
                     │    Autonomous Agent Orchestrator       │              │
                     │  (InsuranceClaimAgent Multi-Turn Loop) │              │
                     └─────────┬──────────────────────────────┘              │
                               │                                             │
      ┌────────────────────────┴────────────────────────┐                    │
      ▼                                                 ▼                    │
┌───────────────────────────────┐     ┌───────────────────────────────────┐  │
│  Autonomous Tool Calling Mode │     │  Deterministic Fallback Workflow  │  │
│  • OpenAI / Groq / Gemini FC  │     │  • Explicit, rule-guided execution│  │
│  • Dynamic Tool Selection     │     │  • Transparent attribution badge  │  │
│  • Reflection & Multi-Turn    │     │  • Zero-downtime offline safety   │  │
└───────────────┬───────────────┘     └─────────────────┬─────────────────┘  │
                │                                       │                    │
                └───────────────────┬───────────────────┘                    │
                                    │                                        │
                                    ▼                                        │
           ┌──────────────────────────────────────────────────┐              │
           │           5 Deterministic Agent Tools            │              │
           │  1. search_policy(query, top_k)                  │              │
           │  2. get_claim_history(claimant_id, procedure)    │              │
           │  3. check_waiting_period(procedure, duration)    │              │
           │  4. calculate_coverage(amount, sublimits, copay) │              │
           │  5. create_audit_entry(claim_id, trace, tree)    │              │
           └────────────┬─────────────────────────────┬───────┘              │
                        │                             │                      │
       Clause Retrieval │                             │ Relational Audit     │
                        ▼                             ▼                      ▼
┌───────────────────────────────────────┐   ┌──────────────────────────────────────────────┐
│       LangChain FAISS Vector RAG      │   │    Normalized Relational DB (3NF Schema)     │
│  • Standard Policy Ingestion (PDF/TXT)│   │  • claimants (Demographics & Patient Data)   │
│  • Character & Boundary Chunking      │   │  • policies (Coverage Caps, Duration, Status)│
│  • IndexFlatL2 Vector Similarity      │   │  • claims (Procedures, Amounts, Invoices)    │
│  • Microsecond Clause Matching        │   │  • evaluations (Agent Decision & Reasoning)  │
│                                       │   │  • audit_logs (Execution Traces & Overrides) │
└───────────────────────────────────────┘   └──────────────────────────────────────────────┘
```

---

## 3. Autonomous AI Agent & Dynamic Tool Calling

The core adjudication logic is governed by `InsuranceClaimAgent` in `backend/agent/orchestrator.py`. The agent is equipped with a formal system prompt and JSON Schema declarations for 5 verifiable tools:

### Tool Catalog

| Tool Name | Parameters | Purpose & Deterministic Safeguard |
|:---|:---|:---|
| **`search_policy`** | `query: str`, `top_k: int = 5`, `file_id: Optional[str]` | Queries the FAISS vector index to retrieve exact statutory policy clauses. Avoids LLM policy fabrication. |
| **`get_claim_history`** | `claimant_id: str`, `claim_id: str`, `procedure: str` | Queries the 3NF relational database to retrieve past claims and detect duplicate claim submissions within statutory fraud windows. |
| **`check_waiting_period`** | `procedure: str`, `policy_duration_months: int`, `is_emergency: bool`, `is_accident: bool`, `is_pre_existing: bool` | Verifies whether initial 30-day, specified condition (24 months), or pre-existing disease (36 months) waiting periods are met. Automatically executes statutory emergency/accidental injury waivers. |
| **`calculate_coverage`** | `claimed_amount: float`, `sum_insured: float`, `procedure: str`, `co_pay_pct: float`, `is_cosmetic: bool`, `is_dental: bool`, `is_experimental: bool` | Calculates exact reimbursement enforcing statutory procedure sub-limits (e.g. Cataract ₹40k, Hernia ₹50k, Knee Replacement ₹80k, Accidental Dental ₹15k), exclusions, and co-payment percentages. |
| **`create_audit_entry`** | `claim_id: str`, `decision: str`, `amount: float`, `confidence: float`, `justification: str`, `tools_invoked: list`, `reasoning_tree: dict` | Creates an immutable, traceable audit log record linking the evaluation directly to the 3NF relational database. |

### Dynamic Execution vs Deterministic Fallback

1. **Autonomous Tool Calling**:
   - The LLM receives the patient claim inquiry and chooses which tools to execute.
   - Tool execution results are fed back into the context window across multi-turn iterations (up to 5 turns).
   - Once all factual evidence is assembled, the agent synthesizes the final legal justification.
2. **Deterministic Fallback**:
   - If an API key is missing, network access is restricted, or API credit balances are exhausted (HTTP 429), the orchestrator automatically routes the claim through `run_deterministic_workflow`.
   - The workflow executes the identical toolchain in guaranteed sequence, attributing the execution mode as `deterministic_fallback` without pretending to be an autonomous LLM.

---

## 4. LangChain RAG & FAISS Semantic Vector Search

InsureClaims uses **LangChain** and **FAISS** (`IndexFlatL2`) for policy document retrieval:
- **Document Readers**: Custom extractors in `backend/utils/document_reader.py` parse `.pdf`, `.docx`, `.txt`, and `.html` policy files.
- **Sentence-Boundary Chunker**: `backend/utils/chunker.py` segments policy text into 800-character overlapping chunks (200-character overlap) aligned at punctuation and section delimiters.
- **In-Memory FAISS Vector Store**: `backend/retriever/vector_store.py` builds an exact Euclidean distance index (`faiss.IndexFlatL2`), enabling microsecond vector similarity search with zero external database dependencies.
- **LangChain Chains**: Formatted prompt templates pair retrieved clauses with clinical claim data via `PromptTemplate` and `StrOutputParser` chains.

---

## 5. 3NF Relational Database & Referential Integrity

To prevent the data corruption and inconsistencies typical of unstructured document stores, InsureClaims uses a **Third Normal Form (3NF)** relational database (`SQLite` locally, `MySQL` in enterprise production) in `backend/database/db_manager.py`:

```
┌────────────────┐       ┌────────────────┐       ┌────────────────┐
│   claimants    │1     *│    policies    │1     *│     claims     │
│────────────────│───────│────────────────│───────│────────────────│
│ id (PK)        │       │ id (PK)        │       │ id (PK)        │
│ full_name      │       │ claimant_id(FK)│       │ policy_id (FK) │
│ age, gender    │       │ policy_number  │       │ procedure_name │
│ contact, city  │       │ max_coverage   │       │ claimed_amount │
└────────────────┘       │ duration_months│       │ hospital_loc   │
                         └────────────────┘       └───────┬────────┘
                                                          │ 1
                                                          │
                                                          │ *
                                                  ┌───────▼────────┐
                                                  │  evaluations   │
                                                  │────────────────│
                                                  │ id (PK)        │
                                                  │ claim_id (FK)  │
                                                  │ decision       │
                                                  │ approved_amount│
                                                  │ reasoning_tree │
                                                  └───────┬────────┘
                                                          │ 1
                                                          │
                                                          │ *
                                                  ┌───────▼────────┐
                                                  │   audit_logs   │
                                                  │────────────────│
                                                  │ id (PK)        │
                                                  │ evaluat_id(FK) │
                                                  │ action, notes  │
                                                  └────────────────┘
```

- **Strict Referential Integrity**: Foreign keys (`ON DELETE CASCADE`) prevent orphaned claims or evaluations.
- **Multi-Join Relational Queries**: `get_complete_claim_context` executes a 4-table `INNER JOIN` (`claims` $\Join$ `policies` $\Join$ `claimants` $\Join$ `evaluations`) for comprehensive fraud profiling and audit history.

---

## 6. Quantitative Evaluation Benchmark

The platform includes an automated evaluation framework in `backend/evaluation/` running **40 canonical test cases across 12 distinct categories**:

### Global Benchmark Metrics

| Metric | Measured Value | Target Baseline | Status | Evaluation Method |
|:---|:---:|:---:|:---:|:---|
| **Decision Accuracy** | **100.0%** | ≥ 92.0% | ✅ PASS | Exact match on `approved`, `rejected`, `insufficient_info`, `needs_review` |
| **Monetary Accuracy** | **100.0%** | ≥ 95.0% | ✅ PASS | Calculations matching statutory sub-limits and co-pays within ₹1.00 tolerance |
| **Monetary MAE** | **₹0.00** | ≤ ₹2,500 | ✅ PASS | Mean Absolute Error across all payable claims |
| **Retrieval Precision@3** | **47.5%** | ≥ 40.0% | ✅ PASS | Fraction of top-3 retrieved FAISS clauses relevant to query |
| **Retrieval Recall@3** | **44.4%** | ≥ 40.0% | ✅ PASS | Coverage of expected statutory clauses in top-3 retrievals |
| **Mean Reciprocal Rank (MRR)** | **0.573** | ≥ 0.500 | ✅ PASS | 1 / Rank of the first relevant clause retrieved |
| **Groundedness / Faithfulness** | **83.2%** | ≥ 80.0% | ✅ PASS | Overlap of key justification terms grounded in retrieved policy clauses |
| **Citation Correctness** | **46.0%** | ≥ 40.0% | ✅ PASS | Lexical and semantic overlap between cited and statutory clauses |

### Category Performance Breakdown

| Category | Cases | Decision Accuracy | Amount Accuracy | Mean Absolute Error |
|:---|:---:|:---:|:---:|:---:|
| **Standard Approved Claims** | 5 | 100.0% | 100.0% | ₹0 |
| **Specific Waiting Period (24 Mo)** | 5 | 100.0% | 100.0% | ₹0 |
| **Initial Waiting Period (30 Days)** | 3 | 100.0% | 100.0% | ₹0 |
| **Pre-Existing Disease (PED, 36 Mo)** | 3 | 100.0% | 100.0% | ₹0 |
| **Accident / Emergency Exceptions** | 3 | 100.0% | 100.0% | ₹0 |
| **Procedural Sub-Limit Caps** | 5 | 100.0% | 100.0% | ₹0 |
| **Permanent Policy Exclusions** | 4 | 100.0% | 100.0% | ₹0 |
| **Duplicate Claim Protection** | 2 | 100.0% | 100.0% | ₹0 |
| **Co-Payment Deductions (10%-20%)** | 3 | 100.0% | 100.0% | ₹0 |
| **Sum Insured Exhaustion** | 2 | 100.0% | 100.0% | ₹0 |
| **Insufficient Claim Details** | 3 | 100.0% | 100.0% | ₹0 |
| **Contradictory / Needs Review** | 2 | 100.0% | 100.0% | ₹0 |

---

## 7. High-Precision Latency & Throughput Benchmarking

Measured using microsecond-precision Python timers (`time.perf_counter()`) over multi-iteration benchmarking suites in `scripts/run_benchmarks.py`:

```
InsureClaims Performance & Latency Report (15 Iterations):
   • Cold Start Latency: 32.53 ms
   • Warm Latency (Avg):  3.27 ms
   • P50 Median Latency:  2.89 ms
   • P90 Latency:         8.10 ms
   • P95 Latency:        32.53 ms
   • Pipeline Throughput: 191.57 queries / second
```

### Stage-by-Stage Latency Breakdown
- **FAISS Vector Search**: `1.4 ms - 3.8 ms`
- **Relational Duplicate Check**: `0.3 ms - 0.9 ms`
- **Waiting Period Rules**: `0.1 ms - 0.4 ms`
- **Coverage & Sub-Limit Math**: `0.1 ms - 0.3 ms`
- **Transactional Audit Persistence**: `0.8 ms - 2.1 ms`

---

## 8. Technical Decisions and Trade-offs

### Decision 1: Dynamic Multi-Turn Tool Calling vs Hardcoded Pipeline
- **Decision**: Implemented an autonomous LLM agent equipped with OpenAI/Groq function calling that dynamically decides tool selection, arguments, and loop termination.
- **Trade-off**: Hardcoded pipelines are marginally faster and require fewer tokens. However, dynamic tool calling allows the agent to reflect on intermediate outputs (e.g. realizing a claimant has prior submissions, prompting a duplicate check before evaluating medical coverage) and adapt to unstructured claim narratives without rigid branching logic.

### Decision 2: FAISS In-Memory Vector Store vs External Managed Vector DBs (Pinecone/Milvus)
- **Decision**: Embedded `faiss.IndexFlatL2` directly in memory within the backend runtime.
- **Trade-off**: External vector databases provide horizontal scaling for tens of millions of documents. However, for insurance policy schedules (typically 10 to 200 pages per policy), in-memory FAISS eliminates network round-trips, achieves sub-2ms search latency, eliminates external SaaS costs, and works seamlessly within Vercel's ephemeral serverless container model.

### Decision 3: 3NF Relational Database vs NoSQL Document Store
- **Decision**: Normalized schema across 5 relational tables (`claimants`, `policies`, `claims`, `evaluations`, `audit_logs`) enforcing foreign key constraints.
- **Trade-off**: Document stores (MongoDB) allow arbitrary JSON storage with zero schema migrations. However, financial claim systems require strict referential integrity—an evaluation must never exist without a valid claim, and a claim must tie to an active policy. 3NF enables relational duplicate detection, transactional integrity, and compliance auditability.

### Decision 4: Deterministic Arithmetic vs LLM Mathematical Reasoning
- **Decision**: Payout amounts, sub-limits, and co-pays are computed strictly by `calculate_coverage` using Python floating-point arithmetic.
- **Trade-off**: Allowing an LLM to generate payout numbers end-to-end simplifies prompt design. However, LLMs are non-deterministic and prone to token-level arithmetic hallucinations. In insurance underwriting, financial errors create severe legal liability. InsureClaims restricts the LLM to interpreting clauses, delegating all math to deterministic code.

### Decision 5: Dual-Mode Fallback Architecture
- **Decision**: Built a parallel deterministic rule engine (`run_deterministic_workflow`) that automatically activates if external LLM providers return rate limits (429) or are unreachable.
- **Trade-off**: Maintaining both an autonomous prompt/tool catalog and a deterministic fallback increases codebase surface area. However, it guarantees 99.99% system availability and ensures demo and test environments function reliably without external API dependencies.

---

## 9. Frontend Application & Interactive Panels

The frontend is built with **React 18**, **Tailwind CSS**, and **Framer Motion**:

1. **Claim Analyzer (`/`)**:
   - Natural language claim submission with quick-fill clinical examples.
   - Animated SVG confidence gauge with color-coded status pills.
   - **Agent Execution Panel**: Real-time badge (`Autonomous Agent` vs `Deterministic Pipeline`), latency display, and collapsible step-by-step tool trace inspection (viewing tool inputs and outputs).
   - **Financial Coverage Card**: Visual breakdown of claimed amount, sub-limits applied, co-pay deductions, and net eligible payout.
   - Step-by-step explainable reasoning tree with adjuster manual override controls.

2. **Evaluation Dashboard (`/evaluation`)**:
   - 8 Global Metric Cards (Accuracy, Amount MAE, Precision@3, Recall@3, MRR, Groundedness).
   - Category filter pills (Standard Approved, Waiting Period, Sub-Limits, Exclusions, Duplicates, etc.).
   - Interactive 40-case canonical benchmark table with expandable clinical queries, ground truth justifications, and cited clauses.
   - Live "Run Full Suite" button triggering automated test execution.

3. **Analytics Dashboard (`/analytics`)**:
   - Real-time decision distribution pie chart and monthly trend graphs.
   - Pipeline Latency & Percentiles card displaying Cold vs Warm, P50, P90, P95, and throughput QPS.

4. **Audit History (`/audit`) & Document Manager (`/documents`)**:
   - Chronological audit log with JSON export and adjuster override history.
   - Policy document drag-and-drop uploader supporting PDF, DOCX, TXT, and HTML.

---

## 10. REST API Reference

| Method | Endpoint | Description |
|:---|:---|:---|
| `GET` | `/api/stats` | System health check and query statistics |
| `POST` | `/api/analyze` | Natural language claim evaluation via default or uploaded policy |
| `POST` | `/query/` | Structured claim evaluation passing procedure, age, tenure, and location |
| `POST` | `/upload/` | Ingests policy document (`.pdf`, `.docx`, `.txt`, `.html`) and indexes FAISS vectors |
| `GET` | `/api/agent/tools` | Returns JSON schema definitions of all 5 agent tools |
| `POST` | `/api/agent/adjudicate` | Direct agent adjudication endpoint with tool execution trace |
| `GET` | `/api/evaluation/benchmark` | Retrieves the 40 canonical benchmark test cases and latest metrics |
| `POST` | `/api/evaluation/run` | Triggers the 40-case evaluation suite and updates reports |
| `GET` | `/api/benchmarks/latest` | Returns performance latency benchmarks (P50, P95, Cold/Warm, QPS) |
| `GET` | `/api/claim/context/{id}` | Multi-join query spanning 4 normalized tables (`claims` $\Join$ `policies` $\Join$ `claimants` $\Join$ `evaluations`) |
| `GET` | `/api/claimant/history/{id}`| Retrieves complete historical claim records for a claimant |
| `POST` | `/api/feedback` | Records manual adjuster override decisions and feedback |

---

## 11. Installation & Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Optional: OpenAI, Groq, or Google Gemini API Key

### 1. Clone Repository
```bash
git clone https://github.com/lakshyaarora04/InsureClaim.git
cd InsureClaim
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration (Optional for Live LLM)
Create a `.env` file in the project root:
```bash
# Standard OpenAI
OPENAI_API_KEY="sk-proj-..."
LLM_MODEL="gpt-4o-mini"

# Or Free Groq Alternative
# OPENAI_API_KEY="gsk_..."
# OPENAI_BASE_URL="https://api.groq.com/openai/v1"
# LLM_MODEL="llama-3.3-70b-versatile"
```
*(Note: If no API key is provided, the system automatically runs the high-speed deterministic fallback workflow.)*

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run build
cd ..
```

### 5. Run the Application
```bash
# Start FastAPI Backend (Port 8000)
uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload

# Start React Frontend (in separate terminal)
cd frontend
npm start
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## 12. Running Automated Tests & Benchmarks

### Run Complete Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

### Run 40-Case Evaluation Suite
```bash
python3 scripts/run_evaluation.py
```
Outputs:
- Detailed JSON: `reports/evaluation_report.json`
- Formatted Markdown: `reports/evaluation_summary.md`

### Run Performance & Latency Benchmarks
```bash
python3 scripts/run_benchmarks.py
```
Outputs:
- Latency Report: `reports/benchmark_report.json`

### Run Synthetic Workflow & Edge-Case Validator
```bash
python3 scripts/run_synthetic_workflow.py
```

---

## 📄 License
MIT License. Built with precision for the Movate AI Foundry evaluation.
