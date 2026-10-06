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

    def test_11_unit_relevance_uses_description_and_topics_context(self):
        """TEST 11: validate_unit_relevance uses unit_description and topics_list when unit_name is generic."""
        q_text = "Find the distance between the points A(2, 3) and B(5, 7) in the coordinate plane."
        is_valid = validate_unit_relevance(
            q_text,
            unit_name="Unit 4",
            unit_description="Analytical geometry including Cartesian plane calculations",
            topics_list=["Coordinate Geometry", "Distance Formula"],
        )
        self.assertTrue(is_valid, "validate_unit_relevance must accept coordinate questions when topics_list contains Coordinate Geometry.")

    def test_12_generic_geometry_unit_does_not_route_to_coordinate_fallback(self):
        """TEST 12: Generic Geometry units like 'Geometry of Circles' must not route to Coordinate Geometry fallback templates."""
        fallback = OfflineFallbackProvider()
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Geometry of Circles",
            topic_name="Circles",
            marks=2,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )
        res = fallback.generate_question(prompt)
        self.assertIsNotNone(res)
        self.assertNotIn("coordinate plane", res.question_text.lower())
        self.assertNotIn("distance between the points", res.question_text.lower())


    def test_production_failure_cases_A_to_J(self):
        """Regression test suite covering production failure cases A through J."""
        quad_q = "Solve x² + 5x + 6 = 0 using quadratic formula."
        boat_q = "A motor boat whose speed is 15 km/h in still water goes 30 km downstream and returns upstream in 4 hours 30 minutes. Find speed of the stream."

        # A. Trigonometry + quadratic -> REJECT
        self.assertFalse(validate_unit_relevance(quad_q, "Trigonometry"))

        # B. Coordinate Geometry + quadratic -> REJECT
        self.assertFalse(validate_unit_relevance(quad_q, "Coordinate Geometry"))

        # C. Statistics and Probability + quadratic -> REJECT
        self.assertFalse(validate_unit_relevance(quad_q, "Statistics and Probability"))

        # D. Mensuration + quadratic -> REJECT
        self.assertFalse(validate_unit_relevance(quad_q, "Mensuration"))

        # E. Relations and Functions + quadratic -> REJECT
        self.assertFalse(validate_unit_relevance(quad_q, "Relations and Functions"))

        # F. Algebra / Quadratics + quadratic -> ACCEPT
        self.assertTrue(validate_unit_relevance(quad_q, "Quadratic Equations"))

        # G. Mensuration + motor boat problem -> REJECT
        self.assertFalse(validate_unit_relevance(boat_q, "Mensuration"))

        # H. Correct unit/category question -> ACCEPT
        mens_q = "Find the volume of a solid cylinder of radius 5 cm and height 10 cm."
        self.assertTrue(validate_unit_relevance(mens_q, "Mensuration"))

        # I. Same structural quadratic template with different coefficients -> Structural Duplicate
        q1 = "Solve x² + 5x + 6 = 0 using quadratic formula."
        q2 = "Solve x² + 3x - 10 = 0 using quadratic formula."
        q3 = "Solve x² - 8x + 15 = 0 using quadratic formula."
        self.assertEqual(compute_structural_hash(q1), compute_structural_hash(q2))
        self.assertEqual(compute_structural_hash(q1), compute_structural_hash(q3))

        var_q = "Solve x² + 5x + 6 = 0 using quadratic formula (Variation 49)"
        self.assertEqual(compute_question_hash(q1), compute_question_hash(var_q))
        self.assertEqual(compute_structural_hash(q1), compute_structural_hash(var_q))

    def test_question_bank_filtering_and_cleaning(self):
        """TEST 14: Question Bank filtering rejects misplaced/duplicate bank entries and cleans metadata tags."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 10"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_coord = MagicMock()
        mock_unit_coord.id = 10
        mock_unit_coord.unit_name = "Unit 5 - Coordinate Geometry"
        mock_unit_coord.description = "Cartesian plane calculations"

        mock_unit_mens = MagicMock()
        mock_unit_mens.id = 11
        mock_unit_mens.unit_name = "Unit 7 - Mensuration"
        mock_unit_mens.description = "Surface area and volume"

        # Mock Bank questions with explicit int/str attributes
        q101 = MagicMock()  # Bad: quadratic in Coordinate Geometry
        q101.id = 101; q101.subject_id = 1; q101.unit_id = 10; q101.bloom_level_id = 1; q101.question_text = "Solve x² + 5x + 6 = 0 using quadratic formula."; q101.marks = 3; q101.difficulty = "medium"; q101.question_type = "Short Answer"; q101.status = "approved"; q101.active = True; q101.source = "Bank"; q101.answer = ""; q101.explanation = ""

        q102 = MagicMock()  # Bad: motor boat in Mensuration
        q102.id = 102; q102.subject_id = 1; q102.unit_id = 11; q102.bloom_level_id = 1; q102.question_text = "A motor boat speed in still water is 15 km/h goes 30 km downstream and upstream. Find speed of stream."; q102.marks = 3; q102.difficulty = "medium"; q102.question_type = "Short Answer"; q102.status = "approved"; q102.active = True; q102.source = "Bank"; q102.answer = ""; q102.explanation = ""

        q103 = MagicMock()  # Valid Mensuration with Variation tag
        q103.id = 103; q103.subject_id = 1; q103.unit_id = 11; q103.bloom_level_id = 1; q103.question_text = "Find the volume of a solid cylinder of radius 5 cm and height 10 cm. (Variation 49)"; q103.marks = 3; q103.difficulty = "medium"; q103.question_type = "Short Answer"; q103.status = "approved"; q103.active = True; q103.source = "Bank"; q103.answer = ""; q103.explanation = ""

        q104 = MagicMock()  # Structural duplicate of 103
        q104.id = 104; q104.subject_id = 1; q104.unit_id = 11; q104.bloom_level_id = 1; q104.question_text = "Find the volume of a solid cylinder of radius 8 cm and height 12 cm."; q104.marks = 3; q104.difficulty = "medium"; q104.question_type = "Short Answer"; q104.status = "approved"; q104.active = True; q104.source = "Bank"; q104.answer = ""; q104.explanation = ""

        mock_bloom = MagicMock()
        mock_bloom.id = 1
        mock_bloom.level_name = "Apply"

        from app.models.subject import Subject
        from app.models.unit import Unit
        from app.models.topic import Topic
        from app.models.question import Question
        from app.models.bloom import Bloom

        def query_side_effect(model):
            m = MagicMock()
            if model == Subject:
                m.filter.return_value.first.return_value = mock_subject
            elif model == Unit:
                m.filter.return_value.all.return_value = [mock_unit_coord, mock_unit_mens]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [q101, q102, q103, q104]
                m.filter.return_value.all.return_value = [q101, q102, q103, q104]
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        from app.services.question_generator import generate_question_paper
        res = generate_question_paper(
            db=mock_db,
            subject_id=1,
            selected_units=[10, 11],
            total_marks=3,
            bloom_distribution={"Apply": 100},
            source_mode="bank",
            use_ai=False,
        )

        selected = res["questions"]
        self.assertEqual(len(selected), 1, "Only the 1 valid non-duplicate bank question must be selected.")
        self.assertEqual(selected[0]["question_id"], 103)
        self.assertEqual(selected[0]["question"], "Find the volume of a solid cylinder of radius 5 cm and height 10 cm.")
        self.assertNotIn("(Variation 49)", selected[0]["question"])

    def test_hybrid_mode_bank_filtering_with_ai_fallback(self):
        """TEST 15: In hybrid mode, invalid bank questions are filtered and the resulting shortage is synthesized by AI."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 10"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_coord = MagicMock()
        mock_unit_coord.id = 10
        mock_unit_coord.unit_name = "Unit 5 - Coordinate Geometry"
        mock_unit_coord.description = "Cartesian plane calculations"

        q201 = MagicMock()  # Bad bank question
        q201.id = 201; q201.subject_id = 1; q201.unit_id = 10; q201.bloom_level_id = 1; q201.question_text = "Solve x² + 5x + 6 = 0 using quadratic formula."; q201.marks = 3; q201.difficulty = "medium"; q201.question_type = "Short Answer"; q201.status = "approved"; q201.active = True; q201.source = "Bank"; q201.answer = ""; q201.explanation = ""

        mock_bloom = MagicMock()
        mock_bloom.id = 1
        mock_bloom.level_name = "Apply"

        from app.models.subject import Subject
        from app.models.unit import Unit
        from app.models.topic import Topic
        from app.models.question import Question
        from app.models.bloom import Bloom

        def query_side_effect(model):
            m = MagicMock()
            if model == Subject:
                m.filter.return_value.first.return_value = mock_subject
            elif model == Unit:
                m.filter.return_value.all.return_value = [mock_unit_coord]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [q201]
                m.filter.return_value.all.return_value = [q201]
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        mock_ai_gen = MagicMock()
        mock_ai_gen.generate_question.side_effect = [
            # Invalid candidate for Coordinate Geometry
            GeneratedQuestionResult(
                question_text="Solve 2x² - 5x + 2 = 0 using quadratic formula.",
                answer="x=2",
                explanation="",
                question_type="Numerical",
                marks=3,
                difficulty="medium",
                bloom="Apply",
                unit_name="Unit 5 - Coordinate Geometry"
            ),
            # Valid candidate for Coordinate Geometry
            GeneratedQuestionResult(
                question_text="Find the distance between the points A(2, 3) and B(5, 7) in the coordinate plane.",
                answer="5 units",
                explanation="",
                question_type="Numerical",
                marks=3,
                difficulty="medium",
                bloom="Apply",
                unit_name="Unit 5 - Coordinate Geometry"
            )
        ]

        with patch("app.services.question_generator.get_ai_generator", return_value=mock_ai_gen):
            from app.services.question_generator import generate_question_paper
            res = generate_question_paper(
                db=mock_db,
                subject_id=1,
                selected_units=[10],
                total_marks=3,
                bloom_distribution={"Apply": 100},
                source_mode="hybrid",
            )

        selected = res["questions"]
        self.assertEqual(len(selected), 1)
        self.assertIn("distance between the points", selected[0]["question"])
        self.assertNotIn("quadratic formula", selected[0]["question"])


if __name__ == "__main__":
    unittest.main()
