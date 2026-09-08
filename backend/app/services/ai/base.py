"""Base interfaces for multi-provider AI Question Generation."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AIQuestionPrompt:
    board: str
    class_name: str
    subject_name: str
    unit_name: str
    topic_name: Optional[str]
    marks: int
    difficulty: str  # "easy", "medium", "hard"
    bloom_level: str  # "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"
    question_type: str  # "MCQ", "Short Answer", "Long Answer", "Numerical", "Application Based", etc.


@dataclass
class GeneratedQuestionResult:
    question_text: str
    answer: str
    explanation: Optional[str]
    question_type: str
    marks: int
    difficulty: str
    bloom: str
    unit_name: str
    topic_name: Optional[str] = None
    numerical_data: Optional[str] = None
    application_context: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers (Gemini, OpenAI, etc.)."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider has active API credentials configured."""
        pass

    @abstractmethod
    def generate_question(self, prompt: AIQuestionPrompt) -> Optional[GeneratedQuestionResult]:
        """Generate a single syllabus-aligned, subject-specific question."""
        pass

    @abstractmethod
    def generate_batch(self, prompts: List[AIQuestionPrompt]) -> List[GeneratedQuestionResult]:
        """Generate multiple questions in batch according to blueprint."""
        pass
