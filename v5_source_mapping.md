# AQPG V5 Source Mapping & Metadata Provenance Specification

## Executive Summary

This document maps all raw data sources available in the AQPG project to the **V5 Master Schema**. It defines exact metadata mapping rules, transformation pipelines, verification methods, provenance, license terms, and metadata confidence levels.

Pursuant to Phase 4 rules:
- Metadata fields (`class`, `board`, `unit`) that cannot be established from the source are mapped to `"UNKNOWN"`.
- Target record counts are stated alongside **actual achievable counts** from local data files.

---

## Target vs Achievable Record Count Summary

| Subject Domain | Ideal Target Count | Achievable Count from Raw Files | Data Status |
| :--- | :--- | :--- | :--- |
| **Mathematics** | 15,000 | **~16,000 records** (GSM8K reasoning splits) | **Available & Verified** |
| **Physics** | 10,000 | **0 records** (Not present in current local files) | **[Supervision Gap] Requires Ingestion** |
| **Chemistry** | 10,000 | **0 records** (Not present in current local files) | **[Supervision Gap] Requires Ingestion** |
| **Biology / Health Sciences** | N/A | **~1,200 records** (EduQG OpenStax) | **Available** |
| **Social Sciences & Business** | N/A | **~6,600 records** (EduQG & Formatted) | **Available** |
| **General / Unclassified** | N/A | **~8,700 records** (Bloom Taxonomy) | **Available** |
| **Total Pipeline Volume** | **35,000+** | **~32,500 raw candidate records** | **Proceeding with full verification** |

---

## Detailed Source Mappings

### 1. GSM8K Reasoning Dataset (`gsm8k_reasoning`)

- **Files**: `main_train.csv`, `main_test.csv`, `socratic_train.csv`, `socratic_test.csv`
- **Record Count**: 17,584 raw entries (deduplicates to ~8,800 unique arithmetic word problems)
- **Subject**: `Mathematics` (Confidence: HIGH)
- **Class**: `UNKNOWN` (Grade level not explicit in GSM8K; ranges 6-9)
- **Board**: `UNKNOWN` (Public AI reasoning benchmark)
- **Unit**: `UNKNOWN`
- **Topic**: `Arithmetic & Quantitative Word Problems` (Extracted from formula steps)
- **Question Type**: `Numerical`
- **Bloom Taxonomy**: `Apply` (<= 2 formula steps) / `Analyze` (> 2 formula steps)
- **Difficulty**: `Medium` (<= 2 formula steps) / `Hard` (> 2 formula steps)
- **Marks**: 3 marks (Medium) / 4 marks (Hard)
- **Verification Method**: `sympy_deterministic_calculator` (SymPy symbolic evaluation of extracted `<<...>>` expressions against `####` answer string)
- **Provenance**: OpenAI GSM8K Benchmark (`https://github.com/openai/grade-school-math`)
- **License**: MIT License (Permissive Academic)
- **Metadata Confidence**: HIGH for Subject, Answer, and Formulas; LOW for K-12 Class/Board (marked `UNKNOWN`)
- **Safe for Training**: **YES** (100% verified math problems)

---

### 2. EduQG OpenStax Dataset (`eduqg`)

- **Files**: `eduqg_train.json`, `eduqg_val.json`, `eduqg_llm_formatted.csv`
- **Record Count**: ~6,760 records
- **Subject Mapping**:
  - `biology` / `anatomy_and_physiology` / `microbiology` -> `Biology` / `Anatomy & Physiology`
  - `psychology` / `introduction_to_sociology` -> `Psychology` / `Sociology`
  - `principles_of_accounting...` -> `Accounting`
  - `american_government` / `u.s._history` -> `History & Civics`
  - `business_law_i_essentials` / `business_ethics` -> `Business & Law`
- **Class**: `Higher Education / College` (OpenStax college textbooks; mapped to `UNKNOWN` for K-12)
- **Board**: `OpenStax Academic`
- **Unit**: Extracted from `bname` and `chapter` (e.g. `Chapter 5: Cell Metabolism`)
- **Topic**: Extracted from OpenStax summary text (first 100 chars)
- **Question Type**: `MCQ` (if choices array exists) / `Short Answer` / `Application Based`
- **Bloom Taxonomy**: Mapped from integer tags (`1` -> `Remember`, `2` -> `Understand`, `3` -> `Apply`, `4` -> `Analyze`)
- **Difficulty**: `Easy` (Remember/Understand) / `Medium` (Apply/Analyze)
- **Marks**: 1 mark (MCQ) / 2 marks (Short Answer) / 3 marks (Application)
- **Verification Method**: `textual_heuristic_validator` (Heuristic verification of context highlight `<hl>` and non-empty answer string)
- **Provenance**: OpenStax EduQG Dataset (`https://github.com/eduqg/eduqg`)
- **License**: CC BY 4.0 (Open Textbook License)
- **Metadata Confidence**: HIGH for Subject, Topic, Bloom; LOW for K-12 Board/Class (marked `UNKNOWN`)
- **Safe for Training**: **YES** (Conceptual & Application question generation)

---

### 3. Bloom Taxonomy Dataset (`bloom_taxonomy`)

- **Files**: `blooms_taxonomy_dataset.csv`
- **Record Count**: 8,767 records
- **Subject**: `UNKNOWN` (General questions across unmapped domains)
- **Class**: `UNKNOWN`
- **Board**: `UNKNOWN`
- **Unit**: `UNKNOWN`
- **Topic**: `General Concept Evaluation`
- **Question Type**: `Short Answer` / `Application Based` / `Long Answer`
- **Bloom Taxonomy**: Mapped from category (`BT1` -> `Remember`, `BT2` -> `Understand`, `BT3` -> `Apply`, `BT4` -> `Analyze`, `BT5` -> `Evaluate`, `BT6` -> `Create`)
- **Difficulty**: `Easy` (BT1-BT2) / `Medium` (BT3-BT4) / `Hard` (BT5-BT6)
- **Marks**: 1 mark (BT1-2) / 2 marks (BT3-4) / 4 marks (BT5-6)
- **Verification Method**: `textual_heuristic_validator` (Stem integrity & length >= 10 chars)
- **Provenance**: Kaggle Bloom's Taxonomy Question Dataset
- **License**: Public Domain / Permissive Academic
- **Metadata Confidence**: HIGH for Bloom Taxonomy level; LOW for Subject/Class/Board (marked `UNKNOWN`)
- **Safe for Training**: **YES** (Bloom level conditioning supervision)

---

## Transformation Pipeline Rules for V5

1. **No Hardcoded Defaults**: No field will be defaulted to "Mathematics" or "Class 10" if missing.
2. **Explicit `UNKNOWN` Tagging**: Missing metadata fields will be recorded as `"UNKNOWN"` in both record dicts and constructed `input_text` prompts.
3. **Structured Control Prompt Formatting**:
   ```
   generate question | subject: <subject> | topic: <topic> | unit: <unit> | class: <class> | board: <board> | bloom: <bloom> | difficulty: <difficulty> | marks: <marks> | type: <question_type>
   ```
