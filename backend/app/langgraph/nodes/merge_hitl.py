"""
HITL Response Merger Node - Merges pre-loaded HITL responses into attributes.
This node runs when hitl_responses are provided via API.
"""
from app.langgraph.state import CableValidationState
from app.langgraph.nodes.hitl import parse_single_attribute_with_llm
from app.services.llm_service import llm


def merge_hitl_responses(state: CableValidationState) -> CableValidationState:
    """
    Merge pre-loaded HITL responses into attributes.
    This is used when re-validating with user-provided responses.
    """
    hitl_responses = state.get("hitl_responses", {})
    
    if not hitl_responses:
        # No responses to merge, continue
        return state
    
    print("\n" + "="*80)
    print("🔄 MERGING HITL RESPONSES INTO ATTRIBUTES")
    print("="*80)
    
    attributes = state.get("attributes", {})
    conversation_history = state.get("conversation_history", [])
    
    for attr, user_response in hitl_responses.items():
        print(f"\n   Processing: {attr} = {user_response}")
        
        # Parse the response using LLM
        value = parse_single_attribute_with_llm(llm, attr, user_response)
        
        if value is not None:
            attributes[attr] = value
            print(f"   ✓ Merged {attr} = {value}")
            
            # Add to conversation history
            conversation_history.append(f"Q: {attr} | A: {user_response}")
        else:
            print(f"   ✗ Could not parse {attr} from '{user_response}'")
    
    state["attributes"] = attributes
    state["conversation_history"] = conversation_history
    
    print(f"\n✅ Merged {len(hitl_responses)} HITL responses")
    print("="*80)
    
    return state
