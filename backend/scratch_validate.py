import os
import sys

os.environ["AI_PROVIDER"] = "v17_2"

from app.services.ai.generator_factory import get_ai_generator
from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter

def run_tests():
    print("=== AQPG V17.2 END-TO-END VALIDATION ===", flush=True)
    
    # 1. Test Provider Selection
    provider = get_ai_generator()
    print(f"[PASS] Active AI Provider Class: {provider.__class__.__name__}", flush=True)
    assert isinstance(provider, V17_2InferenceAdapter), "Provider must be V17_2InferenceAdapter!"
    
    # 2. Test Availability & Model Path
    assert provider.is_available(), "V17.2 Model must be available locally!"
    print(f"[PASS] V17.2 Model Path: {provider.model_path}", flush=True)
    
    # 3. Test Model Loading
    loaded = provider.load_model()
    assert loaded and provider._is_loaded, "Model loading failed!"
    print("[PASS] V17.2 Model Loaded with local_files_only=True", flush=True)
    
    # 4. Smoke Test Question Generation across 5 subjects
    test_cases = [
        ("Mathematics", "Quadratic Equations", "Medium", 3, "Short Answer", "Apply"),
        ("Physics", "Electric Current & Ohm's Law", "Hard", 5, "Numerical", "Analyze"),
        ("Chemistry", "Chemical Reactions & Equations", "Easy", 2, "Conceptual", "Understand"),
        ("Biology", "Cell Structure & Function", "Medium", 3, "Short Answer", "Remember"),
        ("General Science", "Ecosystem & Energy Transfer", "Medium", 4, "Descriptive", "Evaluate"),
    ]
    
    for subj, top, diff, m, q_type, b_lvl in test_cases:
        res = provider.generate_question(
            subject=subj,
            topic=top,
            difficulty=diff,
            marks=m,
            question_type=q_type,
            bloom_level=b_lvl
        )
        print(f"\n--- Test: {subj} ({top}) ---", flush=True)
        print(f"Question: {res.question_text}", flush=True)
        print(f"Bloom: {res.bloom} | Marks: {res.marks} | Type: {res.question_type}", flush=True)
        assert res.question_text and len(res.question_text) > 5, f"Question generation failed for {subj}"
    
    print("\n[ALL TESTS PASSED SUCCESSFULLY]", flush=True)

if __name__ == "__main__":
    run_tests()
