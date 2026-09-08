# AQPG Phase 14 Targeted Physics Expansion & Grade 10/12 Curriculum Grounding Implementation Notes

## Executive Summary

This document details the execution of **Phase 14: Targeted Physics Expansion & Grade 10/12 Curriculum Grounding**.
Pursuant to explicit instructions:
- **Baseline Preservation**: All V3, V4, V5, V5.1, and V13 datasets, scripts, audit reports, and checkpoints remain completely untouched.
- **Mandatory Stop Condition**: Model training (FLAN-T5) has **NOT** been launched. Execution strictly stops after Phase 14 dataset construction, deduplication, forensic auditing, and empirical readiness assessment.
- **Zero Metadata Fabrication**: Class, Board, Subject, and Provenance metadata were deterministically mapped solely from verifiable source attributes and explicit benchmark standards. Where unsupported, metadata was preserved as `UNKNOWN`.

---

## 1. Phase 14 Source Discovery, Acceptance & Ingestion

| Source Name | File Name | Format | Status | License & Provenance | Raw Count | Accepted Clean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **MMLU STEM & Secondary Subsets** | `mmlu_stem_expanded_raw.json` | JSON | **Accepted** | UC Berkeley / MIT License | 2,595 | 2,534 |
| **AI2 ARC (Grade 9 & 10 Grounded)** | `ai2_arc_grounded_raw.json` | JSON | **Accepted** | AllenAI / CC BY-SA 4.0 | 7,787 | 7,751 |
| **SciQ & OpenBookQA Benchmarks** | `science_benchmarks_raw.json` | JSON | **Accepted** | AllenAI / CC BY-NC 3.0 & Apache 2.0 | 19,636 | 19,339 |
| **NCERT Exemplar & Benchmark STEM**| `ncert_exemplar_class9_12_raw.json` | JSON | **Accepted** | NCERT Exemplar / CC BY-NC 4.0 | 18 | 18 |
| **GSM8K Reasoning Corpus** | `gsm8k_reasoning_all.csv` | CSV | **Accepted** | OpenAI / MIT License | 17,584 | 8,792 |
| **OpenStax EduQG** | `eduqg_train_val.json` | JSON | **Accepted** | OpenStax / CC BY 4.0 | 3,397 | 3,372 |
| **Bloom Taxonomy** | `blooms_taxonomy_dataset.csv` | CSV | **Accepted** | Kaggle / Public Domain | 8,767 | 8,685 |
| **Synthetic / Unlicensed Sources** | Various | Various | **Rejected** | Prohibited Synthetic QA / No License | 0 | 0 |

---

## 2. Ingestion & V14 Pipeline Rebuild Metrics

- **Raw Candidates Ingested**: **59,784 records**
- **Clean V14 Records Accepted**: **50,491 records**
- **Master Dataset File**: `datasets/v14/qg_dataset_v14.jsonl` (50,491 records)
- **Train / Validation Split (Seed 42)**:
  - **Train V14 (80%)**: **40,392 records** (`datasets/v14/qg_train_dataset_v14.jsonl`)
  - **Validation V14 (20%)**: **10,099 records** (`datasets/v14/qg_validation_dataset_v14.jsonl`)
- **Records Rejected**: **9,293 records**
  - Target Stem Deduplication (Train/Val Protection): **9,248 records**
  - Chemical Domain Sanity Violations: **2 records** (Caught negative moles/concentration anomalies)
  - Empty or Short Stems (<10 chars): **43 records**

---

## 3. Curriculum & STEM Distribution in V14

### A. Subject Distribution & Threshold Analysis
- **Chemistry**: **11,088** (21.96%) [Threshold >=5,000: **PASS**]
- **General Science**: **10,280** (20.36%)
- **Mathematics**: **9,626** (19.06%) [Threshold >=5,000: **PASS**]
- **Biology**: **5,529** (10.95%) [Threshold >=5,000: **PASS**]
- **Physics**: **3,580** (7.09%) [Threshold >=5,000: **FAIL** (3,580 < 5,000)]
- **Social Science**: **630** (1.25%)
- **Business & Law**: **578** (1.14%)
- **History & Civics**: **464** (0.92%)
- **UNKNOWN**: **8,716** (17.26%)

### B. Class Grounding Distribution & Threshold Analysis
- **Class 9**: **3,442** (6.82%) [Threshold >=1,000: **PASS**]
- **Class 10**: **1,291** (2.56%) [Threshold >=1,000: **PASS**] *(430x expansion from 3 records)*
- **Class 11**: **1,043** (2.07%) [Threshold >=1,000: **PASS**]
- **Class 12**: **1,082** (2.14%) [Threshold >=1,000: **PASS**] *(1.85x expansion from 585 records)*
- **Total Explicit Class 9–12**: **6,858 records** (13.58%)
- **Class `UNKNOWN`**: **43,633 records** (86.42%)

### C. Board Grounding Distribution
- **CBSE**: **12** (0.02%)
- **State Board**: **0** (0.00%)
- **OpenStax Academic**: **3,372** (6.68%)
- **Public Benchmark**: **47,107** (93.30%)
- **UNKNOWN**: **0** (0.00%)

---

## 4. Verification & Forensic Quality Gates

- **JSON Syntax Errors**: **0** (PASS)
- **Exact Target Overlap**: **0** (PASS)
- **Normalized Target Overlap**: **0** (PASS)
- **Duplicate Prompt-Target Pairs**: **0** (PASS)
- **Exact Prompt Overlap**: **153** (Control prefixes identical across distinct question stems; zero target leakage)
- **Verification Breakdown**:
  - `VERIFIED_HEURISTIC`: **49,748** (98.53%)
  - `NOT_VERIFIED`: **710** (1.41%)
  - `VERIFIED_DETERMINISTIC`: **31** (0.06%)
  - `REJECTED`: **2** (0.00%)
- **Tokenization Audit (`google/flan-t5-small`, 2,000 samples, seed 42)**:
  - Input Tokens: Min **48**, Max **70**, Avg **53.7** (0.00% > 128 tokens, 0.00% > 256 tokens)
  - Target Tokens: Min **3**, Max **144**, Avg **27.4** (0.30% > 128 tokens, 0.00% > 256 tokens)
- **Quality Gates Status**: **WARN**
  - Warning 1: Physics count (3,580) is below the 5,000 threshold.

---

## 5. Empirical Readiness Verdict & Supporting Evidence

### **FINAL VERDICT: B. NEED MORE DATA**

**Exact Supporting Evidence**:
1. **Class 9–12 Thresholds Fully Satisfied**: All four K-12 secondary classes achieved the required >=1,000 record threshold (Class 9: 3,442; Class 10: 1,291; Class 11: 1,043; Class 12: 1,082).
2. **Physics Representation Deficit**: While Physics grew from 2,872 to 3,580 records, it remains 1,420 records short of the mandatory 5,000-record threshold.
3. **Data Integrity & Zero Leakage**: Exact target leakage = 0, normalized target leakage = 0, and duplicate pairs = 0.
4. **Mandatory Stop Condition**: In accordance with instructions, model training remains prohibited until all threshold gates empirically clear.

---

## 6. Recommended Next Phase (Phase 15)

1. **Targeted Ingestion of 1,500+ Open Physics Records**: Ingest specialized open physics problem collections (e.g., OpenStax College Physics / OpenStax High School Physics problem banks) to push Physics past 5,000 records.
2. **Final Verification & Full Model Training Authorization**: Once Physics crosses 5,000, trigger Phase 15 FLAN-T5 model training with complete curriculum conditioning across all STEM domains and K-12 grades.
