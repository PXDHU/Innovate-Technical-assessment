# Quick Start Guide - Backend Setup

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Google Gemini API Key

## Step-by-Step Setup

### 1. Navigate to Backend Directory

```powershell
cd backend
```

### 2. Create and Activate Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Setup PostgreSQL Database

Open PostgreSQL and create the database:

```sql
CREATE DATABASE cable_validation;
CREATE USER cable_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cable_validation TO cable_user;
```

### 5. Configure Environment

Copy `.env.example` to `.env`:

```powershell
copy .env.example .env
```

Edit `.env` and update:

```env
DATABASE_URL=postgresql://cable_user:your_password@localhost:5432/cable_validation
GOOGLE_API_KEY=your_actual_google_api_key_here
```

### 6. Seed Database

```powershell
python seed_db.py
```

Expected output:
```
Seeding database with designs from notebook...
✅ Seeded 2 designs from notebook
   - DESIGN-001
   - DESIGN-002
```

### 7. Run the Server

```powershell
python -m app.main
```

Or:

```powershell
uvicorn app.main:app --reload
```

### 8. Verify Installation

Open your browser and go to:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/health (Health check)

### 9. Test the API

Try a validation request:

```powershell
curl -X POST http://localhost:8000/api/validations/validate `
  -H "Content-Type: application/json" `
  -d '{\"user_input\": \"Validate DESIGN-001\", \"hitl_mode\": false}'
```

## Troubleshooting

### Database Connection Error

If you see `could not connect to server`:
1. Make sure PostgreSQL is running
2. Verify DATABASE_URL in `.env`
3. Check PostgreSQL is listening on port 5432

### LLM API Error

If you see `API key not found`:
1. Verify GOOGLE_API_KEY in `.env`
2. Make sure the API key is valid
3. Check you have quota remaining

### Import Errors

If you see `ModuleNotFoundError`:
1. Make sure virtual environment is activated
2. Run `pip install -r requirements.txt` again

## Next Steps

Once the backend is running:
1. Test all API endpoints in Swagger UI
2. Proceed to frontend setup
3. Test the full-stack integration

## Notes

- The backend preserves 100% of the notebook's LangChain/LangGraph logic
- All validation prompts and routing are exact copies
- Database schema matches the notebook's data structures
