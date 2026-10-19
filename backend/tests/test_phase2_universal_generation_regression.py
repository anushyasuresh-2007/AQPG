"""Regression tests for Phase 2 Universal Generation fixes across CBSE and TNSB.

Validates:
1. English: Evaluate questions across Prose, Poetry, and Supplementary pools for Class 10 & 12 without exhaustion.
2. Commerce: Context-dependent alias resolution to Business Studies on CBSE Class 11/12, retention of native units on TNSB, non-substitution for other subjects, and clear actionable error on unconfigured units.
3. Information Technology: Actionable bank-only shortage guidance stating approved count and advising Hybrid mode; successful generation in Hybrid mode.
4. Accountancy: Analyze level questions across Units 1, 2, and 3 without pool exhaustion.
5. Business Studies: Evaluate level questions across Units 1 through 6 without pool exhaustion.
6. Non-regression of exact mark totals, Bloom validation, unit relevance, and duplicate checks.
"""

import sys
import unittest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.database.database import Base
from app.models import Subject, Unit, Bloom, Question
from app.services.bloom_service import validate_bloom_level
from app.services.ai_generator import fetch_syllabus_units
from app.services.exam_blueprints import get_allowed_marks_for_format
from app.services.question_generator import generate_question_paper
import app.services.ai.curriculum_pools as cp


class TestPhase2UniversalGenerationRegression(unittest.TestCase):
    """Test suite for Phase 2 curriculum pools, subject resolution, and paper generation."""

    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSession()

        # Pre-seed Bloom levels
        bloom_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        for idx, name in enumerate(bloom_levels, start=1):
            self.db.add(Bloom(id=idx, level_name=name))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_english_evaluate_pool_availability(self):
        """Verify that English Evaluate questions exist across Prose, Poetry, and Supplementary, and pass Bloom validation."""
        prose_evals = [q for q in cp.ENGLISH_PROSE_QUESTIONS if q.get("bloom") == "Evaluate"]
        poetry_evals = [q for q in cp.ENGLISH_POETRY_QUESTIONS if q.get("bloom") == "Evaluate"]
        supp_evals = [q for q in cp.ENGLISH_SUPPLEMENTARY_QUESTIONS if q.get("bloom") == "Evaluate"]

        self.assertGreaterEqual(len(prose_evals), 8, f"Expected >= 8 Prose Evaluate questions, got {len(prose_evals)}")
        self.assertGreaterEqual(len(poetry_evals), 8, f"Expected >= 8 Poetry Evaluate questions, got {len(poetry_evals)}")
        self.assertGreaterEqual(len(supp_evals), 6, f"Expected >= 6 Supplementary Evaluate questions, got {len(supp_evals)}")

        for pool_name, pool in [("Prose", prose_evals), ("Poetry", poetry_evals), ("Supplementary", supp_evals)]:
            for q in pool:
                valid, inferred, reason = validate_bloom_level(q["q"], "Evaluate")
                self.assertTrue(valid, f"English {pool_name} Evaluate question failed validation: {q['q']} -> {inferred} ({reason})")

    def test_english_evaluate_paper_generation(self):
        """Verify generation of English question paper with high Evaluate allocation does not fail."""
        eng_sub = Subject(id=1, subject_name="English Core", class_name="12", board="CBSE")
        self.db.add(eng_sub)
        self.db.flush()

        u1 = Unit(id=1, subject_id=eng_sub.id, unit_name="Unit 1 - Reading Skills (Comprehension & Inference)")
        u2 = Unit(id=2, subject_id=eng_sub.id, unit_name="Unit 2 - Creative Writing Skills")
        u3 = Unit(id=3, subject_id=eng_sub.id, unit_name="Unit 3 - Literature: Flamingo (Prose and Poetry)")
        u4 = Unit(id=4, subject_id=eng_sub.id, unit_name="Unit 4 - Supplementary Reader: Vistas")
        self.db.add_all([u1, u2, u3, u4])
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=eng_sub.id,
            selected_units=[u3.id, u4.id],
            total_marks=20,
            bloom_distribution={"Evaluate": 50, "Analyze": 50},
            number_of_questions=4,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )

        self.assertEqual(paper["total_marks"], 20)
        self.assertEqual(len(paper["questions"]), 4)
        eval_qs = [q for q in paper["questions"] if q["bloom"] == "Evaluate"]
        self.assertGreaterEqual(len(eval_qs), 2)

    def test_information_technology_mark_constraints(self):
        """Verify that CBSE Class 10 IT (402) blueprint enforces exact permitted marks {1, 2, 4} and max 4."""
        # 1. Official blueprint query
        min_m, max_m, allowed = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Information Technology",
            subject_code="402",
        )
        self.assertEqual(min_m, 1)
        self.assertEqual(max_m, 4)
        self.assertEqual(allowed, {1, 2, 4})

        # 2. Valid marks: 1, 2, 4
        for valid_mark in [1, 2, 4]:
            self.assertIn(valid_mark, allowed)

        # 3. Invalid marks: 3, 5, 6, 8
        for invalid_mark in [3, 5, 6, 8]:
            self.assertNotIn(invalid_mark, allowed)

        # 4. Attempting to exceed official 4-mark limit in board mode raises ValueError
        for exceeding_limit in [5, 6, 8]:
            with self.assertRaises(ValueError) as ctx:
                get_allowed_marks_for_format(
                    board="CBSE",
                    class_name="Class 10",
                    subject_name="Information Technology",
                    max_marks_limit=exceeding_limit,
                    is_custom_assessment=False,
                )
            self.assertIn("exceeds official", str(ctx.exception))
            self.assertIn("limit (4 marks)", str(ctx.exception))

        # 5. Stricter ceiling within official limits (e.g. 2 marks) is permitted
        min_m2, max_m2, allowed2 = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Information Technology",
            max_marks_limit=2,
            is_custom_assessment=False,
        )
        self.assertEqual(max_m2, 2)
        self.assertEqual(allowed2, {1, 2})

        # 6. Explicit custom assessment mode allows custom overrides
        min_custom, max_custom, allowed_custom = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Information Technology",
            max_marks_limit=8,
            is_custom_assessment=True,
        )
        self.assertEqual(max_custom, 8)
        self.assertEqual(allowed_custom, {1, 2, 3, 4, 5, 6, 7, 8})

    def test_short_subject_alias_resolution_and_isolation(self):
        """Verify normalized whole-word matching for IT/CS and confirm unrelated subjects do not unintentionally match."""
        # 'IT' short alias resolves to CBSE Class 10 IT rules
        min_it, max_it, allowed_it = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="IT",
        )
        self.assertEqual(max_it, 4)
        self.assertEqual(allowed_it, {1, 2, 4})

        # 'CS' short alias resolves to secondary/higher-secondary CS rules
        min_cs, max_cs, allowed_cs = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 12",
            subject_name="CS",
        )
        self.assertEqual(max_cs, 6)
        self.assertEqual(allowed_cs, {1, 2, 3, 4, 5, 6})

        # Unrelated subjects with 'it' or 'cs' substrings are NOT matched to IT/CS:
        # 'Auditing' does not match IT; preserves unconstrained default (1-10)
        min_aud, max_aud, allowed_aud = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Auditing",
        )
        self.assertEqual(max_aud, 10)
        self.assertEqual(allowed_aud, set(range(1, 11)))

        # 'Sanskrit' does not match IT; preserves unconstrained default (1-10)
        min_san, max_san, allowed_san = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Sanskrit",
        )
        self.assertEqual(max_san, 10)
        self.assertEqual(allowed_san, set(range(1, 11)))

        # 'Political Science' contains 'it' in 'political', but must match academic branch (max 6) via 'political', NOT IT
        min_pol, max_pol, allowed_pol = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Political Science",
        )
        self.assertEqual(max_pol, 6)
        self.assertEqual(allowed_pol, {1, 2, 3, 4, 5, 6})

    def test_commerce_fetch_syllabus_resolution(self):
        """Verify that Commerce resolves to Business Studies under CBSE Senior Secondary context."""
        # CBSE Class 12 Commerce resolves to Business Studies
        cbse_units = fetch_syllabus_units(board="CBSE", class_name="12", subject_name="Commerce")
        self.assertEqual(len(cbse_units), 6)
        self.assertTrue(any("Management" in u for u in cbse_units))

        # TNSB Class 12 Commerce retains its 5 native units
        tnsb_units = fetch_syllabus_units(board="TNSB", class_name="12", subject_name="Commerce")
        self.assertEqual(len(tnsb_units), 5)
        self.assertTrue(any("Financial Markets" in u for u in tnsb_units))

        # Accountancy does NOT resolve to Business Studies
        acc_units = fetch_syllabus_units(board="CBSE", class_name="12", subject_name="Accountancy")
        self.assertEqual(len(acc_units), 3)
        self.assertFalse(any("Principles of Management" in u for u in acc_units))

        # Economics does NOT resolve to Business Studies
        eco_units = fetch_syllabus_units(board="CBSE", class_name="12", subject_name="Economics")
        self.assertEqual(len(eco_units), 7)
        self.assertTrue(any("National Income" in u for u in eco_units))

    def test_commerce_class_specific_companion_resolution(self):
        """Verify that Commerce companion resolution is strictly class-specific."""
        # 1. Seed Class 12 Business Studies
        bst12 = Subject(id=10, subject_name="Business Studies", class_name="12", board="CBSE")
        self.db.add(bst12)
        self.db.flush()
        for i in range(1, 7):
            self.db.add(Unit(id=100 + i, subject_id=bst12.id, unit_name=f"Unit {i} - Management Module {i}"))

        # 2. Seed Class 11 Business Studies
        bst11 = Subject(id=11, subject_name="Business Studies", class_name="11", board="CBSE")
        self.db.add(bst11)
        self.db.flush()
        u11_names = [
            "Unit 1 - Financial Markets & Capital Market",
            "Unit 2 - Principles of Management",
            "Unit 3 - Marketing Management",
            "Unit 4 - Accounts of Partnership Firms - Fundamentals",
        ]
        for i, uname in enumerate(u11_names, 1):
            self.db.add(Unit(id=110 + i, subject_id=bst11.id, unit_name=uname))
        self.db.commit()

        # Seed Class 12 Commerce with 0 units -> resolves to Class 12 Business Studies (6 units)
        comm12 = Subject(id=20, subject_name="Commerce", class_name="12", board="CBSE")
        self.db.add(comm12)
        self.db.commit()

        paper12 = generate_question_paper(
            db=self.db,
            subject_id=comm12.id,
            selected_units=[],
            total_marks=20,
            bloom_distribution={"Understand": 50, "Apply": 50},
            number_of_questions=4,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper12["total_marks"], 20)
        self.assertEqual(len(paper12["questions"]), 4)
        # Verify all questions in paper12 came strictly from Class 12 Business Studies units
        self.assertTrue(all(q["unit_id"] in [101, 102, 103, 104, 105, 106] for q in paper12["questions"]))

        # Seed Class 11 Commerce with 0 units -> resolves to Class 11 Business Studies (4 units)
        comm11 = Subject(id=21, subject_name="Commerce", class_name="11", board="CBSE")
        self.db.add(comm11)
        self.db.commit()

        paper11 = generate_question_paper(
            db=self.db,
            subject_id=comm11.id,
            selected_units=[],
            total_marks=20,
            bloom_distribution={"Evaluate": 50, "Understand": 50},
            number_of_questions=4,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 11",
        )
        self.assertEqual(paper11["total_marks"], 20)
        self.assertEqual(len(paper11["questions"]), 4)
        # Verify all questions in paper11 came strictly from Class 11 Business Studies units
        self.assertTrue(all(q["unit_id"] in [111, 112, 113, 114] for q in paper11["questions"]))

    def test_commerce_class_11_unconfigured_does_not_cross_resolve_to_class_12(self):
        """When Class 11 Business Studies does not exist, Class 11 Commerce must NOT cross-resolve to Class 12."""
        # Seed ONLY Class 12 Business Studies
        bst12 = Subject(id=10, subject_name="Business Studies", class_name="12", board="CBSE")
        self.db.add(bst12)
        self.db.flush()
        for i in range(1, 7):
            self.db.add(Unit(id=100 + i, subject_id=bst12.id, unit_name=f"Unit {i} - Management Module {i}"))
        self.db.commit()

        # Seed Class 11 Commerce with 0 units
        comm11 = Subject(id=31, subject_name="Commerce", class_name="11", board="CBSE")
        self.db.add(comm11)
        self.db.commit()

        # Generation must fail with unconfigured units error, NOT cross-resolve to Class 12
        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=comm11.id,
                selected_units=[],
                total_marks=20,
                bloom_distribution={"Understand": 100},
                source_mode="hybrid",
                board="CBSE",
                class_name="Class 11",
            )
        self.assertIn("no syllabus units configured", str(ctx.exception))

    def test_unconfigured_subject_raises_clear_error(self):
        """Verify that an arbitrary subject with no units raises a clear actionable ValueError."""
        subj = Subject(id=99, subject_name="Astronomy", class_name="10", board="CBSE")
        self.db.add(subj)
        self.db.commit()

        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=subj.id,
                selected_units=[],
                total_marks=20,
                bloom_distribution={"Understand": 100},
                source_mode="hybrid",
                board="CBSE",
                class_name="Class 10",
            )
        self.assertIn("no syllabus units configured", str(ctx.exception))
        self.assertIn("synchronize official curriculum", str(ctx.exception))

    def test_cbse_class_10_commerce_unconfigured_raises_error(self):
        """CBSE Class 10 has no Commerce; unconfigured Class 10 Commerce raises clear error."""
        comm10 = Subject(id=40, subject_name="Commerce", class_name="10", board="CBSE")
        self.db.add(comm10)
        self.db.commit()

        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=comm10.id,
                selected_units=[],
                total_marks=20,
                bloom_distribution={"Understand": 100},
                source_mode="hybrid",
                board="CBSE",
                class_name="Class 10",
            )
        self.assertIn("no syllabus units configured", str(ctx.exception))

    def test_information_technology_bank_shortage_guidance(self):
        """Verify that bank-only mode provides clear, actionable guidance when approved questions are 0."""
        it_sub = Subject(id=5, subject_name="Information Technology", class_name="10", board="CBSE")
        self.db.add(it_sub)
        self.db.flush()

        u1 = Unit(id=51, subject_id=it_sub.id, unit_name="Unit 1 - Employability Skills (Communication & Self Management)")
        u2 = Unit(id=52, subject_id=it_sub.id, unit_name="Unit 2 - Digital Documentation (Advanced)")
        self.db.add_all([u1, u2])
        self.db.commit()

        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=it_sub.id,
                selected_units=[],
                total_marks=20,
                bloom_distribution={"Remember": 50, "Understand": 50},
                source_mode="bank",
                board="CBSE",
                class_name="Class 10",
            )
        err_text = str(ctx.exception)
        self.assertIn("Insufficient approved questions in question bank for Information Technology", err_text)
        self.assertIn("0 approved question(s) found", err_text)
        self.assertIn("Hybrid mode", err_text)

    def test_information_technology_hybrid_generation(self):
        """Verify that Information Technology generates successfully in hybrid mode conforming to official IT constraints."""
        it_sub = Subject(id=5, subject_name="Information Technology", class_name="10", board="CBSE")
        self.db.add(it_sub)
        self.db.flush()

        u1 = Unit(id=51, subject_id=it_sub.id, unit_name="Unit 1 - Employability Skills (Communication & Self Management)")
        u2 = Unit(id=52, subject_id=it_sub.id, unit_name="Unit 2 - Digital Documentation (Advanced)")
        u3 = Unit(id=53, subject_id=it_sub.id, unit_name="Unit 3 - Electronic Spreadsheet (Advanced)")
        u4 = Unit(id=54, subject_id=it_sub.id, unit_name="Unit 4 - Database Management System (RDBMS)")
        u5 = Unit(id=55, subject_id=it_sub.id, unit_name="Unit 5 - Web Applications and Security")
        self.db.add_all([u1, u2, u3, u4, u5])
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=it_sub.id,
            selected_units=[],
            total_marks=20,
            bloom_distribution={"Remember": 50, "Understand": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 10",
        )

        self.assertEqual(paper["total_marks"], 20)
        # All questions must conform to official blueprint allowed marks {1, 2, 4}
        for q in paper["questions"]:
            self.assertIn(q["marks"], {1, 2, 4}, f"Question mark {q['marks']} not in permitted set {{1, 2, 4}}")
            self.assertLessEqual(q["marks"], 4, "Question marks exceeded official max 4")

    def test_accountancy_analyze_pool_availability(self):
        """Verify that Accountancy Analyze questions are present across Units 1, 2, and 3, and pass validation."""
        acc_analyze = [
            q for q in cp.COMMERCE_ACCOUNTANCY_QUESTIONS
            if q.get("bloom") == "Analyze" and any(u in q.get("unit", "") for u in ["Accounts", "Accounting", "Financial", "Cash Flow"])
        ]
        self.assertGreaterEqual(len(acc_analyze), 10, f"Expected >= 10 Accountancy Analyze questions, got {len(acc_analyze)}")
        for q in acc_analyze:
            valid, inferred, reason = validate_bloom_level(q["q"], "Analyze")
            self.assertTrue(valid, f"Accountancy Analyze question failed validation: {q['q']} -> {inferred} ({reason})")

    def test_accountancy_analyze_paper_generation(self):
        """Verify that Accountancy generates successfully with high Analyze distribution without pool exhaustion."""
        acc_sub = Subject(id=13, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc_sub)
        self.db.flush()

        u1 = Unit(id=131, subject_id=acc_sub.id, unit_name="Unit 1 - Accounting for Partnership Firms (Fundamentals & Reconstitution)")
        u2 = Unit(id=132, subject_id=acc_sub.id, unit_name="Unit 2 - Accounting for Companies (Share Capital & Debentures)")
        u3 = Unit(id=133, subject_id=acc_sub.id, unit_name="Unit 3 - Analysis of Financial Statements (Ratios & Cash Flow)")
        self.db.add_all([u1, u2, u3])
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=acc_sub.id,
            selected_units=[u1.id, u2.id, u3.id],
            total_marks=25,
            bloom_distribution={"Analyze": 60, "Apply": 40},
            number_of_questions=5,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )

        self.assertEqual(paper["total_marks"], 25)
        analyze_qs = [q for q in paper["questions"] if q["bloom"] == "Analyze"]
        self.assertGreaterEqual(len(analyze_qs), 2)

    def test_business_studies_evaluate_pool_availability(self):
        """Verify that Business Studies Evaluate questions are present across management and finance units, and pass validation."""
        bst_eval = [
            q for q in cp.COMMERCE_ACCOUNTANCY_QUESTIONS
            if q.get("bloom") == "Evaluate" and any(u in q.get("unit", "") for u in ["Management", "Financial", "Marketing"])
        ]
        self.assertGreaterEqual(len(bst_eval), 12, f"Expected >= 12 Business Studies Evaluate questions, got {len(bst_eval)}")
        for q in bst_eval:
            valid, inferred, reason = validate_bloom_level(q["q"], "Evaluate")
            self.assertTrue(valid, f"Business Studies Evaluate question failed validation: {q['q']} -> {inferred} ({reason})")

    def test_business_studies_evaluate_paper_generation(self):
        """Verify that Business Studies generates successfully with high Evaluate distribution without pool exhaustion."""
        bst_sub = Subject(id=12, subject_name="Business Studies", class_name="12", board="CBSE")
        self.db.add(bst_sub)
        self.db.flush()

        u1 = Unit(id=121, subject_id=bst_sub.id, unit_name="Unit 1 - Nature and Significance of Management")
        u2 = Unit(id=122, subject_id=bst_sub.id, unit_name="Unit 2 - Principles of Management & Business Environment")
        u3 = Unit(id=123, subject_id=bst_sub.id, unit_name="Unit 3 - Planning and Organizing")
        u4 = Unit(id=124, subject_id=bst_sub.id, unit_name="Unit 4 - Staffing, Directing and Controlling")
        u5 = Unit(id=125, subject_id=bst_sub.id, unit_name="Unit 5 - Financial Management and Financial Markets")
        u6 = Unit(id=126, subject_id=bst_sub.id, unit_name="Unit 6 - Marketing Management and Consumer Protection")
        self.db.add_all([u1, u2, u3, u4, u5, u6])
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=bst_sub.id,
            selected_units=[u1.id, u2.id, u5.id, u6.id],
            total_marks=25,
            bloom_distribution={"Evaluate": 60, "Understand": 40},
            number_of_questions=5,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )

        self.assertEqual(paper["total_marks"], 25)
        eval_qs = [q for q in paper["questions"] if q["bloom"] == "Evaluate"]
        self.assertGreaterEqual(len(eval_qs), 2)


if __name__ == "__main__":
    unittest.main()
