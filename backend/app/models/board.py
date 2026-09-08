"""SQLAlchemy model for Educational Boards (CBSE and State Boards)."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Board(Base):
    """Represents an educational board (e.g. CBSE, Tamil Nadu, Kerala, Karnataka, Maharashtra, AP, Telangana)."""

    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)  # e.g. "CBSE", "TNSB", "KBPE", "KSEEB", "MSBSHSE"
    name = Column(String(200), nullable=False)  # e.g. "Central Board of Secondary Education"
    state = Column(String(100), nullable=False, default="All India")
    website_url = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    academic_years = relationship("AcademicYear", back_populates="board", cascade="all, delete-orphan")
    academic_classes = relationship("AcademicClass", back_populates="board", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="board_rel")
    questions = relationship("Question", back_populates="board_rel")
