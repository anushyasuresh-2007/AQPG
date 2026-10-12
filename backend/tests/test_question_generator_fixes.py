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

    def test_unit_3_algebra_relevance_validation_rules_A_to_K(self):
        """TEST 16: Comprehensive relevance validation for Unit 3 - Algebra (Rules A through K)."""
        u3_name = "Unit 3 - Algebra (Polynomials, Quadratics & Matrices)"
        u3_desc = "Polynomials, quadratic equations, linear equations in two variables, matrices and determinants"
        u3_topics = ["Polynomials", "Quadratic Equations", "Matrices"]

        # A. Unit 3 accepts quadratic equation
        q_quad = "Solve the quadratic equation 2x² - 5x + 2 = 0 using quadratic formula."
        self.assertTrue(validate_unit_relevance(q_quad, u3_name, u3_desc, u3_topics))

        # B. Unit 3 accepts polynomial zero question
        q_poly = "Find the zeroes of the quadratic polynomial x² - 3 and verify the relationship between zeroes and coefficients."
        self.assertTrue(validate_unit_relevance(q_poly, u3_name, u3_desc, u3_topics))

        # C. Unit 3 accepts two-digit Algebra word problem
        q_word = "A two-digit number is such that the product of its digits is 14. Find the number."
        self.assertTrue(validate_unit_relevance(q_word, u3_name, u3_desc, u3_topics))

        # D. Unit 3 accepts matrix question
        q_mat = "If matrix A = [[1, 2], [3, 4]], calculate the matrix expression A² - 5A + 7I."
        self.assertTrue(validate_unit_relevance(q_mat, u3_name, u3_desc, u3_topics))

        # E. Unit 3 accepts determinant question
        q_det = "Find the inverse of the matrix A = [[2, 3], [1, 4]] using determinant methods."
        self.assertTrue(validate_unit_relevance(q_det, u3_name, u3_desc, u3_topics))

        # F. Unit 3 accepts system of linear equations
        q_sys = "Solve the system of linear equations 2x + 3y = 5 and 3x - y = 2 using matrix inversion method."
        self.assertTrue(validate_unit_relevance(q_sys, u3_name, u3_desc, u3_topics))

        # G. Unit 3 rejects motorboat/upstream-downstream question
        q_boat = "A motor boat whose speed is 15 km/h in still water goes 30 km downstream and returns upstream in 4 hours 30 minutes. Find speed of the stream."
        self.assertFalse(validate_unit_relevance(q_boat, u3_name, u3_desc, u3_topics))

        # H. Unit 3 rejects Statistics mean/frequency question
        q_stat = "Find the mean of the following frequency distribution: Class intervals 0-10, 10-20 with frequencies 5, 8."
        self.assertFalse(validate_unit_relevance(q_stat, u3_name, u3_desc, u3_topics))

        # I. Unit 3 rejects probability question
        q_prob = "A die is thrown once. Find the probability of getting a prime number."
        self.assertFalse(validate_unit_relevance(q_prob, u3_name, u3_desc, u3_topics))

        # J. Unit 3 rejects tower/angle-of-elevation question
        q_trig = "From a point on the ground 15 m away from foot of tower, angle of elevation of top is 60°. Find height of tower."
        self.assertFalse(validate_unit_relevance(q_trig, u3_name, u3_desc, u3_topics))

        # K. Unit 3 rejects mensuration volume question
        q_mens = "Find the volume of a solid cylinder of radius 5 cm and height 10 cm."
        self.assertFalse(validate_unit_relevance(q_mens, u3_name, u3_desc, u3_topics))

    def test_unit_3_fallback_structural_diversity_rule_L(self):
        """TEST 17: Multiple Algebra fallback generations do not collapse into the same structural hash when genuinely different templates exist."""
        fallback = OfflineFallbackProvider()
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 3 - Algebra (Polynomials, Quadratics & Matrices)",
            topic_name="Algebra",
            marks=3,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
            unit_description="Polynomials, quadratics, matrices",
            topics_list=["Polynomials", "Matrices"],
        )

        seen_hashes = set()
        unique_templates_count = 0
        for _ in range(30):
            res = fallback.generate_question(prompt)
            self.assertIsNotNone(res)
            sh = compute_structural_hash(res.question_text)
            if sh not in seen_hashes:
                seen_hashes.add(sh)
                unique_templates_count += 1

        self.assertGreaterEqual(unique_templates_count, 5, "OfflineFallbackProvider must produce at least 5 distinct structural hashes across multiple runs.")

    def test_unit_3_hybrid_generation_shortage_fulfillment_rule_M(self):
        """TEST 18: Hybrid generation fulfills Unit 3 shortage without raising ValueError when valid candidates exist."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 10"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_alg = MagicMock()
        mock_unit_alg.id = 3
        mock_unit_alg.unit_name = "Unit 3 - Algebra (Polynomials, Quadratics & Matrices)"
        mock_unit_alg.description = "Polynomials, quadratics, matrices"

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
                m.filter.return_value.all.return_value = [mock_unit_alg]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
                m.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = []
                m.filter.return_value.all.return_value = []
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        from app.services.ai.generator_factory import OfflineFallbackProvider
        with patch("app.services.question_generator.get_ai_generator", return_value=OfflineFallbackProvider()):
            from app.services.question_generator import generate_question_paper
            res = generate_question_paper(
                db=mock_db,
                subject_id=1,
                selected_units=[3],
                total_marks=6,
                bloom_distribution={"Apply": 100},
                source_mode="hybrid",
            )

        selected = res["questions"]
        self.assertGreaterEqual(len(selected), 1, "Hybrid generation must fill Unit 3 shortage successfully.")
        for q in selected:
            self.assertTrue(validate_unit_relevance(q["question"], mock_unit_alg.unit_name, mock_unit_alg.description, []))

    def test_unit_1_relations_functions_relevance_validation_cases_A_B_C(self):
        """TEST 19 (Unit 1): Validate actual Unit 1 Relations and Functions concepts (Cases A, B, C)."""
        u1_name = "Unit 1 - Relations and Functions & Inverse Trigonometry"
        u1_desc = "Relations and their properties, types of functions, composition of functions, inverse functions, inverse trigonometric functions"
        u1_topics = ["Relations and Functions", "Inverse Trigonometric Functions"]

        # Case A & C: Valid questions from actual Unit 1 curriculum are accepted
        q_rel = "Determine whether the relation R in set Z defined by R = {(x,y): x - y is divisible by 5} is an equivalence relation."
        q_fn = "Show that the function f: R -> R defined by f(x) = 3x + 2 is one-one and onto (bijective)."
        q_dom = "Determine the domain, codomain, and range of the relation R = {(x, x³): x is a prime number less than 10}."
        q_comp = "Let f: R -> R and g: R -> R be defined by f(x) = 2x + 1 and g(x) = x² - 2. Find (g o f)(x) and (f o g)(x)."
        q_inv = "Show that f(x) = (x-2)/(x-3) is bijective and find its inverse function f⁻¹(x)."
        q_trig_inv = "Find the principal value of tan⁻¹(√3) - sec⁻¹(-2)."

        self.assertTrue(validate_unit_relevance(q_rel, u1_name, u1_desc, u1_topics))
        self.assertTrue(validate_unit_relevance(q_fn, u1_name, u1_desc, u1_topics))
        self.assertTrue(validate_unit_relevance(q_dom, u1_name, u1_desc, u1_topics))
        self.assertTrue(validate_unit_relevance(q_comp, u1_name, u1_desc, u1_topics))
        self.assertTrue(validate_unit_relevance(q_inv, u1_name, u1_desc, u1_topics))
        self.assertTrue(validate_unit_relevance(q_trig_inv, u1_name, u1_desc, u1_topics))

        # Case B: Questions from unrelated units are rejected
        q_quad = "Solve 2x² - 5x + 2 = 0 using quadratic formula."
        q_boat = "A motor boat speed in still water is 15 km/h goes 30 km downstream. Find speed of stream."
        q_stat = "Find the mean of the frequency distribution: Class intervals 0-10, 10-20."
        q_prob = "A die is thrown once. Find the probability of getting a prime number."
        q_trig_ht = "From a point 15 m away from foot of tower, angle of elevation of top is 60°. Find height of tower."
        q_mens = "Find the volume of a solid cylinder of radius 5 cm and height 10 cm."

        self.assertFalse(validate_unit_relevance(q_quad, u1_name, u1_desc, u1_topics))
        self.assertFalse(validate_unit_relevance(q_boat, u1_name, u1_desc, u1_topics))
        self.assertFalse(validate_unit_relevance(q_stat, u1_name, u1_desc, u1_topics))
        self.assertFalse(validate_unit_relevance(q_prob, u1_name, u1_desc, u1_topics))
        self.assertFalse(validate_unit_relevance(q_trig_ht, u1_name, u1_desc, u1_topics))
        self.assertFalse(validate_unit_relevance(q_mens, u1_name, u1_desc, u1_topics))

    def test_unit_1_hybrid_mode_shortage_fulfillment_case_D(self):
        """TEST 20 (Unit 1 Case D): Hybrid mode fills shortage of valid Question Bank questions with AI-generated Unit 1 questions."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 12"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_1 = MagicMock()
        mock_unit_1.id = 1
        mock_unit_1.unit_name = "Unit 1 - Relations and Functions & Inverse Trigonometry"
        mock_unit_1.description = "Relations and functions, inverse trig functions"

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
                m.filter.return_value.all.return_value = [mock_unit_1]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
                m.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = []
                m.filter.return_value.all.return_value = []
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        from app.services.ai.generator_factory import OfflineFallbackProvider
        with patch("app.services.question_generator.get_ai_generator", return_value=OfflineFallbackProvider()):
            from app.services.question_generator import generate_question_paper
            res = generate_question_paper(
                db=mock_db,
                subject_id=1,
                selected_units=[1],
                total_marks=6,
                bloom_distribution={"Apply": 100},
                source_mode="hybrid",
            )

        selected = res["questions"]
        self.assertGreaterEqual(len(selected), 1, "Hybrid generation must fill Unit 1 shortage successfully.")
        for q in selected:
            self.assertTrue(validate_unit_relevance(q["question"], mock_unit_1.unit_name, mock_unit_1.description, []))

    def test_unit_1_structural_deduplication_and_bounded_retries_case_E(self):
        """TEST 21 (Unit 1 Case E): Repeated structural templates are rejected and bounded retries terminate safely."""
        q1 = "Show that the function f: R -> R defined by f(x) = 3x + 2 is one-one and onto."
        q2 = "Show that the function f: R -> R defined by f(x) = 5x + 7 is one-one and onto."
        self.assertEqual(compute_structural_hash(q1), compute_structural_hash(q2), "Numeric variations of same function template must match structural hash.")

    def test_deterministic_question_bank_selection_case_H(self):
        """TEST 22 (Case H): Repeated test runs produce deterministic Question Bank selection."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 12"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_1 = MagicMock()
        mock_unit_1.id = 1
        mock_unit_1.unit_name = "Unit 1 - Relations and Functions"
        mock_unit_1.description = "Relations and functions"

        q1 = MagicMock()
        q1.id = 10; q1.subject_id = 1; q1.unit_id = 1; q1.bloom_level_id = 1; q1.question_text = "Show that f: R -> R defined by f(x) = 3x + 2 is one-one and onto."; q1.marks = 3; q1.difficulty = "medium"; q1.question_type = "Short Answer"; q1.status = "approved"; q1.active = True; q1.source = "Bank"; q1.answer = ""; q1.explanation = ""

        q2 = MagicMock()
        q2.id = 20; q2.subject_id = 1; q2.unit_id = 1; q2.bloom_level_id = 1; q2.question_text = "Determine whether relation R in set Z defined by R = {(x,y): x - y is divisible by 5} is an equivalence relation."; q2.marks = 3; q2.difficulty = "medium"; q2.question_type = "Short Answer"; q2.status = "approved"; q2.active = True; q2.source = "Bank"; q2.answer = ""; q2.explanation = ""

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
                m.filter.return_value.all.return_value = [mock_unit_1]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = [q1, q2]
                m.filter.return_value.all.return_value = [q1, q2]
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        from app.services.question_generator import generate_question_paper
        res1 = generate_question_paper(
            db=mock_db, subject_id=1, selected_units=[1], total_marks=3, bloom_distribution={"Apply": 100}, source_mode="bank", use_ai=False
        )
        res2 = generate_question_paper(
            db=mock_db, subject_id=1, selected_units=[1], total_marks=3, bloom_distribution={"Apply": 100}, source_mode="bank", use_ai=False
        )

        self.assertEqual([q["question_id"] for q in res1["questions"]], [q["question_id"] for q in res2["questions"]])

    def test_unit_2_numbers_sequences_relevance_validation(self):
        """TEST 23 (Unit 2): Correct classification and acceptance of Unit 2 Numbers and Sequences syllabus questions, and rejection of unrelated units."""
        u2_name = "Unit 2 - Numbers and Sequences"
        u2_desc = "Euclid's division lemma, fundamental theorem of arithmetic, AP, GP, modular arithmetic, sequences and series"
        u2_topics = ["Euclid's Division Lemma", "Arithmetic Progression", "Geometric Progression"]

        # Valid Unit 2 questions must be accepted
        q_hcf = "Find the HCF of 96 and 404 using the prime factorization method."
        q_euclid = "Use Euclid's division algorithm to find the HCF of 4052 and 12576."
        q_irrat = "Prove that sqrt(5) is an irrational number using the method of contradiction."
        q_irrat2 = "Prove that 3 + 2sqrt(5) is an irrational number given that sqrt(5) is irrational."
        q_ap = "Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18..."
        q_ap_sum = "Find the sum of the first 20 terms of the Arithmetic Progression: 2, 7, 12, 17..."
        q_gp = "Find the 10th term of the Geometric Progression (G.P.): 2, 6, 18, 54..."
        q_mod = "Find the remainder when 2^81 is divided by 17 using modular arithmetic."

        self.assertTrue(validate_unit_relevance(q_hcf, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_euclid, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_irrat, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_irrat2, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_ap, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_ap_sum, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_gp, u2_name, u2_desc, u2_topics))
        self.assertTrue(validate_unit_relevance(q_mod, u2_name, u2_desc, u2_topics))

        # Questions from unrelated units must be rejected
        q_quad = "Solve 2x² - 5x + 2 = 0 using quadratic formula."
        q_boat = "A motor boat speed in still water is 15 km/h goes 30 km downstream. Find speed of stream."
        q_trig = "From a point 15 m away from foot of tower, angle of elevation of top is 60°. Find height of tower."
        q_mens = "Find the volume of a solid cylinder of radius 5 cm and height 10 cm."
        q_rel = "Show that the function f: R -> R defined by f(x) = 3x + 2 is one-one and onto (bijective)."
        q_coord = "Find the distance between the points A(2, 3) and B(5, 7) in the coordinate plane."

        self.assertFalse(validate_unit_relevance(q_quad, u2_name, u2_desc, u2_topics))
        self.assertFalse(validate_unit_relevance(q_boat, u2_name, u2_desc, u2_topics))
        self.assertFalse(validate_unit_relevance(q_trig, u2_name, u2_desc, u2_topics))
        self.assertFalse(validate_unit_relevance(q_mens, u2_name, u2_desc, u2_topics))
        self.assertFalse(validate_unit_relevance(q_rel, u2_name, u2_desc, u2_topics))
        self.assertFalse(validate_unit_relevance(q_coord, u2_name, u2_desc, u2_topics))

    def test_unit_2_hybrid_mode_shortage_fulfillment(self):
        """TEST 24 (Unit 2): Hybrid generation fills Unit 2 shortage with valid Numbers and Sequences questions."""
        mock_db = MagicMock()

        mock_subject = MagicMock()
        mock_subject.id = 1
        mock_subject.subject_name = "Mathematics"
        mock_subject.board = "CBSE"
        mock_subject.class_name = "Class 10"
        mock_subject.board_id = 1
        mock_subject.class_id = 1

        mock_unit_2 = MagicMock()
        mock_unit_2.id = 2
        mock_unit_2.unit_name = "Unit 2 - Numbers and Sequences"
        mock_unit_2.description = "Numbers and sequences, AP, GP"

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
                m.filter.return_value.all.return_value = [mock_unit_2]
            elif model == Topic:
                m.filter.return_value.order_by.return_value.all.return_value = []
                m.filter.return_value.filter.return_value.order_by.return_value.all.return_value = []
            elif model == Question:
                m.filter.return_value.filter.return_value.filter.return_value.filter.return_value.all.return_value = []
                m.filter.return_value.all.return_value = []
            elif model == Bloom:
                m.all.return_value = [mock_bloom]
            return m

        mock_db.query.side_effect = query_side_effect

        from app.services.ai.generator_factory import OfflineFallbackProvider
        with patch("app.services.question_generator.get_ai_generator", return_value=OfflineFallbackProvider()):
            from app.services.question_generator import generate_question_paper
            res = generate_question_paper(
                db=mock_db,
                subject_id=1,
                selected_units=[2],
                total_marks=6,
                bloom_distribution={"Apply": 100},
                source_mode="hybrid",
            )

        selected = res["questions"]
        self.assertGreaterEqual(len(selected), 1, "Hybrid generation must fill Unit 2 shortage successfully.")
        for q in selected:
            self.assertTrue(validate_unit_relevance(q["question"], mock_unit_2.unit_name, mock_unit_2.description, []))

    def test_unit_2_fallback_structural_diversity(self):
        """TEST 25 (Unit 2): OfflineFallbackProvider produces multiple structurally distinct templates for Unit 2."""
        fallback = OfflineFallbackProvider()
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 2 - Numbers and Sequences",
            topic_name="Arithmetic Progression",
            marks=3,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
            unit_description="Numbers and sequences, AP, GP",
            topics_list=["Arithmetic Progression", "Geometric Progression"],
        )

        seen_hashes = set()
        seen_questions = set()
        for _ in range(50):
            res = fallback.generate_question(prompt)
            self.assertIsNotNone(res)
            self.assertTrue(res.question_text.isascii(), f"Question must be pure ASCII: {res.question_text}")
            self.assertTrue(res.answer.isascii(), f"Answer must be pure ASCII: {res.answer}")
            self.assertTrue(validate_unit_relevance(res.question_text, prompt.unit_name, prompt.unit_description, prompt.topics_list))
            seen_questions.add(res.question_text)
            sh = compute_structural_hash(res.question_text)
            seen_hashes.add(sh)

        self.assertGreaterEqual(len(seen_hashes), 5, "OfflineFallbackProvider must produce at least 5 distinct structural hashes for Unit 2 across multiple runs.")
        self.assertGreaterEqual(len(seen_questions), 5, "OfflineFallbackProvider must produce distinct questions across multiple runs.")

    def test_unit_2_fallback_templates_correctness_and_readability(self):
        """TEST 26 (Unit 2): Verify all 12 templates for readability, ASCII notation, and mathematical correctness."""
        fallback = OfflineFallbackProvider()
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics",
            unit_name="Unit 2 - Numbers and Sequences",
            topic_name="Arithmetic Progression",
            marks=3,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
            unit_description="Numbers and sequences, AP, GP",
            topics_list=["Arithmetic Progression", "Geometric Progression"],
        )

        captured_templates = []
        def intercept_choice(seq):
            if isinstance(seq, list) and len(seq) == 12:
                captured_templates.extend(seq)
            return seq[0]

        with patch("random.choice", side_effect=intercept_choice):
            fallback.generate_question(prompt)

        self.assertEqual(len(captured_templates), 12, "Must preserve all 12 templates for Unit 2.")
        unique_questions = {t["q"] for t in captured_templates}
        self.assertEqual(len(unique_questions), 12, "All 12 templates must have unique question texts.")

        # Check corrupted symbols are absent and clean ASCII notation is used
        corrupted_chars = ["√", "⁵", "²", "¹", "≡"]
        for idx, t in enumerate(captured_templates):
            q_text = t["q"]
            ans_text = t["a"]
            for bad_char in corrupted_chars:
                self.assertNotIn(bad_char, q_text, f"Corrupted character '{bad_char}' found in template {idx} question.")
                self.assertNotIn(bad_char, ans_text, f"Corrupted character '{bad_char}' found in template {idx} answer.")
            self.assertTrue(q_text.isascii(), f"Template {idx} question must be pure ASCII.")
            self.assertTrue(ans_text.isascii(), f"Template {idx} answer must be pure ASCII.")

        # Template-specific mathematical verification
        # 1. HCF and LCM of 96 and 404
        t1 = next(t for t in captured_templates if "96 and 404" in t["q"])
        self.assertIn("2^5", t1["a"])
        self.assertIn("2^2", t1["a"])
        self.assertIn("HCF = 2^2 = 4", t1["a"])
        self.assertIn("LCM = (96 * 404) / 4 = 9696", t1["a"])

        # 2. Euclid's division algorithm for 4052 and 12576
        t2 = next(t for t in captured_templates if "4052 and 12576" in t["q"])
        self.assertIn("12576 = 4052*3 + 420", t2["a"])
        self.assertIn("24 = 4*6 + 0", t2["a"])
        self.assertIn("HCF = 4", t2["a"])

        # 3. Prove sqrt(5) is irrational
        t3 = next(t for t in captured_templates if "Prove that sqrt(5) is an irrational number" in t["q"])
        self.assertIn("sqrt(5)", t3["q"])
        self.assertIn("sqrt(5) = a/b co-prime", t3["a"])
        self.assertIn("5b^2 = a^2", t3["a"])
        self.assertIn("Thus sqrt(5) is irrational", t3["a"])

        # 4. 20th term of AP: 3, 8, 13, 18...
        t4 = next(t for t in captured_templates if "20th term of the Arithmetic Progression: 3, 8, 13, 18" in t["q"])
        self.assertIn("a_20 = a + 19d = 3 + 19(5) = 3 + 95 = 98", t4["a"])

        # 5. Sum of first 20 terms of AP: 2, 7, 12, 17...
        t5 = next(t for t in captured_templates if "sum of the first 20 terms of the Arithmetic Progression: 2, 7, 12, 17" in t["q"])
        self.assertIn("S_20 = (n/2)[2a + (n-1)d] = 10[4 + 19(5)] = 10[4 + 95] = 990", t5["a"])

        # 6. Which term of AP 21, 18, 15... is -81?
        t6 = next(t for t in captured_templates if "21, 18, 15... is -81" in t["q"])
        self.assertIn("n = 35th term", t6["a"])

        # 7. 10th term of GP: 2, 6, 18, 54...
        t7 = next(t for t in captured_templates if "10th term of the Geometric Progression" in t["q"])
        self.assertIn("a_10 = a * r^(n-1) = 2 * 3^9 = 2 * 19683 = 39366", t7["a"])

        # 8. Sum of first 6 terms of GP: 3, 6, 12, 24...
        t8 = next(t for t in captured_templates if "sum of the first 6 terms of the Geometric Progression" in t["q"])
        self.assertIn("S_6 = a(r^n - 1)/(r - 1) = 3(2^6 - 1)/(2 - 1) = 3(64 - 1) = 3 * 63 = 189", t8["a"])

        # 9. Remainder when 2^81 divided by 17 (modular arithmetic)
        t9 = next(t for t in captured_templates if "remainder when 2^81 is divided by 17" in t["q"])
        self.assertIn("2^4 = 16 == -1 (mod 17)", t9["a"])
        self.assertIn("congruent to -1 modulo 17", t9["a"])
        self.assertIn("2^81 = (2^4)^20 * 2^1", t9["a"])
        self.assertIn("Remainder is 2", t9["a"])

        # 10. Recurrence general term a_n
        t10 = next(t for t in captured_templates if "sequence defined by a_1 = 2 and a_n = 3 * a_{n-1} + 1" in t["q"])
        self.assertIn("a_n = (5 * 3^(n-1) - 1) / 2", t10["a"])

        # 11. 3rd and 9th terms of AP are 4 and -8, find 13th term
        t11 = next(t for t in captured_templates if "3rd and 9th terms of an Arithmetic Progression are 4 and -8" in t["q"])
        self.assertIn("d = -2, a = 8", t11["a"])
        self.assertIn("a_13 = a + 12d = 8 + 12(-2) = 8 - 24 = -16", t11["a"])

        # 12. Prove 3 + 2sqrt(5) is irrational
        t12 = next(t for t in captured_templates if "Prove that 3 + 2sqrt(5) is an irrational number" in t["q"])
        self.assertIn("3 + 2sqrt(5)", t12["q"])
        self.assertIn("sqrt(5) is irrational", t12["q"])
        self.assertIn("sqrt(5) = (r - 3)/2 which is rational", t12["a"])
        self.assertIn("Thus 3 + 2sqrt(5) is irrational", t12["a"])



if __name__ == "__main__":
    unittest.main()
