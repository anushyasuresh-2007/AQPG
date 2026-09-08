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
from app.models import Bloom, Question, Subject, Unit


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


def seed_data(db):
    subject = Subject(subject_name="Math", class_name="10", board="CBSE")
    db.add(subject)
    db.flush()

    unit1 = Unit(subject_id=subject.id, unit_name="Algebra")
    unit2 = Unit(subject_id=subject.id, unit_name="Geometry")
    db.add_all([unit1, unit2])
    db.flush()

    remember = Bloom(level_name="Remember")
    understand = Bloom(level_name="Understand")
    db.add_all([remember, understand])
    db.flush()

    q1 = Question(subject_id=subject.id, unit_id=unit1.id, bloom_level_id=remember.id, question_text="Q1", marks=2, difficulty="easy")
    q2 = Question(subject_id=subject.id, unit_id=unit1.id, bloom_level_id=remember.id, question_text="Q2", marks=3, difficulty="easy")
    q3 = Question(subject_id=subject.id, unit_id=unit2.id, bloom_level_id=understand.id, question_text="Q3", marks=5, difficulty="medium")
    db.add_all([q1, q2, q3])
    db.commit()

    return subject, unit1, unit2, remember, understand


def test_generate_paper_validates_blueprint_subject_and_units(client_and_db):
    client, SessionLocal = client_and_db
    seed_data(SessionLocal())

    response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [1, 2],
            "total_marks": 10,
            "bloom_distribution": {"Remember": 50, "Understand": 50},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_marks"] == 10
    assert sum(question["marks"] for question in body["questions"]) == 10
    assert {question["bloom"] for question in body["questions"]} == {"Remember", "Understand"}

    invalid_subject_response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "ICSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [1],
            "total_marks": 10,
            "bloom_distribution": {"Remember": 100},
        },
    )
    assert invalid_subject_response.status_code == 400

    invalid_units_response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [999],
            "total_marks": 10,
            "bloom_distribution": {"Remember": 100},
        },
    )
    assert invalid_units_response.status_code == 400


def test_generate_paper_validates_bloom_distribution_and_marks(client_and_db):
    client, SessionLocal = client_and_db
    seed_data(SessionLocal())

    invalid_distribution_response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [1, 2],
            "total_marks": 10,
            "bloom_distribution": {"Remember": 60, "Understand": 20},
        },
    )
    assert invalid_distribution_response.status_code == 400

    insufficient_marks_response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [1, 2],
            "total_marks": 50,
            "bloom_distribution": {"Remember": 50, "Understand": 50},
        },
    )
    assert insufficient_marks_response.status_code == 400


def test_generate_paper_uses_all_subject_units_when_none_are_selected(client_and_db):
    client, SessionLocal = client_and_db
    seed_data(SessionLocal())

    response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [],
            "total_marks": 10,
            "bloom_distribution": {"Remember": 50, "Understand": 50},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_marks"] == 10
    assert sum(question["marks"] for question in body["questions"]) == 10
    assert {question["bloom"] for question in body["questions"]} == {"Remember", "Understand"}


def test_generate_paper_prevents_duplicates_and_uses_selected_units(client_and_db):
    client, SessionLocal = client_and_db
    seed_data(SessionLocal())

    response = client.post(
        "/api/v1/generate-paper",
        json={
            "board": "CBSE",
            "class_name": "10",
            "subject_id": 1,
            "units": [2],
            "total_marks": 5,
            "bloom_distribution": {"Understand": 100},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total_marks"] == 5
    assert all(question["bloom"] == "Understand" for question in body["questions"])
    assert len({question["question_id"] for question in body["questions"]}) == len(body["questions"])
