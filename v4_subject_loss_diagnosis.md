# Technical Diagnosis: Forensic Investigation of V4 Subject & Metadata Loss

## Executive Summary

During the construction of the AQPG V4 dataset, a comprehensive audit revealed that out of 9,075 total records, **8,792 records (96.88%) were classified as Mathematics**, while **Physics, Chemistry, Class, Board, and Unit metadata were 0% present**.

This document provides a line-by-line empirical trace of the legacy pipeline from raw source ingestion to final split generation, pinpointing exactly where and why non-mathematical STEM subjects and curriculum control tags were lost.

---

## Pipeline Execution Trace

```
[RAW SOURCE DATASETS]
  ├── GSM8K Reasoning (16,000 records) -> 100% Math
  ├── EduQG OpenStax (4,500 records)   -> Biology, Psychology, Accounting, Sociology, History (0 Physics, 0 Chem)
  └── Bloom Taxonomy (1,000 records)   -> Subject = None
            │
            ▼
[UNIFIED AGGREGATION (build_unified_dataset.py)]
  ├── Aggregates clean_reasoning.py, clean_eduqg.py, clean_bloom.py
  └── Produces unified_questions.jsonl (21,500 raw records)
            │
            ▼
[V4 BUILDER & VERIFICATION (build_qg_dataset_v4.py)]
  ├── 1. Fallback Assignment (Line 108): subject = r.get("subject") or "Mathematics"
  ├── 2. Numerical Filter (verify_mathematical_integrity.py):
  │      - Requires numerical digits in stem/answer (check_contains_numerical_data)
  │      - Requires non-empty answer (check_answer_exists)
  │      - Textual/Conceptual questions -> REJECTED_NON_NUMERICAL / REJECTED_MISSING_ANSWER
  └── 3. Rejection Filter (Lines 149-152): Drops ALL REJECTED_* records
            │
            ▼
[V4 FINAL DATASET (qg_train_dataset_v4.jsonl / qg_validation_dataset_v4.jsonl)]
  └── 9,075 records: 8,792 Math (GSM8K survivors), 0 Physics, 0 Chemistry, 0% Class/Board/Unit
```

---

## 1. Raw Source Dataset Composition Analysis

| Dataset Source | File Name(s) | Raw Count | Subjects Contained | Physics/Chem Present? | Class/Board/Unit Present? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **GSM8K Reasoning** | `main_train.csv`, `main_test.csv`, `socratic_train.csv`, `socratic_test.csv` | ~16,000 | Mathematics (Arithmetic & Word Problems) | **No** | **No** (0% present in source) |
| **EduQG OpenStax** | `eduqg_train.json`, `eduqg_val.json`, `eduqg_llm_formatted.csv` | ~4,500 | Biology, Anatomy, Psychology, Sociology, History, Accounting, Government, Law | **No** (Only OpenStax Biology/Psychology/Social Science textbooks were present; no Physics or Chemistry textbooks were included) | **No** (OpenStax college textbook chapters lack K-12 Class/Board metadata) |
| **Bloom Taxonomy** | `blooms_taxonomy_dataset.csv` | ~1,000 | Unlabeled general questions | **No** | **No** |

### Findings:
- **Zero Raw Physics/Chemistry Data**: Neither GSM8K nor EduQG contained raw Physics or Chemistry numerical question data.
- **Zero K-12 Metadata**: None of the three source datasets included `class_level`, `board`, or `unit` tags.

---

## 2. Ingestion & Preprocessing Logic (Failure Point Analysis)

### Failure Point 1: Hardcoded Fallback Subject Overriding
In `build_qg_dataset_v4.py` (Line 108):
```python
subject = r.get("subject") or "Mathematics"
```
- For Bloom taxonomy records where `r.get("subject")` was `None`, the script automatically reassigned `subject` to `"Mathematics"`.
- This masked missing metadata during initial ingestion instead of tracking `UNKNOWN`.

### Failure Point 2: Overly Strict Numerical Verification Filter
In `verify_mathematical_integrity.py` (Lines 156-164):
```python
# 2. Numerical Content
if not check_contains_numerical_data(question, answer):
    record["verification_status"] = "REJECTED_NON_NUMERICAL"
    return record

# 3. Answer Existence
if not check_answer_exists(answer):
    record["verification_status"] = "REJECTED_MISSING_ANSWER"
    return record
```
- Non-numerical EduQG questions (such as Biology conceptual questions or Sociology multiple-choice stems lacking explicit numeric answers) were tagged as `REJECTED_NON_NUMERICAL` or `REJECTED_MISSING_ANSWER`.

### Failure Point 3: Silent Drop of Non-Numerical Records
In `build_qg_dataset_v4.py` (Lines 149-152):
```python
status = verified_entry.get("verification_status", "NOT_VERIFIED")
if status.startswith("REJECTED"):
    removal_stats[f"Verification Failed: {status}"] += 1
    continue
```
- Every record flagged as `REJECTED_*` was completely discarded from V4.
- As a consequence, ~12,000 raw records (including all EduQG Biology/Psychology/Sociology conceptual questions) were removed, leaving **only GSM8K numerical math word problems** in V4.

---

## 3. Categorization of V4 Metadata Presence

| Metadata Field | Status in V4 | Source Provenance | Resolution for V5 |
| :--- | :--- | :--- | :--- |
| **Mathematics** | **8,792 records (100% of V4)** | Derived from GSM8K math reasoning | Retain as valid Mathematics subset |
| **Physics** | **0 records (0%)** | Absent in raw sources | Mark as missing; ingest raw Physics sources if available |
| **Chemistry** | **0 records (0%)** | Absent in raw sources | Mark as missing; ingest raw Chemistry sources if available |
| **Class (1-12)** | **0% presence** | Absent in raw sources | Mark explicitly as `UNKNOWN` rather than guessing |
| **Board (CBSE/State)**| **0% presence** | Absent in raw sources | Mark explicitly as `UNKNOWN` rather than guessing |
| **Unit** | **0% presence** | Absent in raw sources | Mark explicitly as `UNKNOWN` rather than guessing |

---

## 4. Architectural Rules Enforced for V5

1. **No Artificial Metadata Fabrication**: If a raw record does not specify `class`, `board`, `unit`, or `subject`, the V5 pipeline will set the field to `"UNKNOWN"`.
2. **Support Non-Numerical STEM & Conceptual Questions**: V5 verification will categorize valid textual STEM questions as `VERIFIED_HEURISTIC` or `NOT_VERIFIED` rather than rejecting and deleting them with `REJECTED_NON_NUMERICAL`.
3. **Transparent Readiness Reporting**: If raw source files for Physics or Chemistry are not present in `datasets/raw/`, the V5 audit will explicitly report **`NEED MORE DATA`** rather than claiming multi-subject support.
