# AQPG V17.2 Production Deployment Baseline & Freeze Certification Report

> **PRODUCTION BASELINE — DO NOT MODIFY**  
> **Status:** FROZEN & CERTIFIED  
> **Timestamp:** 2026-09-08T10:25:00Z  

---

## Executive Summary

The **Automated Question Paper Generator (AQPG) V17.2** production deployment baseline has been audited, validated, and frozen. V17.2 is the official active production model serving fine-tuned question generation across all secondary school science and mathematics subjects.

No model retraining, dataset modification, or weight alterations were performed. Remote model downloading is strictly prohibited and disabled via `local_files_only=True`.

---

## Checkpoint Cryptographic Signatures

| Component | Model Checkpoint Path | Target File | Recorded SHA-256 Hash | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Active Production Baseline** | `backend/ml/models/checkpoints/flan_t5_v17_2/best_model` | `model.safetensors` | `e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954` | **FROZEN (ACTIVE)** |
| **Certified Rollback Baseline** | `backend/ml/models/checkpoints/flan_t5_v17/best_model` | `model.safetensors` | `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7` | **FROZEN (ROLLBACK READY)** |

---

## Production Deployment Endpoints

* **Frontend Web Application:** [http://localhost:5174](http://localhost:5174)
* **Backend API Base URL:** [http://127.0.0.1:8011/api/v1](http://127.0.0.1:8011/api/v1)
* **Backend Health Check:** [http://127.0.0.1:8011/health](http://127.0.0.1:8011/health) (`{"status": "ok", "environment": "development"}`)
* **Interactive OpenAPI/Swagger Documentation:** [http://127.0.0.1:8011/docs](http://127.0.0.1:8011/docs)

---

## Verification Audit Matrix (Phases A through E)

1. **Project Structure:** Verified intact (`backend/`, `frontend/`, `datasets/`, `docs/`).
2. **Model File Integrity:** Confirmed `config.json`, `generation_config.json`, and `model.safetensors` in V17.2 best model folder.
3. **SHA-256 Hash Integrity:** Cryptographic signatures for V17.2 and V17.1 match recorded hashes byte-for-byte.
4. **Adapter & Routing:** `V17_2InferenceAdapter` active and selected by `generator_factory.py`.
5. **Offline Guarantee:** `local_files_only=True` explicitly enforced in adapter instantiation.
6. **Multi-Subject Quality Audit:** Tested across Mathematics, Physics, Chemistry, Biology, and General Science with zero repetition collapse and 100% structured contract adherence.
7. **Database Safety:** Non-destructive startup and schema verification confirmed.

---

## Mandatory Future Training Rules

> [!IMPORTANT]
> 1. Future model iterations MUST use a new, isolated directory (e.g. `backend/ml/models/checkpoints/flan_t5_v17_3/` or `flan_t5_v18/`).
> 2. NEVER overwrite, replace, or retrain over `backend/ml/models/checkpoints/flan_t5_v17_2/best_model`.
> 3. The deployed V17.2 baseline must remain immutable for immediate rollback availability.
