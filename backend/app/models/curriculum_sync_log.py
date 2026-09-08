"""SQLAlchemy model for logging official board curriculum synchronizations."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.database import Base


class CurriculumSyncLog(Base):
    """Logs metadata whenever an official board curriculum is synchronized."""

    __tablename__ = "curriculum_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    board_code = Column(String(50), nullable=False, index=True)
    academic_year = Column(String(50), nullable=False)
    classes_synced = Column(String(200), nullable=False)
    subjects_count = Column(Integer, nullable=False, default=0)
    units_count = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="success")  # "success", "partial", "failed"
    details = Column(Text, nullable=True)
    source_url = Column(String(255), nullable=True)
    synced_at = Column(DateTime, default=datetime.utcnow, nullable=False)
