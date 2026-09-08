"""
step3_run_all.py — Master runner for AQPG STEP 3 preprocessing pipeline.

Runs all three preprocessors in sequence and produces a final summary report.

EXECUTION ORDER:
  1. step3_preprocess_bloom.py     → bloom_preprocessed.csv + bloom_classifier_data.csv
  2. step3_preprocess_eduqg.py     → eduqg_csv_preprocessed.csv + eduqg_json_preprocessed.csv
                                     + qgen_train_data.csv + qgen_val_data.csv
  3. step3_preprocess_reasoning.py → reasoning_preprocessed.csv + numerical_questions.csv

Run from project root:
  backend\\.venv\\Scripts\\python.exe datasets\\preprocessing\\step3_run_all.py

Time estimate: 2–5 minutes (EduQG JSON is large at ~20MB)
"""

import sys
import os
import time
import traceback

# Allow imports from the preprocessing folder
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd

from config import (
    PREPROCESSED_DIR,
    UNIFIED_DIR,
    OUT_BLOOM_PREPROCESSED,
    OUT_EDUQG_CSV_PREPROCESSED,
    OUT_EDUQG_JSON_PREPROCESSED,
    OUT_REASONING_PREPROCESSED,
    OUT_BLOOM_CLASSIFIER,
    OUT_QGEN_TRAIN,
    OUT_QGEN_VAL,
    OUT_NUMERICAL,
    OUT_UNIFIED,
    OUT_MAPPING_LOG,
    UNIFIED_COLUMNS,
)


def print_header(title: str):
    print(f"\n{'█'*72}")
    print(f"  {title}")
    print(f"{'█'*72}")


def print_section(title: str):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


def run_step(name: str, fn):
    """Run a preprocessing step, catching errors gracefully."""
    print_section(f"Running: {name}")
    t0 = time.time()
    try:
        result = fn()
        elapsed = time.time() - t0
        print(f"\n  ✅ {name} completed in {elapsed:.1f}s")
        return result, True
    except Exception as e:
        elapsed = time.time() - t0
        print(f"\n  ❌ {name} FAILED after {elapsed:.1f}s")
        print(f"     Error: {e}")
        traceback.print_exc()
        return None, False


def build_unified_dataset():
    """
    Combine all preprocessed datasets into a single unified_questions.csv.
    Also builds the mapping_log.csv for provenance tracking.
    """
    print_section("Building unified_questions.csv")

    frames = []
    logs   = []

    sources = [
        ("Bloom CSV",      OUT_BLOOM_PREPROCESSED),
        ("EduQG CSV",      OUT_EDUQG_CSV_PREPROCESSED),
        ("EduQG JSON",     OUT_EDUQG_JSON_PREPROCESSED),
        ("Reasoning/Math", OUT_REASONING_PREPROCESSED),
    ]

    for name, path in sources:
        if not path.exists():
            print(f"  ⚠  {name}: file not found → {path}")
            continue

        df = pd.read_csv(path, low_memory=False)

        # Keep only unified schema columns
        available = [c for c in UNIFIED_COLUMNS if c in df.columns]
        missing   = [c for c in UNIFIED_COLUMNS if c not in df.columns]
        df_unified = df[available].copy()
        for col in missing:
            df_unified[col] = None

        df_unified = df_unified[UNIFIED_COLUMNS]
        frames.append(df_unified)

        for _, row in df_unified.iterrows():
            logs.append({
                "unified_id":     row["id"],
                "source_dataset": row["source_dataset"],
                "source":         row["source"],
                "question_type":  row["question_type"],
                "bloom_level":    row["bloom_level"],
                "marks":          row["marks"],
            })

        print(f"  Loaded {len(df_unified):,} rows from {name}")

    if not frames:
        print("  ❌ No data to combine!")
        return

    unified = pd.concat(frames, ignore_index=True)

    # Final deduplication across all datasets
    print(f"\n  Total rows before global dedup : {len(unified):,}")
    unified = unified.drop_duplicates(subset=["question"], keep="first").reset_index(drop=True)
    print(f"  Total rows after global dedup  : {len(unified):,}")
    dupes_removed = len(pd.concat(frames, ignore_index=True)) - len(unified)
    print(f"  Cross-dataset duplicates removed: {dupes_removed}")

    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)
    unified.to_csv(OUT_UNIFIED, index=False, encoding="utf-8")
    print(f"\n  ✅ Saved unified_questions.csv → {OUT_UNIFIED}  ({len(unified):,} rows)")

    # Mapping log
    log_df = pd.DataFrame(logs)
    log_df.to_csv(OUT_MAPPING_LOG, index=False, encoding="utf-8")
    print(f"  ✅ Saved mapping_log.csv → {OUT_MAPPING_LOG}  ({len(log_df):,} rows)")

    return unified


def print_file_report():
    """Print a table of all output files with row counts."""
    print_section("OUTPUT FILE REPORT")

    output_files = [
        ("PREPROCESSED",  "bloom_preprocessed.csv",        OUT_BLOOM_PREPROCESSED),
        ("PREPROCESSED",  "eduqg_csv_preprocessed.csv",    OUT_EDUQG_CSV_PREPROCESSED),
        ("PREPROCESSED",  "eduqg_json_preprocessed.csv",   OUT_EDUQG_JSON_PREPROCESSED),
        ("PREPROCESSED",  "reasoning_preprocessed.csv",    OUT_REASONING_PREPROCESSED),
        ("UNIFIED (ML)",  "bloom_classifier_data.csv",     OUT_BLOOM_CLASSIFIER),
        ("UNIFIED (ML)",  "qgen_train_data.csv",           OUT_QGEN_TRAIN),
        ("UNIFIED (ML)",  "qgen_val_data.csv",             OUT_QGEN_VAL),
        ("UNIFIED (ML)",  "numerical_questions.csv",       OUT_NUMERICAL),
        ("UNIFIED (ALL)", "unified_questions.csv",         OUT_UNIFIED),
        ("LOG",           "mapping_log.csv",               OUT_MAPPING_LOG),
    ]

    print(f"\n  {'Category':<16} {'File':<40} {'Rows':>8}")
    print(f"  {'─'*16} {'─'*40} {'─'*8}")
    total = 0
    for cat, fname, fpath in output_files:
        if fpath.exists():
            try:
                df = pd.read_csv(fpath, low_memory=False)
                rows = len(df)
            except Exception:
                rows = -1
        else:
            rows = -1

        rows_str = f"{rows:,}" if rows >= 0 else "MISSING"
        print(f"  {cat:<16} {fname:<40} {rows_str:>8}")

    print()


def main():
    print_header("AQPG — STEP 3: Full Preprocessing Pipeline")
    t_start = time.time()

    # ── Create output directories ───────────────────────────────────────────────
    PREPROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    UNIFIED_DIR.mkdir(parents=True, exist_ok=True)

    results = {}

    # ── Step 1: Bloom ──────────────────────────────────────────────────────────
    import step3_preprocess_bloom as bloom_module
    result, ok = run_step("Bloom Taxonomy Preprocessor", bloom_module.run)
    results["bloom"] = ok

    # ── Step 2: EduQG ─────────────────────────────────────────────────────────
    import step3_preprocess_eduqg as eduqg_module
    result, ok = run_step("EduQG Dataset Preprocessor", eduqg_module.run)
    results["eduqg"] = ok

    # ── Step 3: Reasoning ─────────────────────────────────────────────────────
    import step3_preprocess_reasoning as reasoning_module
    result, ok = run_step("Reasoning/GSM8K Preprocessor", reasoning_module.run)
    results["reasoning"] = ok

    # ── Step 4: Build unified dataset ─────────────────────────────────────────
    unified_ok = True
    try:
        build_unified_dataset()
    except Exception as e:
        print(f"\n  ❌ Unified dataset build FAILED: {e}")
        traceback.print_exc()
        unified_ok = False
    results["unified"] = unified_ok

    # ── Final report ───────────────────────────────────────────────────────────
    print_file_report()

    t_total = time.time() - t_start
    print_header("STEP 3 COMPLETE")
    print(f"\n  Total time: {t_total:.1f}s\n")

    all_passed = all(results.values())
    for step, ok in results.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {step}")

    if all_passed:
        print(f"\n  🎉 All preprocessing steps passed!")
        print(f"\n  Next step: Review outputs, then proceed to STEP 4 (Unified Dataset)")
    else:
        print(f"\n  ⚠  Some steps failed. Check errors above before proceeding.")

    print(f"""
  Output locations:
    datasets\\preprocessed\\   ← per-dataset cleaned files
    datasets\\unified\\        ← ML-ready and combined files

  STEP 4 → Column mapping review + final unified dataset
  STEP 5 → Split into Bloom, QGen, Numerical sub-datasets
  STEP 6 → Model recommendations
""")


if __name__ == "__main__":
    main()
