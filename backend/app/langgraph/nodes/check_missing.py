"""
Check Missing Attributes Node - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - This is the exact implementation from the notebook.
"""
from app.langgraph.state import CableValidationState
from app.utils.constants import REQUIRED_ATTRIBUTES


def check_missing_attributes(state: CableValidationState) -> CableValidationState:
    """Check for missing attributes"""
    attributes = state.get("attributes", {})
    missing = [attr for attr in REQUIRED_ATTRIBUTES
               if attributes.get(attr) is None or attributes.get(attr) == ""]

    state["missing_attributes"] = missing

    if missing:
        print(f"\n⚠️  MISSING ATTRIBUTES: {missing}")
        if state.get("hitl_mode", False):
            print("   → Will proceed to HITL interaction after initial validation")
        else:
            print("   → Will validate with WARN status for missing fields")
    else:
        print(f"\n✅ ALL ATTRIBUTES PRESENT")

    return state
