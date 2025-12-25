"""
Validation service - Orchestrates the LangGraph workflow.
This service executes the exact notebook logic without database persistence.
"""
from app.langgraph.workflow import create_validation_graph
from sqlalchemy.orm import Session
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig


class ValidationService:
    """Service for running cable design validation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.graph = create_validation_graph()
    
    def run_validation(
        self,
        user_input: str,
        hitl_mode: bool = False
    ) -> Dict[str, Any]:
        """
        Run validation workflow (exact logic from notebook).
        
        Args:
            user_input: Cable design specification or design ID
            hitl_mode: Enable Human-in-the-Loop mode
        
        Returns:
            Final state dictionary with validation results
        """
        # Create initial state (exact from notebook)
        initial_state = {
            "user_input": user_input,
            "route": None,
            "design_id": None,
            "attributes": {},
            "missing_attributes": [],
            "validation": None,
            "reasoning": None,
            "confidence": None,
            "conversation_history": [],
            "skip_missing_prompts": not hitl_mode,
            "initial_validation_done": False,
            "hitl_mode": hitl_mode,
            "hitl_retry_count": {},  # Track retry attempts per attribute
            "hitl_max_retries": 3  # Maximum retries before giving up
        }
        
        # Run the graph with increased recursion limit for HITL interactions
        final_state = self.graph.invoke(
            initial_state,
            config=RunnableConfig(recursion_limit=50)
        )
        
        return final_state
    
    def run_validation_with_responses(
        self,
        user_input: str,
        hitl_responses: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Re-run validation with HITL responses provided.
        
        Args:
            user_input: Original user input
            hitl_responses: Dictionary of user responses for missing attributes
        
        Returns:
            Final state dictionary with validation results
        """
        # Create initial state with HITL responses pre-loaded
        initial_state = {
            "user_input": user_input,
            "route": None,
            "design_id": None,
            "attributes": {},
            "missing_attributes": [],
            "validation": None,
            "reasoning": None,
            "confidence": None,
            "conversation_history": [],
            "skip_missing_prompts": False,  # Enable HITL workflow
            "initial_validation_done": False,
            "hitl_mode": True,
            "hitl_responses": hitl_responses,  # Pre-load responses
            "hitl_retry_count": {},
            "hitl_max_retries": 3
        }
        
        print("\n" + "="*80)
        print("🚀 STARTING VALIDATION WITH HITL RESPONSES")
        print("="*80)
        print(f"Initial state hitl_responses: {initial_state['hitl_responses']}")
        print(f"Number of responses: {len(initial_state['hitl_responses'])}")
        print("="*80)
        
        # Run the graph with pre-loaded responses
        final_state = self.graph.invoke(
            initial_state,
            config=RunnableConfig(recursion_limit=50)
        )
        
        print("\n" + "="*80)
        print("VALIDATION COMPLETE")
        print("="*80)
        print(f"Final attributes: {final_state.get('attributes', {})}")
        print(f"Final missing: {final_state.get('missing_attributes', [])}")
        print("="*80)
        
        return final_state
