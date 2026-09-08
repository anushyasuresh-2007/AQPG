# AQPG Phase 13 Large-Scale Automated STEM Dataset Ingestion & Class Grounding Implementation Notes

## Executive Summary

This document details the execution of **Phase 13: Large-Scale Automated STEM Dataset Ingestion & Class Grounding**.
Pursuant to strict data integrity and quality rules:
- **Baseline Preservation**: All existing V3, V4, V5, and V5.1 datasets, scripts, audit reports, and checkpoints remain completely untouched.
- **Mandatory Stop Condition**: Model training (FLAN-T5) has **NOT** been launched. Execution strictly stops after Phase 13 dataset construction, deduplication, forensic auditing, and empirical readiness assessment.
- **Zero Metadata Fabrication**: Class, Board, Subject, and Provenance metadata were deterministically mapped solely from verifiable source attributes and explicit benchmark standards. Where unsupported, metadata was preserved as `UNKNOWN`.

---

## 1. Phase 13 Source Discovery, Acceptance & Ingestion

| Source Name | File Name | Format | Status | License & Provenance | Raw Count | Accepted Clean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SciQ Benchmark** | `sciq_dataset_raw.json` | JSON | **Accepted** | AllenAI / CC BY-NC 3.0 | 13,679 | 13,589 |
| **AI2 ARC Benchmark** | `ai2_arc_raw.json` | JSON | **Accepted** | AllenAI / CC BY-SA 4.0 | 7,787 | 7,749 |
| **MMLU STEM Subsets** | `mmlu_stem_raw.json` | JSON | **Accepted** | UC Berkeley / MIT License | 1,667 | 1,615 |
| **OpenBookQA** | `openbookqa_raw.json` | JSON | **Accepted** | AllenAI / Apache 2.0 | 5,957 | 5,753 |
| **NCERT Exemplar & Benchmark** | `ncert_stem_class9_12_raw.json` | JSON | **Accepted** | NCERT Exemplar / CC BY-NC 4.0 | 18 | 18 |
| **GSM8K Reasoning** | `gsm8k_reasoning_all.csv` | CSV | **Accepted** | OpenAI / MIT License | 17,584 | 8,792 |
| **OpenStax EduQG** | `eduqg_train_val.json` | JSON | **Accepted** | OpenStax / CC BY 4.0 | 3,397 | 3,373 |
| **Bloom Taxonomy** | `blooms_taxonomy_dataset.csv` | CSV | **Accepted** | Kaggle / Public Domain | 8,767 | 8,685 |
| **Unlicensed Web Scrapes & PDFs**| Various | Various | **Rejected** | Failed Licensing Verification | 0 | 0 |

---

## 2. Ingestion & V13 Pipeline Rebuild Metrics

- **Raw Candidates Ingested**: **58,856 records**
- **Clean V13 Records Accepted**: **49,574 records**
- **Master Dataset File**: `datasets/v13/qg_dataset_v13.jsonl` (49,574 records)
- **Train / Validation Split (Seed 42)**:
  - **Train V13 (80%)**: **39,659 records** (`datasets/v13/qg_train_dataset_v13.jsonl`)
  - **Validation V13 (20%)**: **9,915 records** (`datasets/v13/qg_validation_dataset_v13.jsonl`)
- **Records Rejected**: **9,282 records**
  - Target Stem Deduplication (Train/Val Protection): **9,237 records**
  - Chemical Domain Sanity Violations: **2 records** (Caught negative moles/concentration anomalies)
  - Empty or Short Stems (<10 chars): **43 records**

---

## 3. Curriculum & STEM Distribution in V13

### A. Subject Distribution
- **Chemistry**: **10,875** (21.94%) [Exceeds >=5,000 threshold]
- **General Science**: **10,867** (21.92%)
- **Mathematics**: **9,204** (18.57%) [Exceeds >=5,000 threshold]
- **Biology**: **5,367** (10.83%) [Exceeds >=5,000 threshold]
- **Physics**: **2,872** (5.79%) [Target: 5,000; Acquired: 2,872]
- **Social Science**: **630** (1.27%)
- **Business & Law**: **579** (1.17%)
- **History & Civics**: **464** (0.94%)
- **UNKNOWN**: **8,716** (17.58%)

### B. Class Grounding Distribution
- **Class 9**: **2,576** (5.20%)
- **Class 10**: **3** (0.01%)
- **Class 11**: **1,042** (2.10%)
- **Class 12**: **585** (1.18%)
- **Total Explicit Class 9–12**: **4,206 records** (8.48%) *(233x expansion from 18 in V5.1)*
- **Class `UNKNOWN`**: **45,368 records** (91.52%)

### C. Board Grounding Distribution
- **CBSE**: **12** (0.02%)
- **State Board**: **0** (0.00%)
- **OpenStax Academic**: **3,373** (6.80%)
- **Public Benchmark**: **17,483** (35.27%)
- **UNKNOWN**: **28,706** (57.91%)

---

## 4. Verification & Forensic Quality Gates

- **JSON Syntax Errors**: **0** (PASS)
- **Exact Target Overlap**: **0** (PASS)
- **Normalized Target Overlap**: **0** (PASS)
- **Duplicate Prompt-Target Pairs**: **0** (PASS)
- **Exact Prompt Overlap**: **143** (Control prefixes identical across distinct question stems; zero target leakage)
- **Verification Breakdown**:
  - `VERIFIED_HEURISTIC`: **49,205** (99.26%)
  - `NOT_VERIFIED`: **338** (0.68%)
  - `VERIFIED_DETERMINISTIC`: **31** (0.06%)
  - `REJECTED`: **2** (0.00%)
- **Tokenization Audit (`google/flan-t5-small`, 2,000 samples, seed 42)**:
  - Input Tokens: Min **49**, Max **57**, Avg **54.9** (0.00% > 128 tokens, 0.00% > 256 tokens)
  - Target Tokens: Min **3**, Max **157**, Avg **27.4** (0.35% > 128 tokens, 0.00% > 256 tokens)
- **Quality Gates Status**: **WARN**
  - Warning 1: Physics count (2,872) is below the ideal >=5,000 threshold.
  - Warning 2: Class metadata is UNKNOWN for 91.52% of records.

---

## 5. Empirical Readiness Verdict & Supporting Evidence

### **FINAL VERDICT: B. NEED MORE DATA**

**Exact Supporting Evidence**:
1. **Physics Volume Under-Threshold**: While Chemistry (10,875) and Mathematics (9,204) successfully surpassed the 5,000-record threshold, Physics stands at 2,872 records (short of the 5,000 threshold).
2. **K-12 Class Supervision Gap**: Although explicit Class 9–12 records expanded from 18 to 4,206, 91.52% (45,368 records) remain `UNKNOWN` because raw open benchmark sources (SciQ, OpenBookQA, GSM8K) do not declare exact single-grade allocations.
3. **Model Training Integrity**: Strict adherence to instructions prohibited fine-tuning or training until comprehensive multi-subject parity and supervision thresholds are satisfied.

---

## 6. Recommended Next Phase (Phase 14)

1. **Targeted Physics Corpus Ingestion**: Ingest open physics textbook question repositories (e.g. OpenStax University Physics volumes 1-3 and High School Physics corpora) to bring Physics above 5,000 records.
2. **Class 10 & 12 Augmentation**: Ingest secondary school public exam and open curriculum collections with explicit Grade 10/12 tags.
3. **Re-Audit and Quality Gate Clearance**: Re-verify zero leakage and tokenization boundaries before commencing model fine-tuning.
