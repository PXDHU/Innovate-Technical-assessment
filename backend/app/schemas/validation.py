"""Validation schemas for API requests and responses."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ValidationRequest(BaseModel):
    """Request schema for validation."""
    user_input: str = Field(..., description="Cable design specification or design ID")
    hitl_mode: bool = Field(default=False, description="Enable Human-in-the-Loop mode")


class HITLResponseRequest(BaseModel):
    """Request schema for submitting HITL responses."""
    user_input: str = Field(..., description="Original user input")
    responses: Dict[str, str] = Field(..., description="User responses for missing attributes")


class ValidationResultItem(BaseModel):
    """Individual field validation result."""
    field: str
    status: str  # PASS, WARN, FAIL
    expected: Optional[str] = None
    comment: Optional[str] = None


class HITLInteractionItem(BaseModel):
    """HITL interaction record."""
    field: str
    user_response: str
    timestamp: Optional[datetime] = None


class ValidationResponse(BaseModel):
    """
    Response schema for validation - complete format with all fields.
    """
    user_input: str = Field(..., description="Original user input")
    route: Optional[str] = Field(None, description="Routing decision (FETCH_DESIGN, EXTRACT_FROM_TEXT, IGNORE)")
    design_id: Optional[str] = Field(None, description="Design ID if fetched from database")
    attributes: Dict[str, Any] = Field(default={}, description="All extracted/fetched cable design attributes")
    missing_attributes: List[str] = Field(default=[], description="List of missing attributes for HITL")
    validation: List[ValidationResultItem] = Field(..., description="Validation results for each field")
    reasoning: Optional[str] = Field(None, description="AI reasoning for validation decisions")
    confidence: Optional[float] = Field(None, description="Overall confidence score (0.0-1.0)")
    hitl_mode: bool = Field(default=False, description="Whether HITL mode was enabled")
    hitl_required: bool = Field(default=False, description="Whether HITL interaction is needed")
    hitl_interactions: List[HITLInteractionItem] = Field(default=[], description="HITL interaction history")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "IEC 60502-1, 0.6/1 kV, Cu Class 2, 10 mm², PVC 1.0mm",
                "route": "EXTRACT_FROM_TEXT",
                "design_id": None,
                "attributes": {
                    "standard": "IEC 60502-1",
                    "voltage": "0.6/1 kV",
                    "conductor_material": "Cu",
                    "conductor_class": "Class 2",
                    "csa": 10,
                    "insulation_material": "PVC",
                    "insulation_thickness": 1.0
                },
                "validation": [
                    {
                        "field": "insulation_thickness",
                        "status": "PASS",
                        "expected": "1.0 mm",
                        "comment": "Consistent with IEC 60502-1 nominal insulation thickness for PVC at 10 mm²."
                    }
                ],
                "reasoning": "All parameters comply with IEC standards...",
                "confidence": 0.91,
                "missing_attributes": [],
                "hitl_mode": False,
                "hitl_required": False,
                "hitl_interactions": []
            }
        }
