"""Pydantic schemas for subject data."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    @field_validator("subject_code", mode="after")
    @classmethod
    def format_subject_code(cls, v: Optional[str], info) -> Optional[str]:
        if not v:
            return v
        board = info.data.get("board", "")
        class_name = info.data.get("class_name", "")
        subject_name = info.data.get("subject_name", "")
        if board and ("TN" in str(board).upper() or "TAMIL" in str(board).upper()):
            from app.services.curriculum.tn_board_importer import resolve_tnsb_subject_code
            cn_lower = str(class_name).lower()
            c_num = 12 if ("12" in cn_lower or "xii" in cn_lower) else (10 if ("10" in cn_lower or "x" in cn_lower) else None)
            resolved = resolve_tnsb_subject_code(v, class_number=c_num, subject_name=subject_name)
            return resolved or v
        return v

