"""Pydantic schemas for unit data."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UnitCreate(BaseModel):
    """Schema for creating a unit."""

    model_config = ConfigDict(str_strip_whitespace=True)

    subject_id: int
    unit_name: str = Field(min_length=1, max_length=100)


class UnitUpdate(BaseModel):
    """Schema for updating a unit."""

    subject_id: Optional[int] = None
    unit_name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class UnitResponse(BaseModel):
    """Schema for returning unit data."""

    id: int
    subject_id: int
    unit_name: str

    model_config = ConfigDict(from_attributes=True)
