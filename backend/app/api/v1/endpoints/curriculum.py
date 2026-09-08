"""API endpoints for Curriculum Catalog, Educational Boards, Classes, and Sync."""

from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.database.database import get_db
from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.board import Board
from app.models.curriculum_sync_log import CurriculumSyncLog
from app.models.stream import Stream
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit
from app.schemas.curriculum import (
    AcademicClassResponse,
    AcademicYearResponse,
    BoardResponse,
    CurriculumStatusResponse,
    CurriculumSyncLogResponse,
    CurriculumSyncRequest,
    StreamResponse,
    TopicResponse,
)
from app.services.curriculum.sync import sync_board_curriculum
from app.services.syllabus_import import import_syllabus_data

router = APIRouter()


@router.post("/syllabus/import", tags=["Curriculum"])
def import_structured_syllabus(
    payload: Any,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Ingest structured JSON syllabus dataset into AQPG catalog."""
    try:
        res = import_syllabus_data(db, payload)
        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Syllabus ingestion failed: {str(e)}",
        )



# =============================================================================
# BOARDS
# =============================================================================
@router.get("/boards", response_model=List[BoardResponse], tags=["Curriculum"])
def list_boards(
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve all supported educational boards (e.g. CBSE, Tamil Nadu State Board)."""
    return db.query(Board).order_by(Board.id).all()


@router.get("/boards/{board_id}", response_model=BoardResponse, tags=["Curriculum"])
def get_board(
    board_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Get board details by ID."""
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Board not found")
    return board


# =============================================================================
# ACADEMIC YEARS
# =============================================================================
@router.get("/academic-years", response_model=List[AcademicYearResponse], tags=["Curriculum"])
def list_academic_years(
    board_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve academic years with optional board filter."""
    query = db.query(AcademicYear)
    if board_id is not None:
        query = query.filter(AcademicYear.board_id == board_id)
    return query.order_by(AcademicYear.year_code.desc()).all()


# =============================================================================
# CLASSES
# =============================================================================
@router.get("/classes", response_model=List[AcademicClassResponse], tags=["Curriculum"])
def list_classes(
    board_id: Optional[int] = None,
    academic_year_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve educational classes with optional board filter."""
    query = db.query(AcademicClass)
    if board_id is not None:
        query = query.filter(AcademicClass.board_id == board_id)
    return query.order_by(AcademicClass.class_number.asc()).all()


# =============================================================================
# STREAMS
# =============================================================================
@router.get("/streams", response_model=List[StreamResponse], tags=["Curriculum"])
def list_streams(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve streams (e.g. Science, Commerce) for a class."""
    query = db.query(Stream)
    if class_id is not None:
        query = query.filter(Stream.class_id == class_id)
    return query.order_by(Stream.id).all()


# =============================================================================
# TOPICS
# =============================================================================
@router.get("/topics", response_model=List[TopicResponse], tags=["Curriculum"])
def list_topics(
    unit_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve topics for a syllabus unit."""
    query = db.query(Topic)
    if unit_id is not None:
        query = query.filter(Topic.unit_id == unit_id)
    return query.order_by(Topic.topic_number.asc()).all()


# =============================================================================
# CURRICULUM SYNC & STATUS
# =============================================================================
@router.post("/curriculum/sync", response_model=CurriculumSyncLogResponse, tags=["Curriculum"])
def sync_curriculum(
    payload: CurriculumSyncRequest,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Synchronize official curriculum from authoritative board catalog."""
    try:
        result = sync_board_curriculum(
            db=db,
            board_key=payload.board,
            academic_year_code=payload.academic_year,
            target_classes=payload.classes,
        )
        
        # Retrieve latest log record
        log = (
            db.query(CurriculumSyncLog)
            .filter(CurriculumSyncLog.board_code == result.board_code)
            .order_by(CurriculumSyncLog.id.desc())
            .first()
        )
        return log
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Curriculum synchronization failed: {str(e)}",
        )


@router.get("/curriculum/status", response_model=CurriculumStatusResponse, tags=["Curriculum"])
def get_curriculum_status(
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Get overview status of all synchronized boards, curriculum counts, and sync history."""
    boards = db.query(Board).all()
    total_subjects = db.query(Subject).count()
    total_units = db.query(Unit).count()
    sync_logs = db.query(CurriculumSyncLog).order_by(CurriculumSyncLog.id.desc()).limit(20).all()

    return CurriculumStatusResponse(
        boards=boards,
        total_subjects=total_subjects,
        total_units=total_units,
        sync_logs=sync_logs,
    )
