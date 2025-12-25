"""
State definition for LangGraph workflow.
EXACT COPY from Jupyter notebook - DO NOT MODIFY.
"""
from typing import TypedDict, Optional, List, Dict, Any


class CableValidationState(TypedDict, total=False):
    """State definition for LangGraph workflow with HITL support."""
    user_input: str
    route: Optional[str]
    design_id: Optional[str]
    attributes: Dict[str, Any]
    missing_attributes: List[str]
    validation: Optional[List[Dict[str, Any]]]
    reasoning: Optional[str]
    confidence: Optional[float]
    conversation_history: List[str]
    skip_missing_prompts: bool
    initial_validation_done: bool
    hitl_mode: bool
    hitl_retry_count: Dict[str, int]  # Track retry attempts per attribute
    hitl_max_retries: int  # Maximum retries before giving up
    hitl_responses: Dict[str, str]  # Pre-loaded HITL responses from API
    skip_hitl_collection: bool  # Flag to skip HITL collection (web-based)
    hitl_responses_processed: bool  # Flag to mark HITL responses as processed
    hitl_required: bool  # Flag indicating HITL interaction is needed
