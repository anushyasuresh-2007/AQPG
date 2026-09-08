import os
import sys
from types import SimpleNamespace
from pathlib import Path

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

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    app.dependency_overrides.clear()


def seed_related_data(db_session):
    subject = Subject(subject_name="Math", class_name="10", board="CBSE")
    db_session.add(subject)
    db_session.flush()

    unit = Unit(subject_id=subject.id, unit_name="Algebra")
    db_session.add(unit)
    db_session.flush()

    bloom = Bloom(level_name="Remember")
    db_session.add(bloom)
    db_session.flush()
    db_session.commit()
    return subject, unit, bloom


def test_question_crud_flow(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    subject, unit, bloom = seed_related_data(db)
    subject_id = subject.id
    unit_id = unit.id
    bloom_id = bloom.id
    db.close()

    payload = {
        "subject_id": subject_id,
        "unit_id": unit_id,
        "bloom_level_id": bloom_id,
        "question_text": "What is 2 + 2?",
        "marks": 5,
        "difficulty": "easy",
    }

    create_response = client.post("/api/v1/questions", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["question_text"] == payload["question_text"]
    assert created["marks"] == 5

    list_response = client.get("/api/v1/questions")
    assert list_response.status_code == 200
    assert any(item["id"] == created["id"] for item in list_response.json())

    detail_response = client.get(f"/api/v1/questions/{created['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == created["id"]

    update_response = client.put(
        f"/api/v1/questions/{created['id']}",
        json={"question_text": "Updated question", "marks": 8},
    )
    assert update_response.status_code == 200
    assert update_response.json()["question_text"] == "Updated question"
    assert update_response.json()["marks"] == 8

    delete_response = client.delete(f"/api/v1/questions/{created['id']}")
    assert delete_response.status_code == 204

    missing_response = client.get(f"/api/v1/questions/{created['id']}")
    assert missing_response.status_code == 404


def test_question_validation_for_invalid_relations_and_values(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    subject, unit, bloom = seed_related_data(db)
    subject_id = subject.id
    unit_id = unit.id
    bloom_id = bloom.id
    db.close()

    invalid_subject_payload = {
        "subject_id": 999,
        "unit_id": unit_id,
        "bloom_level_id": bloom_id,
        "question_text": "Invalid subject",
        "marks": 1,
        "difficulty": "easy",
    }
    invalid_subject_response = client.post("/api/v1/questions", json=invalid_subject_payload)
    assert invalid_subject_response.status_code == 404

    invalid_unit_payload = {
        "subject_id": subject_id,
        "unit_id": 999,
        "bloom_level_id": bloom_id,
        "question_text": "Invalid unit",
        "marks": 1,
        "difficulty": "easy",
    }
    invalid_unit_response = client.post("/api/v1/questions", json=invalid_unit_payload)
    assert invalid_unit_response.status_code == 404

    invalid_bloom_payload = {
        "subject_id": subject_id,
        "unit_id": unit_id,
        "bloom_level_id": 999,
        "question_text": "Invalid bloom",
        "marks": 1,
        "difficulty": "easy",
    }
    invalid_bloom_response = client.post("/api/v1/questions", json=invalid_bloom_payload)
    assert invalid_bloom_response.status_code == 404

    invalid_marks_response = client.post(
        "/api/v1/questions",
        json={
            "subject_id": subject_id,
            "unit_id": unit_id,
            "bloom_level_id": bloom_id,
            "question_text": "Bad marks",
            "marks": 0,
            "difficulty": "easy",
        },
    )
    assert invalid_marks_response.status_code == 422

    invalid_difficulty_response = client.post(
        "/api/v1/questions",
        json={
            "subject_id": subject_id,
            "unit_id": unit_id,
            "bloom_level_id": bloom_id,
            "question_text": "Bad difficulty",
            "marks": 1,
            "difficulty": "very-hard",
        },
    )
    assert invalid_difficulty_response.status_code == 422


def test_bulk_upload_questions(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    subject, unit, bloom = seed_related_data(db)
    subject_id = subject.id
    unit_id = unit.id
    bloom_id = bloom.id
    db.close()

    payload = [
        {
            "subject_name": "Math",
            "unit_name": "Algebra",
            "bloom_level": "Remember",
            "question_text": "Bulk Q1: What is a linear equation?",
            "question_type": "Short Answer",
            "marks": 2,
            "difficulty": "easy",
            "answer": "An equation of first degree.",
            "explanation": "Standard polynomial form.",
        },
        {
            "subject_id": subject_id,
            "unit_id": unit_id,
            "bloom_level_id": bloom_id,
            "question_text": "Bulk Q2: Solve 2x + 4 = 10",
            "question_type": "Short Answer",
            "marks": 3,
            "difficulty": "medium",
            "answer": "x = 3",
        },
        {
            "subject_name": "NonExistentSubject",
            "unit_name": "Algebra",
            "bloom_level": "Remember",
            "question_text": "Bulk Q3: This should fail",
            "marks": 5,
        },
    ]

    response = client.post("/api/v1/questions/bulk-upload", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["total_submitted"] == 3
    assert data["successful_count"] == 2
    assert data["failed_count"] == 1
    assert len(data["errors"]) == 1
    assert "Subject 'NonExistentSubject' not found" in data["errors"][0]["error"]

