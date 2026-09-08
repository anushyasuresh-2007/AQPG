"""SQLAlchemy model for Bloom's taxonomy levels."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


class Bloom(Base):
    """Represents a Bloom's taxonomy level used for question classification."""

    __tablename__ = "bloom_levels"

    id = Column(Integer, primary_key=True, index=True)
    level_name = Column(String(50), nullable=False, unique=True)

    questions = relationship("Question", back_populates="bloom_level", cascade="all, delete-orphan")
