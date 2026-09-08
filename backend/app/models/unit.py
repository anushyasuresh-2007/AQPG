"""SQLAlchemy model for subject syllabus units/chapters."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class Unit(Base):
    """Represents a unit/chapter belonging to a curriculum subject."""

    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False, index=True)
    unit_name = Column(String(255), nullable=False)
    unit_number = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(255), nullable=True)
    active = Column(Boolean, default=True, nullable=False)

    subject = relationship("Subject", back_populates="units")
    topics = relationship("Topic", back_populates="unit", cascade="all, delete-orphan")
    questions = relationship("Question", back_populates="unit", cascade="all, delete-orphan")
