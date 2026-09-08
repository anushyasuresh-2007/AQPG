"""API endpoint for generating a question paper from the stored question bank."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.database.database import get_db
from app.schemas.question_paper import QuestionPaperRequest, QuestionPaperResponse
from app.services.question_generator import generate_question_paper

router = APIRouter()


@router.post(
    "/generate-paper",
    response_model=QuestionPaperResponse,
    status_code=status.HTTP_200_OK,
    tags=["Question Paper"],
)
def generate_paper(
    payload: QuestionPaperRequest,
    db: Session = Depends(get_db),
    current_user: object = Depends(require_teacher_or_admin),
):
    """Generate a question paper based on curriculum subject, units, and Bloom distribution."""
    try:
        user_id = getattr(current_user, "id", None)
        resolved_source_mode = payload.source_mode
        if not resolved_source_mode:
            if payload.use_ai is True:
                resolved_source_mode = "ai"
            elif payload.allow_ai_fallback:
                resolved_source_mode = "hybrid"
            else:
                resolved_source_mode = "bank"

        result = generate_question_paper(
            db=db,
            board=payload.board,
            class_name=payload.class_name,
            board_id=payload.board_id,
            class_id=payload.class_id,
            stream_id=payload.stream_id,
            subject_id=payload.subject_id,
            selected_units=payload.units,
            total_marks=payload.total_marks,
            bloom_distribution=payload.bloom_distribution,
            number_of_questions=payload.number_of_questions,
            difficulty=payload.difficulty or "medium",
            source_mode=resolved_source_mode,
            use_ai=payload.use_ai,
            user_id=user_id,
        )

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return result


