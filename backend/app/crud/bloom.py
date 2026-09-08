"""CRUD helpers for Bloom taxonomy levels."""

from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.bloom import Bloom


def create_bloom(db: Session, bloom_data: dict) -> Bloom:
    """Create a new Bloom level."""
    bloom = Bloom(**bloom_data)
    db.add(bloom)
    db.commit()
    db.refresh(bloom)
    return bloom


def get_blooms(db: Session, skip: int = 0, limit: int = 100) -> List[Bloom]:
    """Return all Bloom levels."""
    return db.query(Bloom).offset(skip).limit(limit).all()


def get_bloom(db: Session, bloom_id: int) -> Optional[Bloom]:
    """Return a Bloom level by identifier."""
    return db.query(Bloom).filter(Bloom.id == bloom_id).first()


def update_bloom(db: Session, bloom: Bloom, update_data: dict) -> Bloom:
    """Update an existing Bloom level."""
    for key, value in update_data.items():
        if value is not None:
            setattr(bloom, key, value)
    db.commit()
    db.refresh(bloom)
    return bloom


def delete_bloom(db: Session, bloom: Bloom) -> None:
    """Delete a Bloom level when no questions still reference it."""
    if bloom.questions:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete Bloom level because questions still reference it",
        )
    db.delete(bloom)
    db.commit()
