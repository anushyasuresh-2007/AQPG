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
from app.models import Subject


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


def test_fetch_syllabus_endpoint(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()

    # Seed English subject
    subject = Subject(subject_name="English", class_name="12", board="CBSE")
    db.add(subject)
    db.flush()
    subject_id = subject.id
    db.commit()
    db.close()

    # Test valid fetch request (should trigger mock fallback listing english chapters)
    payload = {
        "subject_id": subject_id
    }
    response = client.post("/api/v1/units/fetch-syllabus", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "units" in data
    assert len(data["units"]) > 0
    assert "Abdul and Zarina" in data["units"] or "The Last Lesson" in data["units"]


def test_fetch_syllabus_invalid_subject(client_and_db):
    client, _ = client_and_db
    payload = {
        "subject_id": 999
    }
    response = client.post("/api/v1/units/fetch-syllabus", json=payload)
    assert response.status_code == 404
    assert response.json()["detail"] == "Subject not found"
