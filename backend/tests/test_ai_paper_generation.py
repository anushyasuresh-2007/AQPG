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

from app.api.v1.endpoints.auth import verify_password
from app.api.v1.endpoints.protected import require_teacher_or_admin as protected_dependency
from app.database.database import Base, get_db
from app.main import app
from app.models import Bloom, Subject, Unit


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
    app.dependency_overrides[protected_dependency] = lambda: SimpleNamespace(role="teacher")

    from app.core.config import settings
    original_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = ""

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    settings.GEMINI_API_KEY = original_key
    app.dependency_overrides.clear()


def seed_test_curriculum(db):
    subject = Subject(subject_name="Data Structures", class_name="12", board="CBSE")
    db.add(subject)
    db.flush()

    u1 = Unit(subject_id=subject.id, unit_name="Arrays")
    u2 = Unit(subject_id=subject.id, unit_name="Linked Lists")
    u3 = Unit(subject_id=subject.id, unit_name="Trees")
    u4 = Unit(subject_id=subject.id, unit_name="Graphs")
    db.add_all([u1, u2, u3, u4])
    db.flush()

    b1 = Bloom(level_name="Remember")
    b2 = Bloom(level_name="Understand")
    b3 = Bloom(level_name="Apply")
    b4 = Bloom(level_name="Analyze")
    db.add_all([b1, b2, b3, b4])
    db.commit()

    return subject, [u1, u2, u3, u4], [b1, b2, b3, b4]


def test_filter_units_by_subject(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    sub, units, _ = seed_test_curriculum(db)
    sub_id = sub.id
    
    # Create second subject with its own unit
    sub2 = Subject(subject_name="Algorithms", class_name="12", board="CBSE")
    db.add(sub2)
    db.flush()
    u_other = Unit(subject_id=sub2.id, unit_name="Sorting")
    db.add(u_other)
    db.commit()
    sub2_id = sub2.id
    db.close()

    # Query all units
    res_all = client.get("/api/v1/units")
    assert res_all.status_code == 200
    assert len(res_all.json()) == 5

    # Query units for subject 1
    res_sub1 = client.get(f"/api/v1/units?subject_id={sub_id}")
    assert res_sub1.status_code == 200
    sub1_units = res_sub1.json()
    assert len(sub1_units) == 4
    assert all(u["subject_id"] == sub_id for u in sub1_units)

    # Query units for subject 2
    res_sub2 = client.get(f"/api/v1/units?subject_id={sub2_id}")
    assert res_sub2.status_code == 200
    sub2_units = res_sub2.json()
    assert len(sub2_units) == 1
    assert sub2_units[0]["unit_name"] == "Sorting"


def test_automatic_ai_paper_generation_exact_marks_and_questions(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    sub, units, blooms = seed_test_curriculum(db)
    sub_id = sub.id
    unit_ids = [u.id for u in units]
    db.close()

    payload = {
        "subject_id": sub_id,
        "unit_ids": [unit_ids[0], unit_ids[1], unit_ids[2]],
        "total_marks": 50,
        "number_of_questions": 10,
        "difficulty": "medium",
        "bloom_distribution": {
            "Remember": 20,
            "Understand": 30,
            "Apply": 30,
            "Analyze": 20
        },
        "use_ai": True
    }

    response = client.post("/api/v1/generate-paper", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_marks"] == 50
    questions = data["questions"]
    assert len(questions) == 10

    # Verify total marks exact sum
    total_calculated_marks = sum(q["marks"] for q in questions)
    assert total_calculated_marks == 50

    # Verify all question texts are populated and unique
    q_texts = [q["question"] for q in questions]
    assert len(set(q_texts)) == len(q_texts)

    # Verify Bloom distribution presence
    blooms_present = {q["bloom"] for q in questions}
    assert blooms_present == {"Remember", "Understand", "Apply", "Analyze"}

    # Verify questions have valid IDs
    assert all(isinstance(q["question_id"], int) and q["question_id"] > 0 for q in questions)


def test_ai_paper_generation_largest_remainder_odd_distribution(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    sub, units, blooms = seed_test_curriculum(db)
    sub_id = sub.id
    unit_ids = [u.id for u in units]
    db.close()

    # 33% / 33% / 34% distribution for 75 marks with 9 questions
    payload = {
        "subject_id": sub_id,
        "units": [unit_ids[0], unit_ids[1]],
        "total_marks": 75,
        "number_of_questions": 9,
        "difficulty": "hard",
        "bloom_distribution": {
            "Remember": 33,
            "Understand": 33,
            "Apply": 34
        },
        "use_ai": True
    }

    response = client.post("/api/v1/generate-paper", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["total_marks"] == 75
    questions = data["questions"]
    assert len(questions) == 9
    assert sum(q["marks"] for q in questions) == 75


def test_ai_paper_generation_validation_errors(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    sub, units, blooms = seed_test_curriculum(db)
    sub_id = sub.id
    first_unit_id = units[0].id
    db.close()

    # Invalid subject ID
    res = client.post("/api/v1/generate-paper", json={
        "subject_id": 9999,
        "units": [1],
        "total_marks": 50,
        "bloom_distribution": {"Remember": 100},
        "use_ai": True
    })
    assert res.status_code == 400
    assert "Subject not found" in res.json()["detail"]

    # Invalid unit ID
    res = client.post("/api/v1/generate-paper", json={
        "subject_id": sub_id,
        "units": [9999],
        "total_marks": 50,
        "bloom_distribution": {"Remember": 100},
        "use_ai": True
    })
    assert res.status_code == 400
    assert "Selected units are invalid" in res.json()["detail"]

    # Invalid Bloom percentage sum
    res = client.post("/api/v1/generate-paper", json={
        "subject_id": sub_id,
        "units": [first_unit_id],
        "total_marks": 50,
        "bloom_distribution": {"Remember": 40, "Understand": 40},
        "use_ai": True
    })
    assert res.status_code == 400
    assert "percentages must total 100" in res.json()["detail"]



def test_password_verification_safe_from_crashes():
    # Verify valid hash
    from app.api.v1.endpoints.auth import hash_password
    pwd = "mySecurePassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong", hashed) is False

    # Verify corrupt / invalid salt / plaintext does not crash with 500
    assert verify_password("test", "not_a_valid_bcrypt_hash") is False
    assert verify_password("test", "") is False
    assert verify_password("test", "$2b$invalid") is False
