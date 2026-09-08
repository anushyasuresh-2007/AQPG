# AQPG Phase 20 Step 11 — Quality-Gate Evaluation Report

**Execution Statement:** `PHASE 20 STEP 11 — QUALITY-GATE EVALUATION COMPLETE`  
**Overall Verdict:** `OVERALL VERDICT: FAIL`  
**Execution Mode:** ANALYSIS-ONLY (No Model Loading, No Inference, No Retraining)  
**Timestamp:** 2026-08-24 15:28:30  

---

## 1. Executive Summary & Analysis-Only Declaration

This report documents the official execution of **Phase 20 Step 11: Phase 18 Quality-Gate Pass/Fail Evaluation** for the Automated Question Pair Generation (AQPG) project.

> [!IMPORTANT]
> **ANALYSIS-ONLY EVALUATION DECLARATION**:
> - Step 11 evaluates the **authoritative historical recorded metrics** from Phase 20 Step 9 against the mandatory Phase 18 success gate thresholds defined in [`phase18_v16_experiment_plan.json`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase18_v16_experiment_plan.json).
> - **No PyTorch or HuggingFace model was loaded.**
> - **No text generation or inference was executed.**
> - **No model fine-tuning or retraining was performed.**
> - Recovered intermediate checkpoints (`checkpoint-500`, `checkpoint-1000`) were **NOT** substituted for final model evaluation.
> - All prior Step 9 evaluation artifacts remain untouched and un-modified.

---

## 2. Mandatory Quality-Gate Audit Table

Out of **9 mandatory quality gates** established in Phase 18, the V16 model **PASSED 2 gates** and **FAILED 7 gates**, resulting in a overall quality gate pass rate of **22.22%**.

| Gate ID | Metric Name | V16 Recorded Value | Required Threshold | Operator | Verdict | Source Artifact | Directly Verifiable? |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- | :---: |
| **GATE-01** | Question Structural Validity Rate | **98.20%** | `>= 95.0%` | `>=` | <span style="color:green; font-weight:bold;">PASS</span> | Step 9 Report | **YES** |
| **GATE-02** | Subject Conditioning Accuracy | **67.60%** | `>= 85.0%` | `>=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-03** | Topic Alignment Accuracy | **72.60%** | `>= 80.0%` | `>=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-04** | Question-Type Accuracy | **46.80%** | `>= 85.0%` | `>=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-05** | Control Sensitivity Rate | **0.00%** | `>= 80.0%` | `>=` | <span style="color:red; font-weight:bold;">FAIL</span> | `phase17_control_sensitivity.json`, Step 9 Report | **YES** |
| **GATE-06** | Template Concentration Ceiling | **100.00%** *(Top-10)* | `<= 30.0%` | `<=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-07** | Exact Training Memorization Rate | **4.62%** | `<= 2.0%` | `<=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-08** | Numerical Calculation Validity Rate | **19.41%** | `>= 85.0%` | `>=` | <span style="color:red; font-weight:bold;">FAIL</span> | Step 9 Report | **YES** |
| **GATE-09** | Class-Level Grounded Accuracy | **81.60%** | `>= 75.0%` | `>=` | <span style="color:green; font-weight:bold;">PASS</span> | Step 9 Report | **YES** |

---

## 3. Summary Statistics

- **Total Quality Gates Evaluated:** `9`
- **Passed Quality Gates:** `2` (Question Structural Validity: 98.20%, Class-Level Grounded Accuracy: 81.60%)
- **Failed Quality Gates:** `7` (Subject Accuracy, Topic Accuracy, Question-Type Accuracy, Control Sensitivity, Template Concentration Ceiling, Exact Training Memorization, Numerical Calculation Validity)
- **Quality-Gate Pass Rate:** `22.22%`
- **Final Quality-Gate Verdict:** **`OVERALL VERDICT: FAIL`**

---

## 4. Analysis of Gate Failures

1. **Control Sensitivity Deficit (0.00% vs 80.0% required):** The V16 model exhibits total parameter blindness. Changing control attributes in prompts (e.g. difficulty, marks, class) fails to alter output text generation.
2. **Template Collapse Deficit (100.0% Top-10 Concentration vs <= 30.0% required):** 100% of generated outputs collapse into top-10 MCQ template stems ("Which of the following is..."), suppressing non-MCQ generation formats.
3. **Question-Type Mismatch (46.80% vs 85.0% required):** Low question-type accuracy caused directly by MCQ template collapse when non-MCQ question types are requested.
4. **Numerical Solution Failure (19.41% vs 85.0% required):** 80.59% of numerical math/physics prompts fail exact calculation verification.
5. **Training Memorization Breach (4.62% vs <= 2.0% required):** Exact training substring match rate exceeds the 2.0% maximum ceiling.
6. **Subject & Topic Accuracy Deficits:** Subject accuracy (67.60%) and Topic accuracy (72.60%) show marked improvement over V15, but fail strict production benchmarks (85.0% and 80.0%).

---

## 5. System Integrity Check & Verification Log

Prior to finalizing Step 11, a full system safety audit was executed:

- **No PyTorch / Transformers model loaded:** `CONFIRMED`
- **No model inference executed:** `CONFIRMED`
- **No training / fine-tuning executed:** `CONFIRMED`
- **No Step 9 historical artifacts modified:** `CONFIRMED`
- **Step 11 output files created only:** `CONFIRMED` (`phase20_step11_quality_gate_report.json`, `docs/phase20_step11_quality_gate_report.md`)

---

## 6. Project Boundary Statement

> [!WARNING]
> **CRITICAL BOUNDARY ENFORCED**:
> **Steps 12–14 have NOT been executed.**
> Step 11 is now COMPLETED with verdict `FAIL`. Execution has paused. Next step in sequence is **Step 12 — Forensic Failure Mode Audit**.
