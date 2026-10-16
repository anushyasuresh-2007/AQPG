"""Tests for Generated Papers listing, retrieval, and PDF/DOCX downloads."""

import os
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

from app.api.v1.endpoints.protected import require_teacher_or_admin as protected_dependency
from app.database.database import Base, get_db
from app.main import app
from app.models import Bloom, Board, Question, Subject, Unit


@pytest.fixture()
def client_and_db():
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
    b = Board(code="CBSE", name="CBSE", state="All India", active=True)
    db.add(b)
    db.flush()

    s = Subject(subject_name="Science", class_name="10", board="CBSE", board_id=b.id, active=True)
    db.add(s)
    db.flush()

    u = Unit(subject_id=s.id, unit_name="Chemical Reactions", unit_number=1, active=True)
    db.add(u)
    db.flush()

    b1 = Bloom(level_name="Remember")
    b2 = Bloom(level_name="Understand")
    db.add_all([b1, b2])
    db.flush()

    q1 = Question(
        subject_id=s.id,
        unit_id=u.id,
        bloom_level_id=b1.id,
        question_text="Define chemical reaction with example.",
        marks=5,
        difficulty="easy",
        status="approved",
        active=True,
    )
    q2 = Question(
        subject_id=s.id,
        unit_id=u.id,
        bloom_level_id=b2.id,
        question_text="Explain oxidation and reduction reactions.",
        marks=5,
        difficulty="medium",
        status="approved",
        active=True,
    )
    db.add_all([q1, q2])
    db.commit()
    db.close()

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.clear()


def test_generated_papers_flow(client_and_db):
    client, _ = client_and_db

    # 1. Generate Paper via Hybrid mode
    gen_res = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [1],
            "total_marks": 10,
            "difficulty": "medium",
            "bloom_distribution": {"Remember": 50, "Understand": 50},
            "source_mode": "hybrid",
        },
    )
    assert gen_res.status_code == 200
    paper_data = gen_res.json()
    assert paper_data["total_marks"] == 10
    paper_id = paper_data["paper_id"]
    assert paper_id.startswith("QP-")

    # 2. List generated papers
    list_res = client.get("/api/v1/generated-papers")
    assert list_res.status_code == 200
    papers = list_res.json()
    assert any(p["paper_id"] == paper_id for p in papers)

    # 3. Retrieve single paper
    detail_res = client.get(f"/api/v1/generated-papers/{paper_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["paper_id"] == paper_id
    assert len(detail["questions"]) > 0

    # 4. Download DOCX
    docx_res = client.get(f"/api/v1/generated-papers/{paper_id}/docx")
    assert docx_res.status_code == 200
    assert len(docx_res.content) > 1000

    # 5. Download PDF
    pdf_res = client.get(f"/api/v1/generated-papers/{paper_id}/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.content.startswith(b"%PDF")

    # 6. Download Teacher Solutions PDF
    sol_res = client.get(f"/api/v1/generated-papers/{paper_id}/solutions-pdf")
    assert sol_res.status_code == 200
    assert sol_res.content.startswith(b"%PDF")
    assert sol_res.headers["content-type"] == "application/pdf"
    assert f"{paper_id}_AnswerKey_Solutions.pdf" in sol_res.headers["content-disposition"]


def test_solutions_pdf_with_special_xml_characters(client_and_db):
    """Test that questions and answers with <, >, &, and linebreaks render valid PDF bytes without ReportLab errors."""
    client, TestingSessionLocal = client_and_db
    import json
    from app.models.generated_paper import GeneratedPaper

    db = TestingSessionLocal()
    special_paper = GeneratedPaper(
        paper_id="QP-TEST-XML-999",
        title="Physics & Mathematics Examination",
        board_name="TNSB & CBSE",
        class_name="Class 12",
        subject_name="Physics & Chemistry",
        unit_names="Unit 1 - Electrostatics & Kinetics <Advanced>",
        total_marks=20,
        total_questions=2,
        difficulty="medium",
        source="ai",
        status="generated",
        questions_data=json.dumps([
            {
                "question_id": 991,
                "question": "For a charge where q1 * q2 < 0 and r > 0, calculate the force F & vector direction.",
                "marks": 5,
                "bloom": "Apply",
                "difficulty": "medium",
                "answer": "Since q1 * q2 < 0, the force is attractive.\nStep 1: F = (1 / 4πε) * |q1 * q2| / r^2.\nStep 2: Vector points along r_hat if r > 0 & charges differ.",
            },
            {
                "question_id": 992,
                "question": "Discuss the relationship between energy & momentum when v << c versus v ~ c.",
                "marks": 5,
                "bloom": "Analyze",
                "difficulty": "hard",
                "answer": "For v << c, kinetic energy E_k = (1/2)mv^2 & p = mv.\nFor v -> c, E^2 = (pc)^2 + (m0 c^2)^2.",
            },
        ]),
        blueprint_summary=json.dumps([]),
    )
    db.add(special_paper)
    db.commit()
    db.close()

    # Test Solutions PDF with special characters
    sol_res = client.get("/api/v1/generated-papers/QP-TEST-XML-999/solutions-pdf")
    assert sol_res.status_code == 200
    assert sol_res.headers["content-type"] == "application/pdf"
    assert "QP-TEST-XML-999_AnswerKey_Solutions.pdf" in sol_res.headers["content-disposition"]
    assert sol_res.content.startswith(b"%PDF")
    assert len(sol_res.content) > 1000

    # Test Student PDF with special characters
    pdf_res = client.get("/api/v1/generated-papers/QP-TEST-XML-999/pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert "QP-TEST-XML-999_QuestionPaper.pdf" in pdf_res.headers["content-disposition"]
    assert pdf_res.content.startswith(b"%PDF")
    assert len(pdf_res.content) > 1000

    # Test Word document with special characters
    docx_res = client.get("/api/v1/generated-papers/QP-TEST-XML-999/docx?include_answers=true")
    assert docx_res.status_code == 200
    assert len(docx_res.content) > 1000


def test_download_endpoints_reject_unauthenticated():
    """Download endpoints must return 401 or 403 when no auth credentials are provided."""
    with TestClient(app) as unauth_client:
        res = unauth_client.get("/api/v1/generated-papers/QP-123/solutions-pdf")
        assert res.status_code in (401, 403)
