# AQPG V17 Remediation — Step 2: Dataset Redesign & Rebalancing Specification

**Completion Statement:** `PHASE 21A STEP 2 — V17 DATASET REDESIGN SPECIFICATION COMPLETE`  
**Operational Mode:** `DESIGN ONLY — NO DATASET MODIFIED`  
**Safety Declarations:**  
- `NO MODEL LOADED`  
- `NO INFERENCE EXECUTED`  
- `NO TRAINING EXECUTED`  
- `NO PHASE 20 ARTIFACTS MODIFIED`  
**Authorization Requirement:** `V17 DATASET BUILD REQUIRES SEPARATE AUTHORIZATION`  
**Timestamp:** 2026-08-24 17:25:00  

---

## 1. Executive Summary & Design Scope

This document specifies the **quantitative redesign for the AQPG V17 training dataset**, directly addressing the 6 major failure modes isolated during the Phase 21A Step 1 forensic audit of the V16 model.

### V16 Baseline Failure Summary
- **Input Prompt Concentration:** Only 204 unique input prompts across 40,557 training records (`0.50%` unique prompt ratio). Top 3 prompts account for 42.96% of the entire dataset.
- **Control Blindness (`0.00%` sensitivity):** Caused by extreme input prompt repetition.
- **Template Collapse (`100%` Top-10 Concentration):** Caused by 61.55% MCQ target density and prompt concentration.
- **Question-Type Accuracy (`46.80%`):** Caused by a 24x deficit in Conceptual targets (`1.38%` / 560 records in training vs `33.3%` in benchmark).
- **Numerical Validity (`19.41%`):** Caused by 85.3% of numerical prompts being concentrated in a single generic Mathematics prompt.
- **Class Grounding Deficit:** `82.13%` (`33,310 / 40,557`) of records contain `class: UNKNOWN`.

---

## 2. Section A — Target Dataset Size Trade-Off Analysis

Three candidate dataset scale options were evaluated for V17:

| Option | Target Record Count | Pros | Cons / Trade-offs | Verdict |
| :--- | :---: | :--- | :--- | :--- |
| **Option A** | `40,000` | Matches V16 scale; fast training time (~6,000 steps). | Risks insufficient coverage when oversampling Conceptual and Numerical targets. | **Rejected** |
| **Option B** | **`50,000`** | **Optimal balance of prompt diversity, conceptual oversampling, and deduplication.** | Requires slight increase in training steps (~7,500 steps), well within compute budget. | **`SELECTED`** |
| **Option C** | `60,000` | High theoretical diversity. | Increases risk of synthetic duplicate injection and longer training times (~9,000 steps). | **Rejected** |

**Selection:** **Option B — 50,000 Total Records (40,000 Train / 10,000 Validation)**.

---

## 3. Section B — Question-Type Distribution Design

To eliminate MCQ template dominance and solve the 24x Conceptual question deficit, the V17 target distribution is specified as follows:

| Question Type | V16 Baseline % | V17 Target % | V17 Target Count (50k) | Minimum % | Maximum % | Primary Redesign Purpose |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **MCQ** | `61.55%` | **`35.0%`** | **17,500** | `30.0%` | `40.0%` | Downsampled from 61.55% to prevent template collapse |
| **Numerical** | `20.32%` | **`35.0%`** | **17,500** | `30.0%` | `40.0%` | Expanded across Physics, Math, and Chemistry |
| **Conceptual** | `1.38%` | **`25.0%`** | **12,500** | `20.0%` | `30.0%` | Substantially increased from 1.38% (560 records) |
| **Short Answer** | `16.74%` | **`5.0%`** | **2,500** | `3.0%` | `10.0%` | Retained for explanatory text sentence variety |
| **TOTAL** | `100.0%` | **`100.0%`** | **50,000** | — | — | Sum = 100.0% |

---

## 4. Section C — Control Dimension Distribution Specifications

| Control Dimension | Target Distribution | Minimum % | Maximum % | Policy on UNKNOWN Values |
| :--- | :--- | :---: | :---: | :--- |
| **Subject** | Physics (`30%`), Chemistry (`30%`), Math (`30%`), Bio/GenSci (`10%`) | `25%` | `35%` | Require explicit STEM subject taxonomy |
| **Class** | Class 9 (`25%`), Class 10 (`25%`), Class 11 (`25%`), Class 12 (`25%`) | `20%` | `30%` | **`0.0% UNKNOWN`** (100% grounded grade metadata) |
| **Difficulty** | Easy (`33.3%`), Medium (`33.3%`), Hard (`33.4%`) | `30%` | `40%` | Equal balance across difficulty tiers |
| **Marks** | 1 Mark (`30%`), 2 Marks (`30%`), 3 Marks (`25%`), 5 Marks (`15%`) | `10%` | `35%` | Align mark tier with expected answer length |
| **Bloom Level** | Remember (`15%`), Understand (`30%`), Apply (`35%`), Analyze (`15%`), Create (`5%`) | `5%` | `40%` | Balance lower and higher cognitive levels |

---

## 5. Section D — Control Combination Coverage Requirements

To eliminate the V16 prompt concentration defect (where only 204 unique input prompts existed), V17 enforces strict prompt diversification ceilings:

- **Minimum Unique Input Prompts:** **`>= 30,000`** (out of 50,000 total records).
- **Minimum Unique Input Prompt Ratio:** **`>= 60.0%`** (vs V16's `0.50%`).
- **Maximum Single Prompt Frequency:** **`<= 50`** instances (`<= 0.10%` of dataset).
- **Maximum Top-3 Prompt Concentration:** **`<= 0.30%`** (`<= 150` records total).
- **Maximum Top-10 Prompt Concentration:** **`<= 0.80%`** (`<= 400` records total).

---

## 6. Section E — Control Sensitivity Paired Prompt Design

To guarantee parameter sensitivity, V17 requires explicit **Paired Control Quadruplets** in training:
- **Rule:** For identical subject and topic contexts, construct quadruplets where **ONE control tag varies while all other tags remain fixed**.
- **Minimum Required Paired Groups:** **`>= 2,500`** quadruplet groups (`>= 10,000` paired records).
- **Target Non-Identity Requirement:** Changing `difficulty` (`Easy` -> `Hard`), `marks` (`1` -> `5`), or `type` (`MCQ` -> `Conceptual`) **MUST produce non-identical target text stems**. Artificial pairs with identical targets are strictly prohibited.

---

## 7. Section F — Template Diversity Anti-Collapse Requirements

To enforce the Phase 18 Template Concentration Gate (`<= 30.0%` Top-10 concentration):
- **Minimum Unique Normalized Target Stems:** **`>= 90.0%`** (>= 45,000 unique target stems).
- **Top-10 Target Stem Concentration Ceiling:** **`<= 15.0%`** (well below the <= 30.0% threshold).
- **Target Stem Entropy Ceiling:** **`>= 10.0 bits`**.
- **Generic Stem Limit:** Generic prefixes (*"Which of the following is..."*) are constrained to **`<= 5.0%`** of total dataset targets.

---

## 8. Section G — Numerical Data Policy & Multi-Subject Distribution

- **Total Numerical Records:** **`17,500`** (`35.0%` of V17 dataset).
- **Subject Distribution:** Mathematics (`40%` / 7,000), Physics (`40%` / 7,000), Chemistry (`20%` / 3,500).
- **Single-Prompt Numerical Ceiling:** **`<= 1.0%`** (max 175 repeats per prompt, vs V16's 85.3%).
- **Quality Rules:** 100% of numerical targets must contain explicit numbers, valid math relationships, units, and calculable answers.

---

## 9. Section H — Subject / Topic Conditioning & Validation Rules

Every V17 training example must pass automated schema validation:
1. `subject` must match NCERT/OpenStax STEM domain taxonomy.
2. `topic` must belong to the declared subject.
3. `question_type` must match the target text structure (e.g. `Numerical` targets must contain calculation steps; `MCQ` targets must contain multiple-choice options).
4. `difficulty` and `marks` must correlate with target sentence complexity and length.

---

## 10. Section I — Duplication & Memorization Control Policy

- **Level 1 (Exact Input Duplicate):** `0.0%` (Prohibited).
- **Level 2 (Exact Input-Target Pair Duplicate):** `0.0%` (Prohibited).
- **Level 3 (Near-Duplicate Target Stem):** `<= 2.0%`.
- **Train/Val Leakage:** `0` exact target leakage; `<= 1.0%` stem leakage across splits.

---

## 11. Section J — Train / Validation Split Strategy

- **Selected Strategy:** **80 / 20 Stratified Split** (40,000 train / 10,000 validation).
- **Execution:** Deduplication is executed **BEFORE** splitting. Stratification is enforced across `question_type`, `subject`, and `class`.

---

## 12. Section K — Benchmark Alignment (Held-Out Benchmark Defense)

- The frozen **520 evaluation prompts** (`phase20_evaluation_prompts.jsonl`, SHA-256: `91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E`) remain strictly held-out.
- **Zero benchmark prompts or targets** will be included in the V17 training or validation datasets.

---

## 13. Section L — Mandatory Dataset Construction Rules

```
RULE 1: No exact duplicate input-target pairs.
RULE 2: Maximum single input prompt concentration <= 0.10%.
RULE 3: Question-type target distribution must match 35% MCQ / 35% Num / 25% Conc / 5% Short.
RULE 4: 0.0% UNKNOWN class tokens allowed (100% Class 9-12 grounded).
RULE 5: Paired control quadruplets must produce distinct target stems.
RULE 6: Numerical prompts must be distributed across Math (40%), Physics (40%), Chemistry (20%).
RULE 7: Top-10 target stem concentration must be <= 15.0%.
RULE 8: Train/validation target leakage is strictly 0.
RULE 9: Benchmark prompts remain 100% held-out.
RULE 10: All records must retain full source dataset provenance.
```

---

## 14. Section M — V17 Pre-Training Dataset Quality Gates

The V17 dataset cannot proceed to training unless all 13 gates pass:

| Gate ID | Gate Name | Metric Formula | Target Threshold | Type | Failure Addressed |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **GATE-D1** | Unique Input Prompt Ratio | `unique_prompts / total_records` | **`>= 60.0%`** | **MANDATORY** | Control Blindness (`0.00%`) |
| **GATE-D2** | Max Single Prompt Concentration | `max_single_prompt / total_records` | **`<= 0.10%`** | **MANDATORY** | Control Blindness (`0.00%`) |
| **GATE-D3** | Top-3 Prompt Concentration | `top_3_prompts / total_records` | **`<= 0.30%`** | **MANDATORY** | Control Blindness (`0.00%`) |
| **GATE-D4** | Conceptual Question Representation | `conceptual_count / total_records` | **`>= 25.0%`** | **MANDATORY** | Question-Type Mismatch (`46.80%`) |
| **GATE-D5** | Numerical Question Representation | `numerical_count / total_records` | **`>= 35.0%`** | **MANDATORY** | Numerical Validity (`19.41%`) |
| **GATE-D6** | MCQ Representation Ceiling | `mcq_count / total_records` | **`<= 35.0%`** | **MANDATORY** | Template Collapse (`100% Top-10`) |
| **GATE-D7** | Class UNKNOWN Token Rate | `class_unknown_count / total_records` | **`0.0%`** | **MANDATORY** | Subject/Topic Conditioning |
| **GATE-D8** | Numerical Subject Concentration | `max_subject_num / total_num` | **`<= 45.0%`** | **MANDATORY** | Numerical Validity (`19.41%`) |
| **GATE-D9** | Top-10 Target Stem Concentration | `top_10_target_stems / total_records` | **`<= 15.0%`** | **MANDATORY** | Template Collapse (`100% Top-10`) |
| **GATE-D10** | Exact Duplicate Pair Rate | `duplicate_pairs / total_records` | **`0.0%`** | **MANDATORY** | Memorization Breach (`4.62%`) |
| **GATE-D11** | Train/Val Exact Target Leakage | `exact_target_leakage_count` | **`0`** | **MANDATORY** | Train/Val Leakage |
| **GATE-D12** | Paired Control Quadruplets | `paired_quadruplet_count` | **`>= 2,500`** | **MANDATORY** | Control Blindness (`0.00%`) |
| **GATE-D13** | Target Stem Entropy | `normalized_stem_entropy_bits` | **`>= 10.0 bits`** | ADVISORY | Template Diversity |

---

## 15. Section N — Failure Mode to Intervention Mapping

| V16 Failure Mode | V17 Dataset Intervention | Expected Impact | Risk | Measurement Method |
| :--- | :--- | :--- | :--- | :--- |
| **Control Blindness (`0.00%`)** | Prompt deduplication (`>=60%` unique ratio) + paired control quadruplets | Forces parameter attention sensitivity | Synthetic prompt distortion | GATE-D1, GATE-D12 audit |
| **Template Collapse (`100%`)** | Downsample MCQ to 35% + stem anti-collapse filtering | Restores generation variation (`<=15%` Top-10) | Loss of basic MCQ fluency | GATE-D6, GATE-D9 audit |
| **Question-Type Mismatch (`46.80%`)** | Oversample Conceptual targets to 25% (12.5k records) | Corrects 24x benchmark deficit | Synthetic concept noise | GATE-D4 audit |
| **Numerical Validity (`19.41%`)** | Distribute Numerical prompts across Math (40%), Physics (40%), Chem (20%) | Enables cross-subject math reasoning | Formula parsing errors | GATE-D5, GATE-D8 audit |
| **Memorization Breach (`4.62%`)** | Level 1–3 deduplication + prompt concentration ceiling | Reduces exact verbatim copying below 2.0% | Oversampling duplication | GATE-D10, GATE-D11 audit |

---

## 16. Section O — Over-Correction Safeguards & Risk Audit

To prevent negative side effects from aggressive rebalancing:
1. **Safeguard 1 (Fluency Maintenance):** Maintain at least 17,500 high-quality MCQ targets (35%) so the model retains surface question syntax (`>=95%` validity).
2. **Safeguard 2 (Synthetic Noise Prevention):** All oversampled Conceptual and Numerical targets must derive from verified raw STEM corpora (ScienceQA, NCERT, OpenStax, EduQG).
3. **Safeguard 3 (Benchmark Defense):** Benchmark prompts (`phase20_evaluation_prompts.jsonl`) remain strictly held-out.

---

## 17. Section P — Consolidated V17 Dataset Master Specification

| Specification Dimension | V16 Baseline Value | V17 Target Specification | Mandatory Minimum | Mandatory Maximum | Validation Gate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Total Dataset Size** | 40,557 | **50,000** | 45,000 | 55,000 | Record Count Check |
| **Train / Val Split** | 40,557 / 10,138 | **40,000 / 10,000** | 80/20 | 80/20 | Split Ratio Check |
| **Unique Input Prompts** | 204 (`0.50%`) | **`>= 30,000` (`>= 60.0%`)** | `60.0%` | `100.0%` | **GATE-D1** |
| **Max Single Prompt Concentration** | 17.34% (7,034 repeats) | **`<= 0.10%` (<= 50 repeats)** | `0.0%` | `0.10%` | **GATE-D2** |
| **Question Type: MCQ** | `61.55%` | **`35.0%` (17,500)** | `30.0%` | `35.0%` | **GATE-D6** |
| **Question Type: Numerical** | `20.32%` | **`35.0%` (17,500)** | `30.0%` | `40.0%` | **GATE-D5** |
| **Question Type: Conceptual** | `1.38%` (560) | **`25.0%` (12,500)** | `25.0%` | `30.0%` | **GATE-D4** |
| **Question Type: Short Answer** | `16.74%` | **`5.0%` (2,500)** | `3.0%` | `10.0%` | Type Audit |
| **Class UNKNOWN Token Rate** | `82.13%` (33,310) | **`0.0%` (100% Grounded)** | `0.0%` | `0.0%` | **GATE-D7** |
| **Top-10 Target Stem Concentration** | `1.03%` train / `100%` model | **`<= 15.0%`** | `0.0%` | `15.0%` | **GATE-D9** |
| **Exact Duplicate Pair Rate** | `0.0%` | **`0.0%`** | `0.0%` | `0.0%` | **GATE-D10** |
| **Train/Val Exact Target Leakage** | `0` | **`0`** | `0` | `0` | **GATE-D11** |
| **Paired Control Quadruplets** | `0` | **`>= 2,500` groups** | `2,500` | `5,000` | **GATE-D12** |

---

## 18. Section Q — Step 3 Build Execution Sequence

1. Extract raw unified records from verified source datasets (`ScienceQA`, `NCERT`, `EduQG`, `OpenStax`).
2. Standardize control metadata schemas (`subject`, `topic`, `class`, `difficulty`, `marks`, `type`, `bloom`).
3. Replace all `class: UNKNOWN` tokens with grounded `Class 9`, `Class 10`, `Class 11`, or `Class 12` tags.
4. Execute Level 1–3 deduplication.
5. Build paired control quadruplets (`>=2,500` groups).
6. Oversample Conceptual targets to 12,500 records (`25%`) and Numerical targets to 17,500 records (`35%`).
7. Downsample MCQ targets to 17,500 records (`35%`).
8. Distribute Numerical prompts across Physics (`40%`), Math (`40%`), and Chemistry (`20%`).
9. Execute stratified 80/20 train/validation split.
10. Run pre-training dataset quality gates script (`GATE-D1` to `GATE-D13`).
11. Compute SHA-256 hashes of `qg_train_dataset_v17.jsonl` and `qg_validation_dataset_v17.jsonl` and **STOP**.

---

## 19. Mandatory Declarations & Completion Verdict

```
PHASE 21A STEP 2 — V17 DATASET REDESIGN SPECIFICATION COMPLETE

DESIGN ONLY — NO DATASET MODIFIED

NO MODEL LOADED
NO INFERENCE EXECUTED
NO TRAINING EXECUTED
NO PHASE 20 ARTIFACTS MODIFIED

V17 DATASET BUILD REQUIRES SEPARATE AUTHORIZATION
```

> [!STOP]
> **MANDATORY STOP ENFORCED**: Step 2 specification complete. No dataset has been built or modified. Retraining and dataset construction require explicit separate authorization.
