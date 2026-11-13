import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="InsureClaims",
    description="AI-powered system for evaluating insurance claims using LangChain RAG & LLM reasoning",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "message": "InsureClaims Engine is running",
        "docs": "/docs",
        "endpoints": {
            "query": "/query/",
            "health": "/",
            "analyze": "/api/analyze",
            "stats": "/api/stats",
            "relational_context": "/api/claim/context/{claim_id}",
            "claimant_history": "/api/claimant/history/{claimant_id}"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "InsureClaims Engine v2.0"}
