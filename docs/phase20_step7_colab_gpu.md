# AQPG PHASE 20 V16 — REPRODUCIBLE TRAINING & EVALUATION PIPELINE GUIDE

This document provides complete instructions for executing the **AQPG Phase 20 V16 Clean Deterministic Rebuild and Evaluation Pipeline** on **Google Colab GPU**.

---

## 1. Locked Experimental Configuration Matrix

| Parameter / Artifact | Locked Value |
| :--- | :--- |
| **Base Model** | `google/flan-t5-small` |
| **Train Dataset** | `datasets/v16/qg_train_dataset_v16.jsonl` (40,557 records) |
| **Train Dataset SHA-256** | `FFD14E48A376F66CC85F38C907CC2A1CD4BFBD0C7FF9DC49534A4129506C8A90` |
| **Validation Dataset** | `datasets/v16/qg_validation_dataset_v16.jsonl` (10,138 records) |
| **Val Dataset SHA-256** | `E6A5CCD54E14CEB321FF09CB2194DD7107CF114AB07F8C17792E1C4F81679DC0` |
| **Evaluation Set** | `phase20_evaluation_prompts.jsonl` (520 prompts) |
| **Evaluation Set SHA-256** | `91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E` |
| **Total Target Epochs** | `3` |
| **Batches Per Epoch** | `5,069` |
| **Per-Device Batch Size** | `8` |
| **Gradient Accumulation** | `2` |
| **Effective Batch Size** | `16` |
| **Total Optimization Steps**| `7,603` |
| **Learning Rate** | `3e-4` |
| **Warmup Steps** | `380` |
| **Optimizer** | `AdamW` (`weight_decay=0.01`) |
| **Random Seed** | `42` (Locked) |
| **Local Save Path (SSD)** | `/content/aqpg_v16_local_model` |
| **Drive Destination Path** | `/content/drive/MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small/` |

---

## 2. Seven-Cell Logical Pipeline (`docs/phase20_step7_colab_gpu.ipynb`)

1. **CELL A — Environment Setup, GPU Check & Artifact Protection**  
   *Mounts Google Drive, verifies CUDA GPU accelerator, defines canonical paths (`DRIVE_MODEL_DIR`, `LOCAL_MODEL_DIR`, `EVAL_SCRIPT`, `EVAL_PROMPTS`), and protects existing artifacts.*
2. **CELL B — V16 Configuration & Dataset/Prompt Integrity Audit**  
   *Read-only verification of dataset record counts (40,557 train / 10,138 val) and SHA-256 checksums (`FFD14E48...`, `E6A5CCD5...`, `91335C1E...`). Fails closed on any mismatch.*
3. **CELL C — Clean V16 Training with Local SSD Persistence**  
   *Executes clean 3-epoch training from seed 42, persisting intermediate and final model weights exclusively to local Colab SSD (`/content/aqpg_v16_local_model`). Asserts local `model.safetensors` > 300 MB.*
4. **CELL D — Drive Synchronization, SHA-256 Verification & Independent Reload**  
   *Copies local model files to Google Drive, asserts `drive_size == local_size` AND `drive_sha256 == local_sha256`, reloads model from Drive, and executes 1-sentence inference smoke test.*
5. **CELL E — Phase 20 Step 8 Model Integrity Verification**  
   *Audits 76,961,152 total parameters, 0 NaN, 0 Inf on the reloaded Drive model.*
6. **CELL F — Step 9 Pre-Evaluation Gate**  
   *Validates script, prompt set, model file (>300 MB), SHA-256 checksums, and Step 8 audit $\to$ sets `READY FOR CELL G = True`.*
7. **CELL G — Step 9: 520 Controlled Prompt Post-Training Evaluation**  
   *Executes `evaluate_flan_t5_v16.py` against unchanged 520 prompts on GPU.*

---

## 3. Strict Safety Boundaries

- **Local SSD First:** Model binary writes occur exclusively on local Colab SSD (`/content/aqpg_v16_local_model`) to prevent Google Drive FUSE write drops.
- **Fail-Closed Verification:** Drive `model.safetensors` is accepted only if `os.path.getsize() > 300_000_000` bytes, `drive_sha256 == local_sha256`, and independent HuggingFace model reload succeeds.
- **Protected Artifacts:** Datasets (`qg_train_dataset_v16.jsonl`, `qg_validation_dataset_v16.jsonl`) and evaluation prompts (`phase20_evaluation_prompts.jsonl`) are strictly locked and read-only.
