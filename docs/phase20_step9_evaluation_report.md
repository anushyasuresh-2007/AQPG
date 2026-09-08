# AQPG Phase 20 Step 9 — Evaluation Report

**Timestamp:** 2026-08-21 10:56:44  
**Verdict:** `FAIL (LOCAL_CHECKPOINT_MISSING)`  

## Safeguard Pre-Check Results
- **Evaluation Prompts Path:** [`phase20_evaluation_prompts.jsonl`](file:///C:\Users\Divya\OneDrive\Desktop\AQPG\phase20_evaluation_prompts.jsonl)
- **Prompts SHA-256:** `91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E`
- **Prompts Count:** `520` (`PASS - Exactly 520`)
- **Target Model Directory:** `C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\checkpoints\flan_t5_v16_small`
- **Checkpoint Status:** Missing physical checkpoint files `['model.safetensors', 'config.json', 'generation_config.json', 'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json']` locally.

> [!WARNING]
> Training ran on Google Colab GPU (`/content/drive/MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small/`).
> Download/sync the model files to [`backend/ml/models/checkpoints/flan_t5_v16_small/`](file:///C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\checkpoints\flan_t5_v16_small) to complete local execution.
