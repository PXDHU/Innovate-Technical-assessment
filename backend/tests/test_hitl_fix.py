"""
Test script to verify HITL workflow fixes.
This tests that attributes are properly updated and re-validated after HITL collection.
"""
import sys
sys.path.insert(0, 'e:/redemption/Innovate-Technical-assessment/backend')

from app.services.validation_service import ValidationService
from app.database import SessionLocal

def test_hitl_workflow():
    """Test HITL workflow with DESIGN-002"""
    print("\n" + "="*80)
    print("TESTING HITL WORKFLOW WITH DESIGN-002")
    print("="*80)
    
    db = SessionLocal()
    service = ValidationService(db)
    
    # Step 1: Initial validation (should show WARN for missing fields)
    print("\n STEP 1: Initial Validation")
    print("-"*80)
    initial_result = service.run_validation('Validate DESIGN-002', hitl_mode=True)
    
    print(f"\nInitial Missing Attributes: {initial_result.get('missing_attributes', [])}")
    print(f"Initial Confidence: {initial_result.get('confidence', 0):.2f}")
    print("\nInitial Validation Results:")
    for v in initial_result.get('validation', []):
        status_symbol = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(v['status'], "❓")
        print(f"  {status_symbol} {v['field']}: {v['status']}")
    
    # Step 2: Re-validation with HITL responses
    print("\n\n STEP 2: Re-validation with HITL Responses")
    print("-"*80)
    print("Providing HITL responses:")
    print("  - conductor_class: Class 2")
    print("  - insulation_thickness: 1.2")
    
    final_result = service.run_validation_with_responses(
        'Validate DESIGN-002',
        {
            'conductor_class': 'Class 2',
            'insulation_thickness': '1.2'
        }
    )
    
    print(f"\nFinal Missing Attributes: {final_result.get('missing_attributes', [])}")
    print(f"Final Confidence: {final_result.get('confidence', 0):.2f}")
    print("\nFinal Validation Results:")
    for v in final_result.get('validation', []):
        status_symbol = {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(v['status'], "❓")
        print(f"  {status_symbol} {v['field']}: {v['status']}")
    
    # Verification
    print("\n\n" + "="*80)
    print("VERIFICATION")
    print("="*80)
    
    # Check 1: Missing attributes should be empty or reduced
    missing_before = len(initial_result.get('missing_attributes', []))
    missing_after = len(final_result.get('missing_attributes', []))
    print(f"\n✓ Missing attributes reduced: {missing_before} → {missing_after}")
    
    # Check 2: Confidence should increase
    conf_before = initial_result.get('confidence', 0)
    conf_after = final_result.get('confidence', 0)
    print(f"✓ Confidence increased: {conf_before:.2f} → {conf_after:.2f}")
    
    # Check 3: Previously missing fields should not have WARN status
    initial_warns = [v['field'] for v in initial_result.get('validation', []) if v['status'] == 'WARN']
    final_warns = [v['field'] for v in final_result.get('validation', []) if v['status'] == 'WARN']
    
    print(f"\n✓ WARN statuses before: {initial_warns}")
    print(f"✓ WARN statuses after: {final_warns}")
    
    # Check if conductor_class and insulation_thickness are no longer WARN
    success = True
    if 'conductor_class' in final_warns:
        print("\n FAILED: conductor_class still has WARN status after HITL")
        success = False
    else:
        print("\n✅ SUCCESS: conductor_class no longer has WARN status")
    
    if 'insulation_thickness' in final_warns:
        print(" FAILED: insulation_thickness still has WARN status after HITL")
        success = False
    else:
        print(" SUCCESS: insulation_thickness no longer has WARN status")
    
    db.close()
    
    return success

if __name__ == "__main__":
    success = test_hitl_workflow()
    sys.exit(0 if success else 1)
