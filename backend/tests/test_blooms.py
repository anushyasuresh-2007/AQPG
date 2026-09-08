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


def test_bloom_level_crud_flow(client_and_db):
    client, SessionLocal = client_and_db
    response = client.post("/api/v1/bloom-levels", json={"level_name": "Remember"})
    assert response.status_code == 201
    created = response.json()
    bloom_id = created["id"]

    list_response = client.get("/api/v1/bloom-levels")
    assert list_response.status_code == 200
    assert any(item["id"] == bloom_id for item in list_response.json())

    detail_response = client.get(f"/api/v1/bloom-levels/{bloom_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == bloom_id

    update_response = client.put(f"/api/v1/bloom-levels/{bloom_id}", json={"level_name": "Understand"})
    assert update_response.status_code == 200
    assert update_response.json()["level_name"] == "Understand"

    delete_response = client.delete(f"/api/v1/bloom-levels/{bloom_id}")
    assert delete_response.status_code == 204


def test_bloom_level_cannot_be_deleted_when_questions_reference_it(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()

    subject = Subject(subject_name="Math", class_name="10", board="CBSE")
    db.add(subject)
    db.flush()

    unit = Unit(subject_id=subject.id, unit_name="Algebra")
    db.add(unit)
    db.flush()

    bloom = Bloom(level_name="Remember")
    db.add(bloom)
    db.flush()

    question = Question(
        subject_id=subject.id,
        unit_id=unit.id,
        bloom_level_id=bloom.id,
        question_text="What is 2 + 2?",
        marks=1,
        difficulty="easy",
    )
    db.add(question)
    db.commit()
    bloom_id = bloom.id
    db.close()

    response = client.delete(f"/api/v1/bloom-levels/{bloom_id}")
    assert response.status_code == 409
