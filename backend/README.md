# AI-Driven Cable Design Validation System - Backend

FastAPI backend with LangGraph workflow for cable design validation.

## Features

- **Exact LangGraph Implementation**: Preserves 100% of the notebook's LangChain/LangGraph logic
- **FastAPI REST API**: Modern async API with automatic OpenAPI documentation
- **PostgreSQL Database**: Persistent storage for designs and validation results
- **Multi-LLM Support**: Google Gemini (primary), OpenAI, and Azure OpenAI
- **HITL Mode**: Human-in-the-Loop validation for missing attributes

## Project Structure

```
backend/
├── app/
│   ├── api/              # API routes
│   ├── langgraph/        # LangGraph workflow (exact from notebook)
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── utils/            # Constants and utilities
│   ├── config.py         # Configuration
│   ├── database.py       # Database setup
│   └── main.py           # FastAPI app
├── tests/                # Tests
├── seed_db.py            # Database seeding
├── requirements.txt      # Dependencies
└── .env.example          # Environment template
```

## Setup

### 1. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/cable_validation
GOOGLE_API_KEY=your_google_api_key_here
LLM_MODEL=gemini-2.5-flash
LLM_TEMPERATURE=0.1
```

### 4. Setup PostgreSQL Database

Make sure PostgreSQL is running and create the database:

```sql
CREATE DATABASE cable_validation;
```

### 5. Seed Database

```powershell
python seed_db.py
```

This will populate the database with the mock designs from the notebook (DESIGN-001, DESIGN-002).

### 6. Run the Server

```powershell
python -m app.main
```

Or use uvicorn directly:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Validation

- `POST /api/validations/validate` - Run validation
- `GET /api/validations/{id}` - Get validation by ID
- `GET /api/validations/` - List all validations

### Designs

- `POST /api/designs/` - Create design
- `GET /api/designs/` - List all designs
- `GET /api/designs/{id}` - Get design by ID
- `PUT /api/designs/{id}` - Update design
- `DELETE /api/designs/{id}` - Delete design

## Example Usage

### Validate a Complete Design

```bash
curl -X POST http://localhost:8000/api/validations/validate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "IEC 60502-1, 0.6/1 kV, Cu Class 2, 10 mm², PVC 1.0mm",
    "hitl_mode": false
  }'
```

### Validate a Design ID

```bash
curl -X POST http://localhost:8000/api/validations/validate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Validate DESIGN-001",
    "hitl_mode": false
  }'
```

### Validate with HITL Mode

```bash
curl -X POST http://localhost:8000/api/validations/validate \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "10 sqmm copper cable",
    "hitl_mode": true
  }'
```

## LangGraph Workflow

The backend implements the exact LangGraph workflow from the Jupyter notebook:

1. **Supervisor Agent**: Routes input to FETCH_DESIGN, EXTRACT_FROM_TEXT, or IGNORE
2. **Fetch Design**: Retrieves design from database
3. **Extract from Text**: Extracts cable specifications using LLM
4. **Check Missing**: Identifies missing required attributes
5. **Validation Agent**: Validates against IEC standards with PASS/WARN/FAIL
6. **HITL Nodes**: Collects missing attributes interactively (if enabled)
7. **Re-validation**: Re-validates after HITL data collection

## Testing

Run tests:

```powershell
pytest
```

## Development

The codebase is organized to preserve the exact notebook logic:

- **DO NOT MODIFY** files in `app/langgraph/nodes/` - these are exact copies from the notebook
- **DO NOT MODIFY** `app/langgraph/workflow.py` - exact graph construction
- **DO NOT MODIFY** `app/utils/constants.py` - exact constants from notebook

All LangChain/LangGraph code is preserved exactly as-is from the notebook.

## Notes

- The validation prompt is exactly as in the notebook (200+ lines)
- All routing logic is preserved
- Confidence calibration logic is unchanged
- HITL workflow is adapted for web-based interaction (API provides values instead of input())
