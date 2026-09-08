"""SQLAlchemy model for persistently storing generated question papers."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class GeneratedPaper(Base):
    """Represents a generated examination paper with full metadata and questions."""

    __tablename__ = "generated_papers"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(String(100), unique=True, nullable=False, index=True)  # e.g. "QP-2026-CBSE-MATH10-01"
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True, index=True)
    class_id = Column(Integer, ForeignKey("academic_classes.id"), nullable=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True, index=True)

    title = Column(String(255), nullable=False)
    board_name = Column(String(100), nullable=False)
    class_name = Column(String(100), nullable=False)
    subject_name = Column(String(150), nullable=False)
    unit_names = Column(Text, nullable=True)

    total_marks = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    difficulty = Column(String(50), nullable=False, default="Medium")
    source = Column(String(50), nullable=False, default="Hybrid")  # "Question Bank", "AI Generator", "Hybrid"

    # Serialized JSON structures
    questions_data = Column(Text, nullable=False)  # JSON array of question dicts
    sections_data = Column(Text, nullable=True)  # JSON sections breakdown
    blueprint_summary = Column(Text, nullable=True)  # JSON blueprint summary

    status = Column(String(50), nullable=False, default="generated")  # "generated", "saved", "archived"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
