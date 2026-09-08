"""SQLAlchemy model for Educational Classes/Grades (Class 1 to Class 12)."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class AcademicClass(Base):
    """Represents an academic grade/class (e.g. Class 1 to Class 12)."""

    __tablename__ = "academic_classes"

    id = Column(Integer, primary_key=True, index=True)
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False, index=True)
    class_code = Column(String(50), nullable=False)  # e.g. "Class 10", "Class 12", "Class 1"
    class_number = Column(Integer, nullable=False, index=True)  # 1 to 12
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    board = relationship("Board", back_populates="academic_classes")
    streams = relationship("Stream", back_populates="academic_class", cascade="all, delete-orphan")
    subjects = relationship("Subject", back_populates="academic_class_rel")
    questions = relationship("Question", back_populates="academic_class_rel")
