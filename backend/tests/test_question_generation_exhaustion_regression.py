"""Regression tests for question generation across CBSE and TNSB (Classes 10 & 12).

Verifies resolution of the 'distinct questions exhausted' error across diverse subjects,
units, marks profiles, and Bloom taxonomy distributions.
"""

import sys
from pathlib import Path

# Ensure backend directory is in sys.path for standalone execution from any working directory
backend_dir = Path(__file__).resolve().parents[1]
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.subject import Subject
from app.models.unit import Unit
from app.services.question_generator import generate_question_paper
from app.services.bloom_service import infer_bloom_level, validate_bloom_level, BLOOM_HIERARCHY

repo_root = Path(__file__).resolve().parents[2]
db_file = repo_root / "aqpg.db"
if not db_file.exists():
    db_file = repo_root / "backend" / "aqpg.db"

engine = create_engine(f"sqlite:///{db_file.as_posix()}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    """Module-scoped database session for regression tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TestQuestionGenerationExhaustionRegression:
    """Comprehensive regression test suite for question generation across board/class/subject profiles."""

    @pytest.mark.parametrize(
        "board,class_name,subject_query,marks,bloom_dist,unit_mode",
        [
            ("CBSE", "10", "Mathematics Standard", 20, {"Remember": 25, "Understand": 25, "Apply": 25, "Analyze": 25}, "first_two"),
            ("CBSE", "10", "Mathematics Standard", 40, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "all"),
            ("CBSE", "10", "Science", 25, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("CBSE", "10", "Science", 40, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_two"),
            ("CBSE", "10", "Social Science", 25, {"Remember": 25, "Understand": 25, "Apply": 25, "Analyze": 25}, "first_one"),
            ("CBSE", "10", "English Language and Literature", 20, {"Remember": 20, "Understand": 40, "Analyze": 40}, "first_one"),
            ("CBSE", "12", "Physics", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_two"),
            ("CBSE", "12", "Chemistry", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_two"),
            ("CBSE", "12", "Biology", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_two"),
            ("CBSE", "12", "Computer Science", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("CBSE", "12", "Economics", 40, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("CBSE", "12", "Accountancy", 40, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("TNSB", "10", "Mathematics", 25, {"Remember": 25, "Understand": 25, "Apply": 25, "Analyze": 25}, "first_one"),
            ("TNSB", "10", "English", 20, {"Remember": 25, "Understand": 25, "Apply": 25, "Analyze": 25}, "first_one"),
            ("TNSB", "12", "Biology", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("TNSB", "12", "Economics", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
            ("TNSB", "12", "Commerce", 35, {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20}, "first_one"),
        ],
    )
    def test_question_paper_generation_success_and_quality(
        self, db_session, board, class_name, subject_query, marks, bloom_dist, unit_mode
    ):
        """Test paper generation without exhaustion, verifying mark totals, uniqueness, and answers."""
        sub = (
            db_session.query(Subject)
            .filter(Subject.board == board, Subject.subject_name.ilike(f"%{subject_query}%"))
            .first()
        )
        assert sub is not None, f"Subject '{subject_query}' for board '{board}' not found in database."

        units = (
            db_session.query(Unit)
            .filter(Unit.subject_id == sub.id)
            .order_by(Unit.unit_number.asc())
            .all()
        )
        assert len(units) > 0, f"No units found for subject '{sub.subject_name}'."

        if unit_mode == "first_one":
            selected_unit_ids = [units[0].id]
        elif unit_mode == "first_two":
            selected_unit_ids = [u.id for u in units[:2]]
        else:
            selected_unit_ids = [u.id for u in units]

        # Generate paper
        paper = generate_question_paper(
            db=db_session,
            subject_id=sub.id,
            selected_units=selected_unit_ids,
            total_marks=marks,
            difficulty="medium",
            bloom_distribution=bloom_dist,
            source_mode="hybrid",
            board=board,
            class_name=class_name,
        )

        assert paper is not None, "Generated paper returned None"
        questions = paper.get("questions", [])
        assert len(questions) > 0, "Generated paper has 0 questions"

        # 1. Verify exact marks total
        actual_total_marks = sum(q.get("marks", 0) for q in questions)
        assert actual_total_marks == marks, (
            f"Mark total mismatch for {board} {class_name} {sub.subject_name}: "
            f"expected {marks}, got {actual_total_marks}"
        )

        # 2. Verify all individual question marks are valid secondary board denominations (1 to 6)
        for idx, q in enumerate(questions):
            m = q.get("marks", 0)
            assert 1 <= m <= 6, (
                f"Question #{idx+1} has invalid mark {m} (must be 1-6): {q.get('question')}"
            )

        # 3. Verify uniqueness (no duplicate question texts)
        q_texts = [q.get("question", "").strip().lower() for q in questions]
        unique_texts = set(q_texts)
        assert len(q_texts) == len(unique_texts), (
            f"Duplicate questions detected in {board} {class_name} {sub.subject_name}: "
            f"{len(q_texts)} questions with {len(unique_texts)} unique texts"
        )

        # 4. Verify model answers are present, non-empty, and free of generic placeholders
        for idx, q in enumerate(questions):
            ans = str(q.get("answer") or "").strip()
            assert len(ans) >= 10, (
                f"Question #{idx+1} answer is missing or too short ({len(ans)} chars): {q.get('question')}"
            )
            assert not any(ph in ans.lower() for ph in [
                "detailed academic explanation covering key terms",
                "detailed academic explanation covering key concepts",
                "generic placeholder",
            ]), f"Question #{idx+1} contains generic placeholder answer: {ans}"

    def test_single_unit_heavy_marks_does_not_exhaust(self, db_session):
        """Test that single-unit paper with 35 marks does not exhaust questions."""
        sub = db_session.query(Subject).filter(Subject.board == "CBSE", Subject.subject_name.ilike("%Economics%")).first()
        u = db_session.query(Unit).filter(Unit.subject_id == sub.id).first()
        paper = generate_question_paper(
            db=db_session,
            subject_id=sub.id,
            selected_units=[u.id],
            total_marks=35,
            difficulty="medium",
            bloom_distribution={"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 20},
            source_mode="hybrid",
            board="CBSE",
            class_name="12",
        )
        assert paper is not None
        assert sum(q.get("marks", 0) for q in paper.get("questions", [])) == 35

    def test_bloom_validation_resilience_for_analytical_comparisons(self):
        """Test bloom validation accepts comparative analysis and mechanistic questions for Analyze."""
        q1 = "Distinguish between Revenue Deficit and Fiscal Deficit in a government budget."
        valid1, det1, _ = validate_bloom_level(q1, "Analyze")
        assert valid1 is True

        q2 = "Explain the operational mechanism of the Lac Operon in Escherichia coli."
        valid2, det2, _ = validate_bloom_level(q2, "Analyze")
        assert valid2 is True

        q3 = "Why did Lencho write a letter to God, and why did he refer to the post office employees as a bunch of crooks?"
        valid3, det3, _ = validate_bloom_level(q3, "Understand")
        assert valid3 is True
        # Must not be classified as Create
        assert infer_bloom_level(q3) != "Create"

    def test_reject_candidate_with_matching_bloom_label_but_non_matching_wording(self, db_session):
        """Test that a candidate with candidate.bloom='Evaluate' is rejected if question wording only meets Remember."""
        from unittest.mock import MagicMock, patch
        from app.services.ai.base import GeneratedQuestionResult

        # 1. Direct cognitive validation unit check
        low_level_text = "Define the term 'money supply' and state its two primary components."
        valid, inferred, reason = validate_bloom_level(low_level_text, "Evaluate")
        assert valid is False
        assert inferred == "Remember"
        assert "insufficient for target Evaluate" in reason

        # 2. Generator integration check: mock provider returning a mismatched candidate with bloom='Evaluate'
        sub = db_session.query(Subject).filter(Subject.board == "CBSE", Subject.subject_name.ilike("%Science%")).first()
        u = db_session.query(Unit).filter(Unit.subject_id == sub.id).first()

        mismatched_candidate = GeneratedQuestionResult(
            question_text="What is the definition of electric current? State its SI unit.",
            answer="Electric current is the rate of flow of electric charges. Its SI unit is Ampere.",
            explanation=None,
            question_type="Long Answer",
            marks=5,
            difficulty="medium",
            bloom="Evaluate",  # Mismatched label claiming Evaluate
            unit_name=u.unit_name,
        )

        valid_candidate = GeneratedQuestionResult(
            question_text="Critically evaluate whether nuclear power is an effective sustainable energy alternative.",
            answer="Nuclear power provides substantial low-carbon base load electricity, but poses trade-offs regarding radioactive waste storage and accident risks.",
            explanation=None,
            question_type="Long Answer",
            marks=5,
            difficulty="medium",
            bloom="Evaluate",
            unit_name=u.unit_name,
        )

        mock_provider = MagicMock()
        mock_provider.is_available.return_value = True
        mock_provider.generate_question.side_effect = [mismatched_candidate, valid_candidate]

        with patch("app.services.question_generator.get_ai_generator", return_value=mock_provider):
            paper = generate_question_paper(
                db=db_session,
                subject_id=sub.id,
                selected_units=[u.id],
                total_marks=5,
                difficulty="medium",
                bloom_distribution={"Evaluate": 100},
                source_mode="ai",
                board="CBSE",
                class_name="10",
            )

        assert paper is not None
        questions = paper.get("questions", [])
        assert len(questions) == 1
        # The mismatched candidate must have been rejected
        assert "What is the definition of electric current" not in questions[0]["question"]
        # The valid candidate must have been accepted
        assert "Critically evaluate" in questions[0]["question"]
