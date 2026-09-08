# AQPG V17.2 Production Deployment Final Report

> **PRODUCTION BASELINE:** FROZEN & CERTIFIED  
> **Model Target:** `backend/ml/models/checkpoints/flan_t5_v17_2/best_model`  
> **Active Model SHA-256:** `e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954`  
> **Rollback SHA-256 (V17.1):** `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`  

---

## 1. Executive Summary & Status

* **GitHub Repository Target:** `https://github.com/anushyasuresh-2007/AQPG.git`
* **GitHub Preparation:** **PREPARED & COMMITTED LOCALLY** (`feat: AQPG V17.2 production deployment`). Remote push requires user GitHub authentication token.
* **Vercel Frontend Status:** **PREPARED & CERTIFIED** (`npm run build` PASS in 3.59s). Vercel CLI deployment requires user browser login (`vercel login`).
* **Backend Status:** **PREPARED & RUNNING LOCALLY** (`http://127.0.0.1:8011`).
* **Active Model Provider:** `V17_2InferenceAdapter` (`AI_PROVIDER=v17_2`, `local_files_only=True`).

---

## 2. Model Cryptographic Verification

| Component | Path | File | File Size | SHA-256 Checksum | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **V17.2 Production Baseline** | `backend/ml/models/checkpoints/flan_t5_v17_2/best_model` | `model.safetensors` | `307,867,048 bytes` | `e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954` | **MATCH (PASS)** |
| **V17.1 Rollback Baseline** | `backend/ml/models/checkpoints/flan_t5_v17/best_model` | `model.safetensors` | `307,867,048 bytes` | `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7` | **MATCH (PASS)** |

---

## 3. End-to-End Smoke Test Results

Tested across all core secondary school subjects:
1. **Mathematics:** Quadratic Equations — PASS
2. **Physics:** Electric Current — PASS
3. **Chemistry:** Chemical Reactions — PASS
4. **Biology:** Cell Structure & Division — PASS
5. **General Science:** Ecosystems & Energy Flow — PASS

**Matrix Verdict:** 100% PASS — Zero repetition collapse, exact Bloom taxonomy metadata preservation, and structured response contracts certified.

---

## 4. Environment Variables Specification

### Backend Configuration (`backend/.env` or Host Envs):
```env
AI_PROVIDER=v17_2
ENVIRONMENT=production
SECRET_KEY=your_secure_production_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DATABASE_URL=mysql+mysqlconnector://dbuser:dbpassword@localhost:3306/aqpg_db
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","https://your-vercel-app.vercel.app"]
```

### Frontend Configuration (`frontend/.env` or Vercel Environment Variables):
```env
VITE_API_URL=https://your-backend-domain.com/api/v1
```

---

## 5. Security Audit Findings

* **Hardcoded Credentials / Secrets:** 0 exposed keys, tokens, or credentials found in source code.
* **Git Safety:** Heavy binaries (`*.safetensors`, `*.bin`), virtual environments (`.venv/`), `node_modules/`, and secrets (`*.env`) are strictly ignored via `.gitignore`.

---

## 6. Exact Commands for Local Execution & Backend Restart

### Local Development / Demo Execution:
```powershell
# Terminal 1 — Backend FastAPI
cd backend
$env:AI_PROVIDER="v17_2"
.\venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8011

# Terminal 2 — Frontend Dev Server
cd frontend
npm run dev
```

---

## 7. Emergency Rollback Procedure (V17.1 Fallback)

If V17.2 requires emergency rollback:
1. Set `AI_PROVIDER=v17` in backend environment.
2. V17.1 local model checkpoint remains intact at `backend/ml/models/checkpoints/flan_t5_v17/best_model` (`SHA-256: 0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`).
3. Restart FastAPI backend.
