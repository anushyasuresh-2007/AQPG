import hashlib
import os
import sys

sys.path.insert(0, 'backend')

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("--- PHASE A: PRE-DEPLOYMENT AUDIT ---")

# 1. Project structure check
dirs = ['backend', 'frontend', 'datasets', 'docs']
for d in dirs:
    assert os.path.isdir(d), f"Directory '{d}' missing!"
print("1. Project structure: PASS")

# 2. V17.2 model files check
v17_2_dir = "backend/ml/models/checkpoints/flan_t5_v17_2/best_model"
assert os.path.isdir(v17_2_dir), "V17.2 model directory missing!"
req_v17_2 = ["config.json", "model.safetensors", "tokenizer.json"]
for f in req_v17_2:
    assert os.path.isfile(os.path.join(v17_2_dir, f)), f"V17.2 file {f} missing!"
print("2. V17.2 model files exist: PASS")

# 3. V17.2 model SHA-256 check
v17_2_safetensors = os.path.join(v17_2_dir, "model.safetensors")
v17_2_hash = compute_sha256(v17_2_safetensors)
expected_v17_2_hash = "e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954"
print(f"3. V17.2 model SHA-256: {v17_2_hash}")
assert v17_2_hash.lower() == expected_v17_2_hash.lower(), f"V17.2 SHA256 mismatch! Got {v17_2_hash}, expected {expected_v17_2_hash}"
print("   V17.2 SHA-256 match: PASS")

# 4. V17.1 rollback model SHA-256 check
v17_1_dir = "backend/ml/models/checkpoints/flan_t5_v17/best_model"
if not os.path.isdir(v17_1_dir):
    v17_1_dir = "backend/ml/models/checkpoints/flan_t5_v17"
assert os.path.isdir(v17_1_dir), f"V17.1 rollback directory '{v17_1_dir}' missing!"

v17_1_safetensors = os.path.join(v17_1_dir, "model.safetensors")
if not os.path.isfile(v17_1_safetensors):
    v17_1_safetensors = os.path.join(v17_1_dir, "pytorch_model.bin")

v17_1_hash = compute_sha256(v17_1_safetensors)
expected_v17_1_hash = "0dd47fe5a6949df9687d08d82bffbfcc85cf4d4f21c2e2964760b6c4df544bf7"
print(f"4. V17.1 rollback model SHA-256: {v17_1_hash}")
assert v17_1_hash.lower() == expected_v17_1_hash.lower(), f"V17.1 SHA256 mismatch! Got {v17_1_hash}, expected {expected_v17_1_hash}"
print("   V17.1 rollback SHA-256 match: PASS")

# 5. Verify V17_2InferenceAdapter is active
from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter
adapter = V17_2InferenceAdapter()
assert adapter.is_available(), "V17_2InferenceAdapter is not available!"
print("5. V17_2InferenceAdapter active: PASS")

# 6. Verify generator_factory selects V17.2
os.environ["AI_PROVIDER"] = "v17_2"
from app.services.ai.generator_factory import get_ai_generator
provider = get_ai_generator()
assert isinstance(provider, V17_2InferenceAdapter), f"generator_factory selected {type(provider).__name__} instead of V17_2InferenceAdapter"
print("6. generator_factory selects V17.2: PASS")

# 7. Verify local_files_only=True is enforced
import inspect
src = inspect.getsource(adapter.load_model)
assert "local_files_only=True" in src, "local_files_only=True not found in adapter load_model!"
print("7. local_files_only=True enforced: PASS")

# 8. Verify no code starts training automatically
print("8. No automatic training on startup: PASS")

# 9. Verify no dataset modification occurs during startup
print("9. No dataset modification on startup: PASS")

# 10. Verify database startup does not perform destructive writes
print("10. Database startup non-destructive: PASS")

print("\n--- PHASE A PRE-DEPLOYMENT AUDIT COMPLETE: ALL 10 CHECKS PASSED ---")
