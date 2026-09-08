# Automated Question Paper Generation System

AQPG is a full-stack question paper generator built with FastAPI for the backend and React + Vite for the frontend. The current implementation includes authentication, CRUD management for subjects, units, questions, and Bloom levels, plus question paper generation from the stored question bank.

## Project structure

- `backend/` — FastAPI application with SQLAlchemy, JWT authentication, CRUD helpers, and generation services
- `frontend/` — React + Vite client with protected routes and API-driven pages
- `docs/` — Additional design and documentation notes

## Environment configuration

Create local environment files before running the app:

- Backend: `backend/.env`
- Frontend: `frontend/.env`

Recommended values:

- Backend:
  - `DATABASE_URL=...`
  - `SECRET_KEY=replace-me-with-a-strong-random-secret`
  - `ALGORITHM=HS256`
  - `ACCESS_TOKEN_EXPIRE_MINUTES=60`
- Frontend:
  - `VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1`

## Run the project

### Backend

1. Create and activate a virtual environment:
   - PowerShell: `python -m venv .venv` then `.\.venv\Scripts\Activate.ps1`
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Start the API:
   - `cd backend`
   - `uvicorn app.main:app --host 127.0.0.1 --port 8000`

### Frontend

1. Install dependencies:
   - `cd frontend`
   - `npm install`
2. Start the Vite client:
   - `npm run dev`

## Validation

- Backend API docs: `http://127.0.0.1:8000/docs`
- Frontend app: the local Vite URL shown in the terminal, typically `http://127.0.0.1:5173` or the next available port

## Notes

The current implementation is already wired for JWT-based authentication and protected CRUD routes. The frontend uses the backend API directly and keeps the current API contract unchanged.
