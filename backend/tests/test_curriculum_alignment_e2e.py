"""
test_curriculum_alignment_e2e.py
Comprehensive regression tests for curriculum alignment, board-class isolation,
Bloom's taxonomy validation, subject-specific question formats, and examination blueprints.
"""

import unittest
from unittest.mock import MagicMock, patch

from app.services.ai.base import AIQuestionPrompt
from app.services.ai.generator_factory import OfflineFallbackProvider
from app.services.bloom_service import infer_bloom_level, validate_bloom_level
from app.services.exam_blueprints import (
    OFFICIAL_BLUEPRINTS,
    get_exam_blueprint,
    build_custom_paper_blueprint,
)


class TestCurriculumAlignmentE2E(unittest.TestCase):
    """Authoritative test suite covering all requirements in Section 10 of the specification."""

    def setUp(self):
        self.provider = OfflineFallbackProvider()

    # =========================================================================
    # 1. TNSB CLASS 10 ENGLISH
    # =========================================================================
    def test_tnsb_class_10_english_prose(self):
        """TNSB Class 10 English: Questions must use verified prose topics (e.g. His First Flight, The Attic)."""
        prompt = AIQuestionPrompt(
            board="TNSB",
            class_name="Class 10",
            subject_name="English",
            unit_name="Unit 1 - Prose",
            topic_name="His First Flight",
            marks=3,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        self.assertNotIn("operational models", res.question_text.lower())
        self.assertNotIn("foundational principles and historical evolution", res.question_text.lower())
        # Verify genuine literary question
        valid_keywords = ["seagull", "aditya", "attic", "flight", "ghost", "parents"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_keywords))

    def test_tnsb_class_10_english_poetry(self):
        """TNSB Class 10 English: Questions must use verified poetry topics (e.g. Life, Secret of the Machines)."""
        prompt = AIQuestionPrompt(
            board="TNSB",
            class_name="Class 10",
            subject_name="English",
            unit_name="Unit 1 - Poem",
            topic_name="Life",
            marks=3,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        self.assertNotIn("standard domain frameworks", res.question_text.lower())
        valid_keywords = ["poem", "poet", "life", "machine", "courage", "van dyke", "kipling"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_keywords))

    def test_tnsb_class_10_english_grammar(self):
        """TNSB Class 10 English: Questions must use prescribed grammar concepts."""
        prompt = AIQuestionPrompt(
            board="TNSB",
            class_name="Class 10",
            subject_name="English",
            unit_name="Unit 3 - Grammar",
            topic_name="Reported Speech",
            marks=2,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_grammar = ["reported speech", "voice", "passive", "sentence", "modal", "error"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_grammar))

    # =========================================================================
    # 2. TNSB CLASS 10 SOCIAL SCIENCE
    # =========================================================================
    def test_tnsb_class_10_social_science_history(self):
        """TNSB Class 10 Social Science: Questions must use verified TN/National history (e.g. VOC, League of Nations)."""
        prompt = AIQuestionPrompt(
            board="TNSB",
            class_name="Class 10",
            subject_name="Social Science",
            unit_name="Unit 1 - History",
            topic_name="Outbreak of World War I",
            marks=3,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["league of nations", "chidambaram", "swadeshi", "vallalar", "war", "revolt"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    def test_tnsb_class_10_social_science_map(self):
        """TNSB Class 10 Social Science: Must generate map-based questions for geographic features."""
        prompt = AIQuestionPrompt(
            board="TNSB",
            class_name="Class 10",
            subject_name="Social Science",
            unit_name="Unit 2 - Geography",
            topic_name="Physical Geography of Tamil Nadu",
            marks=2,
            difficulty="easy",
            bloom_level="Remember",
            question_type="Map-based",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        self.assertTrue("map" in res.question_text.lower() or "soil" in res.question_text.lower() or "port" in res.question_text.lower())

    # =========================================================================
    # 3. CBSE CLASS 10 ENGLISH LANGUAGE AND LITERATURE
    # =========================================================================
    def test_cbse_class_10_english_literature(self):
        """CBSE Class 10 English: Prescribed textbook lessons (e.g. Lencho, Mandela, Buddha)."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="English Language and Literature",
            unit_name="Unit 1 - First Flight (Prose)",
            topic_name="A Letter to God",
            marks=3,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["lencho", "mandela", "buddha", "kisa gotami", "post office"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    def test_cbse_class_10_english_writing(self):
        """CBSE Class 10 English: Official writing formats (Formal Letter / Analytical Paragraph)."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 10",
            subject_name="English Language and Literature",
            unit_name="Unit 2 - Creative Writing Skills",
            topic_name="Formal Letter",
            marks=5,
            difficulty="medium",
            bloom_level="Create",
            question_type="Long Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        self.assertTrue("letter" in res.question_text.lower() or "analytical paragraph" in res.question_text.lower())

    # =========================================================================
    # 4. CBSE CLASS 12 ENGLISH CORE
    # =========================================================================
    def test_cbse_class_12_english_core_prose(self):
        """CBSE Class 12 English: Flamingo lessons (The Last Lesson, Lost Spring, The Rattrap)."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="English Core",
            unit_name="Unit 1 - Flamingo (Prose)",
            topic_name="The Last Lesson",
            marks=3,
            difficulty="medium",
            bloom_level="Analyze",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["franz", "m. hamel", "saheb", "mukesh", "rattrap", "edla", "alsace"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    def test_cbse_class_12_english_core_poetry(self):
        """CBSE Class 12 English: Prescribed poems (My Mother at Sixty-Six, Keeping Quiet, Aunt Jennifer)."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="English Core",
            unit_name="Unit 2 - Flamingo (Poetry)",
            topic_name="My Mother at Sixty-Six",
            marks=3,
            difficulty="medium",
            bloom_level="Analyze",
            question_type="Short Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["mother", "kamala das", "neruda", "silence", "tigers", "aunt jennifer"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    # =========================================================================
    # 5. CLASS 12 SCIENCE & COMMERCE
    # =========================================================================
    def test_class_12_biology(self):
        """Class 12 Biology: Biological processes, genetics, biotechnology."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="Biology",
            unit_name="Unit 2 - Genetics and Evolution",
            topic_name="Molecular Basis of Inheritance",
            marks=5,
            difficulty="hard",
            bloom_level="Analyze",
            question_type="Long Answer",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["operon", "dna", "pcr", "taq", "lac", "gene"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    def test_class_12_economics(self):
        """Class 12 Economics: National income, fiscal policy, money creation."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="Economics",
            unit_name="Unit 1 - National Income and Related Aggregates",
            topic_name="GDP Calculation",
            marks=4,
            difficulty="medium",
            bloom_level="Apply",
            question_type="Numerical",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["gnp", "gdp", "national income", "multiplier", "aggregate"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    def test_class_12_accountancy(self):
        """Class 12 Accountancy: Accounting entries, share capital, cash flow."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="Accountancy",
            unit_name="Unit 1 - Accounting for Share Capital",
            topic_name="Forfeiture of Shares",
            marks=4,
            difficulty="hard",
            bloom_level="Apply",
            question_type="Numerical",
        )
        res = self.provider.generate_question(prompt)
        self.assertIsNotNone(res)
        valid_terms = ["journal", "share capital", "forfeiture", "cash flow", "debentures"]
        self.assertTrue(any(kw in res.question_text.lower() for kw in valid_terms))

    # =========================================================================
    # 6. BLOOM'S TAXONOMY VALIDATION AND MISMATCH REJECTION
    # =========================================================================
    def test_blooms_remember_rejects_critical_evaluation(self):
        """Remember must REJECT high-order critical evaluation and case studies."""
        high_order_q = "Critically evaluate the geopolitical ramifications of the Treaty of Versailles and formulate a policy alternative."
        is_valid, inferred, reason = validate_bloom_level(high_order_q, "Remember")
        self.assertFalse(is_valid, "Remember must reject critical evaluation.")
        self.assertIn("severely exceeds target Remember", reason)

    def test_blooms_evaluate_rejects_simple_recall(self):
        """Evaluate must REJECT simple one-word naming or definition recall."""
        recall_q = "Name the capital of Tamil Nadu."
        is_valid, inferred, reason = validate_bloom_level(recall_q, "Evaluate")
        self.assertFalse(is_valid, "Evaluate must reject basic factual recall.")

    def test_blooms_exact_cognitive_level_matches(self):
        """Verify accurate categorization across all 6 cognitive levels."""
        self.assertEqual(infer_bloom_level("Define photosynthesis and state its chemical formula."), "Remember")
        self.assertEqual(infer_bloom_level("Explain the double circulation process in humans with a diagram."), "Understand")
        self.assertEqual(infer_bloom_level("Calculate the molar mass and solve for the number of moles."), "Apply")
        self.assertEqual(infer_bloom_level("Analyze the causes that led to the collapse of the Roman Empire."), "Analyze")
        self.assertEqual(infer_bloom_level("Critically evaluate the effectiveness of the Monetary Policy."), "Evaluate")
        self.assertEqual(infer_bloom_level("Write a formal letter to the Municipal Commissioner proposing solutions."), "Create")

    # =========================================================================
    # 7. EXAMINATION BLUEPRINTS
    # =========================================================================
    def test_cbse_class_10_mathematics_blueprint(self):
        """CBSE Class 10 Math blueprint carries 80 marks, 180 minutes, 5 sections."""
        bp = get_exam_blueprint(board_code="CBSE", class_number=10, subject_code="041")
        self.assertIsNotNone(bp)
        self.assertEqual(bp.total_marks, 80)
        self.assertEqual(bp.duration_minutes, 180)
        self.assertEqual(len(bp.sections), 5)
        self.assertTrue(bp.validate_totals())

    def test_tnsb_class_10_english_blueprint(self):
        """TNSB Class 10 English blueprint carries 100 marks, 180 minutes."""
        bp = get_exam_blueprint(board_code="TNSB", class_number=10, subject_name="English")
        self.assertIsNotNone(bp)
        self.assertEqual(bp.total_marks, 100)
        self.assertEqual(bp.duration_minutes, 180)
        self.assertTrue(bp.validate_totals())

    def test_custom_paper_blueprint_computation(self):
        """Custom total marks (e.g. 50 marks) dynamically calculates duration and balanced sections."""
        custom_bp = build_custom_paper_blueprint(
            board_code="CBSE",
            class_name="Class 10",
            subject_name="Science",
            total_marks=50,
        )
        self.assertIsNotNone(custom_bp)
        self.assertEqual(custom_bp.total_marks, 50)
        self.assertTrue(custom_bp.duration_minutes > 0)
        self.assertEqual(sum(s.total_marks for s in custom_bp.sections), 50)


if __name__ == "__main__":
    unittest.main()
