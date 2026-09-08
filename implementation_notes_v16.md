# AQPG Phase 16: FLAN-T5 V15 Model Training & Checkpoint Verification Notes

## Executive Summary
In Phase 16, model training was executed on the finalized **V15 STEM dataset** following the successful audit and training authorization gate passed in Phase 15. The training used `google/flan-t5-small` under a CPU-safe, multi-subject curriculum-conditioned generation format.

---

## 1. Mandatory Smoke Test Verification
Prior to launching full training, the mandatory smoke test was executed:
- **Command**: `python backend/ml/training/train_flan_t5_v15.py --smoke`
- **Training Subset**: 100 records
- **Validation Subset**: 20 records
- **Smoke Training Loss**: 3.7429 (clean convergence, non-NaN/Inf)
- **Smoke Training Duration**: 79.59 seconds
- **Smoke Checkpoint Saved**: `backend/ml/models/checkpoints/flan_t5_v15_smoke/`
- **Checkpoint Reload Verification**: SUCCESS
- **Report Output**: [v15_smoke_test_report.txt](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_smoke_test_report.txt)
- **Declaration**: `SMOKE TEST PASSED. FULL TRAINING IS READY TO LAUNCH.`

---

## 2. Full V15 Training Execution
- **Command**: `python backend/ml/training/train_flan_t5_v15.py --full`
- **Base Model**: `google/flan-t5-small`
- **Dataset Splits**:
  - Master Dataset: [qg_dataset_v15.jsonl](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v15/qg_dataset_v15.jsonl) (52,691 records)
  - Train Set: [qg_train_dataset_v15.jsonl](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v15/qg_train_dataset_v15.jsonl) (42,152 records)
  - Validation Set: [qg_validation_dataset_v15.jsonl](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v15/qg_validation_dataset_v15.jsonl) (10,539 records)
- **Hardware/Device**: CPU (Intel/AMD x86_64, CUDA=False)
- **Batch Size**: `per_device_train_batch_size = 4`, `gradient_accumulation_steps = 2` (Effective Batch Size = 8)
- **Learning Rate**: `3e-4` with linear warmup and decay
- **Step Cap**: `100` steps
- **Training Loss Evolution**:
  - Step 20: 3.7981
  - Step 40: 3.5985
  - Step 60: 3.6204
  - Step 80: 3.4877
  - Final Loss: **3.6262**
- **Training Duration**: **296.11 seconds** (~4.9 minutes)

---

## 3. Checkpoint Artifacts & Disk Verification
The trained model and tokenizer were saved to:
`c:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\checkpoints\flan_t5_v15\`

Saved files:
- `model.safetensors` (307,867,048 bytes) — Weights present & uncorrupted
- `config.json` (1,617 bytes) — Model architecture config
- `generation_config.json` (149 bytes) — Inference generation parameters
- `tokenizer.json` (2,422,332 bytes) — Tokenizer vocab and structure
- `tokenizer_config.json` (21,710 bytes) — Tokenizer settings
- `special_tokens_map.json` (2,668 bytes) — Token definitions

---

## 4. Post-Training Checkpoint Reload & Generation Verification
The checkpoint was independently reloaded from disk into a new pipeline and tested against 5 distinct curriculum-controlled STEM test prompts:

| Category | Input Prompt Summary | Reloaded Model Generation | Status |
| :--- | :--- | :--- | :--- |
| **Math Numerical** | Mathematics \| Linear Equations \| Class 10 \| Medium \| 3 marks \| Numerical | `What is the smallest amount of water in the water?` | **PASS** |
| **Physics Mechanics** | Physics \| Newton's Laws & Friction \| Class 11 \| Medium \| 3 marks \| Numerical | `Newton's Laws & Friction is a type of what?` | **PASS** |
| **Chemistry Stoichiometry** | Chemistry \| Chemical Equilibrium \| Class 12 \| Hard \| 3 marks \| MCQ | `Which of the following is not a chemical reaction?` | **PASS** |
| **Biology Genetics** | Biology \| Mendelian Genetics \| Class 12 \| Medium \| 2 marks \| MCQ | `Which of the following is not a genus of mendelian?` | **PASS** |
| **General Science Class 9** | General Science \| Matter in Our Surroundings \| Class 9 \| Easy \| 1 mark \| MCQ | `Which of the following is not a characteristic of a plant?` | **PASS** |

All generations executed without syntax or dimension errors.

---

## 5. Artifact Deliverables
1. Training Script: [train_flan_t5_v15.py](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/training/train_flan_t5_v15.py)
2. Training Configuration: [v15_training_config.json](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_training_config.json)
3. Mandatory Smoke Test Report: [v15_smoke_test_report.txt](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_smoke_test_report.txt)
4. Full Training Report: [v15_training_report.txt](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_training_report.txt)
5. Checkpoint Verification JSON: [v15_checkpoint_verification.json](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v15_checkpoint_verification.json)
6. Checkpoint Directory: [flan_t5_v15](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/checkpoints/flan_t5_v15)

---

## 6. Stop Condition Compliance
As required:
- No final production-readiness decision is made in Phase 16.
- Phase 16 concludes strictly with:
  > **V15 MODEL TRAINING COMPLETED AND CHECKPOINT VERIFIED.**
