# AQPG (Automated Question Paper Generation) Comprehensive Handoff Document

## 1. Project Title and Objective
- **Project Title**: Automated Question Paper Generation (AQPG) System
- **Objective**: Fine-tune transformer-based sequence-to-sequence neural networks (specifically `google/flan-t5-small`) to generate curriculum-grounded, high-entropy, subject-aligned examination questions for Indian Secondary and Higher Secondary Education (CBSE / NCERT Class 9–12 across Mathematics, Physics, Chemistry, Biology, and General Science).

---

## 2. Current Architecture Overview
The system follows a modern decoupled architecture:
1. **Frontend**: SPA built with React 18, Vite, Tailwind CSS, Lucide icons, and Axios.
2. **Backend**: Asynchronous RESTful API built with Python FastAPI, Pydantic v2, SQLAlchemy ORM, and Uvicorn.
3. **ML Pipeline**: Custom HuggingFace PyTorch fine-tuning and validation pipeline with tokenization profiling, template entropy evaluation, and ROUGE/BLEU metrics calculation.
4. **Database**: Dual-support architecture supporting MySQL (`aqpg_db`) via `mysql-connector-python` or file-based SQLite (`aqpg_audit.db`).

---

## 3. Backend Technology and Structure
- **Framework**: FastAPI (Python)
- **Directory**: `backend/`
  - `backend/app/api/v1/routes/`: Endpoint handlers (`questions.py`, `subjects.py`, `paper_generation.py`, `auth.py`, `bloom.py`).
  - `backend/app/core/`: Application settings and security config (`config.py`).
  - `backend/app/database/`: Database session, base model, schema auto-migrations (`database.py`, `seed.py`).
  - `backend/app/models/`: SQLAlchemy ORM entity definitions (`Question`, `Subject`, `Unit`, `User`, `Bloom`).
  - `backend/ml/training/`: Training scripts (`train_flan_t5_v16.py`, `train_flan_t5_v15.py`).
  - `backend/ml/evaluation/`: Evaluation scripts (`evaluate_flan_t5_v16.py`, `audit_qg_dataset_v16.py`).
  - `backend/ml/preprocessing/`: Data extraction, cleaning, and schema normalization scripts.

---

## 4. Frontend Technology and Structure
- **Framework**: React 18 + Vite
- **Directory**: `frontend/`
  - `frontend/src/pages/`: Page components (Dashboard, Question Generator, Question Bank, Settings).
  - `frontend/src/components/`: Modular UI elements (Navigation, Filters, Modal forms).
  - `frontend/src/services/`: API client services wrapper using Axios.
  - `frontend/vite.config.js`: Dev server host and port configurations.

---

## 5. Database Configuration Requirements
- **MySQL Requirements** (Production/Recommended):
  - Database Name: `aqpg_db`
  - Connection String Format: `mysql+mysqlconnector://<user>:<password>@<host>:3306/aqpg_db`
  - Automatic Schema Migration: FastAPI auto-executes column additions (`ALTER TABLE`) on startup.
- **SQLite Requirements** (Development/Fallback):
  - Automatically initializes `backend/aqpg_audit.db` if MySQL connection is unconfigured.

---

## 6. Python and Node.js Environment Requirements
- **Python Version**: Python 3.10.x or 3.13.x (64-bit Windows)
- **Node.js Version**: Node.js v18.0+ or v24.0+
- **npm Version**: npm 9.0+ or 11.0+

---

## 7. Required Dependencies
- **Backend (`backend/requirements.txt`)**:
  - `fastapi`, `uvicorn`, `sqlalchemy`, `mysql-connector-python`, `pydantic`, `python-jose`, `passlib`
  - PyTorch (`torch`), `transformers`, `datasets`, `evaluate`, `rouge-score`, `nltk`, `scikit-learn`, `numpy`, `pandas`
- **Frontend (`frontend/package.json`)**:
  - `react`, `react-dom`, `react-router-dom`, `axios`, `lucide-react`, `tailwindcss`, `vite`

---

## 8. Environment Variables Required

### `backend/.env`
```ini
DATABASE_URL=mysql+mysqlconnector://root:@localhost:3306/aqpg_db
SECRET_KEY=replace-with-a-strong-random-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
GEMINI_API_KEY=your_gemini_api_key_here
```

### `frontend/.env`
```ini
VITE_API_BASE_URL=http://127.0.0.1:8011/api/v1
```

---

## 9. Dataset Locations and Versions
- **Current Active Version**: **V16**
- **Location**: [`datasets/v16/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16)
  - `qg_dataset_v16.jsonl` (50,695 total records)
  - `qg_train_dataset_v16.jsonl` (40,557 training records — 80%)
  - `qg_validation_dataset_v16.jsonl` (10,138 validation records — 20%)
- **Legacy Datasets**: `datasets/v15/`, `datasets/v14/`, `datasets/v13/`, `datasets/v5/`, `datasets/raw/`

---

## 10. Current Model & Checkpoint Status
- **Base Architecture**: `google/flan-t5-small` (60M parameters)
- **V15 Model Checkpoint**: [`backend/ml/models/checkpoints/flan_t5_v15/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/checkpoints/flan_t5_v15) (Present — 307.8 MB)
- **V16 Target Checkpoint**: [`backend/ml/models/checkpoints/flan_t5_v16_small/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small) (Directory exists; weights pending Step 7 completion)

---

## 11. Training & Phase 20 Execution Status
- **CURRENT PHASE**: Phase 20 (V16 Model Training, Forensic Audit & Production Readiness)
- **Completed Steps**:
  - Step 1: Environment & Dependency Logging
  - Step 2: Evaluation Prompt Set Selection (520 representative prompts)
  - Step 3: Zero-Shot / Base Model Generation (`phase20_base_outputs.jsonl`)
  - Step 4: Pre-Training Data Leakage Audit (0 leakage confirmed)
  - Step 5: Hyperparameter Configuration (`v16_training_config.json`)
  - Step 6: Pre-Flight Checkpoint Directory & System RAM Verification
- **Active / Pending Step**:
  - **Step 7 — V16 FLAN-T5-Small Training**: 3 full epochs, 7,602 optimization steps, effective batch size 16.

---

## 12. Phase Roadmap & Next Steps

### Completed Phases
- **Phase 1 to 17**: Baseline setup, raw dataset accumulation, initial FLAN-T5 pilot training, evaluation schema construction.
- **Phase 18**: Forensic error analysis identifying target template over-concentration in V15.
- **Phase 19**: V16 dataset rebalancing, template ceiling capping (350 ceiling), prompt schema optimization (removing dilutive `UNKNOWN` tokens).
- **Phase 20 (Steps 1–6)**: Environment preparation, prompt freeze, pre-training audits.

### Pending Phase 20 Steps (Immediate Action Required)
- **Step 7**: Complete/Verify V16 training process.
- **Step 8**: Checkpoint Weight Verification & NaN/Inf Audit.
- **Step 9**: 520-Prompt Post-Training Evaluation (`evaluate_flan_t5_v16.py`).
- **Step 10**: Comparative Metric Analysis (Base vs V15 vs V16).
- **Step 11**: Phase 18 Quality-Gate Pass/Fail Decision.
- **Step 12**: Forensic Failure Mode Audit.
- **Step 13**: Production Model Deployment Decision.
- **Step 14**: Final Documentation & Artifact Packaging.

### Future Phase
- **Phase 21**: Real-time inference integration into FastAPI backend endpoints and React UI controls.

---

## 13. Important Scripts Inventory

| Script Path | Purpose / Description |
| :--- | :--- |
| `backend/ml/training/train_flan_t5_v16.py` | Executes PyTorch training loop for FLAN-T5-Small on V16 dataset (7,602 steps). |
| `backend/ml/evaluation/evaluate_flan_t5_v16.py` | Runs 520-prompt evaluation pipeline and computes ROUGE-L, BLEU, and structural metrics. |
| `backend/ml/evaluation/audit_qg_dataset_v16.py` | Verifies zero leakage, template distribution, and class groundedness for V16 dataset. |
| `backend/ml/evaluation/build_qg_dataset_v16.py` | Re-builds V16 dataset from raw sources with template capping and schema optimization. |
| `backend/scripts/seed_questions_from_unified.py` | Seeds initial question bank into SQL database from JSON dataset. |
| `backend/app/main.py` | Backend FastAPI application entrypoint and schema migration handler. |

---

## 14. Known Issues & Operational Gotchas
1. **Physical Checkpoint Delays**: The V16 checkpoint directory may be empty if training is in progress. Check process status before running evaluation.
2. **CPU Training Duration**: Training 7,602 steps on CPU takes ~4–6 hours depending on hardware. GPU execution recommended if CUDA is available.
3. **Python Path Environment Variable**: On Windows PowerShell, python scripts under `backend/ml/` require setting `env:PYTHONPATH="."` from the `backend/` root directory.

---

## 15. Standard Command Reference

### Run Backend API
```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8011
```

### Run Frontend Development Server
```powershell
cd frontend
npm run dev
```

### Continue / Run V16 Model Training
```powershell
# From project root
$env:PYTHONPATH="backend"
python backend/ml/training/train_flan_t5_v16.py
```

### Run V16 Model Evaluation Pipeline
```powershell
# From project root
$env:PYTHONPATH="backend"
python backend/ml/evaluation/evaluate_flan_t5_v16.py
```

---

## 16. Invariant Files (DO NOT MODIFY)
> [!CAUTION]
> The following files represent locked experimental baselines and MUST NOT be edited or overwritten:
> - `datasets/v16/qg_dataset_v16.jsonl`
> - `datasets/v16/qg_train_dataset_v16.jsonl`
> - `datasets/v16/qg_validation_dataset_v16.jsonl`
> - `v16_training_config.json`
> - `v16_prompt_schema.json`
> - `phase20_evaluation_prompts.jsonl`
> - `phase20_base_outputs.jsonl`

---

## 17. Large Files Exclusion List
The following paths exceed standard Git limits and should be synced via Cloud Storage (Google Drive / OneDrive):
- `backend/.venv/` (~2.0 GB)
- `frontend/node_modules/` (~60 MB)
- `backend/ml/models/checkpoints/` (~600 MB - 1.2 GB)
- `datasets/raw/` (~300 MB)
