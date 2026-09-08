"""SQLAlchemy model for Academic Years (e.g. 2026-27)."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class AcademicYear(Base):
    """Represents an academic session/year for a board."""

    __tablename__ = "academic_years"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    year_code = Column(String(50), nullable=False)  # e.g. "2026-27"
    is_current = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    board = relationship("Board", back_populates="academic_years")
    subjects = relationship("Subject", back_populates="academic_year_rel")
    questions = relationship("Question", back_populates="academic_year_rel")
