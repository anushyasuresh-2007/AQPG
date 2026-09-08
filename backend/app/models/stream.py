"""SQLAlchemy model for Educational Streams (e.g. Science, Commerce, Humanities)."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Stream(Base):
    """Represents an academic stream for senior secondary classes."""

    __tablename__ = "streams"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("academic_classes.id"), nullable=False, index=True)
    stream_name = Column(String(100), nullable=False)  # e.g. "Science", "Commerce", "General"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    academic_class = relationship("AcademicClass", back_populates="streams")
    subjects = relationship("Subject", back_populates="stream_rel")
