# AQPG Phase 12 External K-12 STEM Data Acquisition & Metadata Expansion Implementation Notes

## Executive Summary

This document details the execution of Phase 12: External K-12 STEM Data Acquisition, Source Inventory, Ingestion, Class & Board Metadata Population, Extended Physical/Chemical Domain Verification, Versioned V5.1 Rebuild, Forensic Audit, and Empirical Readiness Verdict.

Pursuant to explicit instructions:
- **Baseline Preservation**: V3 datasets, V4 datasets, V4 pilot checkpoints, and initial V5 files remain untouched.
- **Mandatory Stop Condition**: Model training (FLAN-T5) has **NOT** been launched. Execution stops immediately following Phase 12 dataset auditing and readiness assessment.

---

## 1. Source Discovery, Acceptance & Ingestion Summary

| Source Name | File Name | Format | Status | Provenance / License | Records Ingested |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **NCERT Physics 11–12** | `ncert_physics_class11_12.json` | JSON | **Accepted** | NCERT Exemplar / CC BY-NC 4.0 | 6 |
| **NCERT Chemistry 11–12** | `ncert_chemistry_class11_12.json` | JSON | **Accepted** | NCERT Exemplar / CC BY-NC 4.0 | 6 |
| **ScienceQA (Physics/Chem)** | `scienceqa_physics_chemistry.json` | JSON | **Accepted** | ScienceQA Benchmark / CC BY-NC-SA 4.0 | 4 |
| **SciQ (Physics/Chem)** | `sciq_science_questions.json` | JSON | **Accepted** | SciQ Benchmark / CC BY-NC 3.0 | 2 |
| **GSM8K Reasoning** | `main_*.csv`, `socratic_*.csv` | CSV | **Accepted** | OpenAI GSM8K / MIT License | 17,584 |
| **EduQG OpenStax** | `eduqg_train.json`, `eduqg_val.json` | JSON | **Accepted** | OpenStax / CC BY 4.0 | 3,397 |
| **Bloom Taxonomy** | `blooms_taxonomy_dataset.csv` | CSV | **Accepted** | Kaggle Benchmark / Public Domain | 8,767 |
| **Unlicensed / Unverified Web Sources** | N/A | Various | **Rejected** | Failed License Verification | 0 |

---

## 2. Ingestion & V5.1 Pipeline Rebuild Metrics

- **Raw Candidates Ingested**: **29,766 records**
- **Accepted Clean V5.1 Records**: **20,872 records**
- **Rejected Records**: **8,894 records** (8,882 duplicate target question stems + 12 empty/short stems)
- **Train / Validation Split (Seed 42)**:
  - **Train V5.1 (80%)**: **16,697 records**
  - **Validation V5.1 (20%)**: **4,175 records**
- **Data Integrity & Leakage Verification**:
  - JSON Syntax Errors: **0** (PASS)
  - Exact Target Overlap: **0** (PASS)
  - Normalized Target Overlap: **0** (PASS)
  - Duplicate Prompt-Target Pairs: **0** (PASS)
- **Subject Distribution**:
  - Mathematics: **8,792** (42.12%)
  - Biology: **1,672** (8.01%)
  - Social Science: **630** (3.02%)
  - Business & Law: **580** (2.78%)
  - History & Civics: **464** (2.22%)
  - Unclassified / General: **8,716** (41.76%)
  - Physics: **9** (0.04%)
  - Chemistry: **9** (0.04%)
- **Curriculum Metadata Coverage**:
  - Class Specified (Class 9–12): **18 records** (Class 9: 3, Class 10: 3, Class 11: 6, Class 12: 6)
  - Class `UNKNOWN`: **20,854 records** (99.91%)
  - Board Specified (`CBSE`): **12 records**
  - Board `OpenStax Academic`: **3,397 records**
  - Board `Public Benchmark`: **17,463 records**
  - Board `UNKNOWN`: **0 records**
  - Unit Specified: **3,395 records**
- **Verification Status Breakdown**:
  - `VERIFIED_HEURISTIC`: **20,565** (98.53%)
  - `NOT_VERIFIED`: **307** (1.47%)
  - `REJECTED`: **0**
- **Tokenization Audit (`google/flan-t5-small`)**:
  - Input Tokens: Avg **54.4**, Max **57** (0% > 256)
  - Target Tokens: Avg **36.1**, Max **187** (0% > 256)

---

## 3. Empirical Readiness Verdict & Supporting Evidence

### **FINAL VERDICT: B. NEED MORE DATA**

**Exact Supporting Evidence**:
1. **STEM Volume Limitations**: While Phase 12 successfully created the ingestion pipeline and integrated NCERT Class 11 & 12 Exemplar, ScienceQA, and SciQ benchmarks, the total volume of verified Physics (9 records) and Chemistry (9 records) is far below the target threshold (~10,000 records per subject) required for deep neural model generalization.
2. **Class Supervision Gap**: Class metadata is explicitly populated for 18 records (Class 9: 3, Class 10: 3, Class 11: 6, Class 12: 6), but remains `UNKNOWN` for 20,854 out of 20,872 records (99.91%).
3. **Data Integrity Adherence**: Pursuant to Phase 12 rules, Class and Board metadata were NOT fabricated or predicted by model inference.

---

## 4. Recommended Next Phase (Phase 13)

**Phase 13: Large-Scale Bulk STEM Dataset Acquisition (Physics & Chemistry)**
1. Perform automated bulk ingestion from large open educational repositories (e.g. Hugging Face `NCERTQABench` containing ~222,000 QA pairs, SciQ full science splits, and OpenStax Physics & Chemistry textbook archives).
2. Map explicit K-12 Class 9–12 and CBSE annotations from source attributes into `build_qg_dataset_v5.py`.
3. Re-run forensic audit to confirm multi-thousand record STEM volume prior to launching FLAN-T5 model training.
