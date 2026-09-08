# AQPG Developer Handoff Summary

This document provides a concise, practical guide for handing over the **AQPG (Automated Question Paper Generation)** project to your developer colleague.

---

## 1. Five Critical Handoff Questions

### Q1: What does she need to do first?
1. Copy or clone the project source files onto her machine.
2. Set up a Python 3.10/3.13 virtual environment in `backend/.venv` and install `backend/requirements.txt`.
3. Run `npm install` in `frontend/`.
4. Check if `backend/ml/models/checkpoints/flan_t5_v16_small/model.safetensors` exists on her machine or cloud link before touching ML scripts.

### Q2: What files does she need?
- **All source code**: `backend/app/`, `frontend/src/`, `backend/scripts/`, `backend/ml/`.
- **Config & schemas**: `v16_training_config.json`, `v16_prompt_schema.json`, `.env.example`.
- **Active V16 dataset**: `datasets/v16/qg_train_dataset_v16.jsonl` & `qg_validation_dataset_v16.jsonl`.
- **Phase 20 evaluation set**: `phase20_evaluation_prompts.jsonl`.
- **Model Checkpoints**: Download V15 and V16 safety tensors from Google Drive / Cloud storage.

### Q3: What should she NOT touch?
- **Do NOT modify or re-run V16 dataset generation**: `datasets/v16/*` are locked and verified for zero leakage.
- **Do NOT alter prompt schemas**: `v16_prompt_schema.json` and `v16_training_config.json` must remain intact.
- **Do NOT delete previous phase reports**: All `phase17_*`, `phase18_*`, `phase19_*`, and `implementation_notes_*.md` files represent frozen forensic history.

### Q4: What is the exact next phase?
- **Current Phase**: **Phase 20**
- **Current Step**: **Step 7 (V16 FLAN-T5-Small Training)** / **Step 8 (Checkpoint NaN/Inf Verification)**.

### Q5: How does she continue without repeating completed work?
- Phases 1 through 19 and Phase 20 Steps 1–6 are **already completed**.
- Once the V16 model safety tensors file (`model.safetensors`) is present in `backend/ml/models/checkpoints/flan_t5_v16_small/`, she should immediately start at **Step 9 — Post-Training 520-Prompt Evaluation** by executing:
  ```powershell
  python backend/ml/evaluation/evaluate_flan_t5_v16.py
  ```

---

## 2. Safety Rules Compliance

> [!CAUTION]
> 1. Do **NOT** restart training automatically if it is currently running on the primary computer.
> 2. Do **NOT** launch Phase 21 production integration until Phase 20 evaluation quality gates pass.
> 3. Do **NOT** overwrite existing V15 or V16 model checkpoints.
> 4. Do **NOT** push `.env` files containing actual passwords or secret keys to Git.

---

## 3. Final Handoff Transfer Deliverables

### 1. Exact List of Files/Directories to Transfer

#### Via Git / Zip Archive:
- `backend/app/`
- `backend/ml/` (scripts, training, evaluation, preprocessing)
- `backend/scripts/`
- `backend/requirements.txt` & `backend/Dockerfile`
- `frontend/src/` & `frontend/public/`
- `frontend/package.json` & `frontend/package-lock.json`
- `frontend/vite.config.js` & `frontend/tailwind.config.js`
- `docs/` (`PROJECT_HANDOFF.md`, `SETUP_FOR_NEW_DEVELOPER.md`, `CURRENT_STATUS.md`, `TRANSFER_MANIFEST.md`, `HANDOFF_SUMMARY.md`)
- `datasets/v16/` (`qg_dataset_v16.jsonl`, `qg_train_dataset_v16.jsonl`, `qg_validation_dataset_v16.jsonl`)
- Configuration & reports: `v16_training_config.json`, `v16_prompt_schema.json`, `qg_dataset_v16_schema.json`, `phase20_evaluation_prompts.jsonl`, `phase20_environment.json`, `implementation_notes_*.md`, `.env.example`

#### Via Google Drive / Cloud Storage / Git LFS:
- `backend/ml/models/checkpoints/flan_t5_v15/model.safetensors` (307.8 MB)
- `backend/ml/models/checkpoints/flan_t5_v16_small/model.safetensors` (~308 MB when training completes)

### 2. Approximate Total Transfer Size
- **Source Code + Config + Docs**: **~5.5 MB**
- **V16 Datasets & Phase Reports**: **~75 MB**
- **Codebase Total (excluding `.venv`, `node_modules`, checkpoints)**: **~80 MB**
- **Model Weights (Checkpoints via Cloud)**: **~615 MB** (FLAN-T5-V15 + FLAN-T5-V16)

### 3. Whether Git/GitHub is Sufficient
- **Yes**, Git/GitHub is sufficient for all source code, documentation, config files, and the V16 datasets (80 MB total).
- Standard GitHub file limit is 100 MB per file, and all V16 `.jsonl` files are under 35 MB.

### 4. Which Files Need Google Drive / OneDrive / Git LFS Instead
- Model checkpoint weight files (`model.safetensors` files ~308 MB each) exceed standard Git limits and should be shared via **Google Drive**, **OneDrive**, or **Git LFS**.
- `backend/.venv/` (2.0 GB) and `frontend/node_modules/` (60 MB) must **NOT** be transferred and should be re-installed using `pip` and `npm`.

### 5. Exact First Command She Should Run After Receiving the Project

```powershell
# Step 1: Open PowerShell in project root and verify system setup
cd AQPG; Get-Content docs/SETUP_FOR_NEW_DEVELOPER.md
```
Then follow the setup instructions to create `.venv`, run `pip install -r backend/requirements.txt`, and launch the backend verification:
```powershell
cd backend; .venv\Scripts\Activate.ps1; python -m uvicorn app.main:app --reload --port 8011
```
