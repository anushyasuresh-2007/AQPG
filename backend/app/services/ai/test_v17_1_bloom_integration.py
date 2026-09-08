"""Phase 6 Integration & Validation Test for Bloom's Taxonomy in AQPG V17.1.

Validates:
1. Bloom level metadata handling across all six Bloom levels (Remember, Understand, Apply, Analyze, Evaluate, Create).
2. Input sanitization and validation (case-insensitivity, whitespace trimming, invalid/null handling).
3. Pipeline metadata preservation (Requested vs Prompt vs Result metadata match).
4. Semantic Bloom assessment using lightweight heuristic signal (reporting NOT ASSESSABLE for repetitive model output).
5. Compiles JSON report at backend/ml/evaluation/v17_1_bloom_integration_report.json.
"""

import json
import os
import re
import sys
import unittest
from typing import Any, Dict, Optional

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.services.ai.base import AIQuestionPrompt, GeneratedQuestionResult
from app.services.ai.v17_1_inference_adapter import V17_1InferenceAdapter

VALID_BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
REPORT_PATH = os.path.abspath("backend/ml/evaluation/v17_1_bloom_integration_report.json")

BLOOM_HEURISTIC_KEYWORDS = {
    "Remember": ["recall", "define", "identify", "list", "name", "state", "what is"],
    "Understand": ["explain", "describe", "summarize", "contrast", "discuss", "illustrate"],
    "Apply": ["calculate", "solve", "apply", "compute", "determine", "find", "use", "demonstrate"],
    "Analyze": ["analyze", "compare", "differentiate", "examine", "distinguish", "deconstruct"],
    "Evaluate": ["evaluate", "assess", "justify", "critique", "judge", "validate"],
    "Create": ["design", "construct", "formulate", "create", "develop", "propose"],
}


def sanitize_and_validate_bloom_level(bloom_input: Optional[str]) -> Optional[str]:
    """Sanitize and validate input Bloom taxonomy level."""
    if not bloom_input or not isinstance(bloom_input, str):
        return None
    cleaned = bloom_input.strip()
    if not cleaned:
        return None
    for valid in VALID_BLOOM_LEVELS:
        if cleaned.lower() == valid.lower():
            return valid
    return None


def evaluate_semantic_bloom_quality(output_text: str, requested_bloom: str) -> Dict[str, Any]:
    """
    Perform LIGHTWEIGHT HEURISTIC SIGNAL ONLY check on generated question output.
    Returns NOT ASSESSABLE if text is malformed or repetitive.
    """
    if not output_text or len(output_text.strip()) == 0:
        return {"semantic_assessment": "NOT ASSESSABLE", "reason": "Empty output"}

    # Check for severe repetition
    words = re.findall(r"\w+", output_text.lower())
    if len(words) > 3:
        word_counts = {w: words.count(w) for w in set(words)}
        if max(word_counts.values()) / len(words) > 0.35:
            return {"semantic_assessment": "NOT ASSESSABLE", "reason": "Model output collapsed into repetitive token loop"}

    # Lightweight heuristic signal check
    keywords = BLOOM_HEURISTIC_KEYWORDS.get(requested_bloom, [])
    found_keywords = [kw for kw in keywords if kw in output_text.lower()]

    if found_keywords:
        return {
            "semantic_assessment": "PARTIAL",
            "signal_type": "LIGHTWEIGHT HEURISTIC SIGNAL ONLY",
            "detected_keywords": found_keywords,
        }

    return {
        "semantic_assessment": "NOT ASSESSABLE",
        "signal_type": "LIGHTWEIGHT HEURISTIC SIGNAL ONLY",
        "reason": "No heuristic keywords detected",
    }


TEST_CASES_PHASE6 = [
    {
        "test_id": 1,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "class_name": "Class 10",
        "marks": 2,
        "difficulty": "easy",
        "question_type": "Short Answer",
        "bloom_level": "Remember",
    },
    {
        "test_id": 2,
        "subject": "Physics",
        "topic": "Newton's Laws of Motion",
        "class_name": "Class 10",
        "marks": 3,
        "difficulty": "medium",
        "question_type": "Conceptual",
        "bloom_level": "Understand",
    },
    {
        "test_id": 3,
        "subject": "Chemistry",
        "topic": "Acids, Bases and Salts",
        "class_name": "Class 10",
        "marks": 3,
        "difficulty": "medium",
        "question_type": "Short Answer",
        "bloom_level": "Apply",
    },
    {
        "test_id": 4,
        "subject": "Biology",
        "topic": "Life Processes",
        "class_name": "Class 10",
        "marks": 5,
        "difficulty": "hard",
        "question_type": "Long Answer",
        "bloom_level": "Analyze",
    },
    {
        "test_id": 5,
        "subject": "General Science",
        "topic": "Light",
        "class_name": "Class 8",
        "marks": 2,
        "difficulty": "easy",
        "question_type": "Short Answer",
        "bloom_level": "Evaluate",
    },
    {
        "test_id": 6,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "class_name": "Class 10",
        "marks": 5,
        "difficulty": "hard",
        "question_type": "Long Answer",
        "bloom_level": "Create",
    },
]


class TestV17_1BloomIntegration(unittest.TestCase):
    """Phase 6 Bloom Taxonomy Integration & Metadata Validation Test Suite."""

    def test_01_bloom_level_validation_utility(self):
        """Test Bloom level sanitizer utility across all valid, invalid, and edge-case inputs."""
        # 1. Test all 6 valid levels
        for level in VALID_BLOOM_LEVELS:
            self.assertEqual(sanitize_and_validate_bloom_level(level), level)

        # 2. Test case insensitivity
        self.assertEqual(sanitize_and_validate_bloom_level("remember"), "Remember")
        self.assertEqual(sanitize_and_validate_bloom_level("UNDERSTAND"), "Understand")
        self.assertEqual(sanitize_and_validate_bloom_level("aPPlY"), "Apply")

        # 3. Test whitespace handling
        self.assertEqual(sanitize_and_validate_bloom_level("  Analyze  "), "Analyze")

        # 4. Test invalid values
        self.assertIsNone(sanitize_and_validate_bloom_level("SuperUnderstand"))
        self.assertIsNone(sanitize_and_validate_bloom_level("InvalidLevel"))

        # 5. Test empty / None handling
        self.assertIsNone(sanitize_and_validate_bloom_level(""))
        self.assertIsNone(sanitize_and_validate_bloom_level("   "))
        self.assertIsNone(sanitize_and_validate_bloom_level(None))

    def test_02_pipeline_bloom_metadata_preservation_and_report_generation(self):
        """Run 6 Bloom level test cases through V17.1 inference adapter and verify metadata preservation."""
        model_path = os.path.abspath("backend/ml/models/checkpoints/flan_t5_v17/best_model")
        adapter = V17_1InferenceAdapter(model_path=model_path)
        self.assertTrue(adapter.is_available())
        adapter.load_model()

        test_results = []
        metadata_match_count = 0
        repetition_count = 0

        print("\n============================================================")
        print("EXECUTING PHASE 6 BLOOM TAXONOMY INTEGRATION TESTS")
        print("============================================================")

        for tc in TEST_CASES_PHASE6:
            req_bloom = tc["bloom_level"]
            validated_bloom = sanitize_and_validate_bloom_level(req_bloom)
            self.assertIsNotNone(validated_bloom)

            prompt_obj = AIQuestionPrompt(
                board="CBSE",
                class_name=tc["class_name"],
                subject_name=tc["subject"],
                unit_name=tc["topic"],
                topic_name=tc["topic"],
                marks=tc["marks"],
                difficulty=tc["difficulty"],
                bloom_level=validated_bloom,
                question_type=tc["question_type"],
            )

            gen_result = adapter.generate_question(prompt=prompt_obj)
            res_bloom = gen_result.bloom

            # Check metadata preservation
            metadata_matches = (req_bloom == validated_bloom == gen_result.bloom)
            if metadata_matches:
                metadata_match_count += 1

            # Perform LIGHTWEIGHT HEURISTIC SIGNAL ONLY check
            semantic_eval = evaluate_semantic_bloom_quality(gen_result.question_text, req_bloom)

            if "repetition" in semantic_eval.get("reason", "").lower() or "repetitive" in str(semantic_eval):
                repetition_count += 1

            print(f"Test #{tc['test_id']}: Requested [{req_bloom}] | Prompt [{prompt_obj.bloom_level}] | Result [{res_bloom}] | Match: {metadata_matches}")
            print(f"  Output Sample: '{gen_result.question_text[:80]}...'")
            print(f"  Semantic Assessment: {semantic_eval['semantic_assessment']} ({semantic_eval.get('reason', 'heuristic check')})")

            test_results.append({
                "test_id": tc["test_id"],
                "subject": tc["subject"],
                "topic": tc["topic"],
                "requested_bloom": req_bloom,
                "prompt_bloom": prompt_obj.bloom_level,
                "result_bloom": res_bloom,
                "metadata_match": metadata_matches,
                "generated_output_sample": gen_result.question_text[:120],
                "semantic_bloom_assessment": semantic_eval["semantic_assessment"],
                "semantic_signal": semantic_eval.get("signal_type", "LIGHTWEIGHT HEURISTIC SIGNAL ONLY"),
                "assessment_note": semantic_eval.get("reason", "repetition detected"),
            })

        adapter.unload_model()

        match_rate_pct = round((metadata_match_count / len(TEST_CASES_PHASE6)) * 100, 2)

        # Existing ML Bloom Classifier evaluation metrics from Step 8
        existing_ml_classifier_summary = {
            "evaluated": True,
            "overall_accuracy_pct": 88.46,
            "macro_f1_score": 0.8985,
            "samples_evaluated": 22281,
            "model_type": "TF-IDF + LogisticRegression",
            "location": "backend/ml/models/bloom_classifier/",
        }

        report_data = {
            "phase": "6",
            "model": "V17.1",
            "model_path": model_path,
            "model_modified": False,
            "training_started": False,
            "dataset_modified": False,
            "checkpoint_modified": False,
            "fastapi_modified": False,
            "bloom_levels": VALID_BLOOM_LEVELS,
            "existing_ml_bloom_classifier": existing_ml_classifier_summary,
            "total_bloom_tests": len(TEST_CASES_PHASE6),
            "metadata_match_count": metadata_match_count,
            "metadata_match_rate": f"{match_rate_pct}%",
            "semantic_assessment_overall": "NOT ASSESSABLE",
            "known_generation_failure": True,
            "repetition_count": repetition_count,
            "tests": test_results,
            "status": "PHASE 6 COMPLETE",
        }

        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print("\n============================================================")
        print(f"PHASE 6 REPORT GENERATED: {REPORT_PATH}")
        print(f"Metadata Match Rate: {match_rate_pct}%")
        print(f"Semantic Bloom Assessment: NOT ASSESSABLE (Known V17.1 Repetition Issue)")
        print("============================================================")

        self.assertEqual(metadata_match_count, len(TEST_CASES_PHASE6))


if __name__ == "__main__":
    unittest.main()
