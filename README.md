# 🛡️ InsureClaims

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-purple.svg)](https://www.langchain.com/)
[![React](https://img.shields.io/badge/React-18.2-blue.svg)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **End-to-End AI Insurance Claim Evaluation & Document Intelligence Platform**

InsureClaims is a full-stack, enterprise-grade AI system designed to automate insurance claim eligibility, policy verification, and adjudications. By pairing a **FastAPI** backend with a **LangChain-based Retrieval-Augmented Generation (RAG)** pipeline, a **normalized 3NF relational schema with multi-join retrieval queries**, and a modern **React/Tailwind** dashboard, InsureClaims delivers sub-2-second, explainable claim decisions with verifiable legal and policy justifications.

---

## 🌟 Key Capabilities

### 1. 🧠 LangChain-Powered Retrieval-Augmented Generation (RAG)
- **Semantic Document Ingestion**: Ingests and processes complex policy documents across standard formats (`.pdf`, `.docx`, `.txt`, `.html`).
- **Vector Search & Indexing**: Uses high-dimensional TF-IDF / semantic embeddings indexed in **FAISS** (`faiss-cpu`) for millisecond-level clause retrieval.
- **Explainable Decision Engine**: Combines retrieved policy clauses with patient claim parameters inside LangChain `PromptTemplate` and `StrOutputParser` chains, rendering structured decisions (APPROVED / REJECTED), coverage amount, confidence score, and human-readable reasoning trees.
- **Zero-Downtime Fallback**: Features a deterministic policy-compliance rule engine fallback when external LLM API keys are unavailable.

### 2. 🗄️ Normalized Relational Schema & Multi-Join Queries
- **3NF Relational Architecture**: Designed with strict referential integrity across 5 core entities:
  - `claimants` — Demographic profiles and patient identity.
  - `policies` — Policy numbers, plan tiers, coverage caps, and duration (FK $\to$ `claimants`).
  - `claims` — Claim submissions, procedures, hospital locations, and claimed amounts (FK $\to$ `policies`).
  - `evaluations` — RAG decision outcomes, approved amounts, confidence scores, and reasoning trees (FK $\to$ `claims`).
  - `audit_logs` — Immutable audit trails of adjuster overrides and evaluations (FK $\to$ `evaluations`).
- **Database Flexibility**: Native support for **MySQL** (`mysql+pymysql`) and zero-configuration **SQLite** (`PRAGMA foreign_keys = ON;`).
- **Multi-Join Retrieval Queries**: Executes complex 4-table `INNER JOIN` queries (`claims` $\Join$ `policies` $\Join$ `claimants` $\Join$ `evaluations`) for comprehensive historical context and fraud/risk profiling.

### 3. 🧪 Data Validation & Synthetic Data Generation Workflows
- **Pydantic V2 Validation**: Validates incoming claim payloads against strong bounds (age verification, standardized medical procedures, policy duration, location checks).
- **Synthetic Edge-Case Generator**: Automated generator producing realistic synthetic policies and edge-case claim scenarios:
  - Waiting period boundaries (e.g. 23 months vs 24 months for specified conditions like Cataract or Joint Replacements).
  - Cosmetic surgery exclusions vs post-accident trauma reconstruction exceptions.
  - Emergency cardiovascular interventions overriding standard waiting periods.
  - Accidental dental trauma overrides vs routine dental cleaning exclusions.
- **Automated Validation Workflow**: Includes `scripts/run_synthetic_workflow.py` to evaluate edge cases against ground-truth benchmarks.

### 4. 💻 Modern Full-Stack Web Dashboard
- **React 18 + Tailwind CSS**: Real-time Claim Analyzer with dynamic confidence gauges, policy document manager, live analytics, and adjuster override dashboards.
- **RESTful API**: Document uploads, natural language claim parsing, audit reports, and multi-join context inspection.

---

## 🏗️ Architecture Overview

```
                      ┌───────────────────────────────────────────┐
                      │        InsureClaims React Frontend        │
                      └─────────────────────┬─────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                      ┌───────────────────────────────────────────┐
                      │              FastAPI Backend              │
                      └───────┬───────────────────────────┬───────┘
                              │                           │
          LangChain RAG Flow  │                           │ Relational DB Flow
                              ▼                           ▼
            ┌──────────────────────────────────┐ ┌──────────────────────────────────┐
            │   LangChain RAG Pipeline         │ │   Normalized Relational DB (3NF) │
            │ ┌──────────────────────────────┐ │ │ ┌──────────────────────────────┐ │
            │ │ LangChain Document Ingestion │ │ │ │ claimants ──< policies       │ │
            │ ├──────────────────────────────┤ │ │ │                    │         │ │
            │ │ FAISS Vector Similarity      │ │ │ │                 claims       │ │
            │ ├──────────────────────────────┤ │ │ │                    │         │ │
            │ │ PromptTemplate + OutputParser│ │ │ │               evaluations    │ │
            │ ├──────────────────────────────┤ │ │ │                    │         │ │
            │ │ OpenAI GPT-3.5 / Rule Engine │ │ │ │                audit_logs    │ │
            │ └──────────────────────────────┘ │ │ └──────────────────────────────┘ │
            │       ▲                          │ │  Multi-Join Retrieval Queries    │
            │       │ Documents (PDF, DOCX)    │ │  (claims ⋈ policies ⋈ claimants) │
            │ ┌─────┴────────────────────────┐ │ └──────────────────────────────────┘
            │ │ Policy Document Store        │ │
            │ └──────────────────────────────┘ │
            └──────────────────────────────────┘
```

---

## 📁 Repository Structure

```
InsureClaims/
├── backend/
│   ├── api/
│   │   ├── main.py                   # FastAPI application initialization & routing
│   │   ├── routes.py                 # Core API endpoints (Analyze, Query, Upload, Stats)
│   │   └── models.py                 # API request/response schemas
│   ├── database/
│   │   ├── schema.sql                # 3NF relational schema DDL (MySQL/SQLite compatible)
│   │   └── db_manager.py             # Database manager & multi-join query engine
│   ├── retriever/
│   │   ├── langchain_rag.py          # LangChain RAG pipeline (FAISS + Prompts + Evaluator)
│   │   ├── embedder.py               # Medical semantic query enrichment & TF-IDF
│   │   └── vector_store.py           # FAISS vector store wrapper
│   ├── decision_engine/
│   │   ├── evaluator.py              # Claim evaluation logic & waiting period checker
│   │   ├── llm_decision.py           # LLM reasoning & prompt engineering
│   │   └── reasoning_tree.py         # Visual reasoning tree generator
│   ├── validation/
│   │   └── claim_validator.py        # Pydantic V2 validation schemas
│   ├── data_generator/
│   │   └── synthetic_generator.py    # Synthetic edge cases & multi-format doc generator
│   └── utils/
│       ├── document_reader.py        # Multi-format document parser (PDF, DOCX, TXT, HTML)
│       └── chunker.py                # Sliding window text chunker
├── frontend/                         # React 18 frontend dashboard
│   ├── src/                          # UI components (ClaimAnalyzer, Analytics, Navbar)
│   └── public/                       # HTML assets and icons
├── scripts/
│   └── run_synthetic_workflow.py     # Automated synthetic data & edge-case test workflow
├── documents/                        # Sample policy documents (PDF)
├── requirements.txt                  # Python dependencies
└── vercel.json                       # Vercel serverless deployment config
```

---

## 🚀 Quickstart Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) OpenAI API key for live GPT-3.5 evaluations

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/lakshyaarora04/ai-insurance-analyzer.git
cd ai-insurance-analyzer

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Start FastAPI server
python run_server.py
```
Backend will be available at: `http://localhost:8000` (Interactive Swagger docs: `http://localhost:8000/docs`).

### 2. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start React development server
npm start
```
Frontend will be live at: `http://localhost:3000`.

---

## 🧪 Testing & Validation

### Run Synthetic Data & Edge-Case Workflow
```bash
python scripts/run_synthetic_workflow.py
```
This script:
1. Generates synthetic policy documents in JSON, HTML, and TXT formats.
2. Indexes clauses into the LangChain RAG pipeline with FAISS.
3. Tests 8 boundary edge cases (waiting periods, exclusions, accident overrides).
4. Persists results transactionally into the normalized relational database.
5. Executes multi-join queries to verify referential integrity.

---

## 📡 API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Health check & system status |
| `POST` | `/api/analyze` | Natural language claim analysis via LangChain RAG |
| `POST` | `/query/` | Structured claim evaluation against indexed document |
| `POST` | `/upload/` | Ingest and chunk policy documents (PDF, DOCX, TXT, HTML) |
| `GET` | `/api/claim/context/{claim_id}` | Multi-join query across 4 normalized tables |
| `GET` | `/api/claimant/history/{claimant_id}`| Multi-join query for claimant policy & claims history |
| `POST` | `/api/feedback` | Log adjuster override / feedback |
| `GET` | `/api/analytics` | Aggregated claim performance metrics |

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
