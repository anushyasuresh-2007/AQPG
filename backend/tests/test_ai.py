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

    from app.core.config import settings
    original_key = settings.GEMINI_API_KEY
    settings.GEMINI_API_KEY = ""

    with TestClient(app) as client:
        yield client, TestingSessionLocal

    settings.GEMINI_API_KEY = original_key
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


def test_ai_generation_endpoint(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    subject, unit, bloom = seed_related_data(db)
    subject_id = subject.id
    unit_id = unit.id
    bloom_id = bloom.id
    db.close()

    # Test valid request (should return mock list of 2 questions)
    payload = {
        "subject_id": subject_id,
        "unit_id": unit_id,
        "bloom_level_id": bloom_id,
        "difficulty": "medium",
        "marks": 3,
        "count": 2
    }

    response = client.post("/api/v1/questions/generate-ai", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 2
    assert data["questions"][0]["marks"] == 3
    assert data["questions"][0]["difficulty"] == "medium"
    assert "Explain the significance of 'Algebra'" in data["questions"][0]["question_text"]


def test_ai_generation_validation(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    subject, unit, bloom = seed_related_data(db)
    subject_id = subject.id
    unit_id = unit.id
    bloom_id = bloom.id
    db.close()

    # Test invalid subject
    payload = {
        "subject_id": 999,
        "unit_id": unit_id,
        "bloom_level_id": bloom_id,
        "difficulty": "easy",
        "marks": 2,
        "count": 1
    }
    response = client.post("/api/v1/questions/generate-ai", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Subject not found"
