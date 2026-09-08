"""Pydantic schemas for subject data."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class SubjectCreate(BaseModel):
    """Schema for creating a subject."""

    model_config = ConfigDict(str_strip_whitespace=True)

    subject_name: str = Field(min_length=1, max_length=100)
    class_name: str = Field(min_length=1, max_length=50)
    board: str = Field(min_length=1, max_length=50)
    board_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    subject_code: Optional[str] = None
    source_url: Optional[str] = None


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""

    subject_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    class_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    board: Optional[str] = Field(default=None, min_length=1, max_length=50)
    board_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    subject_code: Optional[str] = None
    source_url: Optional[str] = None


class SubjectResponse(BaseModel):
    """Schema for returning subject data."""

    id: int
    subject_name: str
    class_name: str
    board: str
    board_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    subject_code: Optional[str] = None
    source_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

