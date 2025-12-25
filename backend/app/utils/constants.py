"""
Constants from the notebook - DO NOT MODIFY.
These are exact copies from the Jupyter notebook.
"""

# Required attributes for validation (from notebook)
REQUIRED_ATTRIBUTES = [
    "standard",
    "voltage",
    "conductor_material",
    "conductor_class",
    "csa",
    "insulation_material",
    "insulation_thickness"
]

# Mock database from notebook (for reference/seeding)
DESIGN_DATABASE = {
    "DESIGN-001": {
        "standard": "IEC 60502-1",
        "voltage": "0.6/1 kV",
        "conductor_material": "Cu",
        "conductor_class": "Class 2",
        "csa": 10,
        "insulation_material": "PVC",
        "insulation_thickness": 1.0
    },
    "DESIGN-002": {
        "standard": "IEC 60502-1",
        "voltage": "0.6/1 kV",
        "conductor_material": "Cu",
        "conductor_class": None,  # Missing attribute
        "csa": 16,
        "insulation_material": "PVC",
        "insulation_thickness": None  # Missing attribute
    }
}
