"""Unit tests for production-safe AQPG question paper generation fixes."""

import unittest
from unittest.mock import MagicMock, patch

from app.services.ai.base import AIQuestionPrompt, GeneratedQuestionResult
from app.services.ai.generator_factory import OfflineFallbackProvider, get_ai_generator
from app.services.ai.prompt_builder import build_subject_specific_system_prompt
from app.services.question_generator import (
    compute_question_hash,
    compute_structural_hash,
    validate_unit_relevance,
)


class TestQuestionGeneratorFixes(unittest.TestCase):
    """Test suite covering unit grounding, relevance validation, structural deduplication, and safe fallback."""

    def test_1_coordinate_geometry_rejects_quadratic_equation(self):
        """TEST 1: A Coordinate Geometry request must not accept a generic quadratic-equation fallback."""
        q_text = "Solve the quadratic equation x² - 5x + 6 = 0 using the quadratic formula and state the nature of roots."
        is_valid = validate_unit_relevance(q_text, "Unit 5 - Coordinate Geometry")
        self.assertFalse(is_valid, "Coordinate Geometry must reject quadratic equation solver questions.")

    def test_2_statistics_rejects_coordinate_geometry(self):
        """TEST 2: A Statistics request must not receive a Coordinate Geometry question."""
        q_text = "Find the distance between the points A(2, 3) and B(5, 7) in the coordinate plane."
        is_valid = validate_unit_relevance(q_text, "Unit 8 - Statistics and Probability")
        self.assertFalse(is_valid, "Statistics request must reject Coordinate Geometry distance formula questions.")

    def test_3_unit_relevance_validation_accepts_valid_match(self):
        """TEST 3: A question generated for Unit A must be relevant to Unit A."""
        q_text = "Find the coordinates of the point P which divides the line segment joining A(-1, 7) and B(4, -3) in ratio 2:3."
        is_valid = validate_unit_relevance(q_text, "Unit 5 - Coordinate Geometry")
        self.assertTrue(is_valid, "Coordinate Geometry must accept section formula questions.")

    def test_4_exact_duplicate_detection(self):
        """TEST 4: Duplicate exact text must be rejected via question hash."""
        text1 = "Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18..."
        text2 = "Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18... (Unit 1 - AP)"
        self.assertEqual(compute_question_hash(text1), compute_question_hash(text2))

    def test_5_structural_template_deduplication(self):
        """TEST 5: The same question structure with different numeric values should be detected structurally."""
        q1 = "Solve the quadratic equation x² - 5x + 6 = 0 using the quadratic formula."
        q2 = "Solve the quadratic equation x² + 3x - 10 = 0 using the quadratic formula."
        self.assertEqual(
            compute_structural_hash(q1),
            compute_structural_hash(q2),
            "Structural hash must match questions sharing the exact same numeric template.",
        )

    def test_6_bloom_target_in_generation_prompt(self):
        """TEST 6: Bloom target must be included in the generation prompt."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 5 - Coordinate Geometry",
            topic_name="Distance Formula",
            marks=3,
            difficulty="medium",
            bloom_level="Analyze",
            question_type="Numerical",
        )
        sys_prompt = build_subject_specific_system_prompt(prompt)
        self.assertIn("Bloom Taxonomy: Analyze", sys_prompt)
        self.assertIn("CRITICAL CURRICULUM BOUNDARY CONSTRAINTS", sys_prompt)

    def test_7_unit_topic_syllabus_context_in_prompt(self):
        """TEST 7: Unit name/topic/syllabus context must be included in the generation prompt."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 5 - Coordinate Geometry",
            topic_name=None,
            marks=3,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
            unit_description="Distance formula, section formula, midpoint calculation",
            topics_list=["Distance Formula", "Section Formula"],
        )
        sys_prompt = build_subject_specific_system_prompt(prompt)
        self.assertIn("Unit: Unit 5 - Coordinate Geometry", sys_prompt)
        self.assertIn("Distance Formula, Section Formula", sys_prompt)
        self.assertIn("Distance formula, section formula, midpoint calculation", sys_prompt)

    def test_8_blueprint_counts_and_marks_preserved(self):
        """TEST 8: Existing paper blueprint properties are correctly initialized."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 3 - Quadratic Equations",
            topic_name="Roots",
            marks=4,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
        )
        self.assertEqual(prompt.marks, 4)
        self.assertEqual(prompt.bloom_level, "Apply")

    def test_9_v17_2_provider_selection_logic(self):
        """TEST 9: Existing V17.2 provider selection remains unchanged when AI_PROVIDER=v17_2."""
        with patch.dict("os.environ", {"AI_PROVIDER": "v17_2"}):
            with patch("app.services.ai.v17_2_inference_adapter.V17_2InferenceAdapter.is_available", return_value=True):
                provider = get_ai_generator()
                self.assertEqual(provider.__class__.__name__, "V17_2InferenceAdapter")

    def test_10_fallback_provider_fails_safely_on_unmapped_unit(self):
        """TEST 10: The fallback provider must fail safely rather than generating an unrelated unit question."""
        fallback = OfflineFallbackProvider()
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 99 - Quantum Topologies",
            topic_name="Unknown",
            marks=3,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
        )
        res = fallback.generate_question(prompt)
        self.assertIsNone(res, "OfflineFallbackProvider must return None for unmapped math units.")


if __name__ == "__main__":
    unittest.main()
