"""Pydantic schemas for Curriculum, Boards, Academic Years, Classes, and Streams."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class BoardResponse(BaseModel):
    id: int
    code: str
    name: str
    state: str
    website_url: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AcademicYearResponse(BaseModel):
    id: int
    board_id: int
    year_code: str
    is_current: bool

    model_config = ConfigDict(from_attributes=True)


class AcademicClassResponse(BaseModel):
    id: int
    board_id: int
    class_code: str
    class_number: int

    model_config = ConfigDict(from_attributes=True)


class StreamResponse(BaseModel):
    id: int
    class_id: int
    stream_name: str

    model_config = ConfigDict(from_attributes=True)


class TopicResponse(BaseModel):
    id: int
    unit_id: int
    topic_name: str
    topic_number: Optional[int] = None
    description: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CurriculumSyncRequest(BaseModel):
    board: str = Field(default="cbse", description="Board code: 'cbse' or 'tnsb'")
    academic_year: str = Field(default="2026-27", description="Academic session year")
    classes: Optional[List[int]] = None


class CurriculumSyncLogResponse(BaseModel):
    id: int
    board_code: str
    academic_year: str
    classes_synced: str
    subjects_count: int
    units_count: int
    status: str
    details: Optional[str] = None
    source_url: Optional[str] = None
    synced_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurriculumStatusResponse(BaseModel):
    boards: List[BoardResponse]
    total_subjects: int
    total_units: int
    sync_logs: List[CurriculumSyncLogResponse]
