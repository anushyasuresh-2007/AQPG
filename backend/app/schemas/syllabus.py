"""Schemas for AI-powered syllabus importer."""

from pydantic import BaseModel


class SyllabusFetchRequest(BaseModel):
    """Request schema for fetching syllabus chapters."""

    subject_id: int


class SyllabusFetchResponse(BaseModel):
    """Response schema for returning list of syllabus chapters/units."""

    units: list[str]
