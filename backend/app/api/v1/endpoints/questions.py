"""API endpoints for managing questions."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.crud.question import create_question, delete_question, get_question, get_questions, update_question
from app.database.database import get_db
from app.models.question import Question

from app.schemas.question import (
    AIGenerateRequest,
    AIGenerateResponse,
    BulkQuestionUploadItem,
    BulkQuestionUploadResponse,
    BulkUploadRowError,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
)

router = APIRouter()


@router.get("/questions", response_model=list[QuestionResponse], tags=["Questions"])
def read_questions(
    skip: int = 0,
    limit: int = 200,
    subject_id: int | None = None,
    unit_id: int | None = None,
    bloom_level_id: int | None = None,
    marks: int | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
    board_id: int | None = None,
    class_id: int | None = None,
    source_type: str | None = None,
    status_filter: str | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve questions with optional search, curriculum, and status filters."""
    return get_questions(
        db,
        skip=skip,
        limit=limit,
        subject_id=subject_id,
        unit_id=unit_id,
        bloom_level_id=bloom_level_id,
        marks=marks,
        difficulty=difficulty,
        question_type=question_type,
        board_id=board_id,
        class_id=class_id,
        source_type=source_type,
        status=status_filter,
        search=search,
    )


@router.post("/questions/{question_id}/approve", response_model=QuestionResponse, tags=["Questions"])
def approve_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Mark a draft question as Approved for paper generation."""
    question = get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    question.status = "approved"
    db.commit()
    db.refresh(question)
    return question


@router.post("/questions/{question_id}/reject", response_model=QuestionResponse, tags=["Questions"])
def reject_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Mark a question as Rejected."""
    question = get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    question.status = "rejected"
    db.commit()
    db.refresh(question)
    return question




@router.get("/questions/{question_id}", response_model=QuestionResponse, tags=["Questions"])
def read_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve a single question by its identifier."""
    question = get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


@router.post(
    "/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Questions"],
)
def create_new_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Create a new question."""
    return create_question(db, question.model_dump())


@router.put("/questions/{question_id}", response_model=QuestionResponse, tags=["Questions"])
def update_existing_question(
    question_id: int,
    question_update: QuestionUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Update an existing question by its identifier."""
    question = get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return update_question(db, question, question_update.model_dump(exclude_unset=True))


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Questions"])
def delete_existing_question(
    question_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Delete a question by its identifier."""
    question = get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    delete_question(db, question)
    return None


from app.models.subject import Subject
from app.models.unit import Unit
from app.models.bloom import Bloom
from app.services.ai_generator import generate_questions_via_ai
from app.schemas.question import AIGenerateRequest, AIGenerateResponse


@router.post(
    "/questions/generate-ai",
    response_model=AIGenerateResponse,
    status_code=status.HTTP_200_OK,
    tags=["Questions"],
)
def generate_ai_questions(
    payload: AIGenerateRequest,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Generate questions using AI based on criteria."""
    subject = db.query(Subject).filter(Subject.id == payload.subject_id).first()
    if not subject:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subject not found")

    unit = db.query(Unit).filter(Unit.id == payload.unit_id).first()
    if not unit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")

    if unit.subject_id != payload.subject_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit does not belong to the provided subject")

    bloom = db.query(Bloom).filter(Bloom.id == payload.bloom_level_id).first()
    if not bloom:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bloom level not found")

    questions_list = generate_questions_via_ai(
        subject=subject.subject_name,
        unit=unit.unit_name,
        bloom_level=bloom.level_name,
        difficulty=payload.difficulty,
        marks=payload.marks,
        count=payload.count,
        textbook_context=payload.textbook_context,
    )

    return AIGenerateResponse(questions=questions_list)


@router.post(
    "/questions/bulk-upload",
    response_model=BulkQuestionUploadResponse,
    status_code=status.HTTP_200_OK,
    tags=["Questions"],
)
def bulk_upload_questions(
    items: list[BulkQuestionUploadItem],
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Bulk import questions with row validation and clear error reporting."""
    created_questions: list[Question] = []
    errors: list[BulkUploadRowError] = []

    # Cache lookups to optimize validation
    subjects_by_id = {s.id: s for s in db.query(Subject).all()}
    subjects_by_name = {s.subject_name.strip().lower(): s for s in subjects_by_id.values()}
    
    units_by_id = {u.id: u for u in db.query(Unit).all()}
    blooms_by_id = {b.id: b for b in db.query(Bloom).all()}
    blooms_by_name = {b.level_name.strip().lower(): b for b in blooms_by_id.values()}

    for index, item in enumerate(items):
        row_num = index + 1
        q_text = (item.question_text or "").strip()
        if not q_text:
            errors.append(BulkUploadRowError(row_index=row_num, question_text="", error="Question text is empty"))
            continue

        # Resolve subject
        target_subject = None
        if item.subject_id and item.subject_id in subjects_by_id:
            target_subject = subjects_by_id[item.subject_id]
        elif item.subject_name and item.subject_name.strip().lower() in subjects_by_name:
            target_subject = subjects_by_name[item.subject_name.strip().lower()]

        if not target_subject:
            errors.append(BulkUploadRowError(
                row_index=row_num,
                question_text=q_text[:40],
                error=f"Subject '{item.subject_name or item.subject_id}' not found",
            ))
            continue

        # Resolve unit
        target_unit = None
        if item.unit_id and item.unit_id in units_by_id:
            target_unit = units_by_id[item.unit_id]
        elif item.unit_name:
            norm_unit_name = item.unit_name.strip().lower()
            for u in target_subject.units:
                if u.unit_name.strip().lower() == norm_unit_name:
                    target_unit = u
                    break

        if not target_unit:
            errors.append(BulkUploadRowError(
                row_index=row_num,
                question_text=q_text[:40],
                error=f"Unit '{item.unit_name or item.unit_id}' not found under subject '{target_subject.subject_name}'",
            ))
            continue

        if target_unit.subject_id != target_subject.id:
            errors.append(BulkUploadRowError(
                row_index=row_num,
                question_text=q_text[:40],
                error=f"Unit '{target_unit.unit_name}' does not belong to subject '{target_subject.subject_name}'",
            ))
            continue

        # Resolve Bloom level
        target_bloom = None
        if item.bloom_level_id and item.bloom_level_id in blooms_by_id:
            target_bloom = blooms_by_id[item.bloom_level_id]
        elif item.bloom_level and item.bloom_level.strip().lower() in blooms_by_name:
            target_bloom = blooms_by_name[item.bloom_level.strip().lower()]

        if not target_bloom:
            errors.append(BulkUploadRowError(
                row_index=row_num,
                question_text=q_text[:40],
                error=f"Bloom level '{item.bloom_level or item.bloom_level_id}' not found",
            ))
            continue

        # Validate marks and difficulty
        marks = item.marks if item.marks >= 1 else 1
        diff = (item.difficulty or "medium").strip().lower()
        if diff not in {"easy", "medium", "hard"}:
            diff = "medium"

        # Create question record
        new_q = Question(
            subject_id=target_subject.id,
            unit_id=target_unit.id,
            bloom_level_id=target_bloom.id,
            question_text=q_text,
            question_type=item.question_type or "Short Answer",
            marks=marks,
            difficulty=diff,
            answer=item.answer,
            explanation=item.explanation,
        )
        db.add(new_q)
        created_questions.append(new_q)

    db.commit()
    for q in created_questions:
        db.refresh(q)

    return BulkQuestionUploadResponse(
        total_submitted=len(items),
        successful_count=len(created_questions),
        failed_count=len(errors),
        created_questions=[QuestionResponse.model_validate(q) for q in created_questions],
        errors=errors,
    )

