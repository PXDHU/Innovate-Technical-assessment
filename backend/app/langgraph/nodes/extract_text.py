"""
Extract From Text Node - EXACT COPY from Jupyter notebook.
DO NOT MODIFY - This is the exact implementation from the notebook.
"""
from app.langgraph.state import CableValidationState
from app.services.llm_service import llm
import json
import re


def extract_from_text_node(state: CableValidationState) -> CableValidationState:
    """Extract cable specifications from text"""
    user_input = state["user_input"]

    prompt = f"""Extract cable specifications from text. Return ONLY values explicitly stated.

Input: "{user_input}"

Rules:
- Set field to null if not mentioned
- Do NOT infer missing values
- Extract exact values only

Output JSON format:
{{
  "standard": string or null,
  "voltage": string or null,
  "conductor_material": string or null,
  "conductor_class": string or null,
  "csa": number or null,
  "insulation_material": string or null,
  "insulation_thickness": number or null
}}

Examples:
"10 sqmm copper cable" → {{"csa": 10, "conductor_material": "Cu", others: null}}
"IEC 60502-1, 0.6/1kV, Cu Class 2, 16mm², PVC 1.0mm" → all fields filled

Extract now (JSON only):"""

    response = llm.invoke(prompt)

    try:
        content = response.content.strip()
        content = re.sub(r'```json\s*|\s*```', '', content)
        start = content.find('{')
        end = content.rfind('}') + 1
        if start != -1 and end > start:
            attributes = json.loads(content[start:end])
            print(f"\nEXTRACTED ATTRIBUTES:")
            for key, value in attributes.items():
                print(f"   {'✓' if value else '✗'} {key}: {value}")
            state["attributes"] = attributes
        else:
            raise ValueError("No JSON found")
    except Exception as e:
        print(f"\n EXTRACTION FAILED: {e}")
        state["attributes"] = {}

    return state
