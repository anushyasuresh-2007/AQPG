# AQPG Phase 18: Forensic Failure Diagnosis, Dataset Rebalancing & Training Strategy Design

## Executive Summary
Following the empirical Phase 17 evaluation of FLAN-T5-Small V15 (verdict `B. PROMISING — NEEDS IMPROVEMENT`), Phase 18 performed an exhaustive forensic diagnosis across the 52,691 master records, prompt schema, target distributions, and training hyperparameter configurations. 

This diagnosis definitively established the root causes for the measured **88.08% template repetition**, **30% control sensitivity**, and **43.27% topic accuracy**.

---

## 1. Summary of Forensic Discoveries

### A. The Core Training Blocker: Extreme Undertraining (0.019 Epochs)
- In Phase 16, FLAN-T5-Small was fine-tuned for **100 steps** with effective batch size 8 (batch size 4 × gradient accumulation 2).
- This exposed the model to **only 800 training examples** out of the **42,152** training records (**1.898% dataset coverage**).
- **Consequence**: The model completed only **0.019 epochs**. The weights never converged across the diverse multi-subject STEM corpus. The model updated only enough to output basic English question syntax, remaining trapped in the highest-frequency generic MCQ templates.

### B. Class Label Sparsity (82.68% UNKNOWN)
- **Class UNKNOWN**: 34,851 / 42,152 training records (**82.68%**).
- **Explicit Class 9–12 Grounded**: 7,301 records (Class 9: 2,764; Class 10: 1,028; Class 11: 1,920; Class 12: 1,589).
- **Consequence**: Because over 82% of training inputs contain `class: UNKNOWN`, the model learned to treat the class token as an uninformative feature, resulting in the measured `CONTROL-BLIND` rating (30% sensitivity).

### C. Numerical Data Health
- **Total Numerical Labelled Records**: 8,228 records (19.52% of train data).
- **Contains Actual Digits**: 8,094 records (98.37% of numerical subset).
- **Purely Conceptual Mislabelled**: 23 records (0.28%).
- **Finding**: The numerical data in V15 is structurally authentic (98%+ contain numeric quantities and math structures). The failure of V15 to generate numerical questions in Phase 17 was a direct consequence of the 100-step undertraining, which failed to activate the mathematical generation heads.

### D. Prompt Overhead & Dilution
- The current prompt template uses 9 rigid pipe-separated fields (`generate question | subject: ... | topic: ... | unit: ... | class: ... | board: ... | bloom: ... | difficulty: ... | marks: ... | type: ...`).
- When fields are missing, literal `UNKNOWN` strings are injected (`board: UNKNOWN | unit: UNKNOWN`), introducing semantic noise.

---

## 2. Ranked Root Cause Analysis

| Rank | Root Cause | Confidence | Evidence & Measured Impact |
| :---: | :--- | :---: | :--- |
| **1** | **Severe Undertraining (0.019 Epochs)** | **HIGH** | Only 800 / 42,152 samples exposed to model. Primary driver of 88.08% template repetition and control blindness. |
| **2** | **Class Label Sparsity (82.7% UNKNOWN)** | **HIGH** | 34,851 records have no class grounding, causing model to ignore class conditioning. |
| **3** | **MCQ Target Template Skew in Raw Sources** | **HIGH** | Public benchmarks (SciQ, ARC) disproportionately favor `"Which of the following..."` and `"What is the..."`. |
| **4** | **Prompt Delimiter Dilution & UNKNOWN Noise** | **MEDIUM** | 9-tuple prompt with repeated `UNKNOWN` strings dilutes attention over core subject/topic controls. |
| **5** | **Model Parameter Capacity (77M FLAN-T5-Small)** | **MEDIUM** | Secondary factor; capacity is adequate for domain templates, but limits multi-step numerical calculation reasoning. |

---

## 3. Evidence-Based Model Scaling Decision

### **DECISION: B. Move to FLAN-T5-base after data correction**

### Technical Rationale:
Scaling directly to FLAN-T5-Base (250M parameters) or Large (780M parameters) **before** fixing dataset rebalancing, template skew, and prompt schema would simply cause the larger model to overfit faster to the dominant `"Which of the following is not..."` template. 

The correct engineering path is:
1. **Rebalance & Filter Dataset for V16**: Cap dominant MCQ templates, oversample explicit Class 9–12 records, and streamline prompt schema.
2. **Train FLAN-T5-Small on Full Epochs (Experiment B)** as a strict baseline.
3. **Scale to FLAN-T5-Base (Experiment C)** with the clean balanced dataset to unlock senior secondary reasoning.

---

## 4. Proposed V16 Training Strategy & Controlled Experiment Plan

### Experiment Matrix

```
+---------------------------------------------------------------------------------------------------+
| Experiment   | Architecture      | Dataset                          | Training Setup   | Target   |
+---------------------------------------------------------------------------------------------------+
| Exp A        | FLAN-T5-Small     | V15 Raw (42,152)                 | 3 Full Epochs    | Baseline |
| Exp B (Main) | FLAN-T5-Small     | V16 Rebalanced & Filtered        | 3 Full Epochs    | Primary  |
| Exp C        | FLAN-T5-Base      | V16 Rebalanced & Filtered        | 3 Full Epochs    | Scaling  |
+---------------------------------------------------------------------------------------------------+
```

---

## 5. Measurable V16 Production Success Gates

- **Question Validity Rate**: `>= 95.0%`
- **Subject Conditioning Accuracy**: `>= 85.0%`
- **Topic Alignment Rate**: `>= 80.0%`
- **Question-Type Alignment Rate**: `>= 85.0%`
- **Control Sensitivity Rate**: `>= 80.0%`
- **Template Repetition Rate**: `<= 30.0%`
- **Exact Memorization Rate**: `<= 2.0%`
- **Numerical Question Validity**: `>= 85.0%`
- **Class Alignment**: `>= 75.0%` on verified curriculum subset

---

## 6. Generated Artifacts
1. [`phase18_dataset_distribution.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_dataset_distribution.json)
2. [`phase18_template_analysis.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_template_analysis.json)
3. [`phase18_control_supervision.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_control_supervision.json)
4. [`phase18_numerical_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_numerical_audit.json)
5. [`phase18_class_supervision.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_class_supervision.json)
6. [`phase18_prompt_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_prompt_audit.json)
7. [`phase18_training_config_audit.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_training_config_audit.json)
8. [`phase18_root_cause_analysis.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_root_cause_analysis.json)
9. [`phase18_v16_experiment_plan.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_v16_experiment_plan.json)
10. [`phase18_report.txt`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_report.txt)
11. [`phase18_representative_training_samples.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_representative_training_samples.jsonl)
12. [`implementation_notes_v18.md`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/implementation_notes_v18.md)
