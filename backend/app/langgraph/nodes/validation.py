"""
Validation Agent Node - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - This is the exact implementation with the complete validation prompt.
"""
from app.langgraph.state import CableValidationState
from app.services.llm_service import llm
import json
import re


def validation_agent(state: CableValidationState) -> CableValidationState:
    """
    FIXED VALIDATION AGENT - Implements correct WARN logic and confidence calibration
    """
    attributes = state["attributes"]
    missing = state.get("missing_attributes", [])
    is_initial = not state.get("initial_validation_done", False)
    
    # Debug logging to verify state
    print(f"\n VALIDATION AGENT DEBUG:")
    print(f"   Attributes received: {list(attributes.keys())}")
    print(f"   Attribute values: {attributes}")
    print(f"   Missing attributes: {missing}")
    print(f"   Is initial validation: {is_initial}")

    prompt = f"""You are an expert cable design validation engineer.

**VALIDATION INPUT:**
{json.dumps(attributes, indent=2)}

**MISSING FIELDS:** {missing if missing else "None"}
**VALIDATION TYPE:** {"Initial validation with WARN for missing fields" if is_initial else "Re-validation after HITL interaction"}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL INSTRUCTIONS - READ CAREFULLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**1. STATUS CLASSIFICATION RULES (MANDATORY)**

**PASS** - Use when:
✓ Value matches IEC nominal exactly
✓ Value exceeds nominal (e.g., 1.1mm when 1.0mm required)
✓ All requirements fully satisfied
✓ No ambiguity or missing context

**WARN** - Use when:
⚠ Value is 85-99% of nominal (borderline acceptable)
  Example: 0.9mm when nominal is 1.0mm → WARN (90% of nominal)
  Example: 0.85mm when nominal is 1.0mm → WARN (85% of nominal)
⚠ Field is null/missing (cannot validate without data)
⚠ Value is 101-110% of nominal (acceptable but non-standard)
⚠ Standard is missing (validation basis unclear)
⚠ Context insufficient for definitive judgment

**FAIL** - Use when:
✗ Value is <85% of nominal (safety risk)
  Example: 0.5mm when nominal is 1.0mm → FAIL (50% of nominal)
  Example: 0.8mm when nominal is 1.0mm → FAIL (80% of nominal)
✗ Value does not exist in IEC tables
✗ Prohibited combination
✗ Clear safety violation

**TOLERANCE PHILOSOPHY:**
- Nominal values in IEC standards represent design targets
- Manufacturing tolerances typically allow ±10% variation
- 85-99% of nominal = borderline but potentially acceptable (WARN)
- <85% of nominal = unacceptable safety risk (FAIL)
- >110% of nominal = over-designed, acceptable but atypical (WARN or PASS)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**2. CONFIDENCE SCORING RULES (MANDATORY)**

Base confidence calculation:
- Start at 1.0 (perfect confidence)
- Subtract for each uncertainty factor:
  * Missing critical field: -0.15 per field
  * WARN status: -0.10 per WARN
  * Missing standard: -0.25
  * FAIL status: -0.05 (decisive but problem exists)
  * Ambiguous input: -0.20

Target ranges:
- All PASS, no missing data: 0.90-1.0
- 1-2 WARNs: 0.70-0.85
- 3+ WARNs or missing standard: 0.40-0.65
- Mix of WARN+FAIL: 0.50-0.70
- Multiple FAILs: 0.60-0.80 (decisive but multiple issues)

**DO NOT report 0.98-1.0 confidence if there are WARNs or missing fields.**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**3. IEC STANDARDS REFERENCE FRAMEWORK**

**IEC 60228** - Conductors of insulated cables:
- Validates: conductor_material, conductor_class, csa
- Table 1: Nominal CSA values (1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95...)
- Cu (Copper) and Al (Aluminum) both valid
- Class 1 = solid, Class 2 = stranded

**IEC 60502-1** - Power cables 0.6/1 kV to 18/30 kV:
- Validates: voltage, insulation_material, insulation_thickness
- Table 1 (PVC): CSA-specific nominal insulation thickness
- Table 2 (XLPE/EPR): Different thickness requirements
- Voltage range: 0.6/1 kV to 18/30 kV

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**4. VALIDATION EXAMPLES (STUDY THESE)**

**Example 1: Borderline insulation (WARN not FAIL)**
Input: insulation_thickness = 0.9mm, nominal = 1.0mm
Status: WARN
Reasoning: "0.9mm represents 90% of the nominal 1.0mm specified in IEC 60502-1 Table 1 for 10mm² PVC conductors. While below nominal, this falls within potential manufacturing tolerance range (±10%) and may be acceptable. Engineering review recommended."
Confidence impact: -0.10

**Example 2: Missing standard (WARN)**
Input: standard = null
Status: WARN
Reasoning: "No IEC standard specified. Unable to determine applicable validation criteria. Assuming IEC 60502-1 based on voltage rating, but validation basis is uncertain."
Confidence impact: -0.25

**Example 3: Critically low insulation (FAIL)**
Input: insulation_thickness = 0.5mm, nominal = 1.0mm
Status: FAIL
Reasoning: "0.5mm represents only 50% of nominal 1.0mm per IEC 60502-1 Table 1. This is critically below minimum requirements and poses significant safety risk for 0.6/1kV operation."
Confidence impact: -0.05

**Example 4: Missing conductor class (WARN)**
Input: conductor_class = null
Status: WARN
Reasoning: "Conductor class not specified. IEC 60228 requires classification as Class 1 (solid) or Class 2 (stranded). Cannot verify conductor construction compliance."
Confidence impact: -0.15

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**5. OUTPUT FORMAT (STRICT)**

{{
  "validation": [
    {{
      "field": "standard",
      "status": "PASS|WARN|FAIL",
      "expected": "IEC 60502-1",
      "comment": "Detailed explanation with specific IEC references"
    }},
    {{
      "field": "voltage",
      "status": "PASS|WARN|FAIL",
      "expected": "0.6/1 kV to 18/30 kV range (IEC 60502-1)",
      "comment": "..."
    }},
    {{
      "field": "conductor_material",
      "status": "PASS|WARN|FAIL",
      "expected": "Cu or Al per IEC 60228",
      "comment": "IEC 60228 permits both copper and aluminum conductors"
    }},
    {{
      "field": "conductor_class",
      "status": "PASS|WARN|FAIL",
      "expected": "Class 1 or Class 2 per IEC 60228",
      "comment": "..."
    }},
    {{
      "field": "csa",
      "status": "PASS|WARN|FAIL",
      "expected": "Nominal value from IEC 60228 Table 1",
      "comment": "Must match standard sizes: 1.5, 2.5, 4, 6, 10, 16, 25, 35..."
    }},
    {{
      "field": "insulation_material",
      "status": "PASS|WARN|FAIL",
      "expected": "PVC, XLPE, or EPR per IEC 60502-1",
      "comment": "..."
    }},
    {{
      "field": "insulation_thickness",
      "status": "PASS|WARN|FAIL",
      "expected": "Nominal from IEC 60502-1 Table 1/2",
      "comment": "For 10mm² PVC at 0.6/1kV, nominal is 1.0mm. Actual value assessment with tolerance consideration."
    }}
  ],
  "reasoning": "Overall assessment explaining compliance level, cumulative uncertainty from missing fields, and engineering judgment",
  "confidence": 0.75
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**6. MANDATORY REQUIREMENTS**

✓ Validate ALL 7 fields (even if null)
✓ Apply tolerance logic: 85-99% nominal = WARN
✓ Missing field = WARN (not interactive prompt)
✓ Calculate confidence using deduction rules
✓ Reference both IEC 60228 and IEC 60502-1 where applicable
✓ Cite specific table numbers
✓ Explain WARN decisions clearly (not just "needs review")

**NOW VALIDATE THE DESIGN ABOVE**
Return ONLY valid JSON (no markdown, no preamble):"""

    response = llm.invoke(prompt)

    try:
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content)
        start = content.find('{')
        end = content.rfind('}') + 1

        if start != -1 and end > start:
            result = json.loads(content[start:end])

            validation = result.get("validation", [])
            reasoning = result.get("reasoning", "")
            confidence = result.get("confidence", 0.0)

            # Post-process: Ensure confidence aligns with status
            warn_count = sum(1 for v in validation if v.get("status") == "WARN")
            fail_count = sum(1 for v in validation if v.get("status") == "FAIL")

            # Recalibrate if AI still reports inflated confidence
            if warn_count > 0 or fail_count > 0 or missing:
                max_confidence = 1.0 - (warn_count * 0.10) - (len(missing) * 0.15) - (fail_count * 0.05)
                if confidence > max_confidence:
                    print(f"\nRecalibrating confidence: {confidence:.2f} → {max_confidence:.2f}")
                    confidence = max(0.3, max_confidence)

            state["validation"] = validation
            state["reasoning"] = reasoning
            state["confidence"] = confidence
            state["initial_validation_done"] = True  # Mark initial validation as done

            print(f"\n VALIDATION COMPLETE")
            print(f"   Confidence: {confidence:.2f}")
            print(f"   WARN count: {warn_count}, FAIL count: {fail_count}, Missing: {len(missing)}")
        else:
            raise ValueError("No valid JSON found")

    except Exception as e:
        print(f"\n VALIDATION FAILED: {e}")
        state["validation"] = []
        state["reasoning"] = "Validation could not be completed"
        state["confidence"] = 0.0

    return state
