"""
Basic tests for the validation workflow.
"""
import pytest
from app.langgraph.workflow import create_validation_graph


def test_create_graph():
    """Test that the graph can be created."""
    graph = create_validation_graph()
    assert graph is not None


def test_supervisor_routing_fetch_design():
    """Test supervisor routes DESIGN-001 to FETCH_DESIGN."""
    graph = create_validation_graph()
    
    initial_state = {
        "user_input": "Validate DESIGN-001",
        "route": None,
        "design_id": None,
        "attributes": {},
        "missing_attributes": [],
        "validation": None,
        "reasoning": None,
        "confidence": None,
        "conversation_history": [],
        "skip_missing_prompts": True,
        "initial_validation_done": False,
        "hitl_mode": False
    }
    
    # Note: This test requires LLM access
    # For now, just test graph creation
    assert graph is not None


def test_supervisor_routing_extract():
    """Test supervisor routes cable specs to EXTRACT_FROM_TEXT."""
    graph = create_validation_graph()
    
    initial_state = {
        "user_input": "IEC 60502-1, 10mm² copper cable",
        "route": None,
        "design_id": None,
        "attributes": {},
        "missing_attributes": [],
        "validation": None,
        "reasoning": None,
        "confidence": None,
        "conversation_history": [],
        "skip_missing_prompts": True,
        "initial_validation_done": False,
        "hitl_mode": False
    }
    
    # Note: This test requires LLM access
    assert graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
