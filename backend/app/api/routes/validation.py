"""
Validation API routes.
Main endpoint for running cable design validation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_database
from app.schemas import ValidationRequest, HITLResponseRequest, ValidationResponse, ValidationResultItem, HITLInteractionItem
from app.services import ValidationService

router = APIRouter(prefix="/api/validations", tags=["validations"])


@router.post("/validate", response_model=ValidationResponse)
async def validate_design(
    request: ValidationRequest,
    db: Session = Depends(get_database)
):
    """
    Validate a cable design.
    
    This endpoint runs the exact LangGraph workflow from the notebook.
    
    Args:
        request: Validation request with user_input and hitl_mode
        db: Database session
    
    Returns:
        Validation results with PASS/WARN/FAIL status for each field
    """
    try:
        # Create validation service
        service = ValidationService(db)
        
        # Run validation (exact notebook logic)
        result = service.run_validation(
            user_input=request.user_input,
            hitl_mode=request.hitl_mode
        )
        
        # Convert to response schema
        validation_results = [
            ValidationResultItem(**item)
            for item in result.get("validation", [])
        ]
        
        hitl_interactions = []
        for interaction in result.get("conversation_history", []):
            parts = interaction.split(" | ")
            if len(parts) == 2:
                field = parts[0].replace("Q: ", "").strip()
                response = parts[1].replace("A: ", "").strip()
                hitl_interactions.append(
                    HITLInteractionItem(
                        field=field,
                        user_response=response,
                        timestamp=None
                    )
                )
        
        # Determine if HITL is required
        hitl_required = (
            request.hitl_mode and 
            len(result.get("missing_attributes", [])) > 0 and
            not result.get("conversation_history", [])
        )
        
        return ValidationResponse(
            user_input=result["user_input"],
            route=result.get("route"),
            design_id=result.get("design_id"),
            attributes=result.get("attributes", {}),
            missing_attributes=result.get("missing_attributes", []),
            validation=validation_results,
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            hitl_mode=result.get("hitl_mode", False),
            hitl_required=hitl_required,
            hitl_interactions=hitl_interactions
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ VALIDATION ENDPOINT ERROR:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate-with-responses", response_model=ValidationResponse)
async def validate_with_hitl_responses(
    request: HITLResponseRequest,
    db: Session = Depends(get_database)
):
    """
    Re-run validation with HITL responses.
    
    This endpoint accepts user responses for missing attributes and
    re-runs the validation workflow with those values pre-loaded.
    
    Args:
        request: HITL response request with user_input and responses
        db: Database session
    
    Returns:
        Updated validation results with user-provided values
    """
    try:
        # Debug logging
        print("\n" + "="*80)
        print("📥 VALIDATE-WITH-RESPONSES ENDPOINT")
        print("="*80)
        print(f"User input: {request.user_input}")
        print(f"Responses received: {request.responses}")
        print(f"Number of responses: {len(request.responses)}")
        print("="*80)
        
        # Create validation service
        service = ValidationService(db)
        
        # Run validation with HITL responses
        result = service.run_validation_with_responses(
            user_input=request.user_input,
            hitl_responses=request.responses
        )
        
        # Convert to response schema
        validation_results = [
            ValidationResultItem(**item)
            for item in result.get("validation", [])
        ]
        
        hitl_interactions = []
        for interaction in result.get("conversation_history", []):
            parts = interaction.split(" | ")
            if len(parts) == 2:
                field = parts[0].replace("Q: ", "").strip()
                response = parts[1].replace("A: ", "").strip()
                hitl_interactions.append(
                    HITLInteractionItem(
                        field=field,
                        user_response=response,
                        timestamp=None
                    )
                )
        
        return ValidationResponse(
            user_input=result["user_input"],
            route=result.get("route"),
            design_id=result.get("design_id"),
            attributes=result.get("attributes", {}),
            missing_attributes=result.get("missing_attributes", []),
            validation=validation_results,
            reasoning=result.get("reasoning"),
            confidence=result.get("confidence"),
            hitl_mode=result.get("hitl_mode", False),
            hitl_required=False,  # HITL is complete
            hitl_interactions=hitl_interactions
        )
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"\n❌ HITL SUBMISSION ERROR:\n{error_details}")
        raise HTTPException(status_code=500, detail=str(e))
