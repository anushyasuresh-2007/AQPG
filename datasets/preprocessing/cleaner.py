"""
cleaner.py — Text cleaning utilities for AQPG preprocessing pipeline.

All text-level operations live here:
  - Encoding fixes
  - Whitespace normalization
  - Question/answer validation
  - Context truncation

Import this in every preprocessing script.
"""

import re
import unicodedata
from typing import Optional

from config import (
    ENCODING_FIXES,
    MIN_QUESTION_LENGTH,
    MAX_QUESTION_LENGTH,
    MAX_CONTEXT_LENGTH,
    MAX_ANSWER_LENGTH,
)


# ─── Core Text Cleaner ─────────────────────────────────────────────────────────

def fix_encoding(text: str) -> str:
    """
    Fix common encoding corruption (Windows-1252 mojibake, BOM, replacement chars).
    This does NOT change meaning — only repairs broken byte sequences.
    """
    if not isinstance(text, str):
        return ""
    for bad, good in ENCODING_FIXES.items():
        text = text.replace(bad, good)
    # Normalize unicode (e.g. combining characters, NFKC normalization)
    text = unicodedata.normalize("NFKC", text)
    return text


def normalize_whitespace(text: str) -> str:
    """
    Collapse multiple spaces/tabs/newlines into a single space.
    Strip leading/trailing whitespace.
    """
    if not isinstance(text, str):
        return ""
    # Replace all whitespace sequences (including \n, \t, \r) with single space
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_text(text: str) -> str:
    """
    Full cleaning pipeline for any text field:
      1. Fix encoding corruption
      2. Normalize whitespace
    Returns empty string if input is None or non-string.
    """
    if text is None or not isinstance(text, str):
        return ""
    text = fix_encoding(text)
    text = normalize_whitespace(text)
    return text


def clean_question(text: str) -> str:
    """
    Clean a question string.
    Additional rules specific to questions:
      - Remove leading numbering (e.g. "1. ", "Q1:", "(1)")
      - Ensure question ends with "?" or preserve as-is
    """
    text = clean_text(text)
    # Remove leading question numbering like "1.", "Q1:", "(1)", "1)"
    text = re.sub(r"^[\(\[]?\d+[\.\)\]]\s*", "", text)
    text = re.sub(r"^Q\d+[.:]\s*", "", text, flags=re.IGNORECASE)
    return text.strip()


def clean_answer(text: str) -> str:
    """
    Clean an answer string.
    Preserves multi-line step-by-step solutions.
    """
    if text is None or not isinstance(text, str):
        return ""
    text = fix_encoding(text)
    # Normalize but preserve newlines (important for step-by-step answers)
    text = re.sub(r"[ \t]+", " ", text)          # collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)        # collapse excess blank lines
    return text.strip()


def clean_context(text: str) -> str:
    """
    Clean a passage/context string.
    Truncates to MAX_CONTEXT_LENGTH if necessary.
    """
    text = clean_text(text)
    if len(text) > MAX_CONTEXT_LENGTH:
        text = text[:MAX_CONTEXT_LENGTH].rsplit(" ", 1)[0] + "..."
    return text


# ─── Validation ────────────────────────────────────────────────────────────────

def is_valid_question(text: str) -> tuple[bool, str]:
    """
    Check whether a question string is usable.
    Returns (is_valid: bool, reason: str).

    Invalid if:
      - Empty or None
      - Too short (< MIN_QUESTION_LENGTH characters)
      - Too long (> MAX_QUESTION_LENGTH characters) — these are flagged, not dropped
      - Contains only punctuation / digits
      - Is a URL or HTML fragment
      - Looks like a template placeholder ("___", "???", ".....")
    """
    if not text or not isinstance(text, str):
        return False, "empty"

    t = text.strip()

    if len(t) < MIN_QUESTION_LENGTH:
        return False, f"too_short ({len(t)} chars)"

    # Only punctuation or numbers
    if re.fullmatch(r"[\W\d\s]+", t):
        return False, "no_alphabetic_content"

    # HTML tags
    if re.search(r"<[a-zA-Z][^>]*>", t):
        return False, "contains_html"

    # URL only
    if re.fullmatch(r"https?://\S+", t):
        return False, "is_url"

    # Pure placeholder
    if re.fullmatch(r"[_\?\.]{3,}", t):
        return False, "placeholder_only"

    return True, "ok"


def is_valid_answer(text: Optional[str]) -> bool:
    """
    Basic answer validation — just checks it's not empty when present.
    Answers are allowed to be NULL (some datasets don't have them).
    """
    if text is None:
        return True   # NULL is allowed
    return bool(text.strip())


def validate_options(options_dict: Optional[dict]) -> tuple[bool, str]:
    """
    Validate MCQ options dictionary.
    Must have at least A and B, all values non-empty.
    """
    if options_dict is None:
        return True, "ok"   # NULL options are allowed for non-MCQ

    required = {"A", "B"}
    if not required.issubset(options_dict.keys()):
        return False, "missing_required_options_A_or_B"

    for key, val in options_dict.items():
        if not isinstance(val, str) or not val.strip():
            return False, f"empty_option_{key}"

    return True, "ok"


# ─── Specific Cleaners ─────────────────────────────────────────────────────────

def clean_bloom_question(raw_question: str) -> str:
    """
    Extra cleaning for questions from the Bloom's taxonomy CSV.
    These questions sometimes have trailing context clues in parentheses
    that are not part of the question itself.
    """
    text = clean_question(raw_question)
    # Remove trailing citations like (Smith, 2010) that are not question content
    text = re.sub(r"\([A-Z][a-z]+,?\s+\d{4}\)\s*$", "", text).strip()
    return text


def clean_gsm8k_question(raw_question: str) -> str:
    """Cleaning for GSM8K word problems."""
    text = clean_question(raw_question)
    # Fix smart quotes that GSM8K sometimes has
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    return text


def clean_gsm8k_answer(raw_answer: str) -> str:
    """
    Clean GSM8K socratic-format answer.
    Preserves the step structure: "Sub-question? ** computation. #### final"
    Fixes encoding and collapses whitespace within each line.
    """
    if not isinstance(raw_answer, str):
        return ""
    text = fix_encoding(raw_answer)
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Clean each line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line)  # remove blank lines
    return text


def extract_gsm8k_final_answer(answer_text: str) -> Optional[str]:
    """
    Extract the final numeric answer from a GSM8K answer string.
    The format is: step-by-step... #### FINAL_NUMBER
    Returns the final number as a string, or None if not found.
    """
    match = re.search(r"####\s*(.+)$", answer_text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None


def count_computation_steps(answer_text: str) -> int:
    """
    Count the number of <<...>> computation markers in a GSM8K answer.
    Used to filter for curated subset (Decision 3B: max 3 steps).
    """
    return len(re.findall(r"<<[^>]+>>", answer_text))


def clean_eduqg_context(raw_context: str) -> str:
    """
    Clean EduQG hl_sentences / chapter_text context.
    Removes <hl> tags, normalizes whitespace.
    """
    text = fix_encoding(raw_context)
    # Remove <hl> highlight tags
    text = re.sub(r"</?hl>", " ", text)
    text = normalize_whitespace(text)
    if len(text) > MAX_CONTEXT_LENGTH:
        text = text[:MAX_CONTEXT_LENGTH].rsplit(" ", 1)[0] + "..."
    return text


def build_options_json(a: str, b: str, c: str, d: str,
                       e: Optional[str] = None) -> Optional[str]:
    """
    Build a JSON string {"A":..., "B":..., "C":..., "D":...} from option values.
    Drops option E unless it is distinct from all other options.
    Returns None if A and B are both empty.
    """
    import json

    opts = {}
    for label, val in [("A", a), ("B", b), ("C", c), ("D", d)]:
        v = clean_text(str(val)) if val is not None else ""
        if v:
            opts[label] = v

    # Add E only if it's distinct
    if e is not None:
        e_clean = clean_text(str(e))
        if e_clean and e_clean not in opts.values():
            opts["E"] = e_clean

    if "A" not in opts or "B" not in opts:
        return None

    return json.dumps(opts, ensure_ascii=False)


def build_options_json_from_list(choices: list) -> Optional[str]:
    """
    Build options JSON from a list of choice strings (EduQG JSON format).
    Labels as A, B, C, D, E automatically.
    """
    import json

    labels = ["A", "B", "C", "D", "E"]
    opts = {}
    for i, choice in enumerate(choices):
        if i >= len(labels):
            break
        v = clean_text(str(choice)) if choice is not None else ""
        if v:
            opts[labels[i]] = v

    if "A" not in opts or "B" not in opts:
        return None

    return json.dumps(opts, ensure_ascii=False)
