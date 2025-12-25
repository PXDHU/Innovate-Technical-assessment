"""
Fetch Design Node - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - Adapted to use database instead of mock dictionary.
"""
from app.langgraph.state import CableValidationState
from app.services.llm_service import llm
from sqlalchemy.orm import Session
from app.models import Design
import re
import json


def fetch_design_node(state: CableValidationState, db: Session = None) -> CableValidationState:
    """Fetch design from database (adapted from notebook's fetch_design_node)"""
    user_input = state["user_input"]

    pattern = r'DESIGN-\d+'
    match = re.search(pattern, user_input, re.IGNORECASE)

    if match:
        design_id = match.group().upper()
    else:
        prompt = f"""Extract design ID from: "{user_input}"
Return JSON: {{"design_id": "DESIGN-XXX"}} or {{"design_id": null}}"""
        response = llm.invoke(prompt)
        try:
            content = re.sub(r'```json\s*|\s*```', '', response.content.strip())
            match = re.search(r'\{[^}]+\}', content)
            result = json.loads(match.group()) if match else {}
            design_id = result.get("design_id")
        except:
            design_id = None

    if design_id:
        # Preserve any pre-loaded HITL responses before fetching
        hitl_responses = state.get("hitl_responses", {})
        
        # Fetch from database if db session provided
        if db:
            design = db.query(Design).filter(Design.id == design_id).first()
            if design:
                attributes = design.to_dict()
                print(f"\n📦 FETCHED DESIGN: {design_id}")
                state["design_id"] = design_id
                state["attributes"] = attributes
            else:
                print(f"\n❌ DESIGN NOT FOUND: {design_id}")
                state["attributes"] = {}
        else:
            # Fallback to mock database (for testing without DB)
            from app.utils.constants import DESIGN_DATABASE
            if design_id in DESIGN_DATABASE:
                attributes = DESIGN_DATABASE[design_id].copy()
                print(f"\n📦 FETCHED DESIGN: {design_id}")
                state["design_id"] = design_id
                state["attributes"] = attributes
            else:
                print(f"\n❌ DESIGN NOT FOUND: {design_id}")
                state["attributes"] = {}
        
        # Merge HITL responses into attributes if provided
        if hitl_responses:
            print(f"\n🔄 MERGING HITL RESPONSES INTO FETCHED DESIGN")
            from app.langgraph.nodes.hitl import parse_single_attribute_with_llm
            
            attributes = state.get("attributes", {})
            for attr, user_response in hitl_responses.items():
                print(f"   Merging: {attr} = {user_response}")
                value = parse_single_attribute_with_llm(llm, attr, user_response)
                if value is not None:
                    attributes[attr] = value
                    print(f"   ✓ Set {attr} = {value}")
                else:
                    print(f"   ✗ Could not parse {attr}")
            
            state["attributes"] = attributes
            print(f"✅ Merged {len(hitl_responses)} HITL responses into design")
    else:
        print(f"\n❌ DESIGN NOT FOUND: {design_id}")
        state["attributes"] = {}

    return state
