"""API endpoints for managing units."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.crud.unit import create_unit, delete_unit, get_unit, get_units, update_unit
from app.database.database import get_db
from app.schemas.unit import UnitCreate, UnitResponse, UnitUpdate

router = APIRouter()


@router.get("/units", response_model=list[UnitResponse], tags=["Units"])
def read_units(
    skip: int = 0,
    limit: int = 100,
    subject_id: int | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve units with optional subject filter."""
    return get_units(db, skip=skip, limit=limit, subject_id=subject_id)


@router.post(
    "/units",
    response_model=UnitResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Units"],
)
def create_new_unit(
    unit: UnitCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Create a new unit."""
    return create_unit(db, unit.model_dump())


@router.get("/units/{unit_id}", response_model=UnitResponse, tags=["Units"])
def read_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve a single unit by its identifier."""
    unit = get_unit(db, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return unit


@router.put("/units/{unit_id}", response_model=UnitResponse, tags=["Units"])
def update_existing_unit(
    unit_id: int,
    unit_update: UnitUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Update an existing unit by its identifier."""
    unit = get_unit(db, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    return update_unit(db, unit, unit_update.model_dump(exclude_unset=True))


@router.delete("/units/{unit_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Units"])
def delete_existing_unit(
    unit_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Delete a unit by its identifier."""
    unit = get_unit(db, unit_id)
    if unit is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
    delete_unit(db, unit)
    return None


from app.models.subject import Subject
from app.schemas.syllabus import SyllabusFetchRequest, SyllabusFetchResponse
from app.services.ai_generator import fetch_syllabus_units


@router.post(
    "/units/fetch-syllabus",
    response_model=SyllabusFetchResponse,
    status_code=status.HTTP_200_OK,
    tags=["Units"],
)
def fetch_board_syllabus(
    payload: SyllabusFetchRequest,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Query AI to fetch standard chapters for CBSE/Stateboards/NCERT."""
    subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    chapters = fetch_syllabus_units(
        board=subject.board,
        class_name=subject.class_name,
        subject_name=subject.subject_name,
    )
    return SyllabusFetchResponse(units=chapters)
