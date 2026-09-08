"""SQLAlchemy model for syllabus topics within a unit."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Topic(Base):
    """Represents a specific syllabus topic within a unit/chapter."""

    __tablename__ = "topics"

    id = Column(Integer, primary_key=True, index=True)
    unit_id = Column(Integer, ForeignKey("units.id"), nullable=False, index=True)
    topic_name = Column(String(255), nullable=False)
    topic_number = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    unit = relationship("Unit", back_populates="topics")
    questions = relationship("Question", back_populates="topic")
