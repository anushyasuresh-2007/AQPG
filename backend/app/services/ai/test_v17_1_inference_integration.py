"""Phase 4 Integration & Smoke Test for V17.1 Local Model Inference.

Verifies:
1. Integrity of restored V17.1 best_model checkpoint directory and files.
2. Adapter resolves the restored model path and reports is_available() == True.
3. load_model() successfully loads tokenizer and model weights using local_files_only=True.
4. generate_question() produces a valid GeneratedQuestionResult containing generated_text.
5. Output structure fields (question_text, marks, difficulty, bloom, question_type, etc.) are intact.
6. unload_model() safely frees model and tokenizer from memory.
"""

import os
import sys
import unittest

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.services.ai.v17_1_inference_adapter import V17_1InferenceAdapter
from app.services.ai.base import GeneratedQuestionResult


class TestV17_1InferenceIntegration(unittest.TestCase):
    """Smoke & Integration tests for restored V17.1 FLAN-T5 model inference."""

    @classmethod
    def setUpClass(cls):
        cls.expected_model_path = os.path.abspath("backend/ml/models/checkpoints/flan_t5_v17/best_model")
        cls.required_files = [
            "model.safetensors",
            "config.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "generation_config.json",
        ]

    def test_01_checkpoint_file_integrity(self):
        """Verify all expected model weights and configuration files exist locally."""
        self.assertTrue(os.path.exists(self.expected_model_path), f"Path not found: {self.expected_model_path}")
        for fname in self.required_files:
            fpath = os.path.join(self.expected_model_path, fname)
            self.assertTrue(os.path.exists(fpath), f"Required file missing: {fpath}")
            self.assertGreater(os.path.getsize(fpath), 0, f"File is empty: {fpath}")

    def test_02_adapter_availability(self):
        """Verify V17_1InferenceAdapter detects the restored model and reports is_available() == True."""
        adapter = V17_1InferenceAdapter(model_path=self.expected_model_path)
        self.assertTrue(adapter.is_available())

    def test_03_load_model_and_inference_and_unload(self):
        """Verify model loading, actual inference execution, output validation, and model unloading."""
        adapter = V17_1InferenceAdapter(model_path=self.expected_model_path)
        self.assertTrue(adapter.is_available())

        # Load model
        loaded = adapter.load_model()
        self.assertTrue(loaded)
        self.assertIsNotNone(adapter.model)
        self.assertIsNotNone(adapter.tokenizer)
        self.assertTrue(adapter._is_loaded)

        # Run safe inference
        result = adapter.generate_question(
            subject="Physics",
            topic="Newton's Laws of Motion",
            difficulty="medium",
            question_type="Conceptual",
            marks=3,
            bloom_level="Understand",
        )

        # Verify output structure
        self.assertIsInstance(result, GeneratedQuestionResult)
        self.assertIsNotNone(result.question_text)
        self.assertGreater(len(result.question_text.strip()), 0)
        self.assertEqual(result.marks, 3)
        self.assertEqual(result.difficulty, "medium")
        self.assertEqual(result.bloom, "Understand")
        self.assertEqual(result.question_type, "Conceptual")

        print(f"\n--- Phase 4 V17.1 Inference Output Sample ---")
        print(f"Prompt Input: Physics | Newton's Laws of Motion | Conceptual | 3 Marks | Understand")
        print(f"Model Generated Output: '{result.question_text}'")

        # Unload model
        adapter.unload_model()
        self.assertIsNone(adapter.model)
        self.assertIsNone(adapter.tokenizer)
        self.assertFalse(adapter._is_loaded)


if __name__ == "__main__":
    unittest.main()
