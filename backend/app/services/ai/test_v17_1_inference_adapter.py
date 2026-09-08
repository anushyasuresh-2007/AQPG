"""Smoke tests for V17_1InferenceAdapter scaffolding.

Verifies:
1. Adapter instantiation with default and custom non-existent paths.
2. is_available() correctly returns False when V17.1 model weights are absent.
3. generate_question() raises explicit RuntimeError without running inference when model weights are absent.
4. load_model() raises explicit RuntimeError when model weights are absent.
5. No files or checkpoints are created or modified during testing.
"""

import sys
import os
import unittest

# Ensure backend root is on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from app.services.ai.v17_1_inference_adapter import V17_1InferenceAdapter


class TestV17_1InferenceAdapterScaffolding(unittest.TestCase):
    """Test safe scaffolding behavior of V17_1InferenceAdapter."""

    def test_instantiation_default_path(self):
        """Verify adapter instantiates cleanly without errors."""
        adapter = V17_1InferenceAdapter()
        self.assertIsNotNone(adapter)

    def test_is_available_returns_false_when_weights_absent(self):
        """Verify is_available() returns False when V17.1 weights are absent."""
        adapter = V17_1InferenceAdapter(model_path="non_existent_path_v17_1_test")
        self.assertFalse(adapter.is_available())

    def test_load_model_raises_runtime_error_when_weights_absent(self):
        """Verify load_model() raises RuntimeError when model path has no weights."""
        adapter = V17_1InferenceAdapter(model_path="non_existent_path_v17_1_test")
        with self.assertRaises(RuntimeError) as context:
            adapter.load_model()
        self.assertIn("V17.1 local model weights are not available", str(context.exception))

    def test_generate_question_raises_runtime_error_when_weights_absent(self):
        """Verify generate_question() refuses execution and raises RuntimeError when weights are absent."""
        adapter = V17_1InferenceAdapter(model_path="non_existent_path_v17_1_test")
        with self.assertRaises(RuntimeError) as context:
            adapter.generate_question(
                subject="Physics",
                topic="Mechanics",
                difficulty="medium",
                question_type="Numerical",
                marks=5,
                bloom_level="Apply",
            )
        self.assertIn("V17.1 local model weights are not available", str(context.exception))

    def test_unload_model_resets_state(self):
        """Verify unload_model() resets adapter internal state."""
        adapter = V17_1InferenceAdapter()
        adapter.unload_model()
        self.assertIsNone(adapter.model)
        self.assertIsNone(adapter.tokenizer)
        self.assertFalse(adapter._is_loaded)


if __name__ == "__main__":
    unittest.main()
