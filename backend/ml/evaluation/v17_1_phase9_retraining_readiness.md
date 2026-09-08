# AQPG V17.2 Safe Retraining Readiness & Recovery Plan (Phase 9 Report)

## 1. Executive Summary
Phase 9 establishes the scientifically validated **V17.2 Safe Retraining Readiness Plan** following the Phase 8 root-cause diagnosis of V17.1 (which confirmed **Model Checkpoint Weight Collapse** at token ID 22777 `"reheat"`).

**Strict Safety Mode** was maintained throughout Phase 9:
- **Zero training executed**
- **V17.1 `best_model` remains 100% byte-for-byte unchanged** (`model.safetensors` SHA-256: `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`)
- **No dataset, application, or database files modified**

---

## 2. Phase 8 Findings Re-verification
- **EVIDENCE**: Phase 8 report (`v17_1_phase8_root_cause_report.json`) confirmed with HIGH confidence that V17.1 suffered a complete logit attractor collapse during fine-tuning.
- **EVIDENCE**: Tokenizer, model architecture, and inference code were verified 100% functional.
- **EVIDENCE**: Repetition penalties and beam search tuning failed to recover valid questions (outputting random dictionary words like `"debit"`, `"Bitcoin"`), confirming weight-level representation collapse.

---

## 3. V17.1 Preservation Verification
- **FACT**: Checkpoint path `backend/ml/models/checkpoints/flan_t5_v17/best_model/`
- **FACT**: `model.safetensors` size: `307,867,048` bytes
- **FACT**: `model.safetensors` SHA-256: `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7` (Verified match).

---

## 4. Dataset Audit
- **FACT**: Dataset audited across 40,000 train and 10,000 validation records.
- **EVIDENCE**: 100.00% unique inputs and 100.00% unique targets.
- **EVIDENCE**: Zero empty targets, zero targets < 15 characters.
- **EVIDENCE**: Maximum input length = 63 tokens; maximum target length = 182 tokens. Truncation rate at max_length=256 is 0.00%.
- **EVIDENCE**: Token ID 22777 (`"reheat"`) is NOT present as an abnormal pattern in dataset targets (only 1 natural English usage in validation set).

---

## 5. Prompt / Target Audit
- **FACT**: Comparison of training prompt vs inference prompt:
  - **Training Input**: `generate question | subject: {subj} | topic: {topic} | class: {class} | difficulty: {difficulty} | marks: {marks} | type: {type} | bloom: {bloom} | unit: {unit} | board: {board}`
  - **Inference Input**: `generate question | subject: {subj} | topic: {top} | class: Class 10 | difficulty: {diff} | marks: {m} | type: {q_type} | bloom: {b_lvl}`
- **RECOMMENDATION**: Standardize canonical V17.2 Prompt Format to eliminate `unit` and `board` mismatches:
  `generate question | subject: {subj} | topic: {topic} | class: {class} | difficulty: {difficulty} | marks: {marks} | type: {type} | bloom: {bloom}`

---

## 6. Training Configuration Audit
- **FACT**: V17.1 training config used `learning_rate=5e-5`, `label_smoothing=0.0`, `effective_batch_size=32`.
- **EVIDENCE**: The checkpoint saved in `best_model` resulted from a 100-step smoke script run or premature step saving before convergence.
- **INFERENCE**: Low learning rate without label smoothing under early step termination allowed output logits to settle into a degenerate attractor state.

---

## 7. Label / Loss Pipeline Audit
- **FACT**: Target text converted to input_ids with `pad_token_id` replaced by `-100` for cross-entropy loss computation.
- **EVIDENCE**: Sequence-to-sequence data collator handles label padding correctly. Adding `label_smoothing_factor=0.05` in V17.2 will prevent extreme logit probability spikes.

---

## 8. Model Initialization Audit
- **FACT**: Pretrained base `google/flan-t5-small` loaded with 8 encoder/decoder layers (`d_model=512`, `d_ff=1024`, `num_heads=6`, `vocab_size=32128`).
- **RECOMMENDATION**: Re-initialize V17.2 clean training from base pretrained weights rather than resuming from collapsed V17.1 weights.

---

## 9. Checkpoint Selection Audit
- **FACT**: Best model selected by `metric_for_best_model="eval_loss"`.
- **RECOMMENDATION**: Save top 5 intermediate checkpoints (`save_total_limit=5`) every 250 steps and perform automated quality evaluation on each checkpoint before finalizing `best_model`.

---

## 10. Proposed V17.2 Configuration Matrix
| Parameter | V17.1 Value | Proposed V17.2 Value | Rationale |
|---|---|---|---|
| **Base Model** | `google/flan-t5-small` | `google/flan-t5-small` | Standardized FLAN-T5 architecture |
| **Learning Rate** | `5e-5` | `3e-4` | Standard FLAN-T5 fine-tuning rate for faster convergence |
| **Label Smoothing** | `0.0` | `0.05` | Prevents logit overconfidence and attractor token collapse |
| **Optimizer** | `AdamW` | `AdamW (adamw_torch)` | Standard stable optimizer |
| **Epochs** | 3 (Smoke 100 steps) | 4 full epochs (5,000 steps) | Full convergence across 40k dataset |
| **Effective Batch Size**| 32 | 32 (16 per device x 2 accum) | Proven gradient stability |
| **Warmup Steps** | 187 | 250 steps (5%) | Smooth initial weight updates |
| **Precision** | FP32 / FP16 | FP16 | Efficient CUDA GPU acceleration |
| **Prompt Format** | 10 tags | 8 canonical tags | Parity between training and inference |
| **Checkpoint Strategy**| Every 50 steps | Every 250 steps (limit 5) | Comprehensive checkpoint evaluation |

---

## 11. Recovery Directory Design (Strict Isolation)
```
backend/ml/models/checkpoints/
├── flan_t5_v17/            ← READ-ONLY PRESERVED (V17.1)
│   └── best_model/
└── flan_t5_v17_2/          ← NEW ISOLATED DIRECTORY (V17.2)
    ├── checkpoint-250/
    ├── checkpoint-500/
    └── best_model/
```

---

## 12. Success Gates for Future Retraining
- **GATE 1**: Model loads successfully without error.
- **GATE 2**: Tokenizer round-trip passes 100%.
- **GATE 3**: Unique token ratio in generation > 0.50 (no single-token dominance).
- **GATE 4**: Zero occurrences of token 22777 `"reheat"` repetition loops.
- **GATE 5**: >= 90% of generated outputs are valid question-like structures.
- **GATE 6**: Topic relevance score >= 80%.
- **GATE 7**: Bloom metadata correctly preserved in outputs.
- **GATE 8**: 30-prompt evaluation quality score >= 75/100 (vs V17.1 baseline of 3.67/100).

---

## 13. Abort Conditions for Future Retraining
1. NaN or Inf detected in training or evaluation loss.
2. Gradient norm exceeds 10.0 or becomes NaN.
3. Validation loss diverges for > 3 consecutive evaluation steps.
4. Top single token accounts for > 50% of generated tokens during step evaluation.
5. Repetition failure rate exceeds 10%.

---

## 14. Go / No-Go Decision
**READY**

---

## 15. Final Recommendation
V17.1 forensic investigation and V17.2 recovery design are complete. The project is fully prepared for future V17.2 retraining on GPU hardware when authorized.
