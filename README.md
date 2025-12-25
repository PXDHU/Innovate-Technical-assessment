# 🔌 AI-Driven Cable Design Validation System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent cable design validation system that uses **LangGraph multi-agent workflow** and **Google Gemini AI** to validate cable specifications against IEC standards (IEC 60228, IEC 60502-1).

![Cable Design Validator](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Features

- 🤖 **AI-Powered Validation** - Uses Google Gemini for intelligent specification analysis
- 🔄 **Multi-Agent Workflow** - LangGraph orchestrates supervisor, fetch, extract, and validation agents
- 🧑‍💼 **Human-in-the-Loop (HITL)** - Interactive chat to collect missing attributes
- 📊 **Confidence Scoring** - Provides validation confidence with detailed reasoning
- 🎯 **Smart Routing** - Automatically routes between design ID lookup and text extraction
- 🌐 **Modern Web UI** - Beautiful, responsive frontend with real-time validation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Input                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Supervisor Agent                              │
│         (Routes: FETCH_DESIGN / EXTRACT_FROM_TEXT / IGNORE)     │
└─────────────────────────────────────────────────────────────────┘
                    │                    │
           ┌───────┴───────┐    ┌───────┴───────┐
           ▼               ▼    ▼               ▼
    ┌──────────────┐  ┌──────────────┐
    │ Fetch Design │  │Extract Text  │
    │   (DB/Mock)  │  │   (LLM)      │
    └──────────────┘  └──────────────┘
           │               │
           └───────┬───────┘
                   ▼
    ┌──────────────────────────────┐
    │    Check Missing Attributes  │
    └──────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────┐
    │      Validation Agent        │
    │   (IEC Standards Check)      │
    └──────────────────────────────┘
                   │
          ┌───────┴───────┐
          │   HITL Mode?  │
          └───────┬───────┘
                  │ Yes
                  ▼
    ┌──────────────────────────────┐
    │    HITL Chat Interaction     │
    │  (Collect Missing Values)    │
    └──────────────────────────────┘
                  │
                  ▼
    ┌──────────────────────────────┐
    │        Re-Validation         │
    └──────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google API Key (for Gemini AI)
- PostgreSQL database

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cable-design-validator.git
cd cable-design-validator
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the `backend` directory:

```env
# LLM Configuration
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=google
LLM_MODEL=gemini-2.0-flash
LLM_TEMPERATURE=0.0

# Database (PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost:5432/cable_validation

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Logging
LOG_LEVEL=INFO
```

### 4. Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Start the Frontend

```bash
cd frontend
python -m http.server 3000
```

### 6. Access the Application

Open your browser and navigate to:
- **Frontend:** http://localhost:3000/design-validator.html
- **API Docs:** http://localhost:8000/docs

---

## 📖 Usage

### Input Options

1. **Design ID Lookup**
   ```
   DESIGN-001
   Validate DESIGN-002
   ```

2. **Full Cable Specifications**
   ```
   IEC 60502-1, 0.6/1 kV, Cu Class 2, 10 mm², PVC insulation 1.0 mm
   ```

3. **Partial Specifications** (HITL will ask for missing data)
   ```
   10 sqmm copper cable with PVC insulation
   ```

### HITL Mode

Enable **HITL Mode** toggle to interactively provide missing attributes through a chat interface.

---

## 📁 Project Structure

```
Innovate-Technical-assessment/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── designs.py      # CRUD operations for designs
│   │   │   │   └── validation.py   # Validation endpoints
│   │   │   └── deps.py             # Dependencies
│   │   ├── langgraph/
│   │   │   ├── nodes/
│   │   │   │   ├── supervisor.py   # Routes user input
│   │   │   │   ├── fetch_design.py # Fetches from database
│   │   │   │   ├── extract_text.py # Extracts specs from text
│   │   │   │   ├── check_missing.py# Identifies missing attrs
│   │   │   │   ├── validation.py   # IEC standards validation
│   │   │   │   ├── hitl.py         # Human-in-the-loop logic
│   │   │   │   └── merge_hitl.py   # Merges HITL responses
│   │   │   ├── routing.py          # Workflow routing functions
│   │   │   ├── state.py            # State definition
│   │   │   └── workflow.py         # Graph construction
│   │   ├── models/
│   │   │   ├── design.py           # Design SQLAlchemy model
│   │   │   └── validation.py       # Validation models
│   │   ├── schemas/
│   │   │   ├── design.py           # Pydantic schemas
│   │   │   └── validation.py       # Validation schemas
│   │   ├── services/
│   │   │   ├── llm_service.py      # LLM configuration
│   │   │   └── validation_service.py# Validation orchestration
│   │   ├── utils/
│   │   │   └── constants.py        # Required attributes & mock DB
│   │   ├── config.py               # Application settings
│   │   ├── database.py             # Database configuration
│   │   └── main.py                 # FastAPI application
│   ├── tests/
│   │   ├── test_workflow.py        # Workflow tests
│   │   └── test_hitl_fix.py        # HITL integration tests
│   └── requirements.txt
├── frontend/
│   ├── design-validator.html       # Main HTML page
│   ├── design-validator.css        # Styles
│   └── design-validator.js         # JavaScript logic
└── Innovate_Assessment.ipynb       # Original Jupyter notebook
```

---

## 🔌 API Reference

### Validate Design

```http
POST /api/validations/validate
Content-Type: application/json

{
  "user_input": "DESIGN-001",
  "hitl_mode": false
}
```

**Response:**
```json
{
  "user_input": "DESIGN-001",
  "route": "FETCH_DESIGN",
  "design_id": "DESIGN-001",
  "attributes": {
    "standard": "IEC 60502-1",
    "voltage": "0.6/1 kV",
    "conductor_material": "Cu",
    "conductor_class": "Class 2",
    "csa": 10,
    "insulation_material": "PVC",
    "insulation_thickness": 1.0
  },
  "missing_attributes": [],
  "validation": [
    {
      "field": "standard",
      "status": "PASS",
      "expected": "IEC 60502-1",
      "comment": "Compliant with IEC 60502-1"
    },
    {
      "field": "conductor_material",
      "status": "PASS",
      "expected": "Cu or Al",
      "comment": "Copper conductor per IEC 60228"
    }
  ],
  "reasoning": "All parameters comply with IEC standards...",
  "confidence": 0.95,
  "hitl_mode": false,
  "hitl_required": false,
  "hitl_interactions": []
}
```

### Validate with HITL Responses

Use this endpoint when `hitl_required` is `true` from initial validation:

```http
POST /api/validations/validate-with-responses
Content-Type: application/json

{
  "user_input": "DESIGN-002",
  "responses": {
    "conductor_class": "Class 2",
    "insulation_thickness": "1.2"
  }
}
```

**Response:** Same schema as `/validate` with updated attributes and improved confidence.

### Design CRUD

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/designs/` | List all designs |
| GET | `/api/designs/{design_id}` | Get design by ID |
| POST | `/api/designs/` | Create new design |
| PUT | `/api/designs/{design_id}` | Update design |
| DELETE | `/api/designs/{design_id}` | Delete design |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root - API info and status |
| GET | `/health` | Health check endpoint |

### Response Schema Reference

| Field | Type | Description |
|-------|------|-------------|
| `user_input` | string | Original user input |
| `route` | string | Routing decision: `FETCH_DESIGN`, `EXTRACT_FROM_TEXT`, `IGNORE` |
| `design_id` | string \| null | Design ID if fetched from database |
| `attributes` | object | Extracted/fetched cable design attributes |
| `missing_attributes` | string[] | List of missing attributes for HITL |
| `validation` | array | Validation results for each field |
| `reasoning` | string | AI reasoning for validation decisions |
| `confidence` | float | Overall confidence score (0.0-1.0) |
| `hitl_mode` | boolean | Whether HITL mode was enabled |
| `hitl_required` | boolean | Whether HITL interaction is needed |
| `hitl_interactions` | array | HITL interaction history |

---

## ⚙️ Configuration

### Required Attributes

The system validates these IEC-defined cable attributes:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `standard` | IEC standard reference | IEC 60502-1 |
| `voltage` | Voltage rating | 0.6/1 kV |
| `conductor_material` | Conductor material | Cu, Al |
| `conductor_class` | IEC 60228 class | Class 1, Class 2 |
| `csa` | Cross-sectional area (mm²) | 10, 16, 25 |
| `insulation_material` | Insulation type | PVC, XLPE, EPR |
| `insulation_thickness` | Thickness (mm) | 1.0, 1.2 |

### Mock Database

Two sample designs are included for testing:

| Design ID | Description |
|-----------|-------------|
| DESIGN-001 | Complete design with all attributes |
| DESIGN-002 | Incomplete design (missing conductor_class, insulation_thickness) |

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

---

## 🔧 Development

### Adding New Validation Rules

Edit `backend/app/langgraph/nodes/validation.py` to add new validation rules:

```python
# Add to the validation prompt
"""
NEW RULE:
- Field X: Must be Y for Z
"""
```

### Adding New Attributes

1. Update `REQUIRED_ATTRIBUTES` in `backend/app/utils/constants.py`
2. Update the Design model in `backend/app/models/design.py`
3. Update schemas in `backend/app/schemas/design.py`

---

## 📝 IEC Standards Reference

This system validates against:

- **IEC 60228** - Conductors of insulated cables
- **IEC 60502-1** - Power cables with extruded insulation

### Validation Status Meanings

| Status | Meaning |
|--------|---------|
| ✅ PASS | Fully compliant with IEC standards |
| ⚠️ WARN | Missing data or minor deviation |
| ❌ FAIL | Non-compliant with IEC standards |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework
- [Google Gemini](https://ai.google.dev) - Large Language Model
- IEC Standards Organization - Cable standards reference

---

## 📧 Contact

For questions or support, please open an issue on GitHub.
