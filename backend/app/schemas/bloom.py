"""Pydantic schemas for Bloom taxonomy levels."""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BloomCreate(BaseModel):
    """Schema for creating a Bloom level."""

    model_config = ConfigDict(str_strip_whitespace=True)

    level_name: str = Field(min_length=1, max_length=100)


class BloomUpdate(BaseModel):
    """Schema for updating a Bloom level."""

    level_name: Optional[str] = Field(default=None, min_length=1, max_length=100)


class BloomResponse(BaseModel):
    """Schema for returning a Bloom level."""

    id: int
    level_name: str

    model_config = ConfigDict(from_attributes=True)
