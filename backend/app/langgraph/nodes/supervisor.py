"""
Supervisor Agent Node - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - This is the exact implementation from the notebook.
"""
from app.langgraph.state import CableValidationState
from app.services.llm_service import llm
import json
import re


def supervisor_agent(state: CableValidationState) -> CableValidationState:
    """
    FIXED: Enhanced prompt with clear examples and pattern matching logic
    """
    user_input = state["user_input"]

    prompt = f"""You are a routing supervisor for a cable design validation system.

Classify this input into ONE route:

**FETCH_DESIGN** - Input contains design ID pattern (DESIGN-XXX)
Examples: "Validate DESIGN-001", "Check design DESIGN-002"

**EXTRACT_FROM_TEXT** - Input contains cable technical specifications
Examples: "IEC 60502-1, 10mm² Cu", "0.6/1kV cable with PVC insulation"

**IGNORE** - Input is unrelated to cable design
Examples: "What's the weather?", "Tell me a joke"

Input: "{user_input}"

Respond ONLY with JSON (no markdown):
{{"route":"FETCH_DESIGN"}} or {{"route":"EXTRACT_FROM_TEXT"}} or {{"route":"IGNORE"}}"""

    response = llm.invoke(prompt)

    try:
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content)
        match = re.search(r'\{[^}]+\}', content)
        if match:
            result = json.loads(match.group())
            route = result.get("route", "IGNORE")
        else:
            route = "IGNORE"
    except:
        input_lower = user_input.lower()
        if "design-" in input_lower:
            route = "FETCH_DESIGN"
        elif any(kw in input_lower for kw in ["iec", "kv", "copper", "cu", "cable", "insulation"]):
            route = "EXTRACT_FROM_TEXT"
        else:
            route = "IGNORE"

    print(f"\n SUPERVISOR DECISION: {route}")
    state["route"] = route
    return state
