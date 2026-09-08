# AQPG Phase 19: V16 Dataset Rebalancing, Prompt Optimization & Forensic Validation

## Executive Summary
In Phase 19, the AQPG V16 dataset was constructed to directly mitigate the empirical failure modes diagnosed during Phase 18:
1. **Target-Template Concentration**: Capped extreme high-frequency generic templates (ceiling 350 per template skeleton on ungrounded data), reducing top-10 concentration from **16.10% to 12.80%** and increasing structural entropy from **12.93 bits to 13.20 bits**.
2. **Curriculum Protection**: 100% preserved all 9,058 explicit Class 9–12 records, increasing grounded class representation to **17.87%**.
3. **Numerical Protection**: 100% preserved all 10,304 numerical records across Mathematics, Physics, and Chemistry.
4. **Physics Protection**: 100% preserved all 5,780 Physics records.
5. **Prompt Schema Optimization**: Streamlined prompt schema to eliminate dilutive literal `UNKNOWN` strings (`board: UNKNOWN | unit: UNKNOWN`), shortening prompt length and strengthening attention on core control tags.
6. **Zero Leakage**: Guaranteed 0 exact target leakage, 0 normalized target leakage, 0 prompt-target pair leakage, and 0 internal duplicate pairs across deterministic 80/20 train/validation splits (seed 42).

---

## 1. Dataset Scale & Split Summary
- **V15 Master Records**: `52,691`
- **V16 Master Records**: `50,695` (`-1,996` ungrounded repetitive template instances pruned)
- **V16 Train Split**: `40,557` (80.00%)
- **V16 Validation Split**: `10,138` (20.00%)

---

## 2. Subject & Curriculum Distributions

### Subject Breakdown
- **Mathematics**: 9,626 (18.99%) — 100% Preserved
- **Physics**: 5,780 (11.40%) — 100% Preserved
- **Chemistry**: 10,001 (19.73%)
- **Biology**: 5,264 (10.38%)
- **General Science**: 9,923 (19.57%)

### Class Breakdown
- **Class 9**: 3,442 (6.79%) — 100% Preserved
- **Class 10**: 1,291 (2.55%) — 100% Preserved
- **Class 11**: 2,343 (4.62%) — 100% Preserved
- **Class 12**: 1,982 (3.91%) — 100% Preserved
- **UNKNOWN**: 41,637 (82.13%)
- **Grounded Curriculum Total**: 9,058 records (17.87%)

---

## 3. Question Type & Numerical Distribution
- **Numerical**: 10,304 records (20.33%) — 100% Preserved
- **MCQ**: 31,202 records (61.55%)
- **Conceptual**: 700 records (1.38%)

---

## 4. Prompt Schema Optimization
The V16 prompt formatting rule eliminates dilutive `UNKNOWN` tokens:
- **Canonical Schema**: `generate question | subject: {subject} | topic: {topic} | class: {class} | difficulty: {difficulty} | marks: {marks} | type: {question_type}`
- **Optional Tags Included ONLY When Verified**: `| bloom: {bloom} | unit: {unit} | board: {board}`
- **Result**: Reduced average input token length from 57 to 48.8 tokens while removing attention noise.

---

## 5. Tokenization Profiling (google/flan-t5-small)
- **Input Tokens**: Min 45, Max 70, Mean 48.87, Median 47, P95 56, P99 60, `>256: 0.0%`
- **Target Tokens**: Min 4, Max 191, Mean 28.26, Median 20, P95 72, P99 96, `>256: 0.0%`

---

## 6. Hard Quality Gates Verification

| Quality Gate | Condition | Measured Result | Status |
| :--- | :--- | :--- | :---: |
| **Syntax Errors** | Must be 0 | `0` | **PASS** |
| **Schema Violations** | Must be 0 | `0` | **PASS** |
| **Exact Target Leakage** | Must be 0 | `0` | **PASS** |
| **Normalized Target Leakage** | Must be 0 | `0` | **PASS** |
| **Prompt-Target Pair Leakage** | Must be 0 | `0` | **PASS** |
| **Duplicate Prompt-Target Pairs** | Must be 0 | `0` | **PASS** |
| **Tokenization Bounded <= 256** | Must be 0% > 256 | `0.00%` | **PASS** |

---

## 7. Artifact Deliverables
1. [`build_qg_dataset_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/build_qg_dataset_v16.py)
2. [`audit_qg_dataset_v16.py`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/backend/ml/evaluation/audit_qg_dataset_v16.py)
3. [`qg_dataset_v16_schema.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/qg_dataset_v16_schema.json)
4. [`v16_prompt_schema.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/v16_prompt_schema.json)
5. [`datasets/v16/qg_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_dataset_v16.jsonl)
6. [`datasets/v16/qg_train_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_train_dataset_v16.jsonl)
7. [`datasets/v16/qg_validation_dataset_v16.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/datasets/v16/qg_validation_dataset_v16.jsonl)
8. [`phase19_template_analysis.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_template_analysis.json)
9. [`phase19_class_rebalancing.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_class_rebalancing.json)
10. [`phase19_prompt_schema_analysis.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_prompt_schema_analysis.json)
11. [`phase19_numerical_balance.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_numerical_balance.json)
12. [`phase19_v15_v16_comparison.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_v15_v16_comparison.json)
13. [`phase19_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_audit.json)
14. [`phase19_audit_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase19_audit_report.txt)
15. [`implementation_notes_v19.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/implementation_notes_v19.md)

---

## 8. Final Empirical Verdict

### **FINAL VERDICT: A. READY FOR CONTROLLED TRAINING**
