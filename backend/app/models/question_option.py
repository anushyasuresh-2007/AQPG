"""SQLAlchemy model for MCQ question options (Decision 1B).

Each question_options row represents one answer choice (A/B/C/D)
for a question with question_type = 'MCQ'.
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database.database import Base


class QuestionOption(Base):
    """Represents one MCQ answer choice for a question."""

    __tablename__ = "question_options"

    id           = Column(Integer, primary_key=True, index=True)
    question_id  = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    option_label = Column(String(5), nullable=False,
                          comment="A, B, C, D, or E")
    option_text  = Column(Text, nullable=False)
    is_correct   = Column(Boolean, nullable=False, default=False,
                          comment="True if this is the correct answer")

    # Relationship back to Question
    question = relationship("Question", back_populates="options")
