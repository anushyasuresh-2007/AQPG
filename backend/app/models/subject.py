"""SQLAlchemy model for curriculum subjects."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Subject(Base):
    """Represents a subject belonging to a board and academic class."""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    subject_name = Column(String(150), nullable=False, index=True)
    class_name = Column(String(100), nullable=False)
    board = Column(String(100), nullable=False)

    # Curriculum Catalog Links
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=True, index=True)
    academic_year_id = Column(Integer, ForeignKey("academic_years.id"), nullable=True, index=True)
    class_id = Column(Integer, ForeignKey("academic_classes.id"), nullable=True, index=True)
    stream_id = Column(Integer, ForeignKey("streams.id"), nullable=True, index=True)
    subject_code = Column(String(50), nullable=True, index=True)  # e.g. "041", "086"
    subject_type = Column(String(50), default="core", nullable=False)  # "core", "elective", "language", "skill"
    source_url = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    last_synced_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    # Relationships
    board_rel = relationship("Board", back_populates="subjects")
    academic_year_rel = relationship("AcademicYear", back_populates="subjects")
    academic_class_rel = relationship("AcademicClass", back_populates="subjects")
    stream_rel = relationship("Stream", back_populates="subjects")

    units = relationship("Unit", back_populates="subject", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="subject", cascade="all, delete-orphan")
