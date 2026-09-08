# AQPG V17.1 — Phase 8 Root Cause Forensic Summary

## 1. Executive Summary
Phase 8 performed a comprehensive, read-only diagnostic investigation into the severe V17.1 model output collapse observed in Phase 5 and Phase 7 (0/30 question-like outputs, 100% repetition failures consisting of repetitive `"reheat..."` strings).

The forensic diagnosis confirms that the failure originates from **Model Checkpoint Weight Collapse** (LM Head Logit Attractor at subword token ID 22777 `"reheat"`), caused by premature checkpoint saving or optimization instability during fine-tuning. Decoding parameter adjustments (beam search, sampling, repetition penalties) failed to recover question generation, producing random ungrounded vocabulary tokens instead.

---

## 2. Checkpoint Integrity
- **Path**: `backend/ml/models/checkpoints/flan_t5_v17/best_model/`
- **`model.safetensors` size**: `307,867,048` bytes
- **`model.safetensors` SHA-256**: `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7`
- **Baseline Verification**: **PASS** (100% byte-for-byte match with verified restoration baseline).
- **Files Present**: `config.json`, `generation_config.json`, `model.safetensors`, `tokenizer.json`, `tokenizer_config.json`, `training_args.bin`.

---

## 3. Tokenizer Audit
- **Tokenizer Type**: `T5Tokenizer` (Fast SentencePiece backend)
- **Vocabulary Size**: 32,100 (Model embedding layer 32,128)
- **Special Tokens**: `pad_token` = `<pad>` (0), `eos_token` = `</s>` (1), `unk_token` = `<unk>` (2), `decoder_start_token_id` = 0.
- **Roundtrip Consistency**:
  - English sentence encoding & decoding: **PASS** (100% loss-free roundtrip).
  - V17.1 prompt encoding & decoding: **PASS** (100% loss-free roundtrip).
- **Conclusion**: Tokenizer compatibility is **NORMAL / PASS**.

---

## 4. Generation Configuration
- **`generation_config.json`**: `decoder_start_token_id` = 0, `eos_token_id` = [1], `pad_token_id` = 0.
- **Default Parameters**: Greedy decoding (`do_sample` = False, `num_beams` = 1, `repetition_penalty` = 1.0).
- **Conclusion**: Generation configuration is **NORMAL**.

---

## 5. Inference Pipeline Audit
- **Adapter File**: `backend/app/services/ai/v17_1_inference_adapter.py`
- **Code Trace**: Correctly instantiates `T5ForConditionalGeneration`, loads local tokenizer/weights (`local_files_only=True`), applies `eval()` mode, formats input prompt tags, tokenizes with `max_length=256`, calls `generate()`, and decodes cleanly with `skip_special_tokens=True`.
- **Conclusion**: Inference pipeline code is **PASS / VALID**.

---

## 6. Raw Token Diagnostic
Fixed Diagnostic Prompt:
`generate question | subject: Physics | topic: Newton's Laws of Motion | class: Class 10 | difficulty: medium | marks: 3 | type: Conceptual | bloom: Understand`

- **Input Token Count**: 39 tokens
- **Output Token Count**: 256 tokens
- **Output String**: `'reheatreheatreheatreheatreheatreheat...'` (repeated 255 times)
- **Unique Token Count**: 2
- **Most Frequent Token**: ID 22777 (`'reheat'`), count: 255
- **Repetition Ratio**: 0.9922 (99.22%)

---

## 7. Controlled Decoding Results
| Config | Settings | Output Snippet | Question-Like | Malformed |
|---|---|---|---|---|
| **A** | Greedy / Default | `reheatreheatreheat...` | NO | YES |
| **B** | `num_beams=1, rep_penalty=1.0` | `reheatreheatreheat...` | NO | YES |
| **C** | `num_beams=4, rep_penalty=1.1, no_repeat_ngram=3` | `debit debit debit Bitcoin Bitcoin...` | NO | YES |
| **D** | `do_sample=True, temp=0.7, top_p=0.9, rep_penalty=1.1` | `reheatreheatreheatsynchronousreheat...` | NO | YES |
| **E** | `num_beams=4, rep_penalty=1.2, max_new_tokens=128` | `debit debit debit Bitcoin... desktop...` | NO | YES |

- **Decoding Recovery Result**: **NO** (Decoding adjustments cannot recover question generation; when forced to avoid `reheat`, the model outputs ungrounded dictionary words like `debit`, `Bitcoin`, `blackjack`, `restroom`).

---

## 8. Training Configuration
- **Base Model**: `google/flan-t5-small` (Custom 8-layer architecture, `d_model` = 512, `d_ff` = 1024, `num_heads` = 6)
- **Dataset Size**: 40,000 train / 10,000 validation records
- **Hyperparameters**: `learning_rate` = 5e-05, `epochs` = 3, `effective_batch_size` = 32, `lr_scheduler` = cosine, `warmup_steps` = 187.
- **Anomalies**: `training_args.bin` shows checkpoint saved from a 100-step smoke run or premature save step where model weights were under-trained / trapped in a collapsed attractor logit state.

---

## 9. Dataset Forensics
- **Target Analysis**: 40,000 train targets inspected; 100% unique targets.
- **`"reheat"` search in dataset**: Found 1 natural occurrence in `eduqg_val.json` and 0 abnormal occurrences in training targets.
- **Conclusion**: `"reheat"` is NOT present as a target pattern in the training dataset; the collapse is purely an internal model weight logit failure.

---

## 10. Checkpoint Consistency
- `best_model` directory files internally consistent. `model.safetensors` layer keys (`encoder.block.0`..`7`, `decoder.block.0`..`7`) match `config.json` (`num_layers=8`, `num_decoder_layers=8`).

---

## 11. Differential Diagnosis Table
| Rank | Suspected Cause | Evidence | Confidence | Status |
|---|---|---|---|---|
| **1** | Model Checkpoint Weight Collapse | Model generates token 22777 continuously; anti-repetition decoding yields ungrounded random words. | HIGH | **CONFIRMED** |
| **2** | Training Strategy / Step Count Anomaly | `training_args.bin` reflects smoke script artifact / premature step save. | MEDIUM | **STRONGLY SUSPECTED** |
| **3** | Prompt Format Minor Variation | Inference prompt omits `unit` & `board` tags. | LOW | UNLIKELY |
| **4** | Tokenizer / Decoding Misconfiguration | Tokenizer roundtrip 100% verified; decoding tweaks produce gibberish. | HIGH | **RULED OUT** |
| **5** | Checkpoint File Corruption | SHA-256 byte-for-byte match verified. | HIGH | **RULED OUT** |

---

## 12. Most Likely Root Cause
**Model Checkpoint Weight Collapse (LM Head Logit Attractor at Token ID 22777 `"reheat"`)** caused by fine-tuning optimization failure / premature checkpoint save.

---

## 13. Evidence
1. **Fact**: Checkpoint `model.safetensors` SHA-256 matches verified restoration hash `0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7` (no file corruption).
2. **Fact**: Tokenizer encodes and decodes prompts with zero error.
3. **Fact**: Raw model generation outputs token ID 22777 (`"reheat"`) 255 times across 256 output tokens.
4. **Fact**: Penalizing repetition (repetition_penalty = 1.1 / 1.2, no_repeat_ngram_size = 3) causes the model to output random words (`"debit"`, `"Bitcoin"`, `"blackjack"`, `"restroom"`), demonstrating that the decoder hidden representations lack natural language semantics.
5. **Fact**: `"reheat"` is not present in training target dataset records.

---

## 14. Recommendation
**Retraining is required.** A full GPU training execution across all epochs is necessary with proper evaluation loss monitoring, regularized label smoothing, and verified checkpoint saving.
