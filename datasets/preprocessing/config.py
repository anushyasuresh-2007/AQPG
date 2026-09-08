"""
config.py — Central configuration for AQPG preprocessing pipeline.

All constants, mappings, allowed values, and file paths live here.
Import this in every preprocessing script; never hardcode values elsewhere.

Run from project root:  datasets\\preprocessing\\config.py  (import only)
"""

from pathlib import Path

# ─── Project Paths ─────────────────────────────────────────────────────────────
# All paths are relative to the PROJECT ROOT (c:\\...\\AQPG)
PROJECT_ROOT   = Path(__file__).resolve().parent.parent.parent   # AQPG/
DATASETS_DIR   = PROJECT_ROOT / "datasets"
EXTRACTED_DIR  = DATASETS_DIR / "extracted"
PREPROCESSED_DIR = DATASETS_DIR / "preprocessed"
UNIFIED_DIR    = DATASETS_DIR / "unified"

# Input files
BLOOM_CSV      = EXTRACTED_DIR / "bloom"     / "blooms_taxonomy_dataset.csv"
EDUQG_CSV      = EXTRACTED_DIR / "eduqg"    / "eduqg_llm_formatted.csv"
EDUQG_TRAIN_JSON = EXTRACTED_DIR / "eduqg"  / "eduqg_train.json"
EDUQG_VAL_JSON   = EXTRACTED_DIR / "eduqg"  / "eduqg_val.json"
REASONING_MAIN_TRAIN    = EXTRACTED_DIR / "reasoning" / "main_train.csv"
REASONING_MAIN_TEST     = EXTRACTED_DIR / "reasoning" / "main_test.csv"
REASONING_SOCRATIC_TRAIN = EXTRACTED_DIR / "reasoning" / "socratic_train.csv"
REASONING_SOCRATIC_TEST  = EXTRACTED_DIR / "reasoning" / "socratic_test.csv"

# Output files (preprocessed — per-dataset)
OUT_BLOOM_PREPROCESSED   = PREPROCESSED_DIR / "bloom_preprocessed.csv"
OUT_EDUQG_CSV_PREPROCESSED  = PREPROCESSED_DIR / "eduqg_csv_preprocessed.csv"
OUT_EDUQG_JSON_PREPROCESSED = PREPROCESSED_DIR / "eduqg_json_preprocessed.csv"
OUT_REASONING_PREPROCESSED  = PREPROCESSED_DIR / "reasoning_preprocessed.csv"

# Output files (unified — all datasets merged)
OUT_UNIFIED              = UNIFIED_DIR / "unified_questions.csv"
OUT_BLOOM_CLASSIFIER     = UNIFIED_DIR / "bloom_classifier_data.csv"
OUT_QGEN_TRAIN           = UNIFIED_DIR / "qgen_train_data.csv"
OUT_QGEN_VAL             = UNIFIED_DIR / "qgen_val_data.csv"
OUT_NUMERICAL            = UNIFIED_DIR / "numerical_questions.csv"
OUT_MAPPING_LOG          = UNIFIED_DIR / "mapping_log.csv"

# ─── Unified Schema Column Order ───────────────────────────────────────────────
UNIFIED_COLUMNS = [
    "id",
    "board",
    "class_level",
    "subject",
    "chapter",
    "unit",
    "topic",
    "context",
    "question",
    "question_type",
    "options",          # JSON string {"A":..., "B":..., "C":..., "D":...} or NULL
    "answer",
    "marks",
    "bloom_level",
    "difficulty",
    "source",
    "source_dataset",
]

# ─── Bloom's Taxonomy Mappings ─────────────────────────────────────────────────
BLOOM_CODE_TO_LABEL = {
    "BT1": "Remember",
    "BT2": "Understand",
    "BT3": "Apply",
    "BT4": "Analyze",
    "BT5": "Evaluate",
    "BT6": "Create",
}

BLOOM_VALID_LABELS = set(BLOOM_CODE_TO_LABEL.values())

# Also handle any raw text labels that datasets might use
BLOOM_TEXT_ALIASES = {
    "remember":    "Remember",
    "knowledge":   "Remember",
    "recall":      "Remember",
    "understand":  "Understand",
    "comprehension": "Understand",
    "understanding": "Understand",
    "apply":       "Apply",
    "application": "Apply",
    "analyze":     "Analyze",
    "analysis":    "Analyze",
    "evaluate":    "Evaluate",
    "evaluation":  "Evaluate",
    "create":      "Create",
    "synthesis":   "Create",
    "creation":    "Create",
}

# ─── Question Type Mappings ────────────────────────────────────────────────────
VALID_QUESTION_TYPES = [
    "MCQ",
    "Very Short Answer",
    "Short Answer",
    "Long Answer",
    "Numerical",
    "Application Based",
    "Case Study",
]

# Default marks by question type
MARKS_BY_TYPE = {
    "MCQ":                1,
    "Very Short Answer":  1,
    "Short Answer":       2,
    "Numerical":          2,
    "Application Based":  3,
    "Long Answer":        5,
    "Case Study":         4,
}

# ─── Difficulty Levels ─────────────────────────────────────────────────────────
VALID_DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

# Bloom → default difficulty heuristic
BLOOM_TO_DIFFICULTY = {
    "Remember":   "Easy",
    "Understand": "Easy",
    "Apply":      "Medium",
    "Analyze":    "Medium",
    "Evaluate":   "Hard",
    "Create":     "Hard",
}

# ─── EduQG: Books allowed for import (Decision 4B — biology only) ──────────────
EDUQG_ALLOWED_BOOKS = {
    "biology",
    "microbiology",
    "anatomy_and_physiology",
}

# EduQG bname → subject mapping
BNAME_TO_SUBJECT = {
    "biology":                                            "Biology",
    "microbiology":                                       "Biology",
    "anatomy_and_physiology":                             "Biology",
    "principles_of_accounting,_volume_1:_financial_accounting": "Commerce",
    "principles_of_accounting,_volume_2:_managerial_accounting": "Commerce",
    "business_ethics":                                    "Commerce",
    "business_law_i_essentials":                          "Commerce",
    "introduction_to_sociology":                          "Social Science",
    "psychology":                                         "Social Science",
    "american_government":                                "Social Science",
    "u.s._history":                                       "Social Science",
    "introduction_to_intellectual_property":              "General",
}

# ─── Reasoning (GSM8K): Curated Subset Filter (Decision 3B) ───────────────────
# Max number of <<computation=result>> markers in the answer.
# 1–3 markers = 1–3 arithmetic steps = Class 4–8 level word problems.
# > 5 markers = too complex, reject.
REASONING_MAX_COMPUTATION_STEPS = 3

# ─── Text Cleaning Settings ────────────────────────────────────────────────────
MIN_QUESTION_LENGTH = 10          # characters — shorter than this = invalid
MAX_QUESTION_LENGTH = 2000        # characters — longer than this = truncated/flagged
MAX_CONTEXT_LENGTH  = 2000        # characters for context/passage fields
MAX_ANSWER_LENGTH   = 5000        # characters for answer (socratic can be long)

# Encoding issues: replace common mojibake characters
ENCODING_FIXES = {
    "\u0093": '"',   # left double quotation mark (Windows-1252)
    "\u0094": '"',   # right double quotation mark
    "\u0091": "'",   # left single quotation mark
    "\u0092": "'",   # right single quotation mark (apostrophe)
    "\u0096": "–",   # en dash
    "\u0097": "—",   # em dash
    "\u0085": "...", # horizontal ellipsis
    "â€™":    "'",
    "â€œ":    '"',
    "â€":     '"',
    "â€"":    "—",
    "\ufffd": "",    # replacement character (bad decode)
    "â": "",
    "ï»¿": "",       # BOM
}

# ─── Source Labels ─────────────────────────────────────────────────────────────
SOURCE_BLOOM   = "Bloom's Taxonomy Dataset (Kaggle)"
SOURCE_EDUQG_CSV  = "EduQG OpenStax MCQ Dataset"
SOURCE_EDUQG_JSON = "EduQG OpenStax JSON Dataset"
SOURCE_REASONING  = "GSM8K Grade School Math (OpenAI)"

SOURCE_DATASET_BLOOM        = "blooms_taxonomy_dataset.csv"
SOURCE_DATASET_EDUQG_CSV    = "eduqg_llm_formatted.csv"
SOURCE_DATASET_EDUQG_TRAIN  = "eduqg_train.json"
SOURCE_DATASET_EDUQG_VAL    = "eduqg_val.json"
SOURCE_DATASET_REASONING_TRAIN = "main_train.csv+socratic_train.csv"
SOURCE_DATASET_REASONING_TEST  = "main_test.csv+socratic_test.csv"
