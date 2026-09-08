import sys
import os

sys.path.insert(0, 'backend')

# Check 1: Import torch
import torch
print(f"[CHECK 1] import torch: PASS (version={torch.__version__})")

# Check 2: Import transformers
import transformers
print(f"[CHECK 2] import transformers: PASS (version={transformers.__version__})")

# Check 3: Import FastAPI
import fastapi
print(f"[CHECK 3] import FastAPI: PASS (version={fastapi.__version__})")

# Check 4: Import V17_2InferenceAdapter
from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter
print("[CHECK 4] import V17_2InferenceAdapter: PASS")

# Check 5: Verify best_model directory exists
adapter = V17_2InferenceAdapter()
model_path = adapter.model_path
assert model_path and os.path.isdir(model_path), "V17.2 best_model directory missing!"
print(f"[CHECK 5] V17.2 best_model directory exists: PASS ({model_path})")

# Check 6: Verify model.safetensors exists
safetensors_path = os.path.join(model_path, "model.safetensors")
assert os.path.isfile(safetensors_path), "model.safetensors missing!"
print(f"[CHECK 6] model.safetensors exists: PASS (size={os.path.getsize(safetensors_path)} bytes)")

# Check 7: Verify V17.2 model loaded using local files only
success = adapter.load_model()
assert success and adapter._is_loaded, "Failed to load local V17.2 model!"
print("[CHECK 7] V17.2 model loaded using local files only: PASS")

res = adapter.generate_question(subject="Science", topic="Chemical Reactions", difficulty="Medium", marks=3)
print(f"   Sample Generated Question: '{res.question_text}'")

# Check 8: Verify generator_factory selects V17.2
os.environ["AI_PROVIDER"] = "v17_2"
from app.services.ai.generator_factory import get_ai_generator
provider = get_ai_generator()
assert isinstance(provider, V17_2InferenceAdapter), f"Selected {type(provider)} instead of V17_2InferenceAdapter"
print(f"[CHECK 8] generator_factory selects V17.2: PASS ({type(provider).__name__})")

print("\nALL 8 RUNTIME VERIFICATION CHECKS PASSED SUCCESSFULLY!")
