"""
step3_preprocess_eduqg.py — Preprocess EduQG Dataset (STEP 3)

SOURCES:
  datasets/extracted/eduqg/eduqg_llm_formatted.csv
  datasets/extracted/eduqg/eduqg_train.json
  datasets/extracted/eduqg/eduqg_val.json

OUTPUT:
  datasets/preprocessed/eduqg_csv_preprocessed.csv   ← MCQ questions from CSV
  datasets/preprocessed/eduqg_json_preprocessed.csv  ← MCQ + context from JSON (biology only)
  datasets/unified/qgen_train_data.csv                ← Q-generation training data (context→question)
  datasets/unified/qgen_val_data.csv                  ← Q-generation validation data

WHAT THIS SCRIPT DOES:
  Part A — CSV (eduqg_llm_formatted.csv):
    1. Load CSV
    2. Rename columns: prompt→question, A/B/C/D/E→options
    3. Build options JSON from A,B,C,D columns
    4. Flag 6 records with answer=E for review (not dropped)
    5. Clean question text
    6. Remove invalid / duplicate questions
    7. Set all metadata (board, class, subject, bloom, difficulty) to NULL

  Part B — JSON (eduqg_train.json + eduqg_val.json):
    1. Load JSON
    2. Filter: keep ONLY biology, microbiology, anatomy_and_physiology books (Decision 4B)
    3. Flatten chapter records → one row per question
    4. Extract: bname→subject, chapter→chapter, hl_sentences→context,
                normal_format→question, question_choices→options, ans_text→answer
    5. Clean all text fields
    6. Remove invalid / duplicate questions
    7. Build Q-generation training pairs (context + question)

IMPORTANT:
  - Decision 4B: Only biology books are kept from EduQG JSON
  - All bloom_level values are NULL (the JSON has bloom=null for all records)
  - These are NOT CBSE questions — board, class_level are NULL

Run from project root:
  backend\\.venv\\Scripts\\python.exe datasets\\preprocessing\\step3_preprocess_eduqg.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import json
import pandas as pd

from config import (
    EDUQG_CSV,
    EDUQG_TRAIN_JSON,
    EDUQG_VAL_JSON,
    OUT_EDUQG_CSV_PREPROCESSED,
    OUT_EDUQG_JSON_PREPROCESSED,
    OUT_QGEN_TRAIN,
    OUT_QGEN_VAL,
    UNIFIED_COLUMNS,
    SOURCE_EDUQG_CSV,
    SOURCE_EDUQG_JSON,
    SOURCE_DATASET_EDUQG_CSV,
    SOURCE_DATASET_EDUQG_TRAIN,
    SOURCE_DATASET_EDUQG_VAL,
    EDUQG_ALLOWED_BOOKS,
    BNAME_TO_SUBJECT,
    PREPROCESSED_DIR,
    UNIFIED_DIR,
)
from cleaner import (
    clean_text,
    clean_question,
    clean_eduqg_context,
    clean_answer,
    build_options_json,
    build_options_json_from_list,
    is_valid_question,
)
from normalizer import normalize_marks, normalize_question_type, make_id


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_sub(msg: str):
    print(f"       {msg}")


# ══════════════════════════════════════════════════════════════════════════════
# PART A: EduQG CSV (MCQ dataset)
# ══════════════════════════════════════════════════════════════════════════════

def process_eduqg_csv() -> pd.DataFrame:
    print_section("PART A — eduqg_llm_formatted.csv")

    # ── 1. Load ────────────────────────────────────────────────────────────────
    print("\n[A1/7] Loading CSV ...")
    df = pd.read_csv(EDUQG_CSV, low_memory=False)
    print_sub(f"Loaded {len(df):,} rows × {len(df.columns)} columns")

    # ── 2. Build options JSON ──────────────────────────────────────────────────
    print("\n[A2/7] Building options JSON from A, B, C, D, E columns ...")
    df["options"] = df.apply(
        lambda row: build_options_json(
            a=str(row.get("A", "")),
            b=str(row.get("B", "")),
            c=str(row.get("C", "")),
            d=str(row.get("D", "")),
            e=str(row.get("E", "")) if pd.notna(row.get("E")) else None,
        ),
        axis=1,
    )
    null_options = df["options"].isna().sum()
    print_sub(f"Options built for {len(df) - null_options:,} rows. NULL options: {null_options}")

    # ── 3. Flag answer=E records ───────────────────────────────────────────────
    print("\n[A3/7] Flagging records with answer = E ...")
    e_answer_mask = df["answer"].astype(str).str.upper() == "E"
    n_e = e_answer_mask.sum()
    print_sub(f"Found {n_e} records with answer=E. Flagging (NOT dropping).")
    df["_e_answer_flag"] = e_answer_mask

    if n_e > 0:
        print_sub("  Records with answer=E:")
        for _, row in df[e_answer_mask].iterrows():
            print_sub(f"    id={row['id']} | Q={str(row['prompt'])[:80]}")

    # ── 4. Clean question text ─────────────────────────────────────────────────
    print("\n[A4/7] Cleaning question text ...")
    df["question"] = df["prompt"].apply(clean_question)

    # ── 5. Remove invalid questions ────────────────────────────────────────────
    print("\n[A5/7] Removing invalid questions ...")
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
    print_sub(f"Remaining: {len(df):,} rows")

    # ── 6. Remove duplicates ───────────────────────────────────────────────────
    print("\n[A6/7] Removing duplicate questions ...")
    before = len(df)
    df = df.drop_duplicates(subset=["question"], keep="first").reset_index(drop=True)
    print_sub(f"Removed {before - len(df)} duplicates. Remaining: {len(df):,}")

    # ── 7. Build unified schema ────────────────────────────────────────────────
    print("\n[A7/7] Building unified schema ...")
    out_rows = []
    for i, row in df.iterrows():
        record = {
            "id":             make_id("EDUQG_CSV", i + 1),
            "board":          None,
            "class_level":    None,
            "subject":        None,
            "chapter":        None,
            "unit":           None,
            "topic":          None,
            "context":        None,
            "question":       row["question"],
            "question_type":  "MCQ",
            "options":        row["options"],
            "answer":         clean_text(str(row["answer"])) if pd.notna(row["answer"]) else None,
            "marks":          normalize_marks(question_type="MCQ"),
            "bloom_level":    None,
            "difficulty":     None,
            "source":         SOURCE_EDUQG_CSV,
            "source_dataset": SOURCE_DATASET_EDUQG_CSV,
        }
        # Keep E-answer flag as an annotation (not in unified schema but in preprocessed)
        record["_e_answer_flag"] = row["_e_answer_flag"]
        out_rows.append(record)

    out_df = pd.DataFrame(out_rows)
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_df[UNIFIED_COLUMNS].to_csv(OUT_EDUQG_CSV_PREPROCESSED, index=False, encoding="utf-8")
    print_sub(f"✅ Saved → {OUT_EDUQG_CSV_PREPROCESSED}  ({len(out_df):,} rows)")

    return out_df[UNIFIED_COLUMNS]


# ══════════════════════════════════════════════════════════════════════════════
# PART B: EduQG JSON (context-rich MCQ dataset — biology books only)
# ══════════════════════════════════════════════════════════════════════════════

def flatten_eduqg_json(json_path, source_dataset_label: str) -> list[dict]:
    """
    Flatten a single EduQG JSON file into a list of unified-schema dicts.
    Filters to EDUQG_ALLOWED_BOOKS only (Decision 4B).
    """
    with open(json_path, "r", encoding="utf-8", errors="replace") as f:
        chapters = json.load(f)

    records = []
    skipped_books = set()
    kept_books = set()

    for chapter_rec in chapters:
        bname = chapter_rec.get("bname", "").strip()

        # Decision 4B: skip non-biology books
        if bname not in EDUQG_ALLOWED_BOOKS:
            skipped_books.add(bname)
            continue

        kept_books.add(bname)
        subject = BNAME_TO_SUBJECT.get(bname, "Biology")
        chapter_num = chapter_rec.get("chapter", None)
        chapter_label = f"Chapter {chapter_num}" if chapter_num else None

        # Full chapter text (for context)
        chapter_text = clean_eduqg_context(chapter_rec.get("chapter_text", "") or "")
        # Summary as additional context
        summary = clean_eduqg_context(chapter_rec.get("summary", "") or "")

        questions = chapter_rec.get("questions", [])

        for q_entry in questions:
            q_obj = q_entry.get("question", {})
            a_obj = q_entry.get("answer", {})

            # Prefer hl_sentences as context (more focused than full chapter_text)
            hl_sentences = clean_eduqg_context(q_entry.get("hl_sentences", "") or "")
            context = hl_sentences if hl_sentences else chapter_text[:500] if chapter_text else None

            # Question text: prefer normal_format over cloze_format
            question_text = clean_question(q_obj.get("normal_format", "") or
                                           q_obj.get("question_text", "") or "")

            # Options
            choices = q_obj.get("question_choices", [])
            options_json = build_options_json_from_list(choices) if choices else None

            # Answer
            ans_text = a_obj.get("ans_text", None)
            if ans_text:
                ans_text = clean_text(str(ans_text))

            # Validate question
            valid, reason = is_valid_question(question_text)
            if not valid:
                continue

            records.append({
                "bname":          bname,
                "subject":        subject,
                "chapter":        chapter_label,
                "context":        context if context else None,
                "question":       question_text,
                "options":        options_json,
                "answer":         ans_text,
                "source_dataset": source_dataset_label,
                "chapter_text":   chapter_text,   # keep full text for Q-gen
                "summary":        summary,
            })

    print_sub(f"  Allowed books processed : {sorted(kept_books)}")
    print_sub(f"  Skipped books           : {sorted(skipped_books)}")
    print_sub(f"  Flattened Q records     : {len(records):,}")
    return records


def process_eduqg_json() -> tuple[pd.DataFrame, pd.DataFrame]:
    print_section("PART B — eduqg_train.json + eduqg_val.json (biology books only)")

    # ── Load and flatten ───────────────────────────────────────────────────────
    print("\n[B1/6] Loading and flattening eduqg_train.json ...")
    train_records = flatten_eduqg_json(EDUQG_TRAIN_JSON, SOURCE_DATASET_EDUQG_TRAIN)

    print("\n[B2/6] Loading and flattening eduqg_val.json ...")
    val_records   = flatten_eduqg_json(EDUQG_VAL_JSON,   SOURCE_DATASET_EDUQG_VAL)

    # ── Remove duplicates within each split ────────────────────────────────────
    print("\n[B3/6] Removing duplicate questions within each split ...")
    def dedup(records, split_name):
        seen = set()
        unique = []
        for rec in records:
            q = rec["question"].lower().strip()
            if q not in seen:
                seen.add(q)
                unique.append(rec)
        removed = len(records) - len(unique)
        print_sub(f"{split_name}: removed {removed} duplicates → {len(unique):,} unique records")
        return unique

    train_records = dedup(train_records, "train")
    val_records   = dedup(val_records,   "val")

    # ── Check cross-split overlap ──────────────────────────────────────────────
    print("\n[B4/6] Checking cross-split (train vs val) overlap ...")
    train_qs = {r["question"].lower().strip() for r in train_records}
    val_qs   = {r["question"].lower().strip() for r in val_records}
    overlap  = train_qs & val_qs
    print_sub(f"Cross-split overlap: {len(overlap)} questions appear in both train and val.")
    if overlap:
        # Remove overlapping questions from val to preserve clean split
        val_records = [r for r in val_records if r["question"].lower().strip() not in overlap]
        print_sub(f"Removed {len(overlap)} from val. Val remaining: {len(val_records):,}")

    # ── Build unified schema ───────────────────────────────────────────────────
    print("\n[B5/6] Building unified schema for both splits ...")

    def build_unified(records, prefix, source_label):
        rows = []
        for i, rec in enumerate(records):
            rows.append({
                "id":             make_id(f"EDUQG_JSON_{prefix}", i + 1),
                "board":          None,
                "class_level":    None,
                "subject":        rec["subject"],
                "chapter":        rec["chapter"],
                "unit":           None,
                "topic":          None,
                "context":        rec["context"],
                "question":       rec["question"],
                "question_type":  "MCQ",
                "options":        rec["options"],
                "answer":         rec["answer"],
                "marks":          normalize_marks(question_type="MCQ"),
                "bloom_level":    None,
                "difficulty":     None,
                "source":         SOURCE_EDUQG_JSON,
                "source_dataset": rec["source_dataset"],
                # Extra fields for Q-gen training (not in unified schema)
                "_chapter_text":  rec.get("chapter_text", ""),
                "_summary":       rec.get("summary", ""),
            })
        return rows

    train_rows = build_unified(train_records, "TRAIN", SOURCE_DATASET_EDUQG_TRAIN)
    val_rows   = build_unified(val_records,   "VAL",   SOURCE_DATASET_EDUQG_VAL)

    train_df = pd.DataFrame(train_rows)
    val_df   = pd.DataFrame(val_rows)

    # ── Save preprocessed ─────────────────────────────────────────────────────
    print("\n[B6/6] Saving outputs ...")
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)

    combined_json_df = pd.concat(
        [train_df[UNIFIED_COLUMNS], val_df[UNIFIED_COLUMNS]],
        ignore_index=True
    )
    combined_json_df.to_csv(OUT_EDUQG_JSON_PREPROCESSED, index=False, encoding="utf-8")
    print_sub(f"✅ Saved JSON preprocessed → {OUT_EDUQG_JSON_PREPROCESSED}  ({len(combined_json_df):,} rows)")

    # ── Q-generation training data: context → question pairs ──────────────────
    # For Q-gen, we need rows that HAVE context (hl_sentences or chapter_text)
    def build_qgen(rows, split_name):
        qgen_rows = []
        for row in rows:
            ctx = row.get("context") or row.get("_chapter_text", "")
            if not ctx or len(ctx.strip()) < 20:
                continue
            qgen_rows.append({
                "id":             row["id"],
                "subject":        row["subject"],
                "chapter":        row["chapter"],
                "context":        ctx[:2000],          # truncate for model input
                "question":       row["question"],
                "question_type":  row["question_type"],
                "options":        row["options"],
                "answer":         row["answer"],
                "bloom_level":    row["bloom_level"],
                "difficulty":     row["difficulty"],
                "marks":          row["marks"],
                "source_dataset": row["source_dataset"],
            })
        print_sub(f"Q-gen {split_name}: {len(qgen_rows):,} rows with context")
        return pd.DataFrame(qgen_rows)

    qgen_train_df = build_qgen(train_rows, "train")
    qgen_val_df   = build_qgen(val_rows,   "val")

    qgen_train_df.to_csv(OUT_QGEN_TRAIN, index=False, encoding="utf-8")
    qgen_val_df.to_csv(OUT_QGEN_VAL,   index=False, encoding="utf-8")
    print_sub(f"✅ Saved Q-gen train → {OUT_QGEN_TRAIN}")
    print_sub(f"✅ Saved Q-gen val   → {OUT_QGEN_VAL}")

    print_sub(f"\n  Books kept (Decision 4B): {sorted(EDUQG_ALLOWED_BOOKS)}")
    print_sub(f"  Train unified rows: {len(train_df):,}")
    print_sub(f"  Val unified rows  : {len(val_df):,}")

    return train_df[UNIFIED_COLUMNS], val_df[UNIFIED_COLUMNS]


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def run():
    print_section("STEP 3 — EduQG Dataset Preprocessing")

    csv_df = process_eduqg_csv()
    train_df, val_df = process_eduqg_json()

    print_section("EDUQG PREPROCESSING SUMMARY")
    print(f"  CSV MCQ rows         : {len(csv_df):,}")
    print(f"  JSON train rows      : {len(train_df):,}")
    print(f"  JSON val rows        : {len(val_df):,}")
    print(f"  Total EduQG records  : {len(csv_df) + len(train_df) + len(val_df):,}")
    print(f"  bloom_level          : ALL NULL (not in source data)")
    print(f"  board / class_level  : ALL NULL (not CBSE)")
    print(f"  Books kept (JSON)    : biology, microbiology, anatomy_and_physiology")
    print()

    return csv_df, train_df, val_df


if __name__ == "__main__":
    run()
