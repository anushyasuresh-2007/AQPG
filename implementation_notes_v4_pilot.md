# AQPG Phase V4 Dataset Audit & FLAN-T5-Small Multi-Subject Pilot Implementation Notes

## Executive Summary

This document details the completion of the V4 Dataset Audit, Quality Gates Validation, Tokenization Analysis, Control Condition Verification, FLAN-T5-Small Pilot Training Setup, Multi-Subject Evaluation, SymPy Mathematical Integrity Integration, and Error Analysis.

---

## 1. Files Created & Modified

| File Path | Description | Status |
| :--- | :--- | :--- |
| [`backend/ml/models/qg_flan_t5/audit_qg_dataset_v4.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/audit_qg_dataset_v4.py) | Comprehensive 23-check V4 dataset audit, Quality Gates engine & Tokenization analysis script | Verified & Executed |
| [`backend/ml/models/qg_flan_t5/train_flan_t5_v4_pilot.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/train_flan_t5_v4_pilot.py) | Pilot trainer supporting smoke testing, opt-in full training (`--full`), controlled multi-subject evaluation, SymPy verification, 30-sample error analysis, and final verdict reporting | Verified & Executed |
| [`backend/ml/models/qg_flan_t5/qg_dataset_v4_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/qg_dataset_v4_audit.json) | Full audit output in structured JSON format | Generated |
| [`backend/ml/models/qg_flan_t5/qg_dataset_v4_audit_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/qg_dataset_v4_audit_report.txt) | Forensic audit report text | Generated |
| [`backend/ml/models/qg_flan_t5/numerical_v4_pilot_evaluation.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/numerical_v4_pilot_evaluation.json) | Pilot evaluation metrics, control tag statistics, and error analysis samples in JSON | Generated |
| [`backend/ml/models/qg_flan_t5/numerical_v4_pilot_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/models/qg_flan_t5/numerical_v4_pilot_report.txt) | Final evaluation report text including explicit answers to 10 audit questions | Generated |
| [`implementation_notes_v4_pilot.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/implementation_notes_v4_pilot.md) | Comprehensive Phase 11 documentation | Created |

---

## 2. Execution Commands

### Step 1: Run V4 Forensic Audit & Quality Gates
```powershell
backend\.venv\Scripts\python.exe backend/ml/models/qg_flan_t5/audit_qg_dataset_v4.py
```

### Step 2: Run Pilot Smoke Test (100 train / 20 val, 1 epoch)
```powershell
backend\.venv\Scripts\python.exe backend/ml/models/qg_flan_t5/train_flan_t5_v4_pilot.py
```

### Step 3: Run Full Pilot Training (Opt-in `--full`, 2 epochs)
```powershell
backend\.venv\Scripts\python.exe backend/ml/models/qg_flan_t5/train_flan_t5_v4_pilot.py --full
```

---

## 3. Dataset Audit Statistics (V4)

- **Total Records**: **9,075** (Train: **7,260**, Validation: **1,815**)
- **JSON Validity**: 100% valid (0 syntax errors).
- **Leakage Analysis**: 0% target question overlap (0 exact or normalized target matches across splits).
- **Verification Breakdown**:
  - `VERIFIED_DETERMINISTIC`: **4,563** (50.28%)
  - `VERIFIED_HEURISTIC`: **4,229** (46.60%)
  - `NOT_VERIFIED`: **283** (3.12%)
  - **Overall Verification Rate**: **96.88%**
- **Tokenization Lengths (`google/flan-t5-small`)**:
  - Input prompt: Avg **36.3** tokens, Max **56** tokens (0% > 256).
  - Target text: Avg **59.8** tokens, Max **189** tokens (0% > 256).
- **Control Tag Presence**:
  - `subject`: 100.00%
  - `topic`: 100.00%
  - `bloom`: 100.00%
  - `difficulty`: 100.00%
  - `marks`: 100.00%
  - `unit`: 0.00%
  - `class`: 0.00%
  - `board`: 0.00%
  - `question_type`: 0.00%

---

## 4. Known Limitations & Audit Findings

1. **Multi-Subject Imbalance**:
   - V4 dataset contains 8,792 Mathematics records but **0 Physics** and **0 Chemistry** records.
2. **Supervision Gap for Advanced Metadata**:
   - `class`, `board`, and `unit` tags are 0% present in active V4 records.
   - *Explicit Audit Statement*: *"Architecture supports this control, but the current dataset does not provide sufficient supervision."*

---

## 5. Final Pilot Decision & Verdict

### **FINAL VERDICT: B. NEED MORE DATA**

**Rationale**:
The FLAN-T5-small model architecture and numerical generation pipeline are fully functional and achieve high mathematical integrity on numerical problem solving. However, multi-subject generalization to Physics and Chemistry cannot be confirmed because current V4 dataset records are exclusively Mathematics.

---

## 6. Next Recommended Phase (Phase 12)

**Phase 12: STEM Dataset Expansion (Physics & Chemistry + Curriculum Control Metadata)**
1. Expand dataset to ingest genuine Physics and Chemistry numerical problems with solutions and physical unit annotations.
2. Supervise `class` (Class 9–12), `board` (CBSE/State/ICSE), and `unit` control tags in raw prompt formatting.
3. Upon dataset expansion, re-run pilot evaluation to validate multi-subject STEM performance before scaling to `google/flan-t5-base`.
