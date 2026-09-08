# AQPG Phase V5 Dataset Expansion & Audit Implementation Notes

## Executive Summary

This document details the successful completion of Phase V5 Dataset Expansion, Raw Dataset Forensic Inventory, V5 Master Schema Definition, V4 Subject Loss Forensic Diagnosis, 20-Stage V5 Builder Pipeline Execution, Quality Gates Enforcement, 5 Cross-Tabulation Matrices Generation, FLAN-T5-Small Tokenization Audit, and Empirical Readiness Verdict.

Pursuant to explicit instructions:
- **Preservation Guarantee**: V3 datasets, V4 datasets, `flan_t5_small_numerical/`, and `flan_t5_small_v4_numerical/` baseline checkpoints were preserved completely intact.
- **Mandatory Stop Condition**: Model training (FLAN-T5) has **NOT** been launched. Execution stops immediately following the dataset audit and readiness assessment.

---

## 1. Files Created & Modified

| File Path | Description | Status |
| :--- | :--- | :--- |
| [`v4_subject_loss_diagnosis.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v4_subject_loss_diagnosis.md) | Technical forensic analysis tracing raw ingestion to V4 subject loss | Created |
| [`v5_source_mapping.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v5_source_mapping.md) | Specification of raw source mappings, provenance, license, and confidence levels | Created |
| [`implementation_notes_v5.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/implementation_notes_v5.md) | Complete Phase V5 documentation & empirical readiness verdict | Created |
| [`backend/ml/preprocessing/audit_raw_sources_v5.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/preprocessing/audit_raw_sources_v5.py) | Raw source scanner and inventory generator | Verified & Executed |
| [`backend/ml/preprocessing/qg_dataset_v5_schema.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/preprocessing/qg_dataset_v5_schema.json) | V5 Master Schema JSON specification | Created |
| [`backend/ml/preprocessing/build_qg_dataset_v5.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/preprocessing/build_qg_dataset_v5.py) | 20-stage dataset builder, domain verification, and 80/20 split engine | Verified & Executed |
| [`backend/ml/preprocessing/audit_qg_dataset_v5.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/preprocessing/audit_qg_dataset_v5.py) | V5 forensic audit, cross-tabulation, tokenization, and quality gate engine | Verified & Executed |
| [`datasets/raw_dataset_inventory_v5.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/raw_dataset_inventory_v5.json) | Raw source inventory JSON | Generated |
| [`datasets/raw_dataset_inventory_v5_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/raw_dataset_inventory_v5_report.txt) | Raw source inventory report text | Generated |
| [`datasets/v5/qg_train_dataset_v5.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v5/qg_train_dataset_v5.jsonl) | V5 Training Set (16,683 records) | Generated |
| [`datasets/v5/qg_validation_dataset_v5.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v5/qg_validation_dataset_v5.jsonl) | V5 Validation Set (4,171 records) | Generated |
| [`datasets/v5/qg_dataset_v5_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v5/qg_dataset_v5_report.txt) | V5 Pipeline Build report text | Generated |
| [`datasets/v5/qg_dataset_v5_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v5/qg_dataset_v5_audit.json) | V5 Forensic Audit JSON output | Generated |
| [`datasets/v5/qg_dataset_v5_audit_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v5/qg_dataset_v5_audit_report.txt) | V5 Forensic Audit report text | Generated |

---

## 2. Executed Commands

```powershell
# 1. Raw Dataset Inventory
backend\.venv\Scripts\python.exe backend/ml/preprocessing/audit_raw_sources_v5.py

# 2. V5 Dataset Build Pipeline (20 Stages)
backend\.venv\Scripts\python.exe backend/ml/preprocessing/build_qg_dataset_v5.py

# 3. V5 Forensic Audit & Quality Gates
backend\.venv\Scripts\python.exe backend/ml/preprocessing/audit_qg_dataset_v5.py
```

---

## 3. Dataset Statistics Summary (V5)

- **Raw Candidates Ingested**: 29,748
- **Clean V5 Records Constructed**: **20,854**
- **Rejected Records**: 8,894 (8,882 duplicate target question stems + 12 empty/short stems)
- **Train / Validation Split (Seed 42)**:
  - **Train V5 (80%)**: **16,683 records**
  - **Validation V5 (20%)**: **4,171 records**
- **Data Integrity & Leakage Verification**:
  - JSON Syntax Errors: **0** (PASS)
  - Exact Target Overlap: **0** (PASS)
  - Normalized Target Overlap: **0** (PASS)
  - Duplicate Prompt-Target Pairs: **0** (PASS)
- **Subject Coverage**:
  - Mathematics: **8,792** (42.16%)
  - Biology: **1,672** (8.02%)
  - Social Science: **630** (3.02%)
  - Business & Law: **580** (2.78%)
  - History & Civics: **464** (2.22%)
  - Unclassified / General: **8,716** (41.80%)
  - Physics: **0** (0.00%)
  - Chemistry: **0** (0.00%)
- **Tokenization Audit (`google/flan-t5-small`)**:
  - Input Tokens: Avg **54.7**, Max **57** (0% > 256)
  - Target Tokens: Avg **36.3**, Max **154** (0% > 256)

---

## 4. Empirical Readiness Verdict & Decision

### **FINAL VERDICT: B. NEED MORE DATA**

**Exact Rationale**:
The V5 pipeline successfully established a clean, leak-free, 20,854-record master dataset with zero target overlap and robust schema normalization. However, the raw project archives currently contain **0 Physics records** and **0 Chemistry records**, and **Class level is UNKNOWN across 100% of records**. 

Training or fine-tuning FLAN-T5 at this stage would fail to supervise multi-subject STEM conditioning for Physics, Chemistry, and K-12 Class levels.

---

## 5. Recommended Next Steps (Phase 12)

1. **Ingest External Physics & Chemistry Datasets**: Acquire and extract legitimate raw K-12 Physics and Chemistry problem sets (e.g. ScienceQA, NCERT STEM benchmarks) into `datasets/raw/`.
2. **Supervise K-12 Class & Board Metadata**: Annotate raw records with explicit `Class 9–12` and `CBSE` tags.
3. **Re-run V5 Pipeline & Audit**: Re-execute `build_qg_dataset_v5.py` and `audit_qg_dataset_v5.py` to achieve multi-subject STEM coverage before model training.
