# AQPG V17.2 — GitHub & Vercel Production Deployment Guide

> **PRODUCTION BASELINE STATUS:** FROZEN & CERTIFIED  
> **Model Target:** `backend/ml/models/checkpoints/flan_t5_v17_2/best_model`  
> **Model SHA-256:** `e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954`  
> **Rollback SHA-256 (V17.1):** `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`  

---

## 1. Project Architecture Overview

```
 ┌────────────────────────┐      HTTPS / REST      ┌─────────────────────────────────┐
 │   Vercel Cloud Host    │ ─────────────────────► │ Backend Server (Cloud / On-Prem)│
 │ (Vite + React Frontend)│                        │       (FastAPI + Uvicorn)       │
 └────────────────────────┘                        └────────────────┬────────────────┘
                                                                    │
                                                           Local PyTorch Inference
                                                                    │
                                                                    ▼
                                                   ┌─────────────────────────────────┐
                                                   │    FLAN-T5 V17.2 Local Model    │
                                                   │ (best_model/model.safetensors)  │
                                                   └─────────────────────────────────┘
```

* **Frontend:** Built with Vite + React 18, deployed to Vercel.
* **Backend:** FastAPI + Uvicorn server hosting `V17_2InferenceAdapter` with PyTorch CPU/GPU inference.
* **ML Model:** Local FLAN-T5 fine-tuned model checkpoint (307 MB) loaded with `local_files_only=True`. Never package the 307 MB model into Vercel static output.

---

## 2. GitHub Preparation

Before pushing the codebase to GitHub, verify that sensitive credentials, virtual environments, and heavy node modules are strictly ignored.

### Git Configuration Check
Check that `.gitignore` contains:
```gitignore
# Virtual Envs & Python Cache
.venv/
venv/
__pycache__/
*.pyc
*.env

# Node Dependencies & Build Output
node_modules/
dist/
build/
.vite/

# Logs & Storage
*.log
uploads/
generated_papers/
```

### Commands to Initialize and Push Codebase to GitHub:
```powershell
# 1. Initialize repository (if not already initialized)
git init

# 2. Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/AQPG.git

# 3. Stage and commit source files
git add .
git commit -m "feat: prepare AQPG V17.2 production baseline deployment"

# 4. Push to main branch
git branch -M main
git push -u origin main
```

---

## 3. Vercel Frontend Deployment Steps

### Option A: Via Vercel Dashboard (Recommended)
1. Log in to [Vercel](https://vercel.com).
2. Click **Add New** ➜ **Project**.
3. Import your GitHub repository (`AQPG`).
4. Set the **Root Directory** to `frontend`.
5. Configure Environment Variables:
   * Key: `VITE_API_URL`
   * Value: `https://your-backend-domain.com/api/v1` (or your backend public URL)
6. Click **Deploy**.

### Option B: Via Vercel CLI
```powershell
# From the frontend directory:
cd frontend
npm install -g vercel
vercel --prod
```

---

## 4. Backend Deployment Requirements

The backend requires a server environment capable of running Python 3.10 and executing PyTorch CPU inference (e.g. AWS EC2, DigitalOcean Droplet, Render Web Service, Hetzner, or On-Premises Docker host).

### Backend Startup Command:
```powershell
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8011
```

---

## 5. Required Environment Variables

### Backend Environment Variables (`backend/.env` or Host Environment):
```env
AI_PROVIDER=v17_2
ENVIRONMENT=production
SECRET_KEY=generate_a_secure_random_production_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=mysql+mysqlconnector://dbuser:dbpassword@localhost:3306/aqpg_db
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","https://your-vercel-app.vercel.app"]
```

### Frontend Environment Variables (`frontend/.env` or Vercel Environment Variables):
```env
VITE_API_URL=https://your-backend-domain.com/api/v1
```

---

## 6. CORS Configuration

The backend CORS middleware in `backend/app/main.py` enforces domain isolation:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Ensure your production Vercel frontend URL (e.g. `https://aqpg-frontend.vercel.app`) is included in `BACKEND_CORS_ORIGINS`.

---

## 7. Model Storage & Protection Requirements

* The V17.2 local model directory [`backend/ml/models/checkpoints/flan_t5_v17_2/best_model`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/checkpoints/flan_t5_v17_2/best_model) **MUST** remain intact on the backend host machine.
* Do not delete or modify `model.safetensors` (`SHA-256: e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954`).
* Do not remove `local_files_only=True` in `v17_2_inference_adapter.py`.

---

## 8. Local Development Commands

```powershell
# Terminal 1 — Start Backend Server
cd backend
$env:AI_PROVIDER="v17_2"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8011

# Terminal 2 — Start Frontend Dev Server
cd frontend
npm run dev
```

---

## 9. Production Deployment Considerations

1. **Static Output Exclusions:** Never attempt to bundle `node_modules` or `.venv` into production zips or Vercel uploads.
2. **Model Integrity Audit:** Verify SHA-256 checksums after transferring files to production servers:
   ```powershell
   CertUtil -hashfile backend/ml/models/checkpoints/flan_t5_v17_2/best_model/model.safetensors SHA256
   ```
3. **Database Migration Safety:** Startup schema checks in `app/main.py` automatically apply safe `ALTER TABLE ADD COLUMN IF NOT EXISTS` migrations without data loss.

---

## 10. Rollback Procedure (Instant V17.1 Fallback)

If V17.2 needs emergency rollback:
1. Update `AI_PROVIDER=v17` in backend `.env`.
2. V17.1 checkpoint is preserved at `backend/ml/models/checkpoints/flan_t5_v17/best_model` (`SHA-256: 0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`).
3. Restart FastAPI server.
