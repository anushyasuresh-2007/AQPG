"""SQLAlchemy model for Question Bank repository."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Question(Base):
    """Represents a stored or generated question in the Question Bank."""

    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    bloom_level_id = Column(Integer, ForeignKey("bloom_levels.id"), nullable=False, index=True)

    # Curriculum Catalog Hierarchy
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=True, index=True)
    class_id = Column(Integer, ForeignKey("academic_classes.id"), nullable=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), nullable=True, index=True)

    # Question Content & Metadata
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False, default="Short Answer")  # MCQ, Short Answer, Long Answer, Numerical, Application Based, Assertion Reason, Case Study, Problem Solving, Diagram Based, Source Based, Very Short Answer, Essay
    marks = Column(Integer, nullable=False, default=1)
    difficulty = Column(String(50), nullable=False, default="medium")  # "easy", "medium", "hard"
    answer = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)
    numerical_data = Column(Text, nullable=True)  # Optional JSON / data for mathematical calculations
    application_context = Column(Text, nullable=True)  # Real-world or case context

    # Provenance & Moderation
    source = Column(String(200), nullable=True, default="Question Bank")
    source_type = Column(String(50), nullable=False, default="teacher")  # "teacher", "ai", "official_sample", "imported"
    is_ai_generated = Column(Boolean, default=False, nullable=False)
    approved = Column(Boolean, default=True, nullable=False)
    status = Column(String(50), nullable=False, default="approved")  # "approved", "draft", "rejected"
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    subject = relationship("Subject", back_populates="questions")
    unit = relationship("Unit", back_populates="questions")
    bloom_level = relationship("Bloom", back_populates="questions")
    board_rel = relationship("Board", back_populates="questions")
    academic_year_rel = relationship("AcademicYear", back_populates="questions")
    academic_class_rel = relationship("AcademicClass", back_populates="questions")
    topic = relationship("Topic", back_populates="questions")
    options = relationship("QuestionOption", back_populates="question",
                          cascade="all, delete-orphan",
                          order_by="QuestionOption.option_label")
