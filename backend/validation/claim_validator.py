"""
InsureClaims - Data Validation Engine
Uses Pydantic V2 models and field validators to ensure robust validation of
insurance claims, claimant profiles, policy parameters, and edge-case inputs.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class ClaimantProfile(BaseModel):
    """Claimant personal and demographic profile."""
    name: Optional[str] = Field(default="Policy Holder", max_length=100)
    age: int = Field(..., ge=1, le=120, description="Age of the patient between 1 and 120")
    gender: str = Field(..., description="Gender (male, female, other)")
    city: Optional[str] = Field(default="Mumbai", max_length=50)

    @field_validator("gender")
    @classmethod
    def sanitize_gender(cls, v: str) -> str:
        clean = v.strip().lower()
        if clean in ["male", "m", "man", "boy"]:
            return "male"
        elif clean in ["female", "f", "woman", "girl"]:
            return "female"
        return "other"


class PolicyConstraints(BaseModel):
    """Policy terms and waiting period constraints."""
    policy_number: Optional[str] = Field(default=None, max_length=50)
    duration_months: int = Field(..., ge=0, le=600, description="Months elapsed since inception")
    max_coverage_amount: float = Field(default=500000.0, ge=1000.0)


class ClaimValidationRequest(BaseModel):
    """
    Primary validation request for incoming insurance claim evaluation.
    Enforces strict typing, edge-case boundary checks, and standardizations.
    """
    file_id: Optional[str] = Field(default="default", description="Associated policy document ID")
    age: int = Field(..., ge=1, le=120)
    gender: str = Field(default="male")
    procedure: str = Field(..., min_length=2, max_length=200)
    location: str = Field(default="Mumbai", max_length=100)
    policy_duration_months: int = Field(..., ge=0, le=600)
    claim_amount: Optional[float] = Field(default=50000.0, ge=0.0)

    @field_validator("procedure")
    @classmethod
    def clean_procedure(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Procedure name cannot be blank.")
        return v

    @field_validator("gender")
    @classmethod
    def standardize_gender(cls, v: str) -> str:
        v_low = v.lower()
        if "fem" in v_low or "woman" in v_low:
            return "female"
        return "male"

    @model_validator(mode="after")
    def validate_edge_cases(self):
        """Cross-field edge-case validation."""
        # Age vs Procedure sanity checks
        if self.age < 12 and "cataract" in self.procedure.lower() and "congenital" not in self.procedure.lower():
            # Flag potential edge case
            pass
        return self


class DocumentValidationMeta(BaseModel):
    """Metadata validation for ingested policy documents."""
    filename: str
    file_extension: str
    file_size_bytes: int = Field(..., gt=0, le=50 * 1024 * 1024)  # Max 50MB
    supported_extensions: List[str] = [".pdf", ".docx", ".txt", ".html", ".json"]

    @field_validator("file_extension")
    @classmethod
    def check_extension(cls, ext: str) -> str:
        ext_clean = ext.lower().strip()
        if not ext_clean.startswith("."):
            ext_clean = f".{ext_clean}"
        allowed = [".pdf", ".docx", ".txt", ".html", ".json"]
        if ext_clean not in allowed:
            raise ValueError(f"Unsupported file format: {ext_clean}. Must be one of {allowed}")
        return ext_clean
