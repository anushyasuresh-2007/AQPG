"""Regression tests for Bloom-validation language bypass corrections and question-count/mark allocation validation.

Verifies:
1. Removal of Tamil unconditional Bloom-validation bypass.
2. Prevention of automatic acceptance solely due to Indic characters.
3. Hindi support preservation with explicit language context and safe unsupported behavior otherwise.
4. Accurate English Bloom-validation preservation.
5. Prevention of impossible question-count and mark allocations (e.g. 50 marks across 2 questions).
6. Non-universal, format-specific mark boundaries (CBSE 5/6 vs TNSB 8 vs configurable).
7. Client validation errors before generation starts.
8. Preservation of exact mark totals and valid existing allocations.
"""

import math
import sys
from pathlib import Path
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app
from app.database.database import Base, get_db
from app.api.v1.endpoints.protected import require_teacher_or_admin as protected_dependency
from app.models import Subject, Unit, Bloom, Question
from app.services.bloom_service import (
    validate_bloom_level,
    infer_bloom_level,
    infer_bloom_level_hindi,
)
from app.services.exam_blueprints import (
    get_allowed_marks_for_format,
    validate_paper_allocation_feasibility,
)
from app.services.question_generator import generate_question_paper


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture()
def client_and_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[protected_dependency] = lambda: SimpleNamespace(id=1, role="teacher")

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.clear()


# -----------------------------------------------------------------------------
# Test Suite A: Bloom Validation Language Bypass Regression
# -----------------------------------------------------------------------------

class TestBloomLanguageBypassRegression:
    """Regression tests verifying that Indic/regional scripts do not bypass Bloom cognitive validation."""

    def test_tamil_script_unconditionally_rejected_from_bloom_validation(self):
        """Tamil script is outside project scope and must NEVER pass Bloom validation solely due to script."""
        tamil_question = "அன்னை மொழியே கவிதையில் பெருஞ்சித்திரனார் தமிழின் தொன்மை மற்றும் சிறப்பினை எவ்வாறு போற்றுகிறார்?"
        for target in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
            is_valid, inferred, reason = validate_bloom_level(tamil_question, target)
            assert is_valid is False, f"Tamil question must not pass validation for {target}"
            assert inferred == "Unsupported"
            assert "Tamil script is outside the current project scope" in reason

    def test_english_question_with_tamil_character_does_not_bypass(self):
        """An English question cannot pass high-order validation simply by appending a Tamil character."""
        # Recall question with appended Tamil character '\u0B85' (அ)
        tampered_question = "State Ohm's Law and write its mathematical formula. \u0B85"
        is_valid, inferred, reason = validate_bloom_level(tampered_question, "Evaluate")
        assert is_valid is False, "Question must not bypass validation due to Tamil character"
        assert inferred == "Unsupported"
        assert "Tamil script is outside the current project scope" in reason

    def test_devanagari_without_explicit_language_context_is_unsupported(self):
        """Questions containing Devanagari without explicit language context must NOT pass Bloom validation."""
        hindi_q = "सूरदास के पद के आधार पर गोपियों के वाक्चातुर्य की प्रमुख विशेषताएँ लिखिए।"
        is_valid, inferred, reason = validate_bloom_level(hindi_q, "Understand")
        assert is_valid is False
        assert inferred == "Unsupported"
        assert "requires explicit Hindi language context" in reason

    def test_english_question_with_devanagari_character_does_not_bypass(self):
        """An English recall question cannot pass Evaluate simply by appending a Devanagari character."""
        tampered_question = "Define electric potential and state its SI unit. \u0915"
        # Without explicit language context
        is_valid, inferred, reason = validate_bloom_level(tampered_question, "Evaluate")
        assert is_valid is False
        assert inferred == "Unsupported"

        # Even with language='hindi', it is cognitively evaluated and fails
        is_valid_hi, inferred_hi, reason_hi = validate_bloom_level(tampered_question, "Evaluate", language="hindi")
        assert is_valid_hi is False
        assert "insufficient for target Evaluate" in reason_hi or "mismatch" in reason_hi.lower()

    def test_hindi_support_with_explicit_language_context_matches_cognitive_verbs(self):
        """Preserve Hindi support when explicit language context is provided, validating actual cognitive verbs."""
        # 1. Understand (write key features / explain)
        q_understand = "सूरदास के पद के आधार पर गोपियों के वाक्चातुर्य की प्रमुख विशेषताएँ लिखिए।"
        valid_u, inf_u, _ = validate_bloom_level(q_understand, "Understand", language="hindi")
        assert valid_u is True
        assert inf_u == "Understand"

        # 2. Analyze (satire / comparative / character attributes)
        q_analyze = "लक्ष्मण-परशुराम संवाद में लक्ष्मण के चरित्र की कौन-सी विशेषताएँ उभरकर सामने आती हैं?"
        valid_a, inf_a, _ = validate_bloom_level(q_analyze, "Analyze", language="hindi")
        assert valid_a is True
        assert inf_a == "Analyze"

        # 3. Evaluate (critical judgment / justify stand)
        q_eval = "'नेताजी का चश्मा' पाठ के आधार पर स्पष्ट कीजिए कि देश-प्रेम केवल सीमाओं पर लड़ने से ही नहीं, अपितु दैनिक आचरण से भी प्रकट होता है।"
        valid_e, inf_e, _ = validate_bloom_level(q_eval, "Evaluate", language="hindi")
        assert valid_e is True
        assert inf_e == "Evaluate"

    def test_hindi_cognitive_mismatch_rejected_with_explicit_context(self):
        """A Hindi recall question MUST NOT pass an Evaluate target even with explicit Hindi context."""
        q_recall = "कबीर का जन्म कब और कहाँ हुआ था? नाम लिखिए।"
        valid, inf, reason = validate_bloom_level(q_recall, "Evaluate", language="hindi")
        assert valid is False
        assert inf == "Remember"
        assert "insufficient for target Evaluate" in reason or "mismatch" in reason.lower()

    def test_existing_english_bloom_validation_preserved(self):
        """Standard English cognitive Bloom validation behavior remains fully functional."""
        # Recall question matches Remember
        v1, inf1, _ = validate_bloom_level("Define electric flux and write its SI unit.", "Remember")
        assert v1 is True
        assert inf1 == "Remember"

        # Recall question rejected for Evaluate
        v2, inf2, _ = validate_bloom_level("Define electric flux and write its SI unit.", "Evaluate")
        assert v2 is False
        assert inf2 == "Remember"

        # Evaluative critique matches Evaluate
        v3, inf3, _ = validate_bloom_level("Critically evaluate the economic impact of the Industrial Revolution on urban weavers.", "Evaluate")
        assert v3 is True
        assert inf3 == "Evaluate"


# -----------------------------------------------------------------------------
# Test Suite B: Question-Count and Mark Allocation Validation Regression
# -----------------------------------------------------------------------------

class TestQuestionCountAndMarkAllocationRegression:
    """Regression tests verifying question-count, mark feasibility, and paper-format limits."""

    def test_impossible_allocation_50_marks_2_questions_format_limit_6(self):
        """50 marks across 2 questions where format allows max 6 marks per question must raise ValueError."""
        # Direct feasibility validation helper
        with pytest.raises(ValueError) as excinfo:
            validate_paper_allocation_feasibility(
                total_marks=50,
                bloom_distribution={"Remember": 50, "Understand": 50},
                number_of_questions=2,
                min_allowed_mark=1,
                max_allowed_mark=6,
                format_description="CBSE Class 10 Mathematics format",
            )
        assert "exceeds the maximum possible (12 marks)" in str(excinfo.value)
        assert "maximum 6 marks per question" in str(excinfo.value)

    def test_impossible_allocation_api_client_validation_error_400(self, client_and_test_db):
        """Client receives clear HTTP 400 validation error for impossible 50 marks across 2 questions."""
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Mathematics Standard", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Real Numbers", unit_number=1)
        b1 = Bloom(level_name="Remember")
        b2 = Bloom(level_name="Understand")
        db.add_all([u, b1, b2])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        # Request 50 marks across 2 questions for CBSE Class 10 Math (where format max is 5 marks)
        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 50,
            "number_of_questions": 2,
            "bloom_distribution": {"Remember": 50, "Understand": 50},
            "source_mode": "ai",
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert "Impossible allocation" in detail
        assert "exceeds the maximum possible" in detail

    def test_impossible_allocation_fewer_marks_than_questions(self):
        """Total marks less than number of questions (e.g. 5 marks, 10 questions) must fail validation."""
        with pytest.raises(ValueError) as excinfo:
            validate_paper_allocation_feasibility(
                total_marks=5,
                bloom_distribution={"Remember": 100},
                number_of_questions=10,
                min_allowed_mark=1,
                max_allowed_mark=5,
            )
        assert "less than the minimum required (10 marks)" in str(excinfo.value)

    def test_impossible_allocation_fewer_questions_than_active_bloom_levels(self):
        """Number of questions less than active Bloom levels (e.g. 4 active levels with 2 questions) must fail."""
        with pytest.raises(ValueError) as excinfo:
            validate_paper_allocation_feasibility(
                total_marks=10,
                bloom_distribution={"Remember": 25, "Understand": 25, "Apply": 25, "Analyze": 25},
                number_of_questions=2,
                min_allowed_mark=1,
                max_allowed_mark=5,
            )
        assert "cannot satisfy 4 distinct Bloom taxonomy levels" in str(excinfo.value)

    def test_impossible_allocation_bloom_partition_exceeds_format_marks(self):
        """When a Bloom target requires more questions than total allocated questions under format max marks."""
        # 20 marks total, 4 questions.
        # Bloom: Understand 90% (18 marks), Apply 10% (2 marks).
        # Max marks per question = 5.
        # Understand (18 marks) requires at least ceil(18/5) = 4 questions!
        # Apply (2 marks) requires at least ceil(2/5) = 1 question!
        # Total questions needed is 4 + 1 = 5 questions!
        # Requested questions = 4 is less than the 5 required!
        with pytest.raises(ValueError) as excinfo:
            validate_paper_allocation_feasibility(
                total_marks=20,
                bloom_distribution={"Understand": 90, "Apply": 10},
                number_of_questions=4,
                min_allowed_mark=1,
                max_allowed_mark=5,
            )
        assert "cannot satisfy the requested Bloom distribution" in str(excinfo.value)
        assert "At least 5 questions are required" in str(excinfo.value)

    def test_remember_cognitive_ceiling_conflict_in_board_mode(self):
        """When 5 marks are assigned to Remember across 5 questions total, it fails because Remember <= 4 marks requires 2 questions."""
        with pytest.raises(ValueError) as excinfo:
            validate_paper_allocation_feasibility(
                total_marks=25,
                bloom_distribution={"Remember": 20, "Understand": 20, "Apply": 20, "Analyze": 20, "Evaluate": 20},
                number_of_questions=5,
                min_allowed_mark=1,
                max_allowed_mark=5,
                format_description="CBSE Class 10 Science format",
                is_custom_assessment=False,
            )
        err = str(excinfo.value)
        assert "Foundational recall ('Remember') questions are allocated 5 marks" in err
        assert "cannot be satisfied without assigning 5 marks to a recall question" in err
        assert "increase the question count to at least 6 questions" in err

    def test_remember_cognitive_ceiling_allowed_in_custom_mode(self):
        """In custom assessment mode, recall questions can take higher marks up to max_allowed_mark."""
        # In custom mode, max_allowed_mark is 5, so 5 marks across 5 questions (1 per level) is valid.
        validate_paper_allocation_feasibility(
            total_marks=25,
            bloom_distribution={"Remember": 20, "Understand": 20, "Apply": 20, "Analyze": 20, "Evaluate": 20},
            number_of_questions=5,
            min_allowed_mark=1,
            max_allowed_mark=5,
            format_description="Custom Class 10 Science format",
            is_custom_assessment=True,
        )

    def test_generate_paper_api_rejects_remember_cognitive_ceiling_conflict(self, client_and_test_db):
        """API returns HTTP 400 with actionable error when Remember ceiling is violated in board mode."""
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Science", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Chemical Reactions and Equations", unit_number=1)
        b_rem = Bloom(level_name="Remember")
        b_und = Bloom(level_name="Understand")
        b_app = Bloom(level_name="Apply")
        b_ana = Bloom(level_name="Analyze")
        b_eva = Bloom(level_name="Evaluate")
        db.add_all([u, b_rem, b_und, b_app, b_ana, b_eva])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 25,
            "number_of_questions": 5,
            "bloom_distribution": {"Remember": 20, "Understand": 20, "Apply": 20, "Analyze": 20, "Evaluate": 20},
            "source_mode": "ai",
            "assessment_mode": "board",
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 400
        detail = res.json()["detail"]
        assert "Foundational recall ('Remember') questions are allocated 5 marks" in detail
        assert "increase the question count to at least 6 questions" in detail

    def test_format_rule_distinguishes_cbse_5_marks_vs_tnsb_8_marks(self):
        """Format rules distinguish CBSE (max 5) vs TNSB Class 10 (max 8) without universal hardcoding."""
        min_cbse, max_cbse, _ = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics Standard",
        )
        assert max_cbse == 5

        min_tnsb, max_tnsb, _ = get_allowed_marks_for_format(
            board="TNSB",
            class_name="Class 10",
            subject_name="Mathematics",
        )
        assert max_tnsb == 8

        # For 16 marks across 2 questions:
        # In TNSB 10 (max 8): 2 * 8 = 16 marks is feasible!
        validate_paper_allocation_feasibility(
            total_marks=16,
            bloom_distribution={"Understand": 50, "Apply": 50},
            number_of_questions=2,
            min_allowed_mark=min_tnsb,
            max_allowed_mark=max_tnsb,
        )

        # In CBSE 10 (max 5): 2 * 5 = 10 < 16 marks is impossible!
        with pytest.raises(ValueError):
            validate_paper_allocation_feasibility(
                total_marks=16,
                bloom_distribution={"Understand": 50, "Apply": 50},
                number_of_questions=2,
                min_allowed_mark=min_cbse,
                max_allowed_mark=max_cbse,
            )

    def test_valid_allocation_generates_exact_marks_and_question_counts(self, client_and_test_db):
        """Valid allocation (20 marks across 6 questions) generates exact total marks and question count."""
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Science", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Chemical Reactions and Equations", unit_number=1)
        b_rem = Bloom(level_name="Remember")
        b_und = Bloom(level_name="Understand")
        db.add_all([u, b_rem, b_und])
        db.flush()

        # Pre-seed approved questions in question bank
        q1 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b_rem.id,
            question_text="State the law of conservation of mass in a chemical reaction.",
            answer="Mass can neither be created nor destroyed in a chemical reaction.",
            marks=3, difficulty="medium", question_type="Short Answer", status="approved", active=True,
        )
        q2 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b_und.id,
            question_text="Why do we apply paint on iron articles? Explain the underlying reaction.",
            answer="Painting prevents iron from contacting oxygen and moisture, preventing rusting.",
            marks=4, difficulty="medium", question_type="Short Answer", status="approved", active=True,
        )
        db.add_all([q1, q2])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        # 20 marks across 6 questions: valid (average 3.33 marks, within 1-5 marks)
        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 20,
            "number_of_questions": 6,
            "bloom_distribution": {"Remember": 50, "Understand": 50},
            "source_mode": "hybrid",
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_marks"] == 20
        questions = data["questions"]
        assert len(questions) == 6
        assert sum(q["marks"] for q in questions) == 20
        for q in questions:
            assert 1 <= q["marks"] <= 5, f"Question has invalid mark {q['marks']}"

    def test_board_compliant_request_cannot_exceed_official_mark_limit(self, client_and_test_db):
        """Board-compliant requests cannot override official board ceilings using max_marks_per_question."""
        # 1. Helper check: CBSE Class 10 Math has official max of 5 marks
        with pytest.raises(ValueError) as excinfo:
            get_allowed_marks_for_format(
                board="CBSE",
                class_name="Class 10",
                subject_name="Mathematics Standard",
                max_marks_limit=8,
                is_custom_assessment=False,
            )
        assert "exceeds official CBSE Class 10 Mathematics Standard limit (5 marks)" in str(excinfo.value)
        assert "Specify assessment_mode='custom'" in str(excinfo.value)

        # 2. Board-compliant requests can specify a stricter ceiling within official limits
        min_m, max_m, allowed = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics Standard",
            max_marks_limit=3,
            is_custom_assessment=False,
        )
        assert max_m == 3
        assert allowed == {1, 2, 3}

        # 3. API endpoint check: attempting to exceed official limit under default board mode returns HTTP 400
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Mathematics Standard", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Real Numbers", unit_number=1)
        b1 = Bloom(level_name="Remember")
        db.add_all([u, b1])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 16,
            "number_of_questions": 2,
            "bloom_distribution": {"Remember": 100},
            "source_mode": "ai",
            "max_marks_per_question": 8,
            "assessment_mode": "board",
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 400
        assert "exceeds official" in res.json()["detail"]

    def test_valid_custom_assessment_request_can_use_configured_limit(self, client_and_test_db):
        """Explicit custom-assessment mode allows caller-configured max_marks_per_question."""
        # 1. Helper check: in custom mode, 8 marks per question is permitted
        min_m, max_m, allowed = get_allowed_marks_for_format(
            board="CBSE",
            class_name="Class 10",
            subject_name="Mathematics Standard",
            max_marks_limit=8,
            is_custom_assessment=True,
        )
        assert max_m == 8
        assert allowed == {1, 2, 3, 4, 5, 6, 7, 8}

        # 2. API endpoint check: 16 marks across 2 questions succeeds in custom assessment mode
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Mathematics Standard", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Real Numbers", unit_number=1)
        b1 = Bloom(level_name="Remember")
        db.add_all([u, b1])
        db.flush()
        q1 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b1.id,
            question_text="State and prove the Fundamental Theorem of Arithmetic with comprehensive examples.",
            answer="Every composite number can be expressed as a unique product of primes.",
            marks=8, difficulty="medium", question_type="Long Answer", status="approved", active=True,
        )
        q2 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b1.id,
            question_text="Prove that root 5 is irrational using the method of contradiction.",
            answer="Assume root 5 is rational p/q where p and q are coprime integers...",
            marks=8, difficulty="medium", question_type="Long Answer", status="approved", active=True,
        )
        db.add_all([q1, q2])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 16,
            "number_of_questions": 2,
            "bloom_distribution": {"Remember": 100},
            "source_mode": "hybrid",
            "max_marks_per_question": 8,
            "assessment_mode": "custom",
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_marks"] == 16
        assert len(data["questions"]) == 2
        for q in data["questions"]:
            assert q["marks"] == 8

    def test_conflicting_assessment_inputs_rejected_with_http_422(self, client_and_test_db):
        """Conflicting inputs between assessment_mode and is_custom_assessment are rejected with HTTP 422."""
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Mathematics Standard", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Real Numbers", unit_number=1)
        b1 = Bloom(level_name="Remember")
        db.add_all([u, b1])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        base_payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 10,
            "number_of_questions": 2,
            "bloom_distribution": {"Remember": 100},
            "source_mode": "ai",
        }

        # 1. assessment_mode='board' conflicting with is_custom_assessment=True
        p1 = dict(base_payload, assessment_mode="board", is_custom_assessment=True)
        res1 = client.post("/api/v1/generate-paper", json=p1)
        assert res1.status_code == 422
        assert "Conflicting assessment settings" in str(res1.json())
        assert "assessment_mode is 'board' but is_custom_assessment is True" in str(res1.json())

        # 2. assessment_mode='custom' conflicting with is_custom_assessment=False
        p2 = dict(base_payload, assessment_mode="custom", is_custom_assessment=False)
        res2 = client.post("/api/v1/generate-paper", json=p2)
        assert res2.status_code == 422
        assert "Conflicting assessment settings" in str(res2.json())
        assert "assessment_mode is 'custom' but is_custom_assessment is False" in str(res2.json())

        # 3. Invalid assessment_mode string
        p3 = dict(base_payload, assessment_mode="unsupported_mode")
        res3 = client.post("/api/v1/generate-paper", json=p3)
        assert res3.status_code == 422
        assert "assessment_mode must be either 'board' or 'custom'" in str(res3.json())

    def test_backward_compatible_custom_mode_via_boolean_flag(self, client_and_test_db):
        """Callers passing only is_custom_assessment=True are safely resolved to custom assessment mode."""
        client, SessionLocal = client_and_test_db
        db = SessionLocal()
        sub = Subject(subject_name="Mathematics Standard", class_name="Class 10", board="CBSE")
        db.add(sub)
        db.flush()
        u = Unit(subject_id=sub.id, unit_name="Real Numbers", unit_number=1)
        b1 = Bloom(level_name="Remember")
        db.add_all([u, b1])
        db.flush()
        q1 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b1.id,
            question_text="State and prove the Fundamental Theorem of Arithmetic with comprehensive examples.",
            answer="Every composite number can be expressed as a unique product of primes.",
            marks=8, difficulty="medium", question_type="Long Answer", status="approved", active=True,
        )
        q2 = Question(
            subject_id=sub.id, unit_id=u.id, bloom_level_id=b1.id,
            question_text="Prove that root 5 is irrational using the method of contradiction.",
            answer="Assume root 5 is rational p/q where p and q are coprime integers...",
            marks=8, difficulty="medium", question_type="Long Answer", status="approved", active=True,
        )
        db.add_all([q1, q2])
        db.commit()
        sub_id = sub.id
        u_id = u.id
        db.close()

        # Only pass is_custom_assessment=True, omitting assessment_mode
        payload = {
            "subject_id": sub_id,
            "units": [u_id],
            "total_marks": 16,
            "number_of_questions": 2,
            "bloom_distribution": {"Remember": 100},
            "source_mode": "hybrid",
            "max_marks_per_question": 8,
            "is_custom_assessment": True,
        }
        res = client.post("/api/v1/generate-paper", json=payload)
        assert res.status_code == 200
        data = res.json()
        assert data["total_marks"] == 16
        assert len(data["questions"]) == 2
        for q in data["questions"]:
            assert q["marks"] == 8
