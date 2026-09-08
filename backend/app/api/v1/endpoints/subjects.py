"""API endpoints for managing subjects."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.crud.subject import create_subject, delete_subject, get_subject, get_subjects, update_subject
from app.database.database import get_db
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate

router = APIRouter()


@router.get("/subjects", response_model=list[SubjectResponse], tags=["Subjects"])
def read_subjects(
    skip: int = 0,
    limit: int = 200,
    board_id: int | None = None,
    academic_year_id: int | None = None,
    class_id: int | None = None,
    stream_id: int | None = None,
    board_code: str | None = None,
    class_name: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve subjects with optional board, academic year, class, and stream filters."""
    return get_subjects(
        db,
        skip=skip,
        limit=limit,
        board_id=board_id,
        academic_year_id=academic_year_id,
        class_id=class_id,
        stream_id=stream_id,
        board_code=board_code,
        class_name=class_name,
    )



@router.post(
    "/subjects",
    response_model=SubjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Subjects"],
)
def create_new_subject(
    subject: SubjectCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Create a new subject."""
    return create_subject(db, subject.model_dump())


@router.get("/subjects/{subject_id}", response_model=SubjectResponse, tags=["Subjects"])
def read_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve a single subject by its identifier."""
    subject = get_subject(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return subject


@router.put("/subjects/{subject_id}", response_model=SubjectResponse, tags=["Subjects"])
def update_existing_subject(
    subject_id: int,
    subject_update: SubjectUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Update an existing subject by its identifier."""
    subject = get_subject(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    return update_subject(db, subject, subject_update.model_dump(exclude_unset=True))


@router.delete("/subjects/{subject_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Subjects"])
def delete_existing_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Delete a subject by its identifier."""
    subject = get_subject(db, subject_id)
    if subject is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")
    delete_subject(db, subject)
    return None
