"""Base interfaces and data structures for official board curriculum importers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TopicData:
    topic_name: str
    topic_number: Optional[int] = None
    description: Optional[str] = None


@dataclass
class UnitData:
    unit_name: str
    unit_number: Optional[int] = None
    source_url: Optional[str] = None
    topics: List[TopicData] = field(default_factory=list)


@dataclass
class SubjectData:
    subject_name: str
    class_name: str  # e.g. "Class X", "Class XII"
    class_number: int  # e.g. 10, 12
    subject_code: Optional[str] = None  # e.g. "086"
    stream_name: Optional[str] = None  # e.g. "Science", "Commerce", "General"
    source_url: Optional[str] = None
    units: List[UnitData] = field(default_factory=list)


@dataclass
class BoardCurriculumData:
    board_code: str  # "CBSE", "TNSB"
    board_name: str
    state: str
    academic_year: str  # "2026-27"
    source_name: str
    source_url: str
    subjects: List[SubjectData] = field(default_factory=list)


@dataclass
class CurriculumSyncResult:
    board_code: str
    academic_year: str
    classes_synced: List[str]
    subjects_created: int
    subjects_updated: int
    units_created: int
    units_updated: int
    status: str
    message: str


class BaseCurriculumImporter(ABC):
    """Abstract base class for official board curriculum importers."""

    @abstractmethod
    def get_board_code(self) -> str:
        """Return the unique board code (e.g. 'CBSE', 'TNSB')."""
        pass

    @abstractmethod
    def get_board_name(self) -> str:
        """Return full official name of the board."""
        pass

    @abstractmethod
    def get_state(self) -> str:
        """Return jurisdiction / state."""
        pass

    @abstractmethod
    def fetch_curriculum(self, academic_year: str = "2026-27", target_classes: Optional[List[int]] = None) -> BoardCurriculumData:
        """Fetch and parse official curriculum structure."""
        pass
