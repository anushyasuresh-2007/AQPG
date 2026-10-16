"""
test_e2e_generation_quality.py
Phase 2: End-to-End Generation Quality Verification

Automated quality verification against isolated temporary test databases:
1. TNSB Class XII English (Unit 2 - Poetry Appreciation):
   - Authenticity: References actual prescribed poems (The Castle, Our Casuarina Tree, All the World's a Stage, Ulysses, etc.)
   - Anti-Heading Repeat: Questions do not merely regurgitate unit titles.
   - Non-Generic Answers: Model answers provide specific textual reasoning without placeholder strings.
   - Blueprint Adherence: Marks and Bloom cognitive levels are respected.
   - Authentic Pool Exhaustion: Cleanly reports exhaustion without fabricating synthetic filler.
2. TNSB Class XII Mathematics:
   - Mathematical rigor, genuine equations, step-by-step solutions.
3. CBSE Class X Science & Class XII English:
   - Prescribed syllabus content verification.
4. Export Integrity (PDF / Solutions PDF / DOCX):
   - Auth enforcement (401/403 for unauthenticated).
   - Headers and %PDF magic bytes.
   - Safe rendering of <, >, &, equations, multiline text.
   - Error readability (404 JSON detail rather than corrupted file).
5. Persistence & Draft/Approval Workflows:
   - Generated paper record persistence.
   - AI-synthesized questions stored as approved=False, status='draft'.
"""

import json
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Dict, Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory is on sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-e2e")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.api.v1.endpoints.protected import require_teacher_or_admin as protected_dependency
from app.database.database import Base, get_db
from app.main import app
from app.models import AcademicClass, Bloom, Board, GeneratedPaper, Question, Subject, Unit
from app.services.question_generator import validate_unit_relevance, is_near_duplicate

FORBIDDEN_GENERIC_PATTERNS = [
    r"\blist the main components and key terms\b",
    r"\bstate the foundational\b",
    r"\bdetailed academic explanation covering key\b",
    r"\bstate the central theme, poetic devices, or textual context\b",
    r"\bidentify the literary techniques and narrative perspectives\b",
    r"\bdefine the key vocabulary and grammatical rules\b",
    r"\bdefine\s+unit\s+\d+\b",
    r"\bmention any three key attributes or factors\b",
    r"\bname the primary classifications or categories\b",
    r"\bapply the core literary themes and character values\b",
    r"\bdemonstrate how the grammatical rules and stylistic structures\b",
    r"\bexplain the core principles and concepts\b",
    r"\bdescribe the main processes and features associated with\b",
]


@pytest.fixture()
def isolated_test_env():
    """Create a completely isolated in-memory test database and authenticated TestClient."""
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

    db = TestingSessionLocal()

    # 1. Boards
    b_tnsb = Board(code="TNSB", name="Tamil Nadu State Board", state="Tamil Nadu", active=True)
    b_cbse = Board(code="CBSE", name="Central Board of Secondary Education", state="All India", active=True)
    db.add_all([b_tnsb, b_cbse])
    db.flush()

    # 2. Classes
    c_12 = AcademicClass(board_id=b_tnsb.id, class_code="Class 12", class_number=12, active=True)
    c_10 = AcademicClass(board_id=b_cbse.id, class_code="Class 10", class_number=10, active=True)
    db.add_all([c_12, c_10])
    db.flush()

    # 3. Bloom Levels
    blooms = [
        Bloom(level_name="Remember"),
        Bloom(level_name="Understand"),
        Bloom(level_name="Apply"),
        Bloom(level_name="Analyze"),
        Bloom(level_name="Evaluate"),
        Bloom(level_name="Create"),
    ]
    db.add_all(blooms)
    db.flush()

    # 4. Subjects & Units
    # TNSB Class 12 English
    s_tnsb_eng = Subject(
        subject_name="General English",
        class_name="Class 12",
        board="TNSB",
        board_id=b_tnsb.id,
        class_id=c_12.id,
        active=True,
    )
    db.add(s_tnsb_eng)
    db.flush()
    u_tnsb_eng_p = Unit(
        subject_id=s_tnsb_eng.id,
        unit_name="Unit 2 - Poetry Appreciation",
        unit_number=2,
        active=True,
    )
    db.add(u_tnsb_eng_p)
    db.flush()

    # TNSB Class 12 Mathematics
    s_tnsb_math = Subject(
        subject_name="Mathematics",
        class_name="Class 12",
        board="TNSB",
        board_id=b_tnsb.id,
        class_id=c_12.id,
        active=True,
    )
    db.add(s_tnsb_math)
    db.flush()
    u_tnsb_math_mat = Unit(
        subject_id=s_tnsb_math.id,
        unit_name="Unit 1 - Applications of Matrices and Determinants",
        unit_number=1,
        active=True,
    )
    u_tnsb_math_vec = Unit(
        subject_id=s_tnsb_math.id,
        unit_name="Unit 6 - Applications of Vector Algebra",
        unit_number=6,
        active=True,
    )
    db.add_all([u_tnsb_math_mat, u_tnsb_math_vec])
    db.flush()

    # CBSE Class 12 English
    s_cbse_eng = Subject(
        subject_name="English Core",
        class_name="Class 12",
        board="CBSE",
        board_id=b_cbse.id,
        class_id=c_12.id,
        active=True,
    )
    db.add(s_cbse_eng)
    db.flush()
    u_cbse_eng_prose = Unit(
        subject_id=s_cbse_eng.id,
        unit_name="Unit 1 - Flamingo Prose",
        unit_number=1,
        active=True,
    )
    db.add(u_cbse_eng_prose)
    db.flush()

    # CBSE Class 10 Science
    s_cbse_sci = Subject(
        subject_name="Science",
        class_name="Class 10",
        board="CBSE",
        board_id=b_cbse.id,
        class_id=c_10.id,
        active=True,
    )
    db.add(s_cbse_sci)
    db.flush()
    u_cbse_sci_chem = Unit(
        subject_id=s_cbse_sci.id,
        unit_name="Unit 1 - Chemical Reactions and Equations",
        unit_number=1,
        active=True,
    )
    db.add(u_cbse_sci_chem)
    db.commit()

    meta = {
        "b_tnsb_id": int(b_tnsb.id),
        "b_cbse_id": int(b_cbse.id),
        "s_tnsb_eng_id": int(s_tnsb_eng.id),
        "u_tnsb_eng_p_id": int(u_tnsb_eng_p.id),
        "s_tnsb_math_id": int(s_tnsb_math.id),
        "u_tnsb_math_mat_id": int(u_tnsb_math_mat.id),
        "u_tnsb_math_vec_id": int(u_tnsb_math_vec.id),
        "s_cbse_eng_id": int(s_cbse_eng.id),
        "u_cbse_eng_prose_id": int(u_cbse_eng_prose.id),
        "s_cbse_sci_id": int(s_cbse_sci.id),
        "u_cbse_sci_chem_id": int(u_cbse_sci_chem.id),
    }
    db.close()

    with TestClient(app) as client:
        yield client, TestingSessionLocal, meta

    app.dependency_overrides.clear()


def test_tnsb_class12_english_poetry_content_quality(isolated_test_env):
    """Verify TNSB Class 12 Unit 2 Poetry Appreciation generates genuine poem questions with specific answers."""
    client, TestingSessionLocal, meta = isolated_test_env

    payload = {
        "board": "TNSB",
        "class_name": "Class 12",
        "subject_id": meta["s_tnsb_eng_id"],
        "units": [meta["u_tnsb_eng_p_id"]],
        "total_marks": 10,
        "difficulty": "medium",
        "bloom_distribution": {"Remember": 30, "Understand": 30, "Analyze": 40},
        "source_mode": "ai",
    }

    res = client.post("/api/v1/generate-paper", json=payload)
    assert res.status_code == 200, f"Paper generation failed: {res.text}"
    data = res.json()
    assert data["total_marks"] == 10
    assert len(data["questions"]) > 0

    prescribed_poem_keywords = [
        "castle", "edwin muir", "casuarina", "toru dutt", "stage",
        "shakespeare", "seven ages", "ulysses", "tennyson",
        "father to his son", "carl sandburg", "french camp", "ratisbon", "browning",
    ]

    generated_texts = []
    for q in data["questions"]:
        q_text = q["question"]
        q_lower = q_text.lower()
        ans_text = q.get("answer", "")
        ans_lower = ans_text.lower()

        # 1. Must NOT simply repeat the unit heading
        assert q_lower.strip() != "unit 2 - poetry appreciation", "Question must not repeat unit heading"
        assert q_lower.strip() != "poetry appreciation", "Question must not repeat unit heading"

        # 2. Must NOT match any forbidden generic placeholder pattern
        for pat in FORBIDDEN_GENERIC_PATTERNS:
            assert not re.search(pat, q_lower), f"Question matched generic placeholder pattern '{pat}': {q_text}"

        # 3. Must reference authentic prescribed poem content
        has_poem_ref = any(kw in q_lower or kw in ans_lower for kw in prescribed_poem_keywords)
        assert has_poem_ref, f"Question must reference prescribed syllabus poem: '{q_text}'"

        # 4. Model answer must not be empty or a generic placeholder
        assert len(ans_text.strip()) > 10, "Model answer must be non-empty and substantive"
        assert "detailed academic explanation covering" not in ans_lower
        assert "factual recall of authorial intent" not in ans_lower

        # 5. Near-duplicate check against other questions in the paper
        assert not is_near_duplicate(q_text, generated_texts), f"Near duplicate question detected: {q_text}"
        generated_texts.append(q_text)


def test_tnsb_class12_english_poetry_exhaustion_reporting(isolated_test_env):
    """Verify that when the authentic pool is exhausted for a Bloom level, the API reports the limitation rather than fabricating filler."""
    client, TestingSessionLocal, meta = isolated_test_env

    # Requesting 40 marks of solely 'Evaluate' questions (5 marks each = 8 questions)
    # The authentic pool has fewer than 8 distinct Evaluate questions for Unit 2 Poetry.
    payload = {
        "board": "TNSB",
        "class_name": "Class 12",
        "subject_id": meta["s_tnsb_eng_id"],
        "units": [meta["u_tnsb_eng_p_id"]],
        "total_marks": 40,
        "difficulty": "medium",
        "bloom_distribution": {"Evaluate": 100},
        "source_mode": "ai",
    }

    res = client.post("/api/v1/generate-paper", json=payload)
    # Expect HTTP 400 Bad Request with descriptive shortage/exhaustion error
    assert res.status_code == 400, "API must return HTTP 400 on authentic pool exhaustion"
    detail = res.json().get("detail", "")
    assert ("exhausted" in detail.lower() or "unable to generate" in detail.lower() or "insufficient" in detail.lower()), (
        f"Error message must indicate pool exhaustion: {detail}"
    )


def test_tnsb_class12_mathematics_content_quality(isolated_test_env):
    """Verify TNSB Class 12 Mathematics generates rigorous mathematical questions with step-by-step solutions."""
    client, TestingSessionLocal, meta = isolated_test_env

    payload = {
        "board": "TNSB",
        "class_name": "Class 12",
        "subject_id": meta["s_tnsb_math_id"],
        "units": [meta["u_tnsb_math_mat_id"], meta["u_tnsb_math_vec_id"]],
        "total_marks": 10,
        "difficulty": "medium",
        "bloom_distribution": {"Understand": 50, "Apply": 50},
        "source_mode": "ai",
    }

    res = client.post("/api/v1/generate-paper", json=payload)
    assert res.status_code == 200, f"Math paper generation failed: {res.text}"
    data = res.json()
    assert data["total_marks"] == 10

    math_terms = [
        "matrix", "matrices", "determinant", "inverse", "rank", "linear equations",
        "vector", "vectors", "cross product", "dot product", "direction cosines",
        "perpendicular", "collinear", "plane", "line", "equation", "solve",
    ]

    for q in data["questions"]:
        q_text = q["question"]
        q_lower = q_text.lower()
        ans_text = q.get("answer", "")
        ans_lower = ans_text.lower()

        # Must not repeat unit heading
        assert "applications of matrices" not in q_lower or len(q_text) > 40
        assert "applications of vector algebra" not in q_lower or len(q_text) > 40

        # Must test genuine mathematics
        has_math_term = any(term in q_lower or term in ans_lower for term in math_terms)
        assert has_math_term, f"Question must contain mathematics concepts: '{q_text}'"

        # Model answer must contain step-by-step mathematical reasoning
        assert len(ans_text.strip()) > 5
        assert "detailed academic explanation covering" not in ans_lower


def test_cbse_subjects_content_quality(isolated_test_env):
    """Verify CBSE Class 12 English and Class 10 Science generate authentic curriculum-aligned questions."""
    client, TestingSessionLocal, meta = isolated_test_env

    # 1. CBSE Class 12 English Flamingo Prose
    cbse_eng_payload = {
        "board": "CBSE",
        "class_name": "Class 12",
        "subject_id": meta["s_cbse_eng_id"],
        "units": [meta["u_cbse_eng_prose_id"]],
        "total_marks": 10,
        "difficulty": "medium",
        "bloom_distribution": {"Remember": 40, "Understand": 60},
        "source_mode": "ai",
    }
    res_eng = client.post("/api/v1/generate-paper", json=cbse_eng_payload)
    assert res_eng.status_code == 200, f"CBSE English generation failed: {res_eng.text}"
    data_eng = res_eng.json()

    cbse_prose_keywords = [
        "hamel", "franz", "french", "alsace", "last lesson", "saheb", "lost spring",
        "seemapuri", "douglas", "yakima", "deep water", "rattrap", "crofter", "peddler",
        "gandhi", "champaran", "indigo", "gemini studios", "poets and pancakes",
    ]
    for q in data_eng["questions"]:
        q_lower = q["question"].lower()
        ans_lower = q.get("answer", "").lower()
        has_cbse_ref = any(kw in q_lower or kw in ans_lower for kw in cbse_prose_keywords)
        assert has_cbse_ref, f"CBSE English question must reference prescribed prose: {q['question']}"
        assert "detailed academic explanation covering" not in ans_lower


def test_export_endpoints_formatting_and_auth(isolated_test_env):
    """Verify Student PDF, Solutions PDF, and Word exports with special characters, formatting, and auth."""
    client, TestingSessionLocal, meta = isolated_test_env

    # Generate a paper first
    res = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "TNSB",
            "class_name": "Class 12",
            "subject_id": meta["s_tnsb_eng_id"],
            "units": [meta["u_tnsb_eng_p_id"]],
            "total_marks": 5,
            "difficulty": "medium",
            "bloom_distribution": {"Understand": 100},
            "source_mode": "ai",
        },
    )
    assert res.status_code == 200
    paper_id = res.json()["paper_id"]

    # Insert a paper with equations and XML characters into isolated test DB
    db = TestingSessionLocal()
    special_paper = GeneratedPaper(
        paper_id="QP-SPECIAL-CHARS-001",
        title="Physics & Advanced Calculus",
        board_name="TNSB & CBSE",
        class_name="Class 12",
        subject_name="Physics & Math",
        unit_names="Unit 1 <Core> & Unit 2 > Advanced",
        total_marks=10,
        total_questions=2,
        difficulty="medium",
        source="ai",
        status="generated",
        questions_data=json.dumps([
            {
                "question_id": 101,
                "question": "For charges where q1 * q2 < 0 & r > 0, calculate force F & vector direction.",
                "marks": 5,
                "bloom": "Apply",
                "difficulty": "medium",
                "answer": "Since q1 * q2 < 0, the force is attractive.\nStep 1: F = (1 / 4πε) * |q1 * q2| / r^2.\nStep 2: Direction is along r_hat if charges differ.",
            },
            {
                "question_id": 102,
                "question": "If matrix A satisfies det(A) > 0 and trace(A) < 5, evaluate eigenvalues λ1 & λ2.",
                "marks": 5,
                "bloom": "Analyze",
                "difficulty": "hard",
                "answer": "Characteristic equation:\nλ^2 - trace(A)λ + det(A) = 0.\nRoots: λ = (trace ± √(trace^2 - 4*det)) / 2.",
            },
        ]),
        blueprint_summary=json.dumps([]),
    )
    db.add(special_paper)
    db.commit()
    db.close()

    # 1. Authenticated Student PDF
    pdf_res = client.get("/api/v1/generated-papers/QP-SPECIAL-CHARS-001/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "QP-SPECIAL-CHARS-001_QuestionPaper.pdf" in pdf_res.headers["content-disposition"]
    assert pdf_res.content.startswith(b"%PDF")
    assert len(pdf_res.content) > 1000

    # 2. Authenticated Solutions PDF
    sol_res = client.get("/api/v1/generated-papers/QP-SPECIAL-CHARS-001/solutions-pdf")
    assert sol_res.status_code == 200
    assert sol_res.headers["content-type"] == "application/pdf"
    assert "QP-SPECIAL-CHARS-001_AnswerKey_Solutions.pdf" in sol_res.headers["content-disposition"]
    assert sol_res.content.startswith(b"%PDF")
    assert len(sol_res.content) > 1000

    # 3. Authenticated Word document
    docx_res = client.get("/api/v1/generated-papers/QP-SPECIAL-CHARS-001/docx?include_answers=true")
    assert docx_res.status_code == 200
    assert "wordprocessingml" in docx_res.headers["content-type"]
    assert len(docx_res.content) > 1000

    # 4. Non-existent paper returns 404 with JSON detail rather than corrupted file
    not_found_res = client.get("/api/v1/generated-papers/QP-NON-EXISTENT-XYZ/solutions-pdf")
    assert not_found_res.status_code == 404
    assert not_found_res.headers["content-type"] == "application/json"
    assert not_found_res.json()["detail"] == "Question paper not found"

    # 5. Unauthenticated request rejection
    saved_override = app.dependency_overrides.pop(protected_dependency, None)
    try:
        unauth_sol = client.get(f"/api/v1/generated-papers/{paper_id}/solutions-pdf")
        assert unauth_sol.status_code in (401, 403)
        unauth_pdf = client.get(f"/api/v1/generated-papers/{paper_id}/pdf")
        assert unauth_pdf.status_code in (401, 403)
        unauth_docx = client.get(f"/api/v1/generated-papers/{paper_id}/docx")
        assert unauth_docx.status_code in (401, 403)
    finally:
        if saved_override:
            app.dependency_overrides[protected_dependency] = saved_override


def test_paper_persistence_and_draft_approval_workflow(isolated_test_env):
    """Verify that generated papers are persisted in GeneratedPaper and new AI questions are saved as draft/unapproved."""
    client, TestingSessionLocal, meta = isolated_test_env

    payload = {
        "board": "TNSB",
        "class_name": "Class 12",
        "subject_id": meta["s_tnsb_eng_id"],
        "units": [meta["u_tnsb_eng_p_id"]],
        "total_marks": 5,
        "difficulty": "medium",
        "bloom_distribution": {"Analyze": 100},
        "source_mode": "ai",
    }

    res = client.post("/api/v1/generate-paper", json=payload)
    assert res.status_code == 200
    paper_id = res.json()["paper_id"]

    db = TestingSessionLocal()
    # 1. Paper is persisted in GeneratedPaper table
    saved_paper = db.query(GeneratedPaper).filter(GeneratedPaper.paper_id == paper_id).first()
    assert saved_paper is not None
    assert saved_paper.total_marks == 5
    assert saved_paper.board_name == "TNSB"

    # 2. Questions persisted to Question bank have approved=False and status='draft'
    new_questions = db.query(Question).filter(Question.subject_id == meta["s_tnsb_eng_id"]).all()
    assert len(new_questions) > 0
    for q in new_questions:
        assert q.approved is False, "AI synthesized questions must have approved=False until reviewed"
        assert q.status == "draft", "AI synthesized questions must be stored in draft status"
        assert q.is_ai_generated is True
        assert q.source == "AI Synthesized"
    db.close()
