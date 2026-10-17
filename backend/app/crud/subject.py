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
    from sqlalchemy import or_
    from app.models.academic_class import AcademicClass
    from app.models.board import Board

    query = db.query(Subject)

    if board_id is not None:
        try:
            b_rec = db.query(Board).filter(Board.id == board_id).first()
            if b_rec and b_rec.code:
                query = query.filter(or_(Subject.board_id == board_id, (Subject.board_id.is_(None) & (Subject.board == b_rec.code.upper()))))
            else:
                query = query.filter(Subject.board_id == board_id)
        except Exception:
            query = query.filter(Subject.board_id == board_id)
    elif board_code:
        b_clean = board_code.strip().upper()
        try:
            matching_boards = db.query(Board).filter(Board.code.ilike(b_clean)).all()
            b_ids = [b.id for b in matching_boards]
            if b_ids:
                query = query.filter(or_(Subject.board_id.in_(b_ids), Subject.board.ilike(b_clean)))
            else:
                query = query.filter(Subject.board.ilike(b_clean))
        except Exception:
            query = query.filter(Subject.board.ilike(b_clean))

    if academic_year_id is not None:
        query = query.filter(Subject.academic_year_id == academic_year_id)

    if class_id is not None:
        query = query.filter(Subject.class_id == class_id)
    elif class_name:
        cn_clean = class_name.strip()
        cn_lower = cn_clean.lower()
        candidates = {cn_clean, cn_clean.upper(), cn_clean.lower()}

        num_str = None
        if "12" in cn_lower or "xii" in cn_lower:
            num_str = "12"
            candidates.update(["12", "Class 12", "Class XII", "XII"])
        elif "10" in cn_lower or "x" in cn_lower:
            num_str = "10"
            candidates.update(["10", "Class 10", "Class X", "X"])
        elif cn_clean.isdigit():
            num_str = cn_clean
            candidates.add(f"Class {cn_clean}")

        # Resolve any corresponding AcademicClass IDs
        matching_c_ids = []
        try:
            c_query = db.query(AcademicClass)
            if board_id is not None:
                c_query = c_query.filter(AcademicClass.board_id == board_id)
            matching_classes = [
                c for c in c_query.all()
                if (num_str and c.class_number == int(num_str)) or (c.class_code in candidates)
            ]
            matching_c_ids = [c.id for c in matching_classes]
        except Exception:
            matching_c_ids = []

        if matching_c_ids:
            query = query.filter(or_(Subject.class_id.in_(matching_c_ids), Subject.class_name.in_(candidates)))
        else:
            query = query.filter(Subject.class_name.in_(candidates))

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
