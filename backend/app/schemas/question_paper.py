from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QuestionPaperRequest(BaseModel):
    """Schema for requesting a generated question paper."""

    model_config = ConfigDict(str_strip_whitespace=True)

    board: Optional[str] = Field(default=None, max_length=100)
    class_name: Optional[str] = Field(default=None, max_length=50)
    board_id: Optional[int] = None
    academic_year_id: Optional[int] = None
    class_id: Optional[int] = None
    stream_id: Optional[int] = None
    subject_id: int
    units: List[int] = Field(default_factory=list)
    unit_ids: Optional[List[int]] = None
    topic_ids: Optional[List[int]] = None
    total_marks: int = Field(ge=1)
    number_of_questions: Optional[int] = Field(default=None, ge=1)
    difficulty: Optional[str] = Field(default="medium")
    difficulty_distribution: Optional[Dict[str, int]] = Field(default_factory=lambda: {"easy": 30, "medium": 50, "hard": 20})
    bloom_distribution: Dict[str, int]
    question_types: Optional[List[str]] = None
    source_mode: Optional[str] = Field(default=None)  # "hybrid", "bank", "ai"
    use_ai: Optional[bool] = Field(default=None)
    allow_ai_fallback: Optional[bool] = Field(default=False)




    @model_validator(mode="before")
    @classmethod
    def unify_units(cls, data: dict):
        if isinstance(data, dict):
            # Accept unit_ids if units is missing or empty
            if "unit_ids" in data and ("units" not in data or not data["units"]):
                data["units"] = data["unit_ids"]
        return data


class BlueprintSummaryItem(BaseModel):
    """Summary of marks and question counts allocated per Bloom level."""

    bloom: str
    required_percentage: int
    required_marks: int
    generated_marks: int
    required_questions: Optional[int] = None
    generated_questions: int


class GeneratedQuestion(BaseModel):
    """Schema for a single selected question in the generated paper."""

    question_id: int
    question: str
    marks: int
    bloom: str
    difficulty: Optional[str] = "medium"
    question_type: Optional[str] = "Short Answer"
    unit_id: Optional[int] = None
    unit_name: Optional[str] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None


class QuestionPaperResponse(BaseModel):
    """Schema for returning the generated question paper."""

    id: Optional[int] = None
    paper_id: Optional[str] = None
    title: Optional[str] = None
    total_marks: int
    total_questions: Optional[int] = None
    questions: List[GeneratedQuestion]
    subject_name: Optional[str] = None
    board: Optional[str] = None
    class_name: Optional[str] = None
    unit_names: Optional[str] = None
    blueprint_summary: Optional[List[BlueprintSummaryItem]] = None
    source: Optional[str] = "Hybrid"

    model_config = ConfigDict(from_attributes=True)



