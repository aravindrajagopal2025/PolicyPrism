"""Pydantic models for policy extraction using Pydantic AI."""
from pydantic import BaseModel, Field
from datetime import date
from typing import List, Optional


class CoverageExtraction(BaseModel):
    """Extracted coverage criteria from policy section."""
    
    procedure_name: str = Field(description="Name of the medical procedure or service")
    procedure_code: Optional[str] = Field(None, description="CPT or HCPCS code if mentioned")
    covered_scenarios: str = Field(description="Description of when the procedure is covered")
    required_documentation: Optional[str] = Field(None, description="Required documentation for coverage")
    prior_authorization_required: bool = Field(False, description="Whether prior authorization is required")
    age_restrictions: Optional[str] = Field(None, description="Age restrictions if any (e.g., '18-65 years')")
    frequency_limitations: Optional[str] = Field(None, description="Frequency limitations if any (e.g., 'once per year')")
    confidence_score: float = Field(description="Confidence in extraction accuracy (0.0-1.0)")


class ExclusionExtraction(BaseModel):
    """Extracted exclusion from policy section."""
    
    excluded_procedure: str = Field(description="What is excluded from coverage")
    exclusion_rationale: Optional[str] = Field(None, description="Why it is excluded")
    exceptions_to_exclusion: Optional[str] = Field(None, description="Scenarios where exclusion doesn't apply")
    confidence_score: float = Field(description="Confidence in extraction accuracy (0.0-1.0)")


class PolicySectionExtraction(BaseModel):
    """Extracted policy section with structured data."""
    
    section_type: str = Field(
        description="Type of section: COVERAGE_CRITERIA, EXCLUSIONS, REQUIREMENTS, DEFINITIONS, PRIOR_AUTHORIZATION, LIMITATIONS, APPEALS_PROCESS, or OTHER"
    )
    title: str = Field(description="Section title or heading")
    section_number: Optional[str] = Field(None, description="Section number if present (e.g., '2.1.3')")
    content_summary: str = Field(description="Brief summary of section content")
    coverage_criteria: List[CoverageExtraction] = Field(
        default_factory=list,
        description="List of coverage criteria found in this section"
    )
    exclusions: List[ExclusionExtraction] = Field(
        default_factory=list,
        description="List of exclusions found in this section"
    )
    confidence_score: float = Field(description="Overall confidence in section extraction (0.0-1.0)")


class PolicyExtraction(BaseModel):
    """Complete policy document extraction."""
    
    policy_name: str = Field(description="Official policy name or title")
    policy_number: Optional[str] = Field(None, description="Policy number or identifier")
    payer_name: str = Field(description="Name of the payer organization")
    effective_date: date = Field(description="Policy effective date")
    expiration_date: Optional[date] = Field(None, description="Policy expiration date if specified")
    document_type: str = Field(
        description="Type of policy: MEDICAL, PHARMACY, DENTAL, VISION, or OTHER"
    )
    sections: List[PolicySectionExtraction] = Field(
        description="List of extracted policy sections"
    )
    overall_confidence_score: float = Field(
        description="Overall confidence in entire document extraction (0.0-1.0)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "policy_name": "Medical Policy: Knee Replacement Surgery",
                "policy_number": "MP-2024-001",
                "payer_name": "Cigna",
                "effective_date": "2024-01-01",
                "expiration_date": None,
                "document_type": "MEDICAL",
                "sections": [
                    {
                        "section_type": "COVERAGE_CRITERIA",
                        "title": "Coverage Criteria",
                        "section_number": "1",
                        "content_summary": "Criteria for knee replacement coverage",
                        "coverage_criteria": [
                            {
                                "procedure_name": "Total Knee Replacement",
                                "procedure_code": "27447",
                                "covered_scenarios": "Covered when conservative treatment has failed and patient has severe arthritis",
                                "required_documentation": "X-rays showing joint damage, documentation of failed conservative treatment",
                                "prior_authorization_required": True,
                                "age_restrictions": "18 years and older",
                                "frequency_limitations": None,
                                "confidence_score": 0.95
                            }
                        ],
                        "exclusions": [],
                        "confidence_score": 0.92
                    }
                ],
                "overall_confidence_score": 0.90
            }
        }
