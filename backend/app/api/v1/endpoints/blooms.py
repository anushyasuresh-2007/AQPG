"""API endpoints for managing Bloom taxonomy levels."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.crud.bloom import create_bloom, delete_bloom, get_bloom, get_blooms, update_bloom
from app.database.database import get_db
from app.schemas.bloom import BloomCreate, BloomResponse, BloomUpdate

router = APIRouter()


@router.get("/bloom-levels", response_model=list[BloomResponse], tags=["Bloom Levels"])
def read_blooms(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve all Bloom levels."""
    return get_blooms(db, skip=skip, limit=limit)


@router.post(
    "/bloom-levels",
    response_model=BloomResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Bloom Levels"],
)
def create_new_bloom(
    bloom: BloomCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Create a new Bloom level."""
    return create_bloom(db, bloom.model_dump())


@router.get("/bloom-levels/{bloom_id}", response_model=BloomResponse, tags=["Bloom Levels"])
def read_bloom(
    bloom_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve a single Bloom level by its identifier."""
    bloom = get_bloom(db, bloom_id)
    if bloom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloom level not found")
    return bloom


@router.put("/bloom-levels/{bloom_id}", response_model=BloomResponse, tags=["Bloom Levels"])
def update_existing_bloom(
    bloom_id: int,
    bloom_update: BloomUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Update an existing Bloom level by identifier."""
    bloom = get_bloom(db, bloom_id)
    if bloom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloom level not found")
    return update_bloom(db, bloom, bloom_update.model_dump(exclude_unset=True))


@router.delete("/bloom-levels/{bloom_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bloom Levels"])
def delete_existing_bloom(
    bloom_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Delete a Bloom level by identifier."""
    bloom = get_bloom(db, bloom_id)
    if bloom is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloom level not found")
    delete_bloom(db, bloom)
    return None
