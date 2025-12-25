# Quick Start - Frontend
## Step 1: Ensure Backend is Running
Make sure the backend server is running on `http://localhost:8000`
```powershell
cd backend
python -m app.main
```
Verify at: http://localhost:8000/health
## Step 2: Start Frontend Server
Navigate to frontend directory:
```powershell
cd frontend
```
Start a local server using Python:
```powershell
python -m http.server 3000
```
## Step 3: Open in Browser
Open your browser and go to:
```
http://localhost:3000
```
## Step 4: Test the Application
1. **Try a sample validation:**
   - Enter: `DESIGN-001`
   - Click "Validate Design"
   - Watch the workflow visualization
   - View color-coded results
2. **Check history:**
   - History panel updates automatically
   - Click any item to view details
3. **Try HITL mode:**
   - Enable the toggle
   - Enter a design query
   - Provide feedback when prompted
## Troubleshooting
### CORS Error?
Make sure backend CORS is configured for `http://localhost:3000`
Check `backend/app/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
### Backend Not Running?
Start the backend first:
```powershell
cd backend
.\\venv\\Scripts\\Activate
python -m app.main
```
---
**That's it! You're ready to validate cable designs! 🚀**
