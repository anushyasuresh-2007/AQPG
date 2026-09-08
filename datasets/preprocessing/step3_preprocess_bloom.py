"""
step3_preprocess_bloom.py — Preprocess Bloom's Taxonomy Dataset (STEP 3)

SOURCE: datasets/extracted/bloom/blooms_taxonomy_dataset.csv
OUTPUT:
  datasets/preprocessed/bloom_preprocessed.csv   ← cleaned, full record
  datasets/unified/bloom_classifier_data.csv      ← ML training input (question, bloom_level)

WHAT THIS SCRIPT DOES:
  1. Load blooms_taxonomy_dataset.csv
  2. Rename columns: Questions→question, Category→bloom_level
  3. Fix encoding corruption in question text
  4. Remove empty / too-short questions
  5. Normalize Bloom labels: BT1→Remember, BT2→Understand, etc.
  6. Infer question_type from Bloom level + question length heuristic
  7. Assign default marks based on question_type
  8. Assign difficulty from Bloom level heuristic
  9. Remove duplicate questions (exact text)
 10. Add unified schema columns (board, class_level, subject, etc.) as NULL
 11. Save preprocessed CSV and classifier-ready CSV

IMPORTANT:
  - This dataset has NO answers. board/class_level/subject are all NULL.
  - Decision 2A: Do NOT import into MySQL question bank.
  - Only use for Bloom classifier training.

Run from project root:
  backend\\.venv\\Scripts\\python.exe datasets\\preprocessing\\step3_preprocess_bloom.py
"""

import sys
import os
# Allow imports from the preprocessing folder when run as a script
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd

from config import (
    BLOOM_CSV,
    OUT_BLOOM_PREPROCESSED,
    UNIFIED_COLUMNS,
    SOURCE_BLOOM,
    SOURCE_DATASET_BLOOM,
    PREPROCESSED_DIR,
    UNIFIED_DIR,
    OUT_BLOOM_CLASSIFIER,
)
from cleaner import clean_bloom_question, is_valid_question
from normalizer import (
    normalize_bloom_label,
    normalize_question_type,
    normalize_marks,
    normalize_difficulty,
    make_id,
)


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def run():
    print_section("STEP 3 — Preprocessing: bloom/blooms_taxonomy_dataset.csv")

    # ── 1. Load ────────────────────────────────────────────────────────────────
    print(f"\n[1/10] Loading {BLOOM_CSV.name} ...")
    df = pd.read_csv(BLOOM_CSV, low_memory=False)
    print(f"       Loaded {len(df):,} rows × {len(df.columns)} columns")
    print(f"       Original columns: {list(df.columns)}")

    # ── 2. Rename columns ──────────────────────────────────────────────────────
    print("\n[2/10] Renaming columns ...")
    df = df.rename(columns={
        "Questions": "question_raw",
        "Category":  "bloom_raw",
    })

    # ── 3. Fix encoding ────────────────────────────────────────────────────────
    print("\n[3/10] Fixing encoding and cleaning question text ...")
    df["question"] = df["question_raw"].apply(clean_bloom_question)

    # ── 4. Remove invalid questions ────────────────────────────────────────────
    print("\n[4/10] Removing empty / too-short / invalid questions ...")
    validity = df["question"].apply(is_valid_question)
    df["_valid"]  = validity.apply(lambda x: x[0])
    df["_reason"] = validity.apply(lambda x: x[1])

    invalid_mask = ~df["_valid"]
    n_invalid = invalid_mask.sum()
    if n_invalid > 0:
        print(f"       ⚠  Removed {n_invalid} invalid questions:")
        reason_counts = df.loc[invalid_mask, "_reason"].value_counts()
        for reason, count in reason_counts.items():
            print(f"          {reason}: {count}")
    else:
        print("       ✓  All questions are valid.")

    df = df[df["_valid"]].drop(columns=["_valid", "_reason"]).reset_index(drop=True)
    print(f"       Remaining: {len(df):,} rows")

    # ── 5. Normalize Bloom labels ──────────────────────────────────────────────
    print("\n[5/10] Normalizing Bloom labels ...")
    df["bloom_level"] = df["bloom_raw"].apply(normalize_bloom_label)

    n_unrecognized = df["bloom_level"].isna().sum()
    if n_unrecognized > 0:
        bad_vals = df.loc[df["bloom_level"].isna(), "bloom_raw"].unique().tolist()
        print(f"       ⚠  {n_unrecognized} unrecognized Bloom codes: {bad_vals}")
        print(f"          These rows will be set to bloom_level = NULL.")
    else:
        print("       ✓  All Bloom labels recognized.")

    print("       Bloom distribution after normalization:")
    for lv, cnt in df["bloom_level"].value_counts().sort_index().items():
        print(f"          {lv}: {cnt:,}")

    # ── 6. Infer question_type ─────────────────────────────────────────────────
    print("\n[6/10] Inferring question_type from Bloom level + question length ...")
    df["question_type"] = df.apply(
        lambda row: normalize_question_type(
            has_options=False,
            has_computation_markers=False,
            question_text=row["question"],
            bloom_level=row["bloom_level"],
        ),
        axis=1,
    )
    print("       question_type distribution:")
    for qt, cnt in df["question_type"].value_counts().items():
        print(f"          {qt}: {cnt:,}")

    # ── 7. Assign marks ────────────────────────────────────────────────────────
    print("\n[7/10] Assigning default marks by question_type ...")
    df["marks"] = df["question_type"].apply(lambda qt: normalize_marks(question_type=qt))
    print(f"       marks distribution: {df['marks'].value_counts().to_dict()}")

    # ── 8. Assign difficulty ───────────────────────────────────────────────────
    print("\n[8/10] Assigning difficulty from Bloom level heuristic ...")
    df["difficulty"] = df["bloom_level"].apply(
        lambda bl: normalize_difficulty(bloom_level=bl)
    )
    print("       difficulty distribution:")
    for d, cnt in df["difficulty"].value_counts().items():
        print(f"          {d}: {cnt:,}")

    # ── 9. Remove duplicate questions ─────────────────────────────────────────
    print("\n[9/10] Removing duplicate questions ...")
    before = len(df)
    df = df.drop_duplicates(subset=["question"], keep="first").reset_index(drop=True)
    after = len(df)
    print(f"       Removed {before - after} duplicate(s). Remaining: {after:,}")

    # ── 10. Build unified schema ───────────────────────────────────────────────
    print("\n[10/10] Building unified schema ...")
    df["id"]             = [make_id("BLOOM", i + 1) for i in range(len(df))]
    df["board"]          = None
    df["class_level"]    = None
    df["subject"]        = None
    df["chapter"]        = None
    df["unit"]           = None
    df["topic"]          = None
    df["context"]        = None
    df["options"]        = None
    df["answer"]         = None
    df["source"]         = SOURCE_BLOOM
    df["source_dataset"] = SOURCE_DATASET_BLOOM

    # Select and order unified columns
    out_df = df[UNIFIED_COLUMNS].copy()

    # ── Save outputs ───────────────────────────────────────────────────────────
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)

    out_df.to_csv(OUT_BLOOM_PREPROCESSED, index=False, encoding="utf-8")
    print(f"\n  ✅ Saved preprocessed file → {OUT_BLOOM_PREPROCESSED}")
    print(f"     Rows: {len(out_df):,} | Columns: {len(out_df.columns)}")

    # Bloom classifier CSV: only question + bloom_level (rows where bloom is not null)
    classifier_df = out_df[out_df["bloom_level"].notna()][["id", "question", "bloom_level"]].copy()
    classifier_df.to_csv(OUT_BLOOM_CLASSIFIER, index=False, encoding="utf-8")
    print(f"\n  ✅ Saved Bloom classifier data → {OUT_BLOOM_CLASSIFIER}")
    print(f"     Rows: {len(classifier_df):,} (only rows with Bloom label)")

    # ── Final summary ──────────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print("  BLOOM PREPROCESSING SUMMARY")
    print(f"{'─'*70}")
    print(f"  Input rows           : {len(pd.read_csv(BLOOM_CSV)):,}")
    print(f"  After cleaning       : {len(out_df):,}")
    print(f"  Bloom classifier rows: {len(classifier_df):,}")
    print(f"  NULLs - board        : ALL (expected)")
    print(f"  NULLs - class_level  : ALL (expected)")
    print(f"  NULLs - subject      : ALL (expected)")
    print(f"  NULLs - answer       : ALL (expected — no answers in this dataset)")
    print(f"  MySQL import?        : NO (Decision 2A)")
    print(f"{'─'*70}\n")

    return out_df


if __name__ == "__main__":
    run()
