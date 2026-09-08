"""AQPG V17.2 AI Provider Contract Tests.

Verifies that V17_2InferenceAdapter satisfies all BaseAIProvider interface requirements,
preserves required metadata, executes local inference without remote downloads,
and unloads cleanly.
"""

import os
import unittest
import torch

from app.services.ai.base import AIQuestionPrompt, BaseAIProvider, GeneratedQuestionResult
from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter


class TestV17_2ProviderContract(unittest.TestCase):
    """Test suite for V17.2 AI Provider Contract verification."""

    def setUp(self):
        self.adapter = V17_2InferenceAdapter()

    def tearDown(self):
        if hasattr(self, 'adapter') and self.adapter:
            self.adapter.unload_model()

    def test_01_instantiation(self):
        """1. Verify adapter can be instantiated."""
        self.assertIsNotNone(self.adapter)
        self.assertIsInstance(self.adapter, BaseAIProvider)
        self.assertIsInstance(self.adapter, V17_2InferenceAdapter)

    def test_02_is_available(self):
        """2. Verify is_available() returns True for valid local V17.2 checkpoint."""
        self.assertTrue(self.adapter.is_available(), "V17.2 model weights should be present locally.")

    def test_03_04_load_model_tokenizer(self):
        """3 & 4. Verify local tokenizer and V17.2 model load properly with local_files_only=True."""
        loaded = self.adapter.load_model()
        self.assertTrue(loaded)
        self.assertIsNotNone(self.adapter.tokenizer)
        self.assertIsNotNone(self.adapter.model)
        self.assertFalse(self.adapter.model.training, "Model must be in eval() mode.")

    def test_05_06_07_08_prompt_conversion_inference_result_metadata(self):
        """5, 6, 7, 8. Verify prompt conversion, inference execution, GeneratedQuestionResult, and metadata preservation."""
        test_prompt = AIQuestionPrompt(
            board="CBSE",
            subject_name="Physics",
            topic_name="Optics",
            unit_name="Unit 3: Light",
            class_name="Class 10",
            difficulty="Hard",
            marks=5,
            question_type="Long Answer",
            bloom_level="Apply"
        )

        result = self.adapter.generate_question(prompt=test_prompt)

        # 6 & 7. Verification of execution & result type
        self.assertIsNotNone(result)
        self.assertIsInstance(result, GeneratedQuestionResult)
        self.assertIsInstance(result.question_text, str)
        self.assertGreater(len(result.question_text.strip()), 0)

        # 8. Required metadata preservation check
        self.assertEqual(result.question_type, "Long Answer")
        self.assertEqual(result.marks, 5)
        self.assertEqual(result.difficulty, "Hard")
        self.assertEqual(result.bloom, "Apply")
        self.assertEqual(result.unit_name, "Unit 3: Light")
        self.assertEqual(result.topic_name, "Optics")

    def test_09_unload_model(self):
        """9. Verify unload_model() clears references and frees model memory state."""
        self.adapter.load_model()
        self.assertIsNotNone(self.adapter.model)
        self.assertIsNotNone(self.adapter.tokenizer)

        self.adapter.unload_model()
        self.assertIsNone(self.adapter.model)
        self.assertIsNone(self.adapter.tokenizer)
        self.assertFalse(self.adapter._is_loaded)

    def test_10_no_remote_download(self):
        """10. Verify adapter fails safely when path is invalid without attempting remote download."""
        invalid_adapter = V17_2InferenceAdapter(model_path="non_existent_path_v17_2")
        self.assertFalse(invalid_adapter.is_available())
        with self.assertRaises(RuntimeError) as ctx:
            invalid_adapter.load_model()
        self.assertIn("No inference was performed", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
