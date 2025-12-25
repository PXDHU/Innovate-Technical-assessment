"""
HITL (Human-in-the-Loop) Nodes - EXACT LOGIC from Jupyter notebook.
Adapted for web-based interaction (returns data for frontend to handle).
"""
from app.langgraph.state import CableValidationState
from app.services.llm_service import llm
from typing import Any
import json
import re


def hitl_prompt_node(state: CableValidationState) -> CableValidationState:
    """
    Human-in-the-Loop: Prompt for missing attributes
    NOTE: For web-based HITL, this prepares the data for frontend interaction.
    The actual user interaction happens via API calls.
    """
    missing = state.get("missing_attributes", [])
    validation = state.get("validation", [])
    hitl_responses = state.get("hitl_responses", {})

    print("\n" + "="*80)
    print("HUMAN-IN-THE-LOOP INTERACTION")
    print("="*80)
    print(f"\n STATE DEBUG:")
    print(f"   Missing attributes: {missing}")
    print(f"   HITL responses: {hitl_responses}")
    print(f"   Has pre-loaded responses: {bool(hitl_responses)}")
    print("\n The following fields have WARN status due to missing data:")

    # Show which fields need input
    for field in missing:
        warn_item = next((v for v in validation if v['field'] == field), None)
        if warn_item and warn_item['status'] == 'WARN':
            print(f"\n   • {field}")
            print(f"     Status: {warn_item['status']}")
            print(f"     Expected: {warn_item['expected']}")
            print(f"     Reason: {warn_item['comment'][:100]}...")

    print("\n" + "-"*80)
    
    # For web-based HITL, check if we have pre-loaded responses
    if hitl_responses:
        # We have pre-loaded responses, continue with HITL workflow
        print("✓ Pre-loaded HITL responses detected. Proceeding with data collection.")
        state["skip_hitl_collection"] = False
        return state
    else:
        # No pre-loaded responses - this is the initial validation
        # Set flag to skip HITL collection and exit workflow
        # IMPORTANT: Keep missing_attributes so API can return them to frontend
        print(" No pre-loaded responses. Returning to frontend for user input collection.")
        state["skip_hitl_collection"] = True
        return state


def ask_missing_attribute(state: CableValidationState, user_response: str = None, attr: str = None) -> CableValidationState:
    """
    Prompt user for a single missing attribute
    NOTE: For web-based HITL, user_response and attr are provided via API
    """
    missing = state.get("missing_attributes", [])

    print(f"\nASK_MISSING_ATTRIBUTE DEBUG:")
    print(f"   Missing: {missing}")
    print(f"   Has hitl_responses: {bool(state.get('hitl_responses', {}))}")
    print(f"   Responses processed: {state.get('hitl_responses_processed', False)}")

    if not missing:
        print("No missing attributes, returning state")
        return state

    # Initialize retry tracking if not present
    if "hitl_retry_count" not in state:
        state["hitl_retry_count"] = {}
    if "hitl_max_retries" not in state:
        state["hitl_max_retries"] = 3  # Default max retries

    # Check if we have pre-loaded HITL responses (web-based HITL)
    hitl_responses = state.get("hitl_responses", {})
    
    # If we have pre-loaded responses, process ALL of them at once
    if hitl_responses and not state.get("hitl_responses_processed", False):
        print("\n" + "="*80)
        print("PROCESSING PRE-LOADED HITL RESPONSES")
        print("="*80)
        
        attributes = state.get("attributes", {})
        conversation_history = state.get("conversation_history", [])
        
        # Process each response
        for attr_name, user_resp in hitl_responses.items():
            if attr_name in missing:
                print(f"\n   Processing: {attr_name} = {user_resp}")
                
                # Add to conversation history
                conversation_history.append(f"Q: {attr_name} | A: {user_resp}")
                
                # Parse the response
                value = parse_single_attribute_with_llm(llm, attr_name, user_resp)
                
                if value is not None:
                    attributes[attr_name] = value
                    print(f"   ✓ Set {attr_name} = {value}")
                    
                    # Remove from missing list
                    missing.remove(attr_name)
                else:
                    print(f"   ✗ Could not extract {attr_name} from '{user_resp}'")
                    # Still remove to avoid infinite loop
                    missing.remove(attr_name)
        
        state["attributes"] = attributes
        state["conversation_history"] = conversation_history
        state["missing_attributes"] = missing
        state["hitl_responses_processed"] = True  # Mark as processed
        
        print(f"\n Processed {len(hitl_responses)} HITL responses")
        print(f"   Updated attributes: {attributes}")
        print(f"   Remaining missing attributes: {len(missing)}")
        print("="*80)
        
        return state

    # Original logic for interactive HITL (notebook style)
    # If attr not provided, take the first missing attribute
    if attr is None:
        attr = missing[0]

    # Track retry count for this attribute
    retry_count = state["hitl_retry_count"].get(attr, 0)
    max_retries = state["hitl_max_retries"]

    attr_display = {
        "standard": "IEC standard (e.g., IEC 60502-1)",
        "voltage": "voltage rating (e.g., 0.6/1 kV)",
        "conductor_material": "conductor material (Cu or Al)",
        "conductor_class": "conductor class (Class 1 or Class 2)",
        "csa": "cross-sectional area in mm² (e.g., 10)",
        "insulation_material": "insulation material (PVC, XLPE, or EPR)",
        "insulation_thickness": "insulation thickness in mm (e.g., 1.0)"
    }

    print(f"\n Please provide the {attr_display.get(attr, attr)}:")
    
    # For web-based HITL without pre-loaded responses, user_response is provided via API
    if user_response is None:
        # Increment retry count
        state["hitl_retry_count"][attr] = retry_count + 1
        
        # Check if max retries reached
        if retry_count + 1 >= max_retries:
            print(f"No user response after {max_retries} attempts. Skipping attribute.")
            # Remove from missing list to prevent infinite loop
            if attr in missing:
                missing.remove(attr)
            state["missing_attributes"] = missing
        else:
            print(f"No user response provided (web-based HITL) - Attempt {retry_count + 1}/{max_retries}")
        
        return state
    
    print(f">>> {user_response}")

    if "conversation_history" not in state:
        state["conversation_history"] = []

    state["conversation_history"].append(f"Q: {attr} | A: {user_response}")

    # Parse the user response
    attributes = state.get("attributes", {})
    value = parse_single_attribute_with_llm(llm, attr, user_response)

    if value is not None:
        attributes[attr] = value
        print(f"   ✓ Set {attr} = {value}")

        # Remove from missing list
        if attr in missing:
            missing.remove(attr)
        state["missing_attributes"] = missing
        
        # Reset retry count for this attribute
        state["hitl_retry_count"][attr] = 0
    else:
        print(f"   ✗ Could not extract {attr}. Keeping as missing.")
        # Increment retry count
        state["hitl_retry_count"][attr] = retry_count + 1
        
        # If max retries reached, remove from list
        if retry_count + 1 >= max_retries:
            print(f"Max retries reached for {attr}. Skipping.")
            if attr in missing:
                missing.remove(attr)
            state["missing_attributes"] = missing

    state["attributes"] = attributes
    return state


def parse_single_attribute_with_llm(
    llm,
    attribute_name: str,
    user_response: str
) -> Any:
    """Extract single attribute value from user input"""
    prompt = f"""Extract ONLY the value for "{attribute_name}" from this user input.

User input: "{user_response}"

Rules:
- Extract ONLY the {attribute_name} value
- Ignore everything else
- Return null if not found or unclear
- For numbers, return as number type
- For text, return as string

Response format (JSON only):
{{"value": <extracted_value>}}

Examples:
Input: "IEC 60502-1" → {{"value": "IEC 60502-1"}}
Input: "10" → {{"value": 10}}
Input: "Class 2" → {{"value": "Class 2"}}"""

    response = llm.invoke(prompt)

    try:
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content)
        match = re.search(r'\{[^}]+\}', content)
        if match:
            parsed = json.loads(match.group())
            return parsed.get("value")
    except Exception:
        pass

    return None
