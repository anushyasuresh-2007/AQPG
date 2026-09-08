"""
step3_preprocess_reasoning.py — Preprocess Reasoning / GSM8K Dataset (STEP 3)

SOURCES:
  datasets/extracted/reasoning/main_train.csv      ← same 7,473 questions as socratic
  datasets/extracted/reasoning/main_test.csv       ← same 1,319 questions as socratic_test
  datasets/extracted/reasoning/socratic_train.csv  ← socratic answer format (preferred)
  datasets/extracted/reasoning/socratic_test.csv   ← socratic test answers

OUTPUT:
  datasets/preprocessed/reasoning_preprocessed.csv  ← cleaned, filtered, merged
  datasets/unified/numerical_questions.csv           ← ML-ready numerical Q bank

WHAT THIS SCRIPT DOES:
  1. Load main_train + socratic_train → merge on question (same Qs, different answer styles)
  2. Load main_test  + socratic_test  → merge on question
  3. Clean all question text
  4. Apply curated subset filter (Decision 3B): keep rows where answer has ≤ 3 <<...>> markers
     (1–3 arithmetic steps = Class 4–8 level)
  5. Extract final numeric answer from #### marker
  6. Assign question_type = "Numerical", subject = "Mathematics"
  7. Assign marks = 2 (default for numerical), difficulty from step count heuristic
  8. Remove duplicates
  9. Add unified schema columns (board=NULL, class_level=NULL)
 10. Save outputs

IMPORTANT:
  - main_train and socratic_train contain IDENTICAL questions — only answer format differs
  - We use socratic answer as the primary answer (better for answer key generation)
  - The direct answer (from main_train) is stored separately as numerical_data
  - Decision 3B: max 3 computation steps → filters to simpler, school-appropriate problems
  - GSM8K is general English math — NOT CBSE curriculum-mapped

Run from project root:
  backend\\.venv\\Scripts\\python.exe datasets\\preprocessing\\step3_preprocess_reasoning.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import re
import pandas as pd

from config import (
    REASONING_MAIN_TRAIN,
    REASONING_MAIN_TEST,
    REASONING_SOCRATIC_TRAIN,
    REASONING_SOCRATIC_TEST,
    OUT_REASONING_PREPROCESSED,
    OUT_NUMERICAL,
    UNIFIED_COLUMNS,
    SOURCE_REASONING,
    SOURCE_DATASET_REASONING_TRAIN,
    SOURCE_DATASET_REASONING_TEST,
    REASONING_MAX_COMPUTATION_STEPS,
    PREPROCESSED_DIR,
    UNIFIED_DIR,
)
from cleaner import (
    clean_gsm8k_question,
    clean_gsm8k_answer,
    extract_gsm8k_final_answer,
    count_computation_steps,
    is_valid_question,
)
from normalizer import normalize_marks, normalize_difficulty, make_id


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_sub(msg: str):
    print(f"       {msg}")


def load_and_merge(main_path, socratic_path, split_label: str) -> pd.DataFrame:
    """
    Load main_*.csv and socratic_*.csv, merge on question text.
    Returns DataFrame with columns: question, main_answer, socratic_answer.
    """
    print_sub(f"Loading {main_path.name} ...")
    main_df = pd.read_csv(main_path, low_memory=False)
    print_sub(f"  Rows: {len(main_df):,}")

    print_sub(f"Loading {socratic_path.name} ...")
    soc_df  = pd.read_csv(socratic_path, low_memory=False)
    print_sub(f"  Rows: {len(soc_df):,}")

    # Rename columns before merge
    main_df = main_df.rename(columns={"answer": "main_answer"})
    soc_df  = soc_df.rename(columns={"answer": "socratic_answer"})

    # Inner merge on question (they share the exact same questions)
    merged = pd.merge(main_df, soc_df, on="question", how="inner")
    print_sub(f"  After merge: {len(merged):,} matched rows")

    if len(merged) < len(main_df):
        unmatched = len(main_df) - len(merged)
        print_sub(f"  ⚠ {unmatched} rows from main_{split_label} had no match in socratic_{split_label}")

    return merged


def process_split(
    main_path,
    socratic_path,
    split_label: str,
    id_prefix: str,
    source_dataset_label: str,
) -> pd.DataFrame:
    """Process one split (train or test) of the reasoning dataset."""

    print_section(f"Processing {split_label.upper()} split")

    # ── 1. Load and merge ──────────────────────────────────────────────────────
    print(f"\n[{split_label}/1] Loading and merging ...")
    df = load_and_merge(main_path, socratic_path, split_label)

    # ── 2. Clean question text ─────────────────────────────────────────────────
    print(f"\n[{split_label}/2] Cleaning question text ...")
    df["question"] = df["question"].apply(clean_gsm8k_question)

    # ── 3. Remove invalid questions ────────────────────────────────────────────
    print(f"\n[{split_label}/3] Removing invalid questions ...")
    validity = df["question"].apply(is_valid_question)
    df["_valid"]  = validity.apply(lambda x: x[0])
    df["_reason"] = validity.apply(lambda x: x[1])

    invalid_mask = ~df["_valid"]
    n_invalid = invalid_mask.sum()
    if n_invalid > 0:
        print_sub(f"⚠ Removed {n_invalid} invalid questions:")
        for reason, count in df.loc[invalid_mask, "_reason"].value_counts().items():
            print_sub(f"   {reason}: {count}")
    else:
        print_sub("✓ All questions valid.")

    df = df[df["_valid"]].drop(columns=["_valid", "_reason"]).reset_index(drop=True)

    # ── 4. Count computation steps ────────────────────────────────────────────
    print(f"\n[{split_label}/4] Counting computation steps per answer (for curated filter) ...")
    df["_steps"] = df["main_answer"].apply(
        lambda a: count_computation_steps(str(a)) if pd.notna(a) else 0
    )

    step_dist = df["_steps"].value_counts().sort_index()
    print_sub("Step count distribution:")
    for steps, count in step_dist.items():
        marker = " ← KEEP" if steps <= REASONING_MAX_COMPUTATION_STEPS else " ← DROP"
        print_sub(f"   {steps} steps: {count:,} questions{marker}")

    # ── 5. Apply curated filter (Decision 3B) ─────────────────────────────────
    print(f"\n[{split_label}/5] Applying curated subset filter (max {REASONING_MAX_COMPUTATION_STEPS} steps) ...")
    before = len(df)
    df = df[df["_steps"] <= REASONING_MAX_COMPUTATION_STEPS].reset_index(drop=True)
    after = len(df)
    print_sub(f"Before filter: {before:,} | After filter: {after:,} | Dropped: {before - after:,}")

    # ── 6. Clean answer text ───────────────────────────────────────────────────
    print(f"\n[{split_label}/6] Cleaning answer text ...")
    df["answer"]       = df["socratic_answer"].apply(clean_gsm8k_answer)
    df["_direct_ans"]  = df["main_answer"].apply(clean_gsm8k_answer)
    df["_final_num"]   = df["answer"].apply(extract_gsm8k_final_answer)

    n_no_final = df["_final_num"].isna().sum()
    print_sub(f"Final numeric answer extracted: {len(df) - n_no_final:,}/{len(df):,}")
    if n_no_final > 0:
        print_sub(f"⚠ {n_no_final} rows have no #### marker — answer may be non-numeric")

    # ── 7. Assign difficulty from step count ───────────────────────────────────
    print(f"\n[{split_label}/7] Assigning difficulty from computation step count ...")
    df["difficulty"] = df["_steps"].apply(
        lambda s: normalize_difficulty(computation_steps=s)
    )
    print_sub("Difficulty distribution:")
    for d, cnt in df["difficulty"].value_counts().items():
        print_sub(f"   {d}: {cnt:,}")

    # ── 8. Remove duplicates ───────────────────────────────────────────────────
    print(f"\n[{split_label}/8] Removing duplicate questions ...")
    before = len(df)
    df = df.drop_duplicates(subset=["question"], keep="first").reset_index(drop=True)
    print_sub(f"Removed {before - len(df)} duplicates. Remaining: {len(df):,}")

    # ── 9. Build unified schema ────────────────────────────────────────────────
    print(f"\n[{split_label}/9] Building unified schema ...")
    marks = normalize_marks(question_type="Numerical")

    rows = []
    for i, row in df.iterrows():
        rows.append({
            "id":             make_id(id_prefix, i + 1),
            "board":          None,
            "class_level":    None,
            "subject":        "Mathematics",
            "chapter":        None,
            "unit":           None,
            "topic":          None,
            "context":        None,
            "question":       row["question"],
            "question_type":  "Numerical",
            "options":        None,
            "answer":         row["answer"],       # socratic format
            "marks":          marks,
            "bloom_level":    None,                # will be predicted by classifier
            "difficulty":     row["difficulty"],
            "source":         SOURCE_REASONING,
            "source_dataset": source_dataset_label,
            # Extra fields (not in unified schema) for numerical_questions.csv
            "_direct_answer": row["_direct_ans"],  # direct step-by-step
            "_final_number":  row["_final_num"],   # extracted final number
            "_steps":         row["_steps"],
        })

    return pd.DataFrame(rows)


def run():
    print_section("STEP 3 — Reasoning / GSM8K Dataset Preprocessing")
    print(f"  Curated filter: max {REASONING_MAX_COMPUTATION_STEPS} computation steps (Decision 3B)")

    # ── Process train split ────────────────────────────────────────────────────
    train_df = process_split(
        main_path=REASONING_MAIN_TRAIN,
        socratic_path=REASONING_SOCRATIC_TRAIN,
        split_label="train",
        id_prefix="NUMR_TRAIN",
        source_dataset_label=SOURCE_DATASET_REASONING_TRAIN,
    )

    # ── Process test split ─────────────────────────────────────────────────────
    test_df = process_split(
        main_path=REASONING_MAIN_TEST,
        socratic_path=REASONING_SOCRATIC_TEST,
        split_label="test",
        id_prefix="NUMR_TEST",
        source_dataset_label=SOURCE_DATASET_REASONING_TEST,
    )

    # ── Check train/test overlap ───────────────────────────────────────────────
    print_section("Cross-split overlap check (train vs test)")
    train_qs = set(train_df["question"].str.lower().str.strip())
    test_qs  = set(test_df["question"].str.lower().str.strip())
    overlap  = train_qs & test_qs
    print_sub(f"Train/test overlap: {len(overlap)} questions (should be 0)")
    if overlap:
        print_sub(f"⚠ WARNING: {len(overlap)} questions appear in both train and test!")

    # ── Combine and save ───────────────────────────────────────────────────────
    all_df = pd.concat([train_df, test_df], ignore_index=True)

    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)

    # Save full preprocessed (with extra fields)
    all_df.to_csv(OUT_REASONING_PREPROCESSED, index=False, encoding="utf-8")
    print_sub(f"\n✅ Saved reasoning preprocessed → {OUT_REASONING_PREPROCESSED}  ({len(all_df):,} rows)")

    # Save numerical_questions.csv (unified columns + extra numerical fields)
    numerical_extra_cols = UNIFIED_COLUMNS + ["_direct_answer", "_final_number", "_steps"]
    numerical_df = all_df[[c for c in numerical_extra_cols if c in all_df.columns]]
    numerical_df.to_csv(OUT_NUMERICAL, index=False, encoding="utf-8")
    print_sub(f"✅ Saved numerical Q bank → {OUT_NUMERICAL}  ({len(numerical_df):,} rows)")

    # ── Final summary ──────────────────────────────────────────────────────────
    print_section("REASONING PREPROCESSING SUMMARY")
    print(f"  Input (train)        : 7,473 questions (before filter)")
    print(f"  Input (test)         : 1,319 questions (before filter)")
    print(f"  After curated filter (train) : {len(train_df):,} (≤{REASONING_MAX_COMPUTATION_STEPS} steps)")
    print(f"  After curated filter (test)  : {len(test_df):,}  (≤{REASONING_MAX_COMPUTATION_STEPS} steps)")
    print(f"  Total kept           : {len(all_df):,}")
    print(f"  subject              : Mathematics (all rows)")
    print(f"  question_type        : Numerical (all rows)")
    print(f"  bloom_level          : ALL NULL (will be predicted by classifier)")
    print(f"  board / class_level  : ALL NULL (not CBSE-specific)")
    print(f"  Answer format        : Socratic chain-of-thought (primary)")
    print(f"  Difficulty           : Assigned by computation step count heuristic")
    print()

    return train_df, test_df


if __name__ == "__main__":
    run()
