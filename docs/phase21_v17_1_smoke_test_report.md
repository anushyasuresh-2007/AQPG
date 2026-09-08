# AQPG V17.1 — GPU Numerical Stability & 100-Step Smoke Test Report

> **EXECUTIVE VERDICT**: **`V17.1 STABILITY SPECIFICATION AND SMOKE TEST SCRIPT PREPARED`**  
> **Operation Date**: September 4, 2026  
> **Script Path**: [`phase21_v17_colab/train_flan_t5_v17_1_gpu.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_v17_colab/train_flan_t5_v17_1_gpu.py)  
> **Target Checkpoint Directory**: `backend/ml/models/checkpoints/flan_t5_v17_1_gpu_smoketest/`  
> **Safety Boundary Enforced**: Datasets read-only, V16 protected, Phase 20 untouched, FastAPI production code untouched (`approved_for_fastapi: false`, status `BLOCKED`).

---

## 1. Root Cause & V17.1 Numerical Stability Fixes

### Problem Analysis (V17 GPU Failure at Step ~771)
- `eval_loss` diverged to `NaN`
- `training loss` collapsed to `0`
- `grad_norm` diverged to `NaN`

### Remediation Protocol (V17.1 Hyperparameter Matrix)

| Parameter / Configuration | V17 Setting (Failed) | V17.1 Numerical Stability Setting | Rationale |
| :--- | :--- | :--- | :--- |
| **Precision** | `fp16 = True` | **`fp16 = False` (FP32)** | Eliminates underflow/overflow in float16 gradients |
| **BF16 Precision** | `bf16 = False` | **`bf16 = False`** | Ensures pure FP32 IEEE 754 precision stability |
| **Learning Rate** | `1e-4` | **`5e-5`** | 50% LR reduction prevents gradient explosions |
| **Label Smoothing** | `0.05` | **`0.05 -> 0.0`** | Removes cross-entropy division instability |
| **Weight Decay** | `0.01` | **`0.01`** | Standard L2 regularization preserved |
| **Max Grad Norm** | `1.0` | **`1.0`** | Prevents unclipped gradient spikes |
| **Warmup Schedule** | `warmup_steps = 187` | **`warmup_steps = 187`** | Preserves 5% linear warmup ramp |
| **Effective Batch Size** | `32` (16 x 2) | **`32` (16 x 2)** | Identical gradient accumulation step size |
| **Smoke Test Limit** | Full 3 Epochs | **`max_steps = 100`** | Short 100-step smoke test before full run |

---

## 2. Mandatory Dataset Integrity Audit

- **Train Dataset**: `phase21_step3_v17_train_dataset.jsonl`
  - Record Count: **40,000**
  - Cryptographic Hash: `F150ED036D3B1612FB307949323972C40DD7074C8DC3C885621A72B993548C85` (**VERIFIED READ-ONLY**)
- **Validation Dataset**: `phase21_step3_v17_validation_dataset.jsonl`
  - Record Count: **10,000**
  - Cryptographic Hash: `7038D9C15A68269574E413A6C7E7E491A6DF047CD85F3BF9C3FFD82E7B764A3E` (**VERIFIED READ-ONLY**)

---

## 3. Transformers API Compatibility Layer Audit

The V17.1 script [`phase21_v17_colab/train_flan_t5_v17_1_gpu.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_v17_colab/train_flan_t5_v17_1_gpu.py) enforces full compatibility with Transformers v4.49+:
- `eval_strategy="steps"` (Replaces deprecated `evaluation_strategy`)
- `warmup_steps=187` (Replaces deprecated `warmup_ratio`)
- `processing_class=tokenizer` in `Seq2SeqTrainer` (Replaces deprecated `tokenizer=`)
- No `overwrite_output_dir`
- Custom `NumericalStabilityCallback` to catch `NaN` / `Inf` instantly during training steps.

---

## 4. Execution Directives for Google Colab GPU

Run the following command in Google Colab with T4 GPU runtime enabled:

```bash
python phase21_v17_colab/train_flan_t5_v17_1_gpu.py
```

### Success Criteria (100-Step Smoke Test):
1. `loss`, `eval_loss`, and `grad_norm` remain finite (`NaN detected: NO`, `Inf detected: NO`).
2. Completes step 100 cleanly and saves best checkpoint to `backend/ml/models/checkpoints/flan_t5_v17_1_gpu_smoketest/best_model/`.
3. Reports result: `PASS — READY FOR FULL V17.1 GPU TRAINING`.
4. Stops automatically after step 100 without proceeding to 3-epoch training.

---

## 5. Safety Declarations

- **FastAPI Code**: 100% UNTOUCHED
- **FastAPI Integration Status**: **BLOCKED (`approved_for_fastapi: false`)**
- **V16 Artifacts**: 100% PROTECTED
- **Phase 20 Artifacts**: 100% PROTECTED
- **CPU Checkpoint Archive**: `AQPG_V17_CPU_RUN_ARCHIVE_TASK328/` PRESERVED
