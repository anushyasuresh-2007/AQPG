"""API endpoints for managing and downloading generated question papers (PDF & DOCX)."""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.v1.endpoints.protected import require_teacher_or_admin
from app.database.database import get_db
from app.models.generated_paper import GeneratedPaper
from app.services.export_service import generate_paper_docx, generate_paper_pdf

router = APIRouter()


@router.get("/generated-papers", tags=["Generated Papers"])
def list_generated_papers(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """List all saved examination question papers."""
    papers = db.query(GeneratedPaper).order_by(GeneratedPaper.id.desc()).offset(skip).limit(limit).all()
    results = []
    for p in papers:
        results.append({
            "id": p.id,
            "paper_id": p.paper_id,
            "title": p.title,
            "board_name": p.board_name,
            "class_name": p.class_name,
            "subject_name": p.subject_name,
            "unit_names": p.unit_names,
            "total_marks": p.total_marks,
            "total_questions": p.total_questions,
            "difficulty": p.difficulty,
            "source": p.source,
            "status": p.status,
            "created_at": p.created_at.isoformat(),
        })
    return results


@router.get("/generated-papers/{paper_id}", tags=["Generated Papers"])
def get_generated_paper_details(
    paper_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Retrieve detailed question paper including questions data and blueprint summary."""
    paper = (
        db.query(GeneratedPaper)
        .filter((GeneratedPaper.paper_id == paper_id) | (GeneratedPaper.id == int(paper_id) if paper_id.isdigit() else False))
        .first()
    )
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found")

    return {
        "id": paper.id,
        "paper_id": paper.paper_id,
        "title": paper.title,
        "board_name": paper.board_name,
        "class_name": paper.class_name,
        "subject_name": paper.subject_name,
        "unit_names": paper.unit_names,
        "total_marks": paper.total_marks,
        "total_questions": paper.total_questions,
        "difficulty": paper.difficulty,
        "source": paper.source,
        "questions": json.loads(paper.questions_data),
        "blueprint_summary": json.loads(paper.blueprint_summary) if paper.blueprint_summary else [],
        "created_at": paper.created_at.isoformat(),
    }


@router.delete("/generated-papers/{paper_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Generated Papers"])
def delete_generated_paper(
    paper_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Delete a saved question paper."""
    paper = (
        db.query(GeneratedPaper)
        .filter((GeneratedPaper.paper_id == paper_id) | (GeneratedPaper.id == int(paper_id) if paper_id.isdigit() else False))
        .first()
    )
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found")

    db.delete(paper)
    db.commit()
    return None


@router.get("/generated-papers/{paper_id}/docx", tags=["Generated Papers"])
def download_paper_docx(
    paper_id: str,
    include_answers: bool = False,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Export and download question paper as Microsoft Word .docx document."""
    paper = (
        db.query(GeneratedPaper)
        .filter((GeneratedPaper.paper_id == paper_id) | (GeneratedPaper.id == int(paper_id) if paper_id.isdigit() else False))
        .first()
    )
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found")

    buf = generate_paper_docx(paper, include_answers=include_answers)
    filename = f"{paper.paper_id}_{'Solutions' if include_answers else 'Paper'}.docx"
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/generated-papers/{paper_id}/pdf", tags=["Generated Papers"])
def download_paper_pdf(
    paper_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Export and download printable Student Question Paper PDF (without answers)."""
    paper = (
        db.query(GeneratedPaper)
        .filter((GeneratedPaper.paper_id == paper_id) | (GeneratedPaper.id == int(paper_id) if paper_id.isdigit() else False))
        .first()
    )
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found")

    buf = generate_paper_pdf(paper, include_answers=False)
    filename = f"{paper.paper_id}_QuestionPaper.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/generated-papers/{paper_id}/solutions-pdf", tags=["Generated Papers"])
def download_solutions_pdf(
    paper_id: str,
    db: Session = Depends(get_db),
    _: object = Depends(require_teacher_or_admin),
):
    """Export and download Teacher Answer Key & Step-by-Step Solutions PDF."""
    paper = (
        db.query(GeneratedPaper)
        .filter((GeneratedPaper.paper_id == paper_id) | (GeneratedPaper.id == int(paper_id) if paper_id.isdigit() else False))
        .first()
    )
    if not paper:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question paper not found")

    buf = generate_paper_pdf(paper, include_answers=True)
    filename = f"{paper.paper_id}_AnswerKey_Solutions.pdf"
    return StreamingResponse(
        buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
