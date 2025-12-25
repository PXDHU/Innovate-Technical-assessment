"""
LangGraph Workflow Construction - EXACT COPY from Jupyter notebook.
"""
from langgraph.graph import StateGraph, END
from app.langgraph.state import CableValidationState
from app.langgraph.nodes.supervisor import supervisor_agent
from app.langgraph.nodes.fetch_design import fetch_design_node
from app.langgraph.nodes.extract_text import extract_from_text_node
from app.langgraph.nodes.check_missing import check_missing_attributes
from app.langgraph.nodes.validation import validation_agent
from app.langgraph.nodes.hitl import hitl_prompt_node, ask_missing_attribute
from app.langgraph.routing import (
    route_after_supervisor,
    route_after_validation,
    route_after_hitl_prompt,
    route_after_ask
)


def create_validation_graph():
    """Create the validation workflow graph with HITL support"""
    workflow = StateGraph(CableValidationState)

    # Add all nodes
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("fetch_design", fetch_design_node)
    workflow.add_node("extract_from_text", extract_from_text_node)
    workflow.add_node("check_missing", check_missing_attributes)
    workflow.add_node("validate", validation_agent)
    workflow.add_node("hitl_prompt", hitl_prompt_node)
    workflow.add_node("ask_missing", ask_missing_attribute)
    workflow.add_node("revalidate", validation_agent)

    # Entry point
    workflow.set_entry_point("supervisor")

    # Supervisor routing
    workflow.add_conditional_edges("supervisor", route_after_supervisor,
        {"end": END, "fetch_design": "fetch_design", "extract_from_text": "extract_from_text"})

    # Data collection routes
    workflow.add_edge("fetch_design", "check_missing")
    workflow.add_edge("extract_from_text", "check_missing")

    # Initial validation (always happens)
    workflow.add_edge("check_missing", "validate")

    # After validation, check if HITL needed
    workflow.add_conditional_edges("validate", route_after_validation,
        {"end": END, "hitl_prompt": "hitl_prompt"})

    # HITL workflow
    workflow.add_conditional_edges("hitl_prompt", route_after_hitl_prompt,
        {"ask_missing": "ask_missing", "revalidate": "revalidate", "end": END})

    workflow.add_conditional_edges("ask_missing", route_after_ask,
        {"ask_missing": "ask_missing", "revalidate": "revalidate"})

    # After revalidation, end
    workflow.add_edge("revalidate", END)

    return workflow.compile()
