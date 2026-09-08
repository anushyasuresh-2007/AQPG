"""CRUD helpers for unit-related database operations."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.subject import Subject
from app.models.unit import Unit


def create_unit(db: Session, unit_data: dict) -> Unit:
    """Create a new unit record."""
    subject = db.query(Subject).filter(Subject.id == unit_data.get("subject_id")).first()
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    unit = Unit(**unit_data)
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return unit


def get_unit(db: Session, unit_id: int) -> Optional[Unit]:
    """Return a single unit by identifier."""
    return db.query(Unit).filter(Unit.id == unit_id).first()


def get_units(db: Session, skip: int = 0, limit: int = 100, subject_id: Optional[int] = None) -> List[Unit]:
    """Return all units with optional subject filter and pagination support."""
    query = db.query(Unit)
    if subject_id is not None:
        query = query.filter(Unit.subject_id == subject_id)
    return query.offset(skip).limit(limit).all()


def update_unit(db: Session, unit: Unit, update_data: dict) -> Unit:
    """Update an existing unit record."""
    if "subject_id" in update_data and update_data.get("subject_id") is not None:
        subject = db.query(Subject).filter(Subject.id == update_data.get("subject_id")).first()
        if subject is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    for key, value in update_data.items():
        if value is not None:
            setattr(unit, key, value)

    db.commit()
    db.refresh(unit)
    return unit


def delete_unit(db: Session, unit: Unit) -> None:
    """Delete a unit record."""
    db.delete(unit)
    db.commit()
