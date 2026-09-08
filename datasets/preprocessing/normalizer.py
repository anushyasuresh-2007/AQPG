"""
normalizer.py — Value normalization for Bloom labels, question types, marks, difficulty.

All field-level normalization (not text cleaning) lives here.
Import this in every preprocessing script.
"""

import re
from typing import Optional

from config import (
    BLOOM_CODE_TO_LABEL,
    BLOOM_TEXT_ALIASES,
    BLOOM_VALID_LABELS,
    BLOOM_TO_DIFFICULTY,
    VALID_QUESTION_TYPES,
    MARKS_BY_TYPE,
    VALID_DIFFICULTY_LEVELS,
)


# ─── Bloom Level Normalization ─────────────────────────────────────────────────

def normalize_bloom_label(raw: Optional[str]) -> Optional[str]:
    """
    Convert any raw Bloom label into the standard 6-level label.

    Handles:
      - BT codes: "BT1", "BT2", ..., "BT6"
      - Full names: "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"
      - Aliases: "Knowledge", "Comprehension", "Application", "Analysis", "Synthesis"
      - Case-insensitive

    Returns None if unrecognized.
    """
    if raw is None or not isinstance(raw, str):
        return None

    raw_stripped = raw.strip()

    # Direct BT code match (BT1–BT6)
    code_upper = raw_stripped.upper()
    if code_upper in BLOOM_CODE_TO_LABEL:
        return BLOOM_CODE_TO_LABEL[code_upper]

    # Full name / alias match (case-insensitive)
    lower = raw_stripped.lower()
    if lower in BLOOM_TEXT_ALIASES:
        return BLOOM_TEXT_ALIASES[lower]

    # Already a valid label
    if raw_stripped in BLOOM_VALID_LABELS:
        return raw_stripped

    # Partial match (e.g. "BT-1", "Bloom1", "level 1")
    match = re.search(r"[bB][tT]?[-_\s]?([1-6])", raw_stripped)
    if match:
        code = f"BT{match.group(1)}"
        return BLOOM_CODE_TO_LABEL.get(code)

    return None  # Unrecognized — caller should log and set NULL


# ─── Question Type Normalization ───────────────────────────────────────────────

def normalize_question_type(
    raw: Optional[str] = None,
    has_options: bool = False,
    has_computation_markers: bool = False,
    question_text: Optional[str] = None,
    bloom_level: Optional[str] = None,
) -> str:
    """
    Determine the normalized question type.

    Priority order:
      1. If has_options → MCQ
      2. If has_computation_markers (<<>>) → Numerical
      3. Use raw label if provided (map to standard)
      4. Infer from question_text length + bloom_level heuristic
      5. Default: "Short Answer"
    """
    # Rule 1: Options present → MCQ
    if has_options:
        return "MCQ"

    # Rule 2: Computation markers in answer → Numerical
    if has_computation_markers:
        return "Numerical"

    # Rule 3: Normalize raw label
    if raw:
        raw_lower = raw.lower().strip()
        _type_aliases = {
            "mcq":                      "MCQ",
            "multiple choice":          "MCQ",
            "multiple_choice":          "MCQ",
            "very short answer":        "Very Short Answer",
            "very_short_answer":        "Very Short Answer",
            "vsa":                      "Very Short Answer",
            "short answer":             "Short Answer",
            "short_answer":             "Short Answer",
            "sa":                       "Short Answer",
            "long answer":              "Long Answer",
            "long_answer":              "Long Answer",
            "la":                       "Long Answer",
            "essay":                    "Long Answer",
            "numerical":                "Numerical",
            "numerical problem":        "Numerical",
            "problem solving":          "Numerical",
            "application based":        "Application Based",
            "application_based":        "Application Based",
            "application":              "Application Based",
            "case study":               "Case Study",
            "case_study":               "Case Study",
            "passage based":            "Case Study",
        }
        if raw_lower in _type_aliases:
            return _type_aliases[raw_lower]
        # Check if any alias is a substring
        for alias, qtype in _type_aliases.items():
            if alias in raw_lower:
                return qtype

    # Rule 4: Heuristic from bloom level
    if bloom_level in ("Evaluate", "Create"):
        return "Long Answer"
    if bloom_level in ("Remember", "Understand") and question_text:
        if len(question_text) < 80:
            return "Very Short Answer"

    # Rule 4b: Heuristic from question text length
    if question_text:
        if len(question_text) < 60:
            return "Very Short Answer"
        if len(question_text) < 200:
            return "Short Answer"

    # Default
    return "Short Answer"


# ─── Marks Normalization ───────────────────────────────────────────────────────

def normalize_marks(
    raw_marks=None,
    question_type: Optional[str] = None,
) -> int:
    """
    Normalize marks to an integer in {1, 2, 3, 4, 5}.

    If raw_marks is provided and valid → use it.
    Otherwise fall back to type-based default.
    """
    if raw_marks is not None:
        try:
            m = int(float(str(raw_marks)))
            if m in (1, 2, 3, 4, 5):
                return m
        except (ValueError, TypeError):
            pass

    # Type-based default
    if question_type and question_type in MARKS_BY_TYPE:
        return MARKS_BY_TYPE[question_type]

    return 1  # absolute default


# ─── Difficulty Normalization ──────────────────────────────────────────────────

def normalize_difficulty(
    raw: Optional[str] = None,
    bloom_level: Optional[str] = None,
    answer_length: Optional[int] = None,
    computation_steps: Optional[int] = None,
) -> Optional[str]:
    """
    Normalize difficulty to Easy / Medium / Hard.

    If raw is provided and recognized → use it.
    Otherwise use heuristics:
      - Bloom level heuristic
      - Answer length heuristic
      - Computation steps heuristic (for Numerical)

    Returns None if cannot be determined (caller leaves as NULL).
    """
    if raw:
        r = raw.strip().lower()
        if r in ("easy", "simple", "low"):
            return "Easy"
        if r in ("medium", "moderate", "average"):
            return "Medium"
        if r in ("hard", "difficult", "high", "challenging"):
            return "Hard"

    # Bloom heuristic
    if bloom_level and bloom_level in BLOOM_TO_DIFFICULTY:
        return BLOOM_TO_DIFFICULTY[bloom_level]

    # Computation steps heuristic (for numerical)
    if computation_steps is not None:
        if computation_steps <= 1:
            return "Easy"
        if computation_steps <= 3:
            return "Medium"
        return "Hard"

    # Answer length heuristic
    if answer_length is not None:
        if answer_length < 50:
            return "Easy"
        if answer_length < 200:
            return "Medium"
        return "Hard"

    return None  # Cannot determine → NULL


# ─── Subject Normalization ─────────────────────────────────────────────────────

VALID_SUBJECTS = {
    "Mathematics", "Physics", "Chemistry", "Biology", "Science",
    "Social Science", "English", "Computer Science", "Commerce",
    "History", "Geography", "Civics", "Economics", "General",
}

def normalize_subject(raw: Optional[str]) -> Optional[str]:
    """
    Normalize subject name to the standard AQPG subject vocabulary.
    Returns None if unrecognized.
    """
    if not raw:
        return None
    r = raw.strip()
    if r in VALID_SUBJECTS:
        return r
    # Case-insensitive match
    r_lower = r.lower()
    for subj in VALID_SUBJECTS:
        if subj.lower() == r_lower:
            return subj
    return r  # Return as-is (will be validated later during MySQL import)


# ─── ID Generation ─────────────────────────────────────────────────────────────

def make_id(prefix: str, index: int, pad: int = 6) -> str:
    """
    Generate a unified dataset row ID.
    Example: make_id("BLOOM", 42) → "BLOOM_000042"
    """
    return f"{prefix}_{str(index).zfill(pad)}"
