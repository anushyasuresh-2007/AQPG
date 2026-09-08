"""
sync_step9_colab.py
Phase 20 Step 9: Colab File Sync & Pre-Evaluation Verification Script.
Ensures evaluate_flan_t5_v16.py and phase20_evaluation_prompts.jsonl are physically present
and verified at /content/drive/MyDrive/AQPG/backend/ml/evaluation/.
"""

import os
import sys
import shutil
import hashlib
import json

EXPECTED_PROMPT_HASH = "91335C1EC938454BADFD551975018689A2B87489EA10BECDD05C134A1ED3082E"
EXPECTED_PROMPT_COUNT = 520

def compute_sha256(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest().upper()

def count_records(filepath):
    count = 0
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count

def sync_and_verify_colab_files():
    print("=" * 80)
    print("AQPG PHASE 20 STEP 9: COLAB FILE SYNC & VERIFICATION")
    print("=" * 80)

    # Detect Google Drive / Project Root
    drive_eval_dir = "/content/drive/MyDrive/AQPG/backend/ml/evaluation"
    local_eval_dir = os.path.abspath(os.path.dirname(__file__))
    base_dir = os.path.abspath(os.path.join(local_eval_dir, "..", "..", ".."))

    # Determine target evaluation directory
    if os.path.exists("/content/drive/MyDrive/AQPG"):
        target_eval_dir = drive_eval_dir
    else:
        target_eval_dir = os.path.join(base_dir, "backend", "ml", "evaluation")

    os.makedirs(target_eval_dir, exist_ok=True)
    print(f"Target Evaluation Directory: {target_eval_dir}")

    target_script = os.path.join(target_eval_dir, "evaluate_flan_t5_v16.py")
    target_prompts = os.path.join(target_eval_dir, "phase20_evaluation_prompts.jsonl")
    
    # Check Model Path
    if os.path.exists("/content/drive/MyDrive/AQPG"):
        target_model_dir = "/content/drive/MyDrive/AQPG/backend/ml/models/checkpoints/flan_t5_v16_small"
    else:
        target_model_dir = os.path.join(base_dir, "backend", "ml", "models", "checkpoints", "flan_t5_v16_small")

    target_model_file = os.path.join(target_model_dir, "model.safetensors")

    # 1. Sync Script if missing in target_eval_dir
    if not os.path.exists(target_script):
        # Look for script in local working directory
        src_script = os.path.join(base_dir, "backend", "ml", "evaluation", "evaluate_flan_t5_v16.py")
        if os.path.exists(src_script) and src_script != target_script:
            shutil.copy(src_script, target_script)
            print(f"  [SYNC] Copied evaluate_flan_t5_v16.py to {target_eval_dir}")
        elif os.path.exists("evaluate_flan_t5_v16.py"):
            shutil.copy("evaluate_flan_t5_v16.py", target_script)
            print(f"  [SYNC] Copied evaluate_flan_t5_v16.py from current dir to {target_eval_dir}")

    # 2. Sync Prompts File if missing in target_eval_dir
    if not os.path.exists(target_prompts):
        src_prompts1 = os.path.join(base_dir, "phase20_evaluation_prompts.jsonl")
        src_prompts2 = os.path.join(base_dir, "backend", "ml", "evaluation", "phase20_evaluation_prompts.jsonl")
        
        if os.path.exists(src_prompts1):
            shutil.copy(src_prompts1, target_prompts)
            print(f"  [SYNC] Copied phase20_evaluation_prompts.jsonl to {target_eval_dir}")
        elif os.path.exists(src_prompts2) and src_prompts2 != target_prompts:
            shutil.copy(src_prompts2, target_prompts)
            print(f"  [SYNC] Copied phase20_evaluation_prompts.jsonl to {target_eval_dir}")

    # 3. Final Verification Audit
    script_exists = os.path.exists(target_script) and os.path.getsize(target_script) > 0
    prompts_exists = os.path.exists(target_prompts) and os.path.getsize(target_prompts) > 0
    model_exists = os.path.exists(target_model_file) or (os.path.exists(target_model_dir) and len(os.listdir(target_model_dir)) > 0)

    prompt_sha = compute_sha256(target_prompts) if prompts_exists else "N/A"
    prompt_cnt = count_records(target_prompts) if prompts_exists else 0

    print("\n" + "-" * 60)
    print("COLAB STEP 9 PRE-EVALUATION VERIFICATION REPORT:")
    print("-" * 60)
    print(f"Script:  {script_exists}")
    print(f"Prompts: {prompts_exists}")
    print(f"Model:   {model_exists}")
    print()
    print("Prompt SHA-256:")
    print(f"{prompt_sha}")
    print("-" * 60)

    if script_exists and prompts_exists and prompt_sha == EXPECTED_PROMPT_HASH and prompt_cnt == 520:
        print(f"Status:  PASSED (Evaluator ready for Colab Step 9)")
        return True
    else:
        print(f"Status:  FAILED (Missing files or hash mismatch)")
        if not prompts_exists or prompt_sha != EXPECTED_PROMPT_HASH:
            print(f"  Expected Prompt Count: {EXPECTED_PROMPT_COUNT}, Actual: {prompt_cnt}")
            print(f"  Expected SHA-256:     {EXPECTED_PROMPT_HASH}")
            print(f"  Actual SHA-256:       {prompt_sha}")
        return False

if __name__ == "__main__":
    sync_and_verify_colab_files()
