# ====================================================================
# AQPG V16 — STEP 9 RECOVERY CELL
# BYPASS CELLS A–E / NO RETRAINING
# ====================================================================

import os
import sys
import json
import hashlib
import subprocess
import shutil
import time

print("=" * 70)
print("AQPG V16 — STEP 9 RECOVERY / NO-RETRAIN PATH")
print("=" * 70)

# --------------------------------------------------------------------
# 1. MOUNT GOOGLE DRIVE
# --------------------------------------------------------------------

if not os.path.exists("/content/drive/MyDrive"):
    try:
        from google.colab import drive
        drive.mount("/content/drive")
    except Exception:
        pass

MYDRIVE = "/content/drive/MyDrive"

if not os.path.exists(MYDRIVE):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Google Drive is not mounted correctly."
    )

print("[PASS] Google Drive mounted.")

# --------------------------------------------------------------------
# 2. LOCATE AQPG ROOT
# --------------------------------------------------------------------

AQPG_ROOT = os.path.join(MYDRIVE, "AQPG")

if not os.path.isdir(AQPG_ROOT):
    raise RuntimeError(
        f"[FATAL FAIL-CLOSED] AQPG root not found at:\n{AQPG_ROOT}\n\n"
        "Do NOT create a new AQPG folder. The existing project must be located."
    )

print(f"[PASS] AQPG root found: {AQPG_ROOT}")

# --------------------------------------------------------------------
# 3. DEFINE EXPECTED PATHS
# --------------------------------------------------------------------

MODEL_DIR = os.path.join(
    AQPG_ROOT,
    "backend",
    "ml",
    "models",
    "checkpoints",
    "flan_t5_v16_small"
)

EVAL_DIR = os.path.join(
    AQPG_ROOT,
    "backend",
    "ml",
    "evaluation"
)

EVAL_SCRIPT = os.path.join(
    EVAL_DIR,
    "evaluate_flan_t5_v16.py"
)

PROMPTS = os.path.join(
    EVAL_DIR,
    "phase20_evaluation_prompts.jsonl"
)

DOCS_DIR = os.path.join(AQPG_ROOT, "docs")

# --------------------------------------------------------------------
# 4. SHA-256 HELPER
# --------------------------------------------------------------------

def sha256_file(path):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest().upper()


def count_jsonl(path):
    count = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1

    return count

# --------------------------------------------------------------------
# 5. MODEL DIRECTORY CHECK
# --------------------------------------------------------------------

if not os.path.isdir(MODEL_DIR):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Existing V16 model directory was not found:\n"
        f"{MODEL_DIR}\n\n"
        "NO RETRAINING WILL BE STARTED."
    )

print(f"[PASS] V16 model directory found:")
print(MODEL_DIR)

# --------------------------------------------------------------------
# 6. REQUIRED MODEL ARTIFACTS
# --------------------------------------------------------------------

required_model_files = [
    "model.safetensors",
    "config.json",
    "generation_config.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json"
]

print("\n--- MODEL ARTIFACT AUDIT ---")

for filename in required_model_files:
    path = os.path.join(MODEL_DIR, filename)

    if not os.path.isfile(path):
        raise RuntimeError(
            f"[FATAL FAIL-CLOSED] Required model artifact missing:\n{path}"
        )

    size = os.path.getsize(path)

    if size <= 0:
        raise RuntimeError(
            f"[FATAL FAIL-CLOSED] Required model artifact is empty:\n{path}"
        )

    print(f"[PASS] {filename:30s} {size:,} bytes")

# --------------------------------------------------------------------
# 7. MODEL WEIGHT SIZE + SHA
# --------------------------------------------------------------------

MODEL_WEIGHTS = os.path.join(MODEL_DIR, "model.safetensors")

model_size = os.path.getsize(MODEL_WEIGHTS)
model_sha = sha256_file(MODEL_WEIGHTS)

print("\n--- MODEL WEIGHT INTEGRITY ---")

print(f"Model size : {model_size:,} bytes")
print(f"Model SHA  : {model_sha}")

if model_size <= 300_000_000:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] model.safetensors is below the "
        "300 MB integrity threshold."
    )

if len(model_sha) != 64:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Invalid SHA-256 length."
    )

print("[PASS] Model size threshold")
print("[PASS] SHA-256 format")

# --------------------------------------------------------------------
# 8. LOAD MODEL + TOKENIZER
# --------------------------------------------------------------------

print("\n--- INDEPENDENT MODEL RELOAD ---")

import torch
import transformers
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)

if not torch.cuda.is_available():
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] CUDA GPU unavailable. "
        "Step 9 will not run on CPU."
    )

print(f"[PASS] CUDA available")
print(f"[GPU] {torch.cuda.get_device_name(0)}")
print(f"[PyTorch] {torch.__version__}")
print(f"[Transformers] {transformers.__version__}")

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_DIR,
    local_files_only=True
)

print("[PASS] Tokenizer loaded")
print("[PASS] Model loaded")

# --------------------------------------------------------------------
# 9. PARAMETER / NaN / INF AUDIT
# --------------------------------------------------------------------

EXPECTED_PARAMS = 76_961_152

actual_params = 0
nan_tensors = 0
inf_tensors = 0

for p in model.parameters():
    actual_params += p.numel()

    if torch.isnan(p).any():
        nan_tensors += 1

    if torch.isinf(p).any():
        inf_tensors += 1

print("\n--- PARAMETER INTEGRITY ---")
print(f"Actual parameters : {actual_params:,}")
print(f"Expected          : {EXPECTED_PARAMS:,}")
print(f"NaN tensors       : {nan_tensors}")
print(f"Inf tensors       : {inf_tensors}")

if actual_params != EXPECTED_PARAMS:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Parameter count mismatch."
    )

if nan_tensors != 0 or inf_tensors != 0:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] NaN/Inf parameters detected."
    )

print("[PASS] Parameter count")
print("[PASS] NaN check")
print("[PASS] Inf check")

# --------------------------------------------------------------------
# 10. PROMPT INTEGRITY
# --------------------------------------------------------------------

EXPECTED_PROMPT_COUNT = 520

EXPECTED_PROMPT_SHA = (
    "91335C1EC938454BADFD551975018689"
    "A2B87489EA10BECDD05C134A1ED3082E"
)

if not os.path.isfile(PROMPTS):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] 520-prompt evaluation file not found:\n"
        f"{PROMPTS}"
    )

prompt_count = count_jsonl(PROMPTS)
prompt_sha = sha256_file(PROMPTS)

print("\n--- EVALUATION PROMPT INTEGRITY ---")
print(f"Prompt count : {prompt_count}")
print(f"Prompt SHA   : {prompt_sha}")

if prompt_count != EXPECTED_PROMPT_COUNT:
    raise RuntimeError(
        f"[FATAL FAIL-CLOSED] Expected 520 prompts, "
        f"found {prompt_count}."
    )

if prompt_sha != EXPECTED_PROMPT_SHA:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Evaluation prompt SHA mismatch."
    )

print("[PASS] Prompt count = 520")
print("[PASS] Prompt SHA-256")

# --------------------------------------------------------------------
# 11. EVALUATOR CHECK
# --------------------------------------------------------------------

if not os.path.isfile(EVAL_SCRIPT):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Step 9 evaluator not found:\n"
        f"{EVAL_SCRIPT}"
    )

if os.path.getsize(EVAL_SCRIPT) == 0:
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Step 9 evaluator is empty."
    )

print("\n[PASS] Step 9 evaluator exists")
print(EVAL_SCRIPT)

# --------------------------------------------------------------------
# 12. OUTPUT DIRECTORY
# --------------------------------------------------------------------

os.makedirs(DOCS_DIR, exist_ok=True)

if not os.access(DOCS_DIR, os.W_OK):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] AQPG docs directory is not writable."
    )

print("[PASS] Output directory writable")

# --------------------------------------------------------------------
# 13. SMOKE INFERENCE
# --------------------------------------------------------------------

print("\n--- SMOKE INFERENCE ---")

device = torch.device("cuda")
model = model.to(device)
model.eval()

smoke_prompt = (
    "generate question: subject: Physics | "
    "topic: Mechanics | class: Class 11 | "
    "difficulty: Medium | type: Conceptual"
)

inputs = tokenizer(
    smoke_prompt,
    return_tensors="pt"
).to(device)

with torch.no_grad():
    output = model.generate(
        **inputs,
        max_new_tokens=64,
        num_beams=4
    )

smoke_text = tokenizer.decode(
    output[0],
    skip_special_tokens=True
)

print(f"Generated output: {smoke_text}")

if not smoke_text.strip():
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Smoke inference produced empty output."
    )

print("[PASS] Smoke inference")

# --------------------------------------------------------------------
# 14. FINAL STEP 9 PRE-EVALUATION GATE
# --------------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 9 RECOVERY PRE-EVALUATION GATE")
print("=" * 70)

print("CUDA:                 PASS")
print(f"GPU:                  {torch.cuda.get_device_name(0)}")
print("MODEL DIRECTORY:      PASS")
print(f"MODEL SIZE:           {model_size:,} bytes")
print(f"MODEL SHA-256:        {model_sha}")
print("PARAMETERS:           76,961,152")
print("NaN:                  0")
print("Inf:                  0")
print("MODEL RELOAD:         PASS")
print("SMOKE INFERENCE:      PASS")
print("PROMPTS:              PASS")
print("PROMPT COUNT:         520")
print("PROMPT SHA-256:       PASS")
print("EVALUATOR:            PASS")
print("OUTPUT DIRECTORY:     PASS")

print("\n" + "=" * 70)
print("READY FOR STEP 9: TRUE")
print("=" * 70)

# --------------------------------------------------------------------
# 15. RUN STEP 9 EVALUATOR
# --------------------------------------------------------------------

print("\n")
print("=" * 70)
print("STARTING STEP 9 — 520 PROMPT EVALUATION")
print("=" * 70)

cmd = [
    sys.executable,
    EVAL_SCRIPT,
    "--checkpoint_dir",
    MODEL_DIR
]

print("\nCOMMAND:")
print(" ".join(cmd))
print()

result = subprocess.run(
    cmd,
    cwd=AQPG_ROOT
)

if result.returncode != 0:
    raise RuntimeError(
        f"[FATAL FAIL-CLOSED] Step 9 evaluator failed "
        f"with return code {result.returncode}."
    )

print("\n[PASS] Step 9 evaluator process completed.")

# --------------------------------------------------------------------
# 16. VERIFY STEP 9 ARTIFACTS
# --------------------------------------------------------------------

print("\n" + "=" * 70)
print("STEP 9 ARTIFACT VERIFICATION")
print("=" * 70)

required_artifacts = [
    "phase20_v16_generated_outputs.jsonl",
    "phase20_v16_evaluation_summary.json",
    "phase20_quality_evaluation.json",
    "phase20_failure_analysis.json",
    "phase20_subject_confusion_matrix.json",
    "phase20_control_sensitivity.json",
    "phase20_template_diversity.json",
    "phase20_numerical_evaluation.json",
    "phase20_memorization.json",
    os.path.join("docs", "phase20_step9_evaluation_report.md")
]

artifact_manifest = {}
missing = []

outputs_count = 0
evaluation_verdict = "UNKNOWN"

for artifact in required_artifacts:

    artifact_path = os.path.join(AQPG_ROOT, artifact)

    if not os.path.isfile(artifact_path):
        missing.append(artifact)
        continue

    size = os.path.getsize(artifact_path)

    if size <= 0:
        missing.append(artifact)
        continue

    sha = sha256_file(artifact_path)

    artifact_manifest[artifact] = {
        "size_bytes": size,
        "sha256": sha
    }

    print(
        f"[PASS] {artifact} | "
        f"{size:,} bytes | SHA {sha}"
    )

    if artifact == "phase20_v16_generated_outputs.jsonl":
        outputs_count = count_jsonl(artifact_path)

    if artifact == "phase20_v16_evaluation_summary.json":
        try:
            with open(
                artifact_path,
                "r",
                encoding="utf-8"
            ) as f:
                summary = json.load(f)

            evaluation_verdict = summary.get(
                "verdict",
                "UNKNOWN"
            )

        except Exception:
            evaluation_verdict = "INVALID_JSON"

print("\nGenerated outputs:", outputs_count)
print("Evaluation verdict:", evaluation_verdict)

# --------------------------------------------------------------------
# 17. CREATE STEP 9 ARTIFACT MANIFEST
# --------------------------------------------------------------------

step9_manifest = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "model_sha256": model_sha,
    "prompt_sha256": prompt_sha,
    "prompt_count": prompt_count,
    "outputs_count": outputs_count,
    "evaluation_verdict": evaluation_verdict,
    "artifacts": artifact_manifest
}

manifest_path = os.path.join(
    AQPG_ROOT,
    "phase20_v16_step9_artifact_manifest.json"
)

with open(
    manifest_path,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        step9_manifest,
        f,
        indent=2
    )

print(
    f"\n[PASS] Artifact manifest created:\n"
    f"{manifest_path}"
)

# --------------------------------------------------------------------
# 18. IMMUTABLE TIMESTAMPED ARCHIVE
# --------------------------------------------------------------------

timestamp = time.strftime("%Y%m%d_%H%M%S")

archive_dir = os.path.join(
    AQPG_ROOT,
    f"results_backup_v16_{timestamp}"
)

if os.path.exists(archive_dir):
    raise RuntimeError(
        "[FATAL FAIL-CLOSED] Timestamped archive already exists."
    )

os.makedirs(archive_dir)

archive_items = required_artifacts + [
    "phase20_v16_step9_artifact_manifest.json"
]

archive_failures = []

for artifact in archive_items:

    src = os.path.join(AQPG_ROOT, artifact)

    if not os.path.isfile(src):
        archive_failures.append(
            f"MISSING_SOURCE:{artifact}"
        )
        continue

    dst = os.path.join(
        archive_dir,
        os.path.basename(artifact)
    )

    shutil.copy2(src, dst)

    if (
        not os.path.isfile(dst)
        or os.path.getsize(dst) != os.path.getsize(src)
    ):
        archive_failures.append(
            f"ARCHIVE_COPY_FAIL:{artifact}"
        )

print(
    f"\nArchive created:\n{archive_dir}"
)

# --------------------------------------------------------------------
# 19. FINAL FAIL-CLOSED STEP 9 GATE
# --------------------------------------------------------------------

valid_verdict = evaluation_verdict in [
    "PASS",
    "PASS WITH WARNING"
]

if (
    missing
    or archive_failures
    or outputs_count != 520
    or not valid_verdict
):
    print("\n[FATAL FAIL-CLOSED]")
    print("Missing artifacts:", missing)
    print("Archive failures:", archive_failures)
    print("Output count:", outputs_count)
    print("Verdict:", evaluation_verdict)

    raise RuntimeError(
        "[FATAL FAIL-CLOSED] STEP 9 FINAL GATE FAILED."
    )

print("\n")
print("=" * 70)
print("STEP 9 SUCCESS")
print("=" * 70)
print("520 outputs verified")
print(f"Evaluation verdict: {evaluation_verdict}")
print("All required artifacts verified")
print("Artifact manifest created")
print("Immutable archive created")
print("NO RETRAINING WAS PERFORMED")
print("=" * 70)
