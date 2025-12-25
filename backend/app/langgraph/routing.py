"""
Routing Functions - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - These are the exact routing functions from the notebook.
"""
from app.langgraph.state import CableValidationState


def route_after_supervisor(state: CableValidationState) -> str:
    """Route after supervisor agent"""
    route = state.get("route", "IGNORE")
    return {"IGNORE": "end", "FETCH_DESIGN": "fetch_design", "EXTRACT_FROM_TEXT": "extract_from_text"}.get(route, "end")


def route_after_validation(state: CableValidationState) -> str:
    """Route after validation - decide if HITL needed"""
    missing = state.get("missing_attributes", [])
    hitl_mode = state.get("hitl_mode", False)
    initial_done = state.get("initial_validation_done", False)

    # If HITL mode enabled, missing fields exist, and this is the first validation
    if hitl_mode and missing and initial_done:
        # Check if there are WARN statuses due to missing fields
        validation = state.get("validation", [])
        has_missing_warns = any(
            v['status'] == 'WARN' and v['field'] in missing
            for v in validation
        )
        if has_missing_warns:
            # Mark that HITL is required for the API response
            state["hitl_required"] = True
            return "hitl_prompt"

    return "end"


def route_after_hitl_prompt(state: CableValidationState) -> str:
    """Route after HITL prompt - decide if collecting attributes"""
    # Check if we should skip HITL collection (web-based, no responses yet)
    skip_collection = state.get("skip_hitl_collection", False)
    if skip_collection:
        return "end"
    
    # Otherwise, check if we have missing attributes to collect
    missing = state.get("missing_attributes", [])
    return "ask_missing" if missing else "revalidate"


def route_after_ask(state: CableValidationState) -> str:
    """Route after asking for attribute"""
    missing = state.get("missing_attributes", [])
    return "ask_missing" if missing else "revalidate"
