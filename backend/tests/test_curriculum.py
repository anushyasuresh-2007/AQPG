"""Tests for Curriculum Catalog, Board Support, and Sync Endpoints."""

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
from app.services.curriculum.sync import sync_board_curriculum


@pytest.fixture()
def client_and_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed curriculum in test database
    db = TestingSessionLocal()
    try:
        sync_board_curriculum(db, board_key="cbse", academic_year_code="2026-27")
        sync_board_curriculum(db, board_key="tnsb", academic_year_code="2026-27")
        # Add basic bloom
        db.add(Bloom(level_name="Remember"))
        db.add(Bloom(level_name="Understand"))
        db.commit()
    finally:
        db.close()

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


def test_list_boards(client_and_db):
    client, _ = client_and_db
    res = client.get("/api/v1/boards")
    assert res.status_code == 200
    boards = res.json()
    assert len(boards) >= 2
    codes = [b["code"] for b in boards]
    assert "CBSE" in codes and "TNSB" in codes


def test_sync_curriculum_and_status(client_and_db):
    client, _ = client_and_db
    # Test on-demand sync for CBSE
    sync_res = client.post("/api/v1/curriculum/sync", json={"board": "cbse", "academic_year": "2026-27"})
    assert sync_res.status_code == 200
    data = sync_res.json()
    assert data["board_code"] == "CBSE"
    assert data["status"] == "success"

    # Test status endpoint
    status_res = client.get("/api/v1/curriculum/status")
    assert status_res.status_code == 200
    stat_data = status_res.json()
    assert stat_data["total_subjects"] > 0
    assert stat_data["total_units"] > 0
    assert len(stat_data["sync_logs"]) > 0


def test_cascading_classes_and_subjects(client_and_db):
    client, _ = client_and_db
    # Fetch boards
    boards_res = client.get("/api/v1/boards")
    cbse_board = next((b for b in boards_res.json() if b["code"] == "CBSE"), None)
    assert cbse_board is not None

    # Fetch classes for CBSE
    classes_res = client.get(f"/api/v1/classes?board_id={cbse_board['id']}")
    assert classes_res.status_code == 200
    classes = classes_res.json()
    assert len(classes) >= 1

    # Fetch subjects for Class X
    class_10 = next((c for c in classes if c["class_number"] == 10), classes[0])
    subs_res = client.get(f"/api/v1/subjects?board_id={cbse_board['id']}&class_id={class_10['id']}")
    assert subs_res.status_code == 200
    subs = subs_res.json()
    assert len(subs) > 0


def test_question_moderation_flow(client_and_db):
    client, SessionLocal = client_and_db
    db = SessionLocal()
    try:
        sub = db.query(Subject).first()
        unit = sub.units[0] if sub and sub.units else None
        bloom = db.query(Bloom).first()

        assert sub is not None and unit is not None and bloom is not None

        # Create draft question
        create_res = client.post(
            "/api/v1/questions",
            json={
                "subject_id": sub.id,
                "unit_id": unit.id,
                "bloom_level_id": bloom.id,
                "question_text": "Explain the working principle of electric motors.",
                "question_type": "Descriptive",
                "marks": 5,
                "difficulty": "medium",
                "status": "draft",
                "source_type": "ai",
            },
        )
        assert create_res.status_code == 201
        q_id = create_res.json()["id"]

        # Approve question
        approve_res = client.post(f"/api/v1/questions/{q_id}/approve")
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "approved"

        # Reject question
        reject_res = client.post(f"/api/v1/questions/{q_id}/reject")
        assert reject_res.status_code == 200
        assert reject_res.json()["status"] == "rejected"
    finally:
        db.close()
