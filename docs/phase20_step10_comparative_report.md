# AQPG Phase 20 Step 10 — Base vs V15 vs V16 Comparative Analysis Report

**Execution Mode:** ANALYSIS-ONLY (No Model Loading, No Inference, No Retraining)  
**Timestamp:** 2026-08-24 15:20:00  
**Status:** COMPLETED  
**Final Verdict:** `STEP 10 — COMPARATIVE ANALYSIS COMPLETE; NO HISTORICAL ACCEPTANCE THRESHOLD RECOVERED`  

---

## 1. Executive Summary

This report documents **Phase 20 Step 10: Comparative Metric Analysis (Base vs V15 vs V16)** for the Automated Question Pair Generation (AQPG) project. 

Step 10 was executed strictly as an **ANALYSIS-ONLY study** comparing recorded outputs and metrics across three model generations:
1. **Base FLAN-T5-Small** (Un-tuned baseline model evaluated on Phase 20 prompt suite)
2. **V15 FLAN-T5-Small** (Phase 16 trained model evaluated in Phase 17)
3. **V16 FLAN-T5-Small** (Phase 20 Step 9 historical recorded evaluation outputs)

All analysis relies exclusively on surviving, verified project artifacts. **No model weights were loaded, no new inference was executed, no models were retrained, and Step 9 artifacts were strictly preserved.**

---

## 2. Step 10 Objective

The objective of Step 10 is to establish a rigorous, empirical baseline comparison measuring model evolution from the un-tuned base model through V15 to V16. Specifically, Step 10 quantifies:
- Genuine model quality improvements achieved in V16 (e.g., topic grounding, subject conditioning).
- Severe model regressions incurred in V16 (e.g., control sensitivity drop, question-type mismatch).
- Persistent architectural deficits requiring resolution in future phases (e.g., template collapse).
- Methodological limits where direct metric comparison is invalid.

---

## 3. Artifact Provenance & Verification

The primary input artifacts were audited, size-verified, and SHA-256 hashed prior to analysis:

| Input Artifact | Role / Version | Size (Bytes) | SHA-256 Hash |
| :--- | :--- | :--- | :--- |
| `phase20_evaluation_prompts.jsonl` | Benchmark Suite | 196,260 | `91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E` |
| `phase20_base_outputs.jsonl` | Base Model | 190,876 | `9BD203D50205FBF64B3C36A06A465F62930374C2CDDF3BB85F6C070DF26B91A7` |
| `phase17_generated_outputs.jsonl` | V15 Model Outputs | 422,501 | `BEFDEFF74D44F5D1F7AE0AC7F9579BC9E056F2B065102E66AFC390970977C1E7` |
| `phase17_quality_evaluation.json` | V15 Quality Metrics | 1,777 | `3BDF91570C6D0EDDE4A5EAF0723B089C5EBC3C11B172E35C12B1163309E5B751` |
| `phase17_control_sensitivity.json` | V15 Control Sensitivity | 7,064 | `ADAD24A23BA85EB704A756705CFF2CD50904EEF0C4B579E6A675DDA5640237AC` |
| `phase17_confusion_matrices.json` | V15 Confusion Matrices | 773 | `3C1860B07F46BB8A2F1C808A18E239B69EDA34A4414E4E265B19EBE6378B8ADC` |
| `phase18_v16_experiment_plan.json` | V15 Forensic Plan | 3,725 | `758AF0EDB3635898A195F18F9837AA63C0C7B869BBBF7AE7C514FEBA3EA2CBA7` |
| `phase20_v16_evaluation_summary.json` | V16 Step 9 Metadata | 853 | `9DB6C5FA89ABA4A54DF8622804137477715E73E994D0202B06FA153A4B91CD3A` |

---

## 4. Dataset Integrity & Benchmark Identity

- **Benchmark Suite:** [`phase20_evaluation_prompts.jsonl`](file:///c:/Users/Divya/OneDrive/Desktop/AQPG/phase20_evaluation_prompts.jsonl)
- **Prompt Count:** Exactly 520 prompts across STEM subjects (Mathematics, Physics, Chemistry, Biology, General Science).
- **Prompt Hash Verification:** `91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E` (**MATCHES EXPECTED SHA-256 EXACTLY**).
- **Population Alignment:** Base (520 outputs), V15 (520 outputs), V16 (520 historical Step 9 outputs).

---

## 5. Model Lineage & Identity Caveat

> [!IMPORTANT]
> **HISTORICAL MODEL IDENTITY NOTICE**:
> - **Historical V16 Step 9 Model SHA-256:** `E29B95E18DFE5CF6D8DB2D1F8781843C9DD4B8EE2CE81C9ED26E8DF56F443BC4`
> - This historical model weight file was **NOT RECOVERED** in the local workspace.
> - The V16 metrics analyzed in Step 10 represent **authoritative historical recorded outputs** from Step 9 execution.
> - Intermediate recovered checkpoints (`checkpoint-500`, `checkpoint-1000`) represent incomplete training states (step 1000 out of 7602) and were **NOT** loaded or substituted for historical Step 9 evaluation.

---

## 6. Comparative Metrics Table

| Metric | Base Model | V15 Model | V16 (Step 9 Recorded) | Absolute V16 - Base | Absolute V16 - V15 | Direction | Comparable? | Primary Provenance |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Generation Success Rate** | 100.0% | 100.0% | 100.0% | 0.0% | 0.0% | `HIGHER_BETTER` | **YES** | `phase20_base_outputs.jsonl`, `phase17_quality_evaluation.json` |
| **Question Structural Validity** | 100.0%* | 97.31% | 98.20% | -1.80%* | +0.89% | `HIGHER_BETTER` | **YES** (with Base caveat) | `phase17_quality_evaluation.json`, Step 9 report |
| **Subject Accuracy** | 0.0% | 60.77% | 67.60% | +67.60% | +6.83% | `HIGHER_BETTER` | **YES** | `phase17_quality_evaluation.json`, Step 9 report |
| **Topic Accuracy** | 0.0% | 43.27% | 72.60% | +72.60% | +29.33% | `HIGHER_BETTER` | **YES** | `phase17_quality_evaluation.json`, Step 9 report |
| **Class Alignment** | 0.0% | `NOT_VERIFIABLE` | 81.60% | +81.60% | `NOT_COMPARABLE` | `HIGHER_BETTER` | **NO** (vs V15) | `phase18_v16_experiment_plan.json`, Step 9 report |
| **Question-Type Accuracy** | 0.0% | 64.23% | 46.80% | +46.80% | -17.43% | `HIGHER_BETTER` | **YES** | `phase17_quality_evaluation.json`, Step 9 report |
| **Control Sensitivity Rate** | 0.0% | 30.00% | 0.00% | 0.00% | -30.00% | `HIGHER_BETTER` | **YES** | `phase17_control_sensitivity.json`, Step 9 report |
| **Template Concentration / Diversity** | Prompt Echo | 88.08% Repetition | 100.0% Top-10 Conc. | `NOT_COMPARABLE` | `NOT_COMPARABLE` | `LOWER_BETTER` | **NO** | `phase17_quality_evaluation.json`, Step 9 report |
| **Exact Memorization Rate** | 0.0% | 0.96% | 4.62% | +4.62% | `NOT_COMPARABLE` | `LOWER_BETTER` | **NO** (vs V15) | `phase17_quality_evaluation.json`, Step 9 report |
| **Numerical Validity Rate** | 0.0% | `NOT_VERIFIED` | 19.41% | +19.41% | `NOT_COMPARABLE` | `HIGHER_BETTER` | **NO** (vs V15) | `phase18_v16_experiment_plan.json`, Step 9 report |

*\*Note on Base Validity: Raw FLAN-T5-Small echoes the prompt string into a primitive question format ("What is the subject of..."), yielding 100% syntactically valid sentences, but 0% domain-conditioned questions.*

---

## 7. Subject-Wise Comparison

- **Mathematics:** Base echoes prompt text. V15 generated unverified equations. V16 achieved domain subject conditioning but suffered from low numerical question-type compliance.
- **Physics & Chemistry:** V15 demonstrated heuristic verification (`VERIFIED_HEURISTIC` in `phase17_quality_evaluation.json`). V16 achieved significant topic accuracy gains (+29.33% overall) due to Phase 19 prompt optimization (removal of `UNKNOWN` tokens).
- **Biology & General Science:** V15 and V16 both generated valid vocabulary stems, but V16 outputs overwhelmingly collapsed into MCQ template structures ("Which of the following is...").

---

## 8. Question-Type Comparison

- **MCQ (Multiple Choice Questions):** In V15, MCQ accuracy was 64.23% as the model defaulted to high-frequency MCQ templates. In V16, over-concentration on MCQ templates resulted in 100.0% top-10 concentration, causing non-MCQ prompts to fail format requirements.
- **Numerical:** V15 numerical calculation accuracy was marked `NOT_VERIFIED` (generated generic text stems). V16 achieved 19.41% numerical calculation validity, demonstrating initial calculation capability, but 80.59% of numerical prompts still failed exact mathematical verification.
- **Conceptual:** Suppressed in V16 due to template collapse into generic MCQ stems.

---

## 9. Control Sensitivity Analysis

- **V15 Control Sensitivity:** 30.00% (Classified as `CONTROL-BLIND` in `phase17_control_sensitivity.json`).
- **V16 Control Sensitivity:** 0.00% (Complete loss of parameter sensitivity).
- **Finding:** Changing difficulty (Easy to Hard), marks (1 to 5), or class grade levels in prompts produced identical generated outputs in V16, demonstrating total parameter insensitivity.

---

## 10. Diversity / Template Collapse Audit

- **V15:** Reported 88.08% template repetition rate with 62 unique generations across 520 prompts (`phase17_quality_evaluation.json`).
- **V16:** Reported 1.15 bits stem entropy and **100.0% Top-10 Concentration** in Step 9.
- **Comparability:** Marked `NOT_COMPARABLE` for direct delta calculation because V15 used repetition percentage across unique generations while V16 measured stem entropy (bits) and top-10 concentration (%). Both metrics empirically confirm severe template collapse across both models.

---

## 11. Numerical Validity Analysis

- **V15 Status:** `NOT_VERIFIED` (Model generated MCQ stems without performing calculations).
- **V16 Status:** 19.41% numerical validity.
- **Comparability:** Marked `NOT_COMPARABLE` against V15 due to missing V15 baseline verification. V16 shows initial numerical reasoning capability, but 80.59% failure rate remains a major deficit.

---

## 12. Memorization Audit

- **V15 Memorization:** 0.96% exact training match.
- **V16 Memorization:** 4.62% exact training match.
- **Comparability:** Marked `NOT_COMPARABLE` for direct delta because V15 (42,152 records) and V16 (44,534 rebalanced records) used different underlying target datasets for substring matching.

---

## 13. Summary of Improvements in V16

1. **Topic Accuracy:** Substantial improvement from 43.27% (V15) to **72.60% (V16)** [`+29.33 percentage points`].
2. **Subject Accuracy:** Improvement from 60.77% (V15) to **67.60% (V16)** [`+6.83 percentage points`].
3. **Question Validity:** Modest improvement from 97.31% (V15) to **98.20% (V16)** [`+0.89 percentage points`].
4. **Numerical Validity:** Reached **19.41%** in V16 (up from unverified/0% in prior models).

---

## 14. Summary of Regressions in V16

1. **Question-Type Accuracy:** Dropped from 64.23% (V15) to **46.80% (V16)** [`-17.43 percentage points`].
2. **Control Sensitivity:** Dropped from 30.00% (V15) to **0.00% (V16)** [`-30.00 percentage points`].
3. **Template Concentration:** Reached **100.0% Top-10 Concentration** in V16 (total template collapse).

---

## 15. Summary of Persistent Deficits

1. **Total Control Blindness:** 0.0% sensitivity to difficulty, marks, or target question type controls.
2. **Extreme MCQ Template Collapse:** 100.0% concentration in top-10 question stems; low stem entropy (1.15 bits).
3. **Low Numerical Solution Accuracy:** 19.41% calculation validity; 80.59% of numerical prompts generate invalid math reasoning.

---

## 16. Metrics Marked NOT_COMPARABLE

1. **Class Alignment vs V15:** Incomparable because 82.81% of V15 training records contained `class: UNKNOWN` tokens, rendering V15 class accuracy `NOT_VERIFIABLE`.
2. **Template Diversity:** Incomparable due to different metric formulas (V15 88.08% repetition rate vs V16 1.15 bits stem entropy / 100% top-10 concentration).
3. **Exact Memorization:** Incomparable due to different training target dataset sizes and schemas between V15 and V16.
4. **Numerical Validity vs V15:** Incomparable due to unverified V15 numerical calculations.

---

## 17. Historical V16 Weight Caveat

> [!WARNING]
> Historical Step 9 V16 model SHA-256 `E29B95E18DFE5CF6D8DB2D1F8781843C9DD4B8EE2CE81C9ED26E8DF56F443BC4` was not recovered locally. All V16 results analyzed in this report derive from authoritative historical recorded Step 9 outputs. Recovered intermediate checkpoints (`checkpoint-500`, `checkpoint-1000`) were NOT used as substitutes.

---

## 18. Final Step 10 Verdict

Because no historical numerical acceptance threshold was recovered in project documentation for Step 10 specifically:

```
STEP 10 — COMPARATIVE ANALYSIS COMPLETE; NO HISTORICAL ACCEPTANCE THRESHOLD RECOVERED
```
