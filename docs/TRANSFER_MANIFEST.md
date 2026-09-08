# AQPG Project File Transfer Manifest

This document categorizes all project files and directories for transferring the codebase from the primary development environment to a target machine.

---

## Transfer Classification Matrix

| Category | Description | Recommended Transfer Channel | Total Size |
| :--- | :--- | :--- | :--- |
| **A. MUST TRANSFER** | Core source code, configuration, scripts, requirements, documentation | Git / Repository Sync / Zip | **~5.5 MB** |
| **B. SHOULD TRANSFER** | Active V16 dataset, audit schemas, phase 17–20 report metadata | Zip / Git LFS / Direct Copy | **~75 MB** |
| **C. DO NOT TRANSFER** | Virtual environments, node modules, temporary caches, OS metadata | Exclude entirely | **~2.1 GB** |
| **D. REGENERABLE** | SQLite runtime databases, transient generation outputs | Re-generate via script | **~1.2 MB** |
| **E. LARGE FILES** | Pre-trained model weights, legacy datasets, raw web dumps | Cloud Storage (Google Drive/OneDrive) | **~1.2 GB** |

---

## Detailed File Breakdown

### Category A: MUST TRANSFER (Essential Source & Config) — ~5.5 MB
- **Backend Application Code**:
  - [`backend/app/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/app) (routers, models, schemas, core config, database setup)
  - [`backend/scripts/seed_questions_from_unified.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/scripts/seed_questions_from_unified.py)
  - [`backend/requirements.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/requirements.txt)
  - [`backend/Dockerfile`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/Dockerfile)
- **Frontend Code**:
  - [`frontend/src/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/frontend/src) (React components, pages, services)
  - [`frontend/package.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/frontend/package.json) & [`package-lock.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/frontend/package-lock.json)
  - [`frontend/vite.config.js`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/frontend/vite.config.js), [`tailwind.config.js`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/frontend/tailwind.config.js)
- **ML Training & Evaluation Scripts**:
  - [`backend/ml/training/train_flan_t5_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/training/train_flan_t5_v16.py)
  - [`backend/ml/training/validate_env_and_recheck_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/training/validate_env_and_recheck_v16.py)
  - [`backend/ml/training/train_flan_t5_v15.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/training/train_flan_t5_v15.py)
  - [`backend/ml/evaluation/build_qg_dataset_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/build_qg_dataset_v16.py)
  - [`backend/ml/evaluation/audit_qg_dataset_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/audit_qg_dataset_v16.py)
  - [`backend/ml/evaluation/evaluate_flan_t5_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/evaluate_flan_t5_v16.py)
  - [`backend/ml/evaluation/evaluate_flan_t5_v15.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/evaluate_flan_t5_v15.py)
  - [`backend/ml/preprocessing/acquire_phase15_data.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/preprocessing/acquire_phase15_data.py)
- **Configuration & Schemas**:
  - [`v16_training_config.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v16_training_config.json)
  - [`v16_prompt_schema.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v16_prompt_schema.json)
  - [`qg_dataset_v16_schema.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/qg_dataset_v16_schema.json)
  - [`v15_training_config.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_training_config.json)
  - [`docker-compose.yml`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docker-compose.yml)
  - [`.env.example`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/.env.example) & [`backend/.env.example`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/.env.example)
- **Documentation**:
  - [`docs/`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docs) (`PROJECT_HANDOFF.md`, `SETUP_FOR_NEW_DEVELOPER.md`, `CURRENT_STATUS.md`, `TRANSFER_MANIFEST.md`, `HANDOFF_SUMMARY.md`)
  - [`README.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/README.md) & [`implementation_notes_v12.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/implementation_notes_v12.md) to `v19.md`

### Category B: SHOULD TRANSFER (Active V16 Datasets & Phase Reports) — ~75 MB
- **V16 Prepared Datasets**:
  - [`datasets/v16/qg_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_dataset_v16.jsonl) (34.3 MB)
  - [`datasets/v16/qg_train_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_train_dataset_v16.jsonl) (27.5 MB)
  - [`datasets/v16/qg_validation_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_validation_dataset_v16.jsonl) (6.8 MB)
- **Phase Reports & Prompts**:
  - [`phase20_evaluation_prompts.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase20_evaluation_prompts.jsonl) (196 KB)
  - [`phase20_environment.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase20_environment.json)
  - [`phase19_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_audit.json), `phase18_report.txt`, `phase17_evaluation_report.txt`

### Category C: DO NOT TRANSFER (System Dependent / Local Caches) — ~2.1 GB
- **Virtual Environments & Node Modules**:
  - `backend/.venv/` (1,995 MB - Must be re-created on target machine)
  - `frontend/node_modules/` (59.7 MB - Must be re-created via `npm install`)
- **Transient Caches & Build Out**:
  - `.pytest_cache/`, `backend/ml/preprocessing/__pycache__/`, `frontend/dist/`, `test_out/`
  - `.vscode/` (Local IDE user preferences)

### Category D: REGENERABLE (Local Runtime Assets) — ~1.2 MB
- **SQLite Databases**:
  - `backend/aqpg_audit.db` (53 KB) & `backend/scripts/aqpg.db` (753 KB) - Regenerated by backend startup migrations & seeding script.
- **Base Output Dumps**:
  - `phase20_base_outputs.jsonl` (190 KB) - Generated during Phase 20 Step 6, can be re-run if needed.

### Category E: LARGE FILES — USE CLOUD STORAGE / GOOGLE DRIVE — ~1.2 GB
- **Trained Model Checkpoints**:
  - `backend/ml/models/checkpoints/flan_t5_v15/model.safetensors` (307.8 MB)
  - `backend/ml/models/checkpoints/flan_t5_v15_smoke/model.safetensors` (307.8 MB)
  - `backend/ml/models/checkpoints/flan_t5_v16_small/model.safetensors` (~308 MB when Step 7 finishes)
- **Legacy Dataset Dumps**:
  - `datasets/raw/` (Raw NCERT, SQuAD, EduQG files) (~300 MB)
  - `datasets/v13/`, `datasets/v14/`, `datasets/v15/`, `datasets/v5/` (~300 MB)

---

## Security & Secrets Compliance

> [!IMPORTANT]
> - Do **NOT** copy or upload active `.env` files containing real API keys or database passwords to public repositories.
> - Use [`.env.example`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/.env.example) to share required configuration keys with placeholders.
