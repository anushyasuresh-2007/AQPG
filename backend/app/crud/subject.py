"""CRUD helpers for subject-related database operations."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.subject import Subject


def create_subject(db: Session, subject_data: dict) -> Subject:
    """Create a new subject record."""
    subject = Subject(**subject_data)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def get_subjects(
    db: Session,
    skip: int = 0,
    limit: int = 200,
    board_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    class_id: Optional[int] = None,
    stream_id: Optional[int] = None,
    board_code: Optional[str] = None,
    class_name: Optional[str] = None,
) -> List[Subject]:
    """Return subjects with optional board, year, class, and stream filters."""
    query = db.query(Subject)

    if board_id is not None:
        query = query.filter(Subject.board_id == board_id)
    elif board_code:
        query = query.filter(Subject.board == board_code.upper())

    if academic_year_id is not None:
        query = query.filter(Subject.academic_year_id == academic_year_id)

    if class_id is not None:
        query = query.filter(Subject.class_id == class_id)
    elif class_name:
        query = query.filter(Subject.class_name == class_name)

    if stream_id is not None:
        query = query.filter((Subject.stream_id == stream_id) | (Subject.stream_id.is_(None)))

    return query.order_by(Subject.subject_name.asc()).offset(skip).limit(limit).all()



def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    """Return a single subject by identifier."""
    return db.query(Subject).filter(Subject.id == subject_id).first()


def update_subject(db: Session, subject: Subject, update_data: dict) -> Subject:
    """Update an existing subject record."""
    for key, value in update_data.items():
        if value is not None:
            setattr(subject, key, value)
    db.commit()
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject: Subject) -> None:
    """Delete a subject record."""
    db.delete(subject)
    db.commit()
