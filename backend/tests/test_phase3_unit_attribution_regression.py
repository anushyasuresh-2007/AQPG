"""Regression tests for Phase 3 — Cross-Unit Question Attribution Fixes.

Validates:
1. Partnership selection cannot return a Company Accounts question.
2. Company Accounts selection can return an appropriate Company Accounts question.
3. Nature and Significance of Management cannot return a Marketing or Consumer Protection question solely because of a shared keyword.
4. A valid Marketing question remains retrievable for Marketing.
5. A returned question's output unit matches its verified source unit.
6. Multi-unit requests can retrieve questions from each selected unit without cross-unit leakage.
7. Pool exhaustion returns an actionable error instead of relabeling, duplicating, or fabricating questions.
8. Existing valid Class 10 and Class 12 blueprint behavior remains unchanged.
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
import app.services.ai.curriculum_pools as cp
from app.services.ai.curriculum_pools import match_curriculum_question, _match_commerce_unit
from app.services.question_generator import generate_question_paper, validate_unit_relevance


class TestPhase3UnitAttributionRegression(unittest.TestCase):
    """Test suite for Phase 3 cross-unit isolation and authentic attribution."""

    def setUp(self):
        self.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.db = self.TestingSession()

        # Pre-seed standard Bloom levels
        bloom_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
        for idx, name in enumerate(bloom_levels, start=1):
            self.db.add(Bloom(id=idx, level_name=name))
        self.db.commit()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_1_partnership_selection_cannot_return_company_accounts_question(self):
        """1. Partnership selection cannot return a Company Accounts question."""
        partnership_unit = "Unit 1 - Accounting for Partnership Firms (Fundamentals & Reconstitution)"

        # Pool-level verification across all Bloom levels
        for bloom in ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]:
            matched = match_curriculum_question(
                board="CBSE",
                class_name="Class 12",
                subject_name="Accountancy",
                unit_name=partnership_unit,
                bloom_level=bloom,
            )
            if matched:
                cand_u = matched.get("unit", "")
                q_text = matched.get("q", "").lower()
                self.assertNotEqual(cand_u, "Accounting for Share Capital", f"Company Accounts returned for Partnership: {matched}")
                self.assertNotIn("forfeiture of", q_text)
                self.assertNotIn("equity shares", q_text)
                self.assertNotIn("debentures issued", q_text)
                self.assertIn(cand_u, [
                    "Accounts of Partnership Firms - Fundamentals",
                    "Goodwill in Partnership Accounts",
                    "Admission of a Partner",
                ])

        # Paper generation level verification
        acc12 = Subject(id=1, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc12)
        u1 = Unit(id=101, subject_id=acc12.id, unit_name=partnership_unit)
        self.db.add(u1)
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=acc12.id,
            selected_units=[101],
            total_marks=12,
            bloom_distribution={"Remember": 30, "Understand": 30, "Apply": 40},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper["total_marks"], 12)
        for q in paper["questions"]:
            self.assertEqual(q["unit_id"], 101)
            self.assertEqual(q["unit_name"], partnership_unit)
            self.assertIn(q["source_unit"], [
                "Accounts of Partnership Firms - Fundamentals",
                "Goodwill in Partnership Accounts",
                "Admission of a Partner",
            ])
            self.assertNotIn("forfeiture", q["question"].lower())
            self.assertNotIn("equity shares", q["question"].lower())

    def test_2_company_accounts_selection_returns_appropriate_company_question(self):
        """2. Company Accounts selection can return an appropriate Company Accounts question."""
        company_unit = "Unit 2 - Accounting for Companies (Share Capital & Debentures)"

        # Pool-level retrieval for Company Accounts
        matched_apply = match_curriculum_question(
            board="CBSE",
            class_name="Class 12",
            subject_name="Accountancy",
            unit_name=company_unit,
            bloom_level="Apply",
        )
        self.assertIsNotNone(matched_apply)
        self.assertEqual(matched_apply.get("unit"), "Accounting for Share Capital")
        self.assertIn("forfeiture", matched_apply["q"].lower())

        matched_analyze = match_curriculum_question(
            board="CBSE",
            class_name="Class 12",
            subject_name="Accountancy",
            unit_name=company_unit,
            bloom_level="Analyze",
        )
        self.assertIsNotNone(matched_analyze)
        self.assertEqual(matched_analyze.get("unit"), "Accounting for Share Capital")

        # Paper generation level verification
        acc12 = Subject(id=2, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc12)
        u2 = Unit(id=102, subject_id=acc12.id, unit_name=company_unit)
        self.db.add(u2)
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=acc12.id,
            selected_units=[102],
            total_marks=8,
            bloom_distribution={"Apply": 50, "Analyze": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper["total_marks"], 8)
        for q in paper["questions"]:
            self.assertEqual(q["unit_id"], 102)
            self.assertEqual(q["unit_name"], company_unit)
            self.assertEqual(q["source_unit"], "Accounting for Share Capital")
            self.assertTrue(any(term in q["question"].lower() for term in ["share", "debenture", "capital"]))
            self.assertNotIn("partnership deed", q["question"].lower())

    def test_3_nature_of_management_cannot_return_marketing_or_consumer_protection(self):
        """3. Nature and Significance of Management cannot return a Marketing or Consumer Protection question."""
        mgmt_unit = "Unit 1 - Nature and Significance of Management"

        # Direct pool check across all Bloom levels
        for bloom in ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]:
            matched = match_curriculum_question(
                board="CBSE",
                class_name="Class 12",
                subject_name="Business Studies",
                unit_name=mgmt_unit,
                bloom_level=bloom,
            )
            if matched:
                cand_u = matched.get("unit", "")
                q_text = matched.get("q", "").lower()
                self.assertNotEqual(cand_u, "Marketing Management", f"Marketing matched for Management: {matched}")
                self.assertNotEqual(cand_u, "Financial Markets & Capital Market")
                self.assertNotIn("4 ps", q_text)
                self.assertNotIn("societal marketing", q_text)
                self.assertNotIn("quasi-judicial", q_text)
                self.assertIn(cand_u, [
                    "Principles and Functions of Management",
                    "Principles of Management",
                ])

        # Paper generation check
        bst12 = Subject(id=3, subject_name="Business Studies", class_name="12", board="CBSE")
        self.db.add(bst12)
        u1 = Unit(id=201, subject_id=bst12.id, unit_name=mgmt_unit)
        self.db.add(u1)
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=bst12.id,
            selected_units=[201],
            total_marks=12,
            bloom_distribution={"Remember": 30, "Understand": 30, "Analyze": 40},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper["total_marks"], 12)
        for q in paper["questions"]:
            self.assertEqual(q["unit_id"], 201)
            self.assertEqual(q["unit_name"], mgmt_unit)
            self.assertIn(q["source_unit"], [
                "Principles and Functions of Management",
                "Principles of Management",
            ])
            self.assertNotIn("societal marketing", q["question"].lower())
            self.assertNotIn("consumer protection", q["question"].lower())

    def test_4_valid_marketing_question_remains_retrievable_for_marketing(self):
        """4. A valid Marketing question remains retrievable for Marketing."""
        marketing_unit = "Unit 6 - Marketing Management and Consumer Protection"

        matched = match_curriculum_question(
            board="CBSE",
            class_name="Class 12",
            subject_name="Business Studies",
            unit_name=marketing_unit,
            bloom_level="Analyze",
        )
        self.assertIsNotNone(matched)
        self.assertEqual(matched.get("unit"), "Marketing Management")
        self.assertIn("4 ps", matched["q"].lower())

        matched_eval = match_curriculum_question(
            board="CBSE",
            class_name="Class 12",
            subject_name="Business Studies",
            unit_name=marketing_unit,
            bloom_level="Evaluate",
        )
        self.assertIsNotNone(matched_eval)
        self.assertEqual(matched_eval.get("unit"), "Marketing Management")

        # Paper generation check
        bst12 = Subject(id=4, subject_name="Business Studies", class_name="12", board="CBSE")
        self.db.add(bst12)
        u6 = Unit(id=206, subject_id=bst12.id, unit_name=marketing_unit)
        self.db.add(u6)
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=bst12.id,
            selected_units=[206],
            total_marks=8,
            bloom_distribution={"Analyze": 50, "Evaluate": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper["total_marks"], 8)
        for q in paper["questions"]:
            self.assertEqual(q["unit_id"], 206)
            self.assertEqual(q["unit_name"], marketing_unit)
            self.assertEqual(q["source_unit"], "Marketing Management")
            self.assertTrue(any(term in q["question"].lower() for term in ["marketing", "4 ps", "consumer", "societal"]))

    def test_5_returned_question_output_unit_matches_verified_source_unit(self):
        """5. A returned question's output unit matches its verified source unit."""
        acc12 = Subject(id=5, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc12)
        u_part = Unit(id=301, subject_id=acc12.id, unit_name="Unit 1 - Accounting for Partnership Firms (Fundamentals & Reconstitution)")
        u_comp = Unit(id=302, subject_id=acc12.id, unit_name="Unit 2 - Accounting for Companies (Share Capital & Debentures)")
        self.db.add_all([u_part, u_comp])
        self.db.commit()

        # Generate paper for Unit 1
        paper_part = generate_question_paper(
            db=self.db,
            subject_id=acc12.id,
            selected_units=[301],
            total_marks=8,
            bloom_distribution={"Understand": 50, "Apply": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        for q in paper_part["questions"]:
            self.assertEqual(q["unit_name"], u_part.unit_name)
            self.assertTrue(_match_commerce_unit(q["source_unit"], u_part.unit_name))

        # Generate paper for Unit 2
        paper_comp = generate_question_paper(
            db=self.db,
            subject_id=acc12.id,
            selected_units=[302],
            total_marks=8,
            bloom_distribution={"Apply": 50, "Analyze": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        for q in paper_comp["questions"]:
            self.assertEqual(q["unit_name"], u_comp.unit_name)
            self.assertTrue(_match_commerce_unit(q["source_unit"], u_comp.unit_name))

    def test_6_multi_unit_requests_no_cross_unit_leakage(self):
        """6. Multi-unit requests retrieve questions from each selected unit without cross-unit leakage."""
        acc12 = Subject(id=6, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc12)
        u1 = Unit(id=401, subject_id=acc12.id, unit_name="Unit 1 - Accounting for Partnership Firms (Fundamentals & Reconstitution)")
        u2 = Unit(id=402, subject_id=acc12.id, unit_name="Unit 2 - Accounting for Companies (Share Capital & Debentures)")
        self.db.add_all([u1, u2])
        self.db.commit()

        paper = generate_question_paper(
            db=self.db,
            subject_id=acc12.id,
            selected_units=[401, 402],
            total_marks=16,
            bloom_distribution={"Apply": 50, "Analyze": 50},
            number_of_questions=4,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 12",
        )
        self.assertEqual(paper["total_marks"], 16)
        self.assertEqual(len(paper["questions"]), 4)

        u1_questions = [q for q in paper["questions"] if q["unit_id"] == 401]
        u2_questions = [q for q in paper["questions"] if q["unit_id"] == 402]

        self.assertGreater(len(u1_questions), 0, "Expected questions for Unit 1")
        self.assertGreater(len(u2_questions), 0, "Expected questions for Unit 2")

        for q in u1_questions:
            self.assertEqual(q["unit_name"], u1.unit_name)
            self.assertTrue(_match_commerce_unit(q["source_unit"], u1.unit_name))
            self.assertFalse(_match_commerce_unit(q["source_unit"], u2.unit_name))
            self.assertNotIn("forfeiture", q["question"].lower())

        for q in u2_questions:
            self.assertEqual(q["unit_name"], u2.unit_name)
            self.assertTrue(_match_commerce_unit(q["source_unit"], u2.unit_name))
            self.assertFalse(_match_commerce_unit(q["source_unit"], u1.unit_name))
            self.assertNotIn("partnership deed", q["question"].lower())

    def test_7_pool_exhaustion_returns_actionable_error_without_fabrication(self):
        """7. Pool exhaustion returns an actionable error instead of relabeling, duplicating, or fabricating questions."""
        acc12 = Subject(id=7, subject_name="Accountancy", class_name="12", board="CBSE")
        self.db.add(acc12)
        # Unit 2 has only 4 questions total in the curriculum pool
        u2 = Unit(id=502, subject_id=acc12.id, unit_name="Unit 2 - Accounting for Companies (Share Capital & Debentures)")
        self.db.add(u2)
        self.db.commit()

        # Request 20 questions from a 4-question pool
        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=acc12.id,
                selected_units=[502],
                total_marks=50,
                bloom_distribution={"Apply": 50, "Analyze": 50},
                number_of_questions=15,
                source_mode="hybrid",
                board="CBSE",
                class_name="Class 12",
            )
        err_msg = str(ctx.exception)
        self.assertIn("Unable to generate additional distinct, unit-aligned questions", err_msg)
        self.assertIn("exhausted", err_msg)

    def test_8_existing_class_10_and_12_blueprint_behavior_unchanged(self):
        """8. Existing valid Class 10 and Class 12 blueprint behavior remains unchanged."""
        # A. Class 10 English Prose & Poetry
        eng10 = Subject(id=8, subject_name="English Language and Literature", class_name="10", board="CBSE")
        self.db.add(eng10)
        u_prose = Unit(id=601, subject_id=eng10.id, unit_name="Unit 1 - First Flight (Prose)")
        u_poetry = Unit(id=602, subject_id=eng10.id, unit_name="Unit 2 - First Flight (Poetry)")
        self.db.add_all([u_prose, u_poetry])
        self.db.commit()

        eng_paper = generate_question_paper(
            db=self.db,
            subject_id=eng10.id,
            selected_units=[601, 602],
            total_marks=10,
            bloom_distribution={"Understand": 50, "Evaluate": 50},
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 10",
        )
        self.assertEqual(eng_paper["total_marks"], 10)
        self.assertTrue(len(eng_paper["questions"]) >= 2)

        # B. Class 10 Mathematics Geometry Template Retrievability
        math10 = Subject(id=9, subject_name="Mathematics", class_name="10", board="CBSE")
        self.db.add(math10)
        u_geom = Unit(id=701, subject_id=math10.id, unit_name="Unit 4 - Geometry (Triangles & Circles)")
        self.db.add(u_geom)
        self.db.commit()

        math_paper = generate_question_paper(
            db=self.db,
            subject_id=math10.id,
            selected_units=[701],
            total_marks=6,
            bloom_distribution={"Understand": 50, "Apply": 50},
            number_of_questions=2,
            source_mode="hybrid",
            board="CBSE",
            class_name="Class 10",
        )
        self.assertEqual(math_paper["total_marks"], 6)
        self.assertEqual(len(math_paper["questions"]), 2)
        for q in math_paper["questions"]:
            self.assertEqual(q["unit_id"], 701)
            self.assertTrue(validate_unit_relevance(q["question"], u_geom.unit_name, subject_name="Mathematics"))


if __name__ == "__main__":
    unittest.main()
