"""CRUD helpers for question-related database operations."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bloom import Bloom
from app.models.question import Question
from app.models.subject import Subject
from app.models.unit import Unit


def _validate_question_references(db: Session, question_data: dict) -> None:
    """Ensure the referenced subject, unit, and bloom level all exist."""
    subject_id = question_data.get("subject_id")
    unit_id = question_data.get("unit_id")
    bloom_level_id = question_data.get("bloom_level_id")

    if subject_id is None or unit_id is None or bloom_level_id is None:
        return

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    unit = db.query(Unit).filter(Unit.id == unit_id).first()
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")

    if unit.subject_id != subject_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit does not belong to the provided subject")

    bloom_level = db.query(Bloom).filter(Bloom.id == bloom_level_id).first()
    if bloom_level is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloom level not found")


def create_question(db: Session, question_data: dict) -> Question:
    """Create a new question record."""
    _validate_question_references(db, question_data)
    question = Question(**question_data)
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def get_questions(
    db: Session,
    skip: int = 0,
    limit: int = 200,
    subject_id: Optional[int] = None,
    unit_id: Optional[int] = None,
    bloom_level_id: Optional[int] = None,
    marks: Optional[int] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    board_id: Optional[int] = None,
    class_id: Optional[int] = None,
    source_type: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Question]:
    """Return questions with optional search and filters."""
    query = db.query(Question)
    if subject_id is not None:
        query = query.filter(Question.subject_id == subject_id)
    if unit_id is not None:
        query = query.filter(Question.unit_id == unit_id)
    if bloom_level_id is not None:
        query = query.filter(Question.bloom_level_id == bloom_level_id)
    if marks is not None:
        query = query.filter(Question.marks == marks)
    if difficulty:
        query = query.filter(Question.difficulty == difficulty.lower())
    if question_type:
        query = query.filter(Question.question_type == question_type)
    if board_id is not None:
        query = query.filter(Question.board_id == board_id)
    if class_id is not None:
        query = query.filter(Question.class_id == class_id)
    if source_type:
        query = query.filter(Question.source_type == source_type)
    if status:
        query = query.filter(Question.status == status.lower())
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(Question.question_text.ilike(search_term))
    return query.order_by(Question.id.desc()).offset(skip).limit(limit).all()




def get_question(db: Session, question_id: int) -> Optional[Question]:
    """Return a single question by identifier."""
    return db.query(Question).filter(Question.id == question_id).first()


def update_question(db: Session, question: Question, update_data: dict) -> Question:
    """Update an existing question record."""
    if any(key in update_data for key in {"subject_id", "unit_id", "bloom_level_id"}):
        payload = {
            "subject_id": update_data.get("subject_id", question.subject_id),
            "unit_id": update_data.get("unit_id", question.unit_id),
            "bloom_level_id": update_data.get("bloom_level_id", question.bloom_level_id),
        }
        _validate_question_references(db, payload)

    for key, value in update_data.items():
        if value is not None:
            setattr(question, key, value)
    db.commit()
    db.refresh(question)
    return question


def delete_question(db: Session, question: Question) -> None:
    """Delete a question record."""
    db.delete(question)
    db.commit()
