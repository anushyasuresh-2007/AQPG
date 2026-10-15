"""
test_curriculum_alignment_e2e.py
Comprehensive regression tests for curriculum alignment, board-class isolation,
Bloom's taxonomy validation, subject-specific question formats, and examination blueprints.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

    # =========================================================================
    # 8. TNSB SUBJECT CODES & BACKWARD COMPATIBILITY
    # =========================================================================
    def test_tnsb_subject_code_resolution_official_and_legacy(self):
        """Verify resolve_tnsb_subject_code maps both official DGE codes and legacy aliases to canonical codes."""
        from app.services.curriculum.tn_board_importer import resolve_tnsb_subject_code

        # Class 12 Science & Mathematics: Official 500-series vs Shorthand vs Legacy Prefix
        test_cases = [
            ("519", 12, "519"), ("019", 12, "519"), ("TN-12-CS", 12, "519"),
            ("541", 12, "541"), ("041", 12, "541"), ("TN-12-MAT", 12, "541"),
            ("505", 12, "505"), ("005", 12, "505"), ("TN-12-PHY", 12, "505"),
            ("507", 12, "507"), ("007", 12, "507"), ("TN-12-CHEM", 12, "507"),
            ("509", 12, "509"), ("009", 12, "509"), ("TN-12-BIO", 12, "509"),
            ("549", 12, "549"), ("TN-12-ECO", 12, "549"),
            ("555", 12, "555"), ("TN-12-COM", 12, "555"),
            ("557", 12, "557"), ("TN-12-ACC", 12, "557"),
            ("003", 12, "003"), ("TN-12-ENG", 12, "003"),
            ("002", 10, "002"), ("TN-10-ENG", 10, "002"),
            ("003", 10, "003"), ("TN-10-MAT", 10, "003"),
            ("004", 10, "004"), ("TN-10-SCI", 10, "004"),
            ("005", 10, "005"), ("TN-10-SOC", 10, "005"),
        ]
        for input_code, c_num, expected_official in test_cases:
            resolved = resolve_tnsb_subject_code(input_code, class_number=c_num)
            self.assertEqual(
                resolved,
                expected_official,
                f"Expected '{input_code}' (Class {c_num}) to resolve to '{expected_official}', got '{resolved}'"
            )

    def test_tnsb_class_12_blueprint_resolution_official_and_legacy(self):
        """Verify get_exam_blueprint resolves blueprints for TNSB Class 12 across official DGE codes and legacy codes."""
        # Computer Science: official 519, shorthand 019, legacy TN-12-CS
        bp_cs_official = get_exam_blueprint("TNSB", 12, subject_code="519")
        bp_cs_short = get_exam_blueprint("TNSB", 12, subject_code="019")
        bp_cs_legacy = get_exam_blueprint("TNSB", 12, subject_code="TN-12-CS")
        self.assertIsNotNone(bp_cs_official)
        self.assertIsNotNone(bp_cs_short)
        self.assertIsNotNone(bp_cs_legacy)
        self.assertEqual(bp_cs_official.total_marks, 70)
        self.assertEqual(bp_cs_short.total_marks, 70)
        self.assertEqual(bp_cs_legacy.total_marks, 70)
        self.assertTrue(bp_cs_official.validate_totals())

        # Mathematics: official 541, shorthand 041, legacy TN-12-MAT
        bp_mat_official = get_exam_blueprint("TNSB", 12, subject_code="541")
        bp_mat_short = get_exam_blueprint("TNSB", 12, subject_code="041")
        bp_mat_legacy = get_exam_blueprint("TNSB", 12, subject_code="TN-12-MAT")
        self.assertIsNotNone(bp_mat_official)
        self.assertIsNotNone(bp_mat_short)
        self.assertIsNotNone(bp_mat_legacy)
        self.assertEqual(bp_mat_official.total_marks, 90)
        self.assertEqual(bp_mat_short.total_marks, 90)
        self.assertEqual(bp_mat_legacy.total_marks, 90)
        self.assertTrue(bp_mat_official.validate_totals())

        # Accountancy: official 557, legacy TN-12-ACC
        bp_acc_official = get_exam_blueprint("TNSB", 12, subject_code="557")
        bp_acc_legacy = get_exam_blueprint("TNSB", 12, subject_code="TN-12-ACC")
        self.assertIsNotNone(bp_acc_official)
        self.assertIsNotNone(bp_acc_legacy)
        self.assertEqual(bp_acc_official.total_marks, 90)
        self.assertTrue(bp_acc_official.validate_totals())

        # Physics: official 505, shorthand 005, legacy TN-12-PHY
        bp_phy_official = get_exam_blueprint("TNSB", 12, subject_code="505")
        bp_phy_short = get_exam_blueprint("TNSB", 12, subject_code="005")
        self.assertIsNotNone(bp_phy_official)
        self.assertIsNotNone(bp_phy_short)
        self.assertEqual(bp_phy_official.total_marks, 70)
        self.assertTrue(bp_phy_official.validate_totals())

    def test_tnsb_importer_official_dge_subject_codes(self):
        """Verify TamilNaduBoardImporter returns authoritative DGE subject codes."""
        from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter

        cat = TamilNaduBoardImporter().fetch_curriculum()
        code_map = {(s.class_number, s.subject_name): s.subject_code for s in cat.subjects}

        # Class 10 (SSLC) DGE codes
        self.assertEqual(code_map.get((10, "Science")), "004")
        self.assertEqual(code_map.get((10, "Mathematics")), "003")
        self.assertEqual(code_map.get((10, "Social Science")), "005")
        self.assertEqual(code_map.get((10, "English")), "002")

        # Class 12 (+2) DGE codes
        self.assertEqual(code_map.get((12, "Computer Science")), "519")
        self.assertEqual(code_map.get((12, "Mathematics")), "541")
        self.assertEqual(code_map.get((12, "Physics")), "505")
        self.assertEqual(code_map.get((12, "Chemistry")), "507")
        self.assertEqual(code_map.get((12, "Biology")), "509")
        self.assertEqual(code_map.get((12, "Economics")), "549")
        self.assertEqual(code_map.get((12, "Commerce")), "555")
        self.assertEqual(code_map.get((12, "Accountancy")), "557")
        self.assertEqual(code_map.get((12, "English")), "003")

    def test_ambiguous_and_conflicting_context_resolution(self):
        """Verify get_exam_blueprint and resolve_tnsb_subject_code reject ambiguous and conflicting contexts."""
        from app.services.curriculum.tn_board_importer import resolve_tnsb_subject_code
        from app.services.exam_blueprints import get_exam_blueprint

        # 1. Ambiguous code 003 without class or subject context must NOT default or resolve
        self.assertEqual(resolve_tnsb_subject_code("003", class_number=None, subject_name=None), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=None, subject_code="003"))

        # 2. Ambiguous code 005 without class or subject context must NOT default or resolve
        self.assertEqual(resolve_tnsb_subject_code("005", class_number=None, subject_name=None), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=None, subject_code="005"))

        # 3. Disambiguation when class is provided
        self.assertEqual(resolve_tnsb_subject_code("003", class_number=10), "003")
        self.assertEqual(resolve_tnsb_subject_code("003", class_number=12), "003")
        bp_10_003 = get_exam_blueprint("TNSB", class_number=10, subject_code="003")
        bp_12_003 = get_exam_blueprint("TNSB", class_number=12, subject_code="003")
        self.assertIsNotNone(bp_10_003)
        self.assertIsNotNone(bp_12_003)
        self.assertEqual(bp_10_003.subject_name, "Mathematics")
        self.assertEqual(bp_12_003.subject_name, "English")

        self.assertEqual(resolve_tnsb_subject_code("005", class_number=10), "005")
        self.assertEqual(resolve_tnsb_subject_code("005", class_number=12), "505")
        bp_10_005 = get_exam_blueprint("TNSB", class_number=10, subject_code="005")
        bp_12_005 = get_exam_blueprint("TNSB", class_number=12, subject_code="005")
        self.assertIsNotNone(bp_10_005)
        self.assertIsNotNone(bp_12_005)
        self.assertEqual(bp_10_005.subject_name, "Social Science")
        self.assertEqual(bp_12_005.subject_name, "Physics")

        # 4. Conflicting subject code and subject name must be rejected (return None / "")
        self.assertEqual(resolve_tnsb_subject_code("005", class_number=12, subject_name="Mathematics"), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=12, subject_code="005", subject_name="Mathematics"))

        self.assertEqual(resolve_tnsb_subject_code("505", class_number=12, subject_name="English"), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=12, subject_code="505", subject_name="English"))

        self.assertEqual(resolve_tnsb_subject_code("003", class_number=10, subject_name="English"), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=10, subject_code="003", subject_name="English"))

        self.assertEqual(resolve_tnsb_subject_code("003", class_number=12, subject_name="Mathematics"), "")
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=12, subject_code="003", subject_name="Mathematics"))

        # 5. Missing class with unambiguous code deduces class cleanly
        bp_519 = get_exam_blueprint("TNSB", class_number=None, subject_code="519")
        self.assertIsNotNone(bp_519)
        self.assertEqual(bp_519.class_number, 12)
        self.assertEqual(bp_519.subject_name, "Computer Science")

        # 6. Missing class with ambiguous subject name returns None
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=None, subject_name="Mathematics"))
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=None, subject_name="English"))

        # 7. Invalid code returns None
        self.assertIsNone(get_exam_blueprint("TNSB", class_number=12, subject_code="INVALID", subject_name="Astronomy"))


if __name__ == "__main__":
    unittest.main()

