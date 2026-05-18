import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import router

app = FastAPI(
    title="LLM Insurance Claim Evaluation System",
    description="AI-powered system for evaluating insurance claims using LLM reasoning",
    version="1.0.0"
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
        "message": "LLM Insurance Claim Evaluation System is running",
        "docs": "/docs",
        "endpoints": {
            "query": "/query/",
            "health": "/"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "system": "LLM Insurance Claim Evaluator"}
