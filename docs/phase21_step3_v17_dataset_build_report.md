# AQPG V17 Remediation — Phase 21A Step 3: Dataset Build & Pre-Training Quality Audit Report

> **EXECUTIVE VERDICT**: **V17 DATASET BUILD — PASS**  
> **Evaluation Date**: August 24, 2026  
> **Status**: All 12 mandatory pre-training dataset quality gates (`GATE-D1` to `GATE-D12`) and 1 advisory gate (`GATE-D13`) have officially **PASSED**.  
> **Safety Boundary Enforced**: 100% Data Assembly & Pre-Training Audit Only. No model loaded, no PyTorch inference executed, no training started, no V16 datasets modified, no Phase 20 artifacts modified, and no FastAPI code changed.

---

## 1. Summary of Dataset Build & Verification

Phase 21A Step 3 successfully constructed the **AQPG V17 Training and Validation Datasets** in strict accordance with the approved Phase 21A Step 2 Redesign Specification ([`phase21_step2_v17_dataset_specification.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step2_v17_dataset_specification.json)).

### Dataset Artifacts & Cryptographic Signatures

| Artifact Filename | Record Count | File Size (Bytes) | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| [`phase21_step3_v17_train_dataset.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_v17_train_dataset.jsonl) | 40,000 | 17,998,349 | `CFA5B581E0D10D5CD65D7BDB5B0F75D355EE97EDC8F70570ECF12FBB76C7641B` |
| [`phase21_step3_v17_validation_dataset.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_v17_validation_dataset.jsonl) | 10,000 | 4,497,440 | `A6BAAA9DEFAFCEDD924DAFA65BAAA19CD7484B776E013CF1D6EAF32ED021CFDF` |
| **Total V17 Dataset** | **50,000** | **22,495,789** | **Deterministic 80/20 Partition** |

---

## 2. Pre-Training Dataset Quality Gates Evaluation (`GATE-D1` to `GATE-D13`)

All 13 quality gates defined in the Step 2 specification were evaluated against the full 50,000-record V17 dataset corpus.

| Gate ID | Quality Metric Name | Required Threshold | Observed V17 Value | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **GATE-D1** | Unique Input Prompt Ratio | `>= 60.0%` | **100.00%** (50,000 / 50,000) | **PASS** |
| **GATE-D2** | Max Single Prompt Concentration | `<= 0.10%` | **0.002%** (1 record max) | **PASS** |
| **GATE-D3** | Top-3 Prompt Concentration | `<= 0.30%` | **0.006%** (3 records total) | **PASS** |
| **GATE-D4** | Conceptual Representation | `>= 25.0%` | **25.00%** (12,500 records) | **PASS** |
| **GATE-D5** | Numerical Representation | `>= 35.0%` | **35.00%** (17,500 records) | **PASS** |
| **GATE-D6** | MCQ Representation Ceiling | `<= 35.0%` | **35.00%** (17,500 records) | **PASS** |
| **GATE-D7** | Class UNKNOWN Token Rate | `0.0%` | **0.00%** (0 UNKNOWN tokens) | **PASS** |
| **GATE-D8** | Numerical Subject Concentration | `<= 45.0%` | **40.71%** (7,125 Physics / 17.5k) | **PASS** |
| **GATE-D9** | Top-10 Target Stem Concentration | `<= 15.0%` | **6.50%** (3,250 records) | **PASS** |
| **GATE-D10** | Exact Duplicate Pair Rate | `0` | **0** exact duplicates | **PASS** |
| **GATE-D11** | Train/Val Exact Target Leakage | `0` | **0** target leakage | **PASS** |
| **GATE-D12** | Paired Control Quadruplets | `>= 2,500 groups` | **2,500 groups** (10,000 records) | **PASS** |
| **GATE-D13** | Target Stem Entropy (Advisory) | `>= 10.0 bits` | **11.6633 bits** | **PASS** |

---

## 3. Structural Rebalancing & Forensic Comparison vs V16

| Metric Dimension | V16 Training Dataset (Historical) | V17 Constructed Dataset (Remediated) | Status Improvement |
| :--- | :--- | :--- | :--- |
| **Total Scale** | 40,557 records | **50,000 records** | +9,443 high-quality records |
| **Unique Input Prompts** | 204 prompts (0.50% ratio) | **50,000 prompts (100.00% ratio)** | **245x prompt diversity gain** |
| **Top-3 Prompt Share** | 42.96% (17,424 records) | **0.006% (3 records)** | Remediated prompt collapse |
| **Class UNKNOWN Rate** | 82.13% (33,310 records) | **0.00% (0 UNKNOWN tokens)** | 100% grounded Class 9–12 |
| **Conceptual Questions** | 1.38% (560 records) | **25.00% (12,500 records)** | 18x conceptual expansion |
| **MCQ Question Share** | 82.13% (33,310 records) | **35.00% (17,500 records)** | Balanced type distribution |
| **Paired Quadruplets** | 0 groups (0 records) | **2,500 groups (10,000 records)** | Direct sensitivity learning |

---

## 4. Output Artifacts Created in Step 3

1. [`phase21_step3_v17_train_dataset.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_v17_train_dataset.jsonl)
2. [`phase21_step3_v17_validation_dataset.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_v17_validation_dataset.jsonl)
3. [`phase21_step3_quality_gate_results.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_quality_gate_results.json)
4. [`phase21_step3_dataset_distribution.csv`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_dataset_distribution.csv)
5. [`phase21_step3_dataset_build_report.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase21_step3_dataset_build_report.json)
6. [`docs/phase21_step3_v17_dataset_build_report.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/docs/phase21_step3_v17_dataset_build_report.md)

---

## 5. Mandatory Safety Declarations

- **NO MODEL LOADED**: PyTorch, Hugging Face Transformers, or any model weights were NOT loaded.
- **NO INFERENCE EXECUTED**: No model generation or inference was run.
- **NO TRAINING EXECUTED**: Fine-tuning or model training was NOT initiated.
- **NO V16 DATASET MODIFIED**: `datasets/v16/qg_train_dataset_v16.jsonl` was NOT altered.
- **NO PHASE 20 ARTIFACTS MODIFIED**: All Phase 20 evaluation reports remain untouched.
- **NO FASTAPI CODE MODIFIED**: Backend production code (`backend/app/main.py`) remains unmodified.

---
**SUMMARY**: `V17 DATASET BUILD — PASS`. All pre-training quality gates passed. Dataset construction is complete and ready for review before V17 fine-tuning plan specification.
