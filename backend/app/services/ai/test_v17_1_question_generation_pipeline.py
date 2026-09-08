"""Phase 5 Pipeline Test for AQPG V17.1 Question Generation Model.

Executes representative test cases across Mathematics, Physics, Chemistry, Biology, and General Science.
Analyzes outputs for validity, repetition, malformation, and question-like structure.
Generates comprehensive report JSON at backend/ml/evaluation/v17_1_pipeline_test_report.json.
"""

import json
import os
import re
import sys
import unittest
from typing import Any, Dict, List

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.services.ai.base import AIQuestionPrompt, GeneratedQuestionResult
from app.services.ai.v17_1_inference_adapter import V17_1InferenceAdapter

TEST_CASES = [
    {
        "id": 1,
        "subject": "Mathematics",
        "topic": "Quadratic Equations",
        "class_name": "Class 10",
        "marks": 2,
        "difficulty": "easy",
        "question_type": "Short Answer",
        "bloom_level": "Understand",
    },
    {
        "id": 2,
        "subject": "Physics",
        "topic": "Newton's Laws of Motion",
        "class_name": "Class 10",
        "marks": 3,
        "difficulty": "medium",
        "question_type": "Conceptual",
        "bloom_level": "Understand",
    },
    {
        "id": 3,
        "subject": "Chemistry",
        "topic": "Acids Bases and Salts",
        "class_name": "Class 10",
        "marks": 3,
        "difficulty": "medium",
        "question_type": "Short Answer",
        "bloom_level": "Apply",
    },
    {
        "id": 4,
        "subject": "Biology",
        "topic": "Life Processes",
        "class_name": "Class 10",
        "marks": 5,
        "difficulty": "hard",
        "question_type": "Long Answer",
        "bloom_level": "Analyze",
    },
    {
        "id": 5,
        "subject": "General Science",
        "topic": "Light",
        "class_name": "Class 8",
        "marks": 2,
        "difficulty": "easy",
        "question_type": "Short Answer",
        "bloom_level": "Remember",
    },
]

REPORT_PATH = os.path.abspath("backend/ml/evaluation/v17_1_pipeline_test_report.json")


def analyze_output_quality(output_text: str, subject: str, topic: str) -> Dict[str, bool]:
    """Analyze generated output for repetition, malformation, and question structure."""
    text = output_text.strip() if output_text else ""
    if not text:
        return {
            "is_empty": True,
            "is_repetitive": False,
            "is_malformed": True,
            "is_question_like": False,
            "subject_relevant": False,
            "topic_relevant": False,
        }

    words = re.findall(r"\w+", text.lower())
    
    # Repetition Check: Check if any word accounts for > 35% of total words (when > 5 words) or 5+ consecutive repeats
    is_repetitive = False
    if len(words) > 3:
        word_counts = {}
        for w in words:
            word_counts[w] = word_counts.get(w, 0) + 1
        max_freq = max(word_counts.values())
        if (max_freq / len(words)) > 0.35:
            is_repetitive = True
        
        # Check consecutive identical n-grams or tokens
        for i in range(len(words) - 3):
            if words[i] == words[i+1] == words[i+2] == words[i+3]:
                is_repetitive = True
                break

    # Substring repetition check (e.g. "reheatreheatreheat")
    if len(text) > 20:
        for sub_len in range(3, 10):
            sub = text[:sub_len]
            if sub * (len(text) // sub_len) == text[:sub_len * (len(text) // sub_len)]:
                is_repetitive = True
                break

    # Question-like check
    interrogatives = {"what", "why", "how", "calculate", "explain", "state", "define", "find", "derive", "describe", "which", "list", "name", "discuss", "compare", "identify", "evaluate", "prove"}
    contains_interrogative = any(w in interrogatives for w in words)
    ends_with_qmark = text.endswith("?")
    is_question_like = contains_interrogative or ends_with_qmark

    # Malformed check
    is_malformed = is_repetitive or (len(words) < 3 and not ends_with_qmark) or not is_question_like

    # Subject / Topic relevance check
    subj_tokens = set(re.findall(r"\w+", subject.lower()))
    topic_tokens = set(re.findall(r"\w+", topic.lower()))
    subject_relevant = any(w in words for w in subj_tokens) if subj_tokens else False
    topic_relevant = any(w in words for w in topic_tokens) if topic_tokens else False

    return {
        "is_empty": False,
        "is_repetitive": is_repetitive,
        "is_malformed": is_malformed,
        "is_question_like": is_question_like,
        "subject_relevant": subject_relevant,
        "topic_relevant": topic_relevant,
    }


class TestV17_1QuestionGenerationPipeline(unittest.TestCase):
    """Phase 5 Pipeline Test Suite for V17.1 Model."""

    @classmethod
    def setUpClass(cls):
        cls.model_path = os.path.abspath("backend/ml/models/checkpoints/flan_t5_v17/best_model")
        cls.adapter = V17_1InferenceAdapter(model_path=cls.model_path)
        cls.assertTrue(cls.adapter.is_available(), f"V17.1 model not available at {cls.model_path}")
        cls.adapter.load_model()

    @classmethod
    def tearDownClass(cls):
        cls.adapter.unload_model()

    def test_pipeline_execution_and_generate_report(self):
        """Run all 5 representative test cases and compile JSON pipeline evaluation report."""
        results_list = []
        successful_inferences = 0
        failed_inferences = 0
        repetitive_outputs = 0
        malformed_outputs = 0
        question_like_outputs = 0
        lengths = []

        print("\n============================================================")
        print("EXECUTING PHASE 5 V17.1 QUESTION GENERATION PIPELINE TESTS")
        print("============================================================")

        for tc in TEST_CASES:
            prompt_obj = AIQuestionPrompt(
                board="CBSE",
                class_name=tc["class_name"],
                subject_name=tc["subject"],
                unit_name=tc["topic"],
                topic_name=tc["topic"],
                marks=tc["marks"],
                difficulty=tc["difficulty"],
                bloom_level=tc["bloom_level"],
                question_type=tc["question_type"],
            )

            print(f"\nTest Case #{tc['id']}: {tc['subject']} | {tc['topic']} ({tc['question_type']}, {tc['marks']}M, {tc['bloom_level']})")

            try:
                gen_result = self.adapter.generate_question(prompt=prompt_obj)
                out_text = gen_result.question_text
                inference_success = True
                successful_inferences += 1
            except Exception as exc:
                out_text = f"ERROR: {exc}"
                inference_success = False
                failed_inferences += 1

            quality = analyze_output_quality(out_text, tc["subject"], tc["topic"])

            if quality["is_repetitive"]:
                repetitive_outputs += 1
            if quality["is_malformed"]:
                malformed_outputs += 1
            if quality["is_question_like"]:
                question_like_outputs += 1

            out_len = len(out_text) if out_text else 0
            lengths.append(out_len)

            print(f"  Generated Text: '{out_text[:120]}{'...' if len(out_text) > 120 else ''}'")
            print(f"  Output Length: {out_len} chars")
            print(f"  Quality Flags: Repetitive={quality['is_repetitive']}, Malformed={quality['is_malformed']}, QuestionLike={quality['is_question_like']}")

            results_list.append({
                "test_case_id": tc["id"],
                "subject": tc["subject"],
                "topic": tc["topic"],
                "class_name": tc["class_name"],
                "marks": tc["marks"],
                "difficulty": tc["difficulty"],
                "question_type": tc["question_type"],
                "bloom_level": tc["bloom_level"],
                "generated_output": out_text,
                "inference_success": inference_success,
                "output_length": out_len,
                "quality_flags": quality,
            })

        avg_len = sum(lengths) / len(lengths) if lengths else 0.0

        report_data = {
            "phase": "5",
            "model": "V17.1",
            "model_path": self.model_path,
            "model_loaded": True,
            "training_started": False,
            "model_modified": False,
            "dataset_modified": False,
            "remote_download": False,
            "total_test_cases": len(TEST_CASES),
            "successful_inferences": successful_inferences,
            "failed_inferences": failed_inferences,
            "repetitive_outputs": repetitive_outputs,
            "malformed_outputs": malformed_outputs,
            "question_like_outputs": question_like_outputs,
            "average_output_length": round(avg_len, 2),
            "min_output_length": min(lengths) if lengths else 0,
            "max_output_length": max(lengths) if lengths else 0,
            "results": results_list,
        }

        # Save report JSON
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)

        print("\n============================================================")
        print(f"PIPELINE REPORT GENERATED: {REPORT_PATH}")
        print("============================================================")

        self.assertEqual(successful_inferences, len(TEST_CASES))


if __name__ == "__main__":
    unittest.main()
