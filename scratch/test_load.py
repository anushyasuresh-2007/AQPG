import sys
import os
sys.path.insert(0, 'backend')

from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter

adapter = V17_2InferenceAdapter()
print("Model path resolved:", adapter.model_path)

try:
    loaded = adapter.load_model()
    print("Model load status:", loaded, "Is loaded:", adapter._is_loaded)
    res = adapter.generate_question(subject="Science", topic="Forces", difficulty="Medium", marks=3)
    print("Generated question:", res.question_text)
except Exception as e:
    import traceback
    print("ERROR LOAD FAILED:")
    traceback.print_exc()
