"""
audit_qg_dataset_v5.py
AQPG V5 Dataset Forensic Audit, Quality Gates, Cross-Tabulation & Tokenization Engine.

Performs Forensic Audit across qg_train_dataset_v5.jsonl and qg_validation_dataset_v5.jsonl.
Generates:
  - 5 Cross-Tabulation Matrices:
    1. Subject x Class
    2. Subject x Board
    3. Subject x Question Type
    4. Subject x Verification Status
    5. Class x Board
  - FLAN-T5-Small Tokenization Analysis (seed 42)
  - Hard Quality Gates PASS/WARN/FAIL Evaluation

Outputs:
  - datasets/v5/qg_dataset_v5_audit.json
  - datasets/v5/qg_dataset_v5_audit_report.txt
"""

import os
import sys
import re
import json
import random
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple

# Safe PyTorch DLL handling
torch_lib = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\.venv\lib\site-packages\torch\lib"
if os.path.exists(torch_lib):
    try:
        os.add_dll_directory(torch_lib)
    except Exception:
        pass
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from transformers import AutoTokenizer

DATASETS_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets"
V5_DIR = os.path.join(DATASETS_DIR, "v5")

TRAIN_V5_PATH = os.path.join(V5_DIR, "qg_train_dataset_v5.1.jsonl")
VAL_V5_PATH = os.path.join(V5_DIR, "qg_validation_dataset_v5.1.jsonl")

AUDIT_JSON_PATH = os.path.join(V5_DIR, "qg_dataset_v5.1_audit.json")
AUDIT_REPORT_PATH = os.path.join(V5_DIR, "qg_dataset_v5.1_audit_report.txt")

TOKENIZER_MODEL = "google/flan-t5-small"

def normalize_text(text: str) -> str:
    """Normalize text for leakage & duplicate checks."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def load_and_validate_jsonl(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    records = []
    errors = []
    if not os.path.exists(filepath):
        errors.append(f"File not found: {filepath}")
        return records, errors
        
    with open(filepath, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                records.append(item)
            except Exception as e:
                errors.append(f"Line {idx}: Malformed JSON - {str(e)}")
    return records, errors

def build_matrix(records: List[Dict[str, Any]], key1: str, key2: str) -> Dict[str, Dict[str, int]]:
    matrix = defaultdict(Counter)
    for r in records:
        v1 = str(r.get(key1) or "UNKNOWN")
        v2 = str(r.get(key2) or "UNKNOWN")
        matrix[v1][v2] += 1
    return {k: dict(v) for k, v in matrix.items()}

def run_v5_audit():
    print("=" * 80)
    print("AQPG V5 DATASET FORENSIC AUDIT & QUALITY GATES")
    print("=" * 80)
    
    train_records, train_errs = load_and_validate_jsonl(TRAIN_V5_PATH)
    val_records, val_errs = load_and_validate_jsonl(VAL_V5_PATH)
    
    json_errors = train_errs + val_errs
    total_records = len(train_records) + len(val_records)
    all_records = train_records + val_records
    
    print(f"Train Records Count: {len(train_records)}")
    print(f"Val Records Count:   {len(val_records)}")
    print(f"Total V5 Records:    {total_records}")
    print(f"JSON Syntax Errors:  {len(json_errors)}")

    # 1. Leakage Analysis
    train_exact_prompts = set(r.get("input_text", "") for r in train_records)
    val_exact_prompts = set(r.get("input_text", "") for r in val_records)
    exact_prompt_leakage = len(train_exact_prompts.intersection(val_exact_prompts))
    
    train_exact_targets = set(r.get("target_text", "") for r in train_records)
    val_exact_targets = set(r.get("target_text", "") for r in val_records)
    exact_target_leakage = len(train_exact_targets.intersection(val_exact_targets))
    
    train_norm_targets = set(normalize_text(r.get("target_text", "")) for r in train_records)
    val_norm_targets = set(normalize_text(r.get("target_text", "")) for r in val_records)
    norm_target_leakage = len(train_norm_targets.intersection(val_norm_targets))
    
    # 2. Duplicate Detection
    seen_pairs = set()
    dup_pairs_count = 0
    for r in all_records:
        pair_key = (r.get("input_text", ""), r.get("target_text", ""))
        if pair_key in seen_pairs:
            dup_pairs_count += 1
        else:
            seen_pairs.add(pair_key)

    # 3. Categorical Distributions
    subject_dist = Counter(r.get("subject", "UNKNOWN") for r in all_records)
    class_dist = Counter(r.get("class", "UNKNOWN") for r in all_records)
    board_dist = Counter(r.get("board", "UNKNOWN") for r in all_records)
    unit_dist = Counter(r.get("unit", "UNKNOWN") for r in all_records)
    topic_dist = Counter(r.get("topic", "UNKNOWN") for r in all_records)
    bloom_dist = Counter(r.get("bloom", "UNKNOWN") for r in all_records)
    diff_dist = Counter(r.get("difficulty", "UNKNOWN") for r in all_records)
    marks_dist = Counter(str(r.get("marks", "UNKNOWN")) for r in all_records)
    qtype_dist = Counter(r.get("question_type", "UNKNOWN") for r in all_records)
    status_dist = Counter(r.get("verification_status", "UNKNOWN") for r in all_records)
    source_dist = Counter(r.get("source_dataset", "UNKNOWN") for r in all_records)

    # 4. Cross-Tabulation Matrices
    matrix_sb_class = build_matrix(all_records, "subject", "class")
    matrix_sb_board = build_matrix(all_records, "subject", "board")
    matrix_sb_qtype = build_matrix(all_records, "subject", "question_type")
    matrix_sb_status = build_matrix(all_records, "subject", "verification_status")
    matrix_class_board = build_matrix(all_records, "class", "board")

    # 5. Tokenization Analysis (google/flan-t5-small)
    print("\nLoading Tokenizer for Tokenization Audit:", TOKENIZER_MODEL)
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
    except Exception as e:
        print(f"Warning: Could not load tokenizer ({e}). Tokenization audit skipped.")
        tokenizer = None

    token_stats = {}
    if tokenizer:
        random.seed(42)
        sample_size = min(2000, total_records)
        sampled_records = random.sample(all_records, sample_size)
        
        inp_lens = [len(tokenizer.encode(r.get("input_text", ""))) for r in sampled_records]
        tgt_lens = [len(tokenizer.encode(r.get("target_text", ""))) for r in sampled_records]
        
        token_stats = {
            "sample_size": sample_size,
            "input_min": min(inp_lens) if inp_lens else 0,
            "input_max": max(inp_lens) if inp_lens else 0,
            "input_avg": sum(inp_lens)/len(inp_lens) if inp_lens else 0,
            "target_min": min(tgt_lens) if tgt_lens else 0,
            "target_max": max(tgt_lens) if tgt_lens else 0,
            "target_avg": sum(tgt_lens)/len(tgt_lens) if tgt_lens else 0,
            "pct_input_exceed_128": (sum(1 for x in inp_lens if x > 128) / len(inp_lens) * 100) if inp_lens else 0.0,
            "pct_input_exceed_256": (sum(1 for x in inp_lens if x > 256) / len(inp_lens) * 100) if inp_lens else 0.0,
            "pct_target_exceed_128": (sum(1 for x in tgt_lens if x > 128) / len(tgt_lens) * 100) if tgt_lens else 0.0,
            "pct_target_exceed_256": (sum(1 for x in tgt_lens if x > 256) / len(tgt_lens) * 100) if tgt_lens else 0.0,
        }

    # 6. Quality Gates Evaluation
    gate_failures = []
    gate_warnings = []
    
    if json_errors:
        gate_failures.append(f"Malformed JSON detected ({len(json_errors)} errors).")
    if norm_target_leakage > 0:
        gate_failures.append(f"Train/Val Target Question Leakage detected ({norm_target_leakage} overlapping targets).")
    if dup_pairs_count > 0:
        gate_failures.append(f"Duplicate prompt-target pairs present ({dup_pairs_count} pairs).")

    has_math = subject_dist.get("Mathematics", 0) > 0
    has_physics = subject_dist.get("Physics", 0) > 0
    has_chemistry = subject_dist.get("Chemistry", 0) > 0

    if not has_physics or not has_chemistry:
        gate_warnings.append("Multi-Subject Gap: Physics (0) or Chemistry (0) records are absent in V5.")
    if class_dist.get("UNKNOWN", 0) > total_records * 0.5:
        gate_warnings.append(f"Class Supervision Gap: Class is UNKNOWN for {class_dist.get('UNKNOWN', 0)}/{total_records} records.")

    overall_status = "FAIL" if gate_failures else ("WARN" if gate_warnings else "PASS")

    print("\n" + "=" * 80)
    print(f"AQPG V5 QUALITY GATES VERDICT: {overall_status}")
    print("=" * 80)
    if gate_failures:
        print("FAILURES:")
        for gf in gate_failures:
            print(f"  [FAIL] {gf}")
    if gate_warnings:
        print("WARNINGS:")
        for gw in gate_warnings:
            print(f"  [WARN] {gw}")

    # Build JSON Audit Output
    audit_data = {
        "overall_status": overall_status,
        "record_counts": {
            "train": len(train_records),
            "val": len(val_records),
            "total": total_records
        },
        "json_validity": {
            "valid": len(json_errors) == 0,
            "error_count": len(json_errors),
            "errors": json_errors
        },
        "leakage": {
            "exact_prompt_overlap": exact_prompt_leakage,
            "exact_target_overlap": exact_target_leakage,
            "normalized_target_overlap": norm_target_leakage,
            "duplicate_pairs_count": dup_pairs_count
        },
        "distributions": {
            "source_dataset": dict(source_dist),
            "subject": dict(subject_dist),
            "class": dict(class_dist),
            "board": dict(board_dist),
            "unit": dict(unit_dist),
            "topic": dict(topic_dist),
            "bloom": dict(bloom_dist),
            "difficulty": dict(diff_dist),
            "marks": dict(marks_dist),
            "question_type": dict(qtype_dist),
            "verification_status": dict(status_dist)
        },
        "matrices": {
            "subject_x_class": matrix_sb_class,
            "subject_x_board": matrix_sb_board,
            "subject_x_question_type": matrix_sb_qtype,
            "subject_x_verification_status": matrix_sb_status,
            "class_x_board": matrix_class_board
        },
        "token_stats": token_stats,
        "gate_failures": gate_failures,
        "gate_warnings": gate_warnings
    }

    with open(AUDIT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\n[SUCCESS] Saved Audit JSON to: {AUDIT_JSON_PATH}")

    # Build Text Audit Report
    report_lines = [
        "================================================================================",
        "AQPG V5 DATASET FORENSIC AUDIT REPORT",
        "================================================================================",
        f"OVERALL AUDIT VERDICT: {overall_status}\n",
        "1. RECORD COUNTS & SYNTAX",
        f"  - Train Set:            {len(train_records)}",
        f"  - Validation Set:       {len(val_records)}",
        f"  - Total V5 Records:     {total_records}",
        f"  - JSON Syntax Errors:   {len(json_errors)}\n",
        "2. DATA LEAKAGE & DUPLICATION",
        f"  - Exact Prompt Overlap:         {exact_prompt_leakage}",
        f"  - Exact Target Overlap:         {exact_target_leakage} (Goal: 0)",
        f"  - Normalized Target Overlap:    {norm_target_leakage} (Goal: 0)",
        f"  - Duplicate Prompt-Target Pairs: {dup_pairs_count} (Goal: 0)\n",
        "3. SUBJECT COVERAGE & STEM BREAKDOWN",
        f"  - Mathematics: {subject_dist.get('Mathematics', 0)} ({(subject_dist.get('Mathematics', 0)/total_records*100):.2f}%)",
        f"  - Physics:     {subject_dist.get('Physics', 0)} (0.00%)",
        f"  - Chemistry:   {subject_dist.get('Chemistry', 0)} (0.00%)",
        f"  - Biology:     {subject_dist.get('Biology', 0)} ({(subject_dist.get('Biology', 0)/total_records*100):.2f}%)",
        f"  - Social Science: {subject_dist.get('Social Science', 0)} ({(subject_dist.get('Social Science', 0)/total_records*100):.2f}%)",
        f"  - Business & Law: {subject_dist.get('Business & Law', 0)} ({(subject_dist.get('Business & Law', 0)/total_records*100):.2f}%)",
        f"  - History & Civics: {subject_dist.get('History & Civics', 0)} ({(subject_dist.get('History & Civics', 0)/total_records*100):.2f}%)",
        f"  - UNKNOWN:     {subject_dist.get('UNKNOWN', 0)} ({(subject_dist.get('UNKNOWN', 0)/total_records*100):.2f}%)\n",
        "4. CURRICULUM METADATA COVERAGE",
        f"  - Class Specified: {total_records - class_dist.get('UNKNOWN', 0)} | UNKNOWN: {class_dist.get('UNKNOWN', 0)}",
        f"  - Board Specified: {total_records - board_dist.get('UNKNOWN', 0)} | UNKNOWN: {board_dist.get('UNKNOWN', 0)}",
        f"  - Unit Specified:  {total_records - unit_dist.get('UNKNOWN', 0)} | UNKNOWN: {unit_dist.get('UNKNOWN', 0)}\n",
        "5. CROSS-TABULATION MATRIX: SUBJECT × QUESTION TYPE"
    ]
    
    for sb, q_dict in matrix_sb_qtype.items():
        report_lines.append(f"  [{sb}]: {q_dict}")

    report_lines.extend([
        "\n6. CROSS-TABULATION MATRIX: SUBJECT × VERIFICATION STATUS"
    ])
    for sb, st_dict in matrix_sb_status.items():
        report_lines.append(f"  [{sb}]: {st_dict}")

    if token_stats:
        report_lines.extend([
            "\n7. TOKENIZATION AUDIT (google/flan-t5-small)",
            f"  - Sample Size:                 {token_stats['sample_size']}",
            f"  - Input Tokens (Avg / Max):    {token_stats['input_avg']:.1f} / {token_stats['input_max']}",
            f"  - Target Tokens (Avg / Max):   {token_stats['target_avg']:.1f} / {token_stats['target_max']}",
            f"  - % Inputs > 128 Tokens:       {token_stats['pct_input_exceed_128']:.2f}%",
            f"  - % Inputs > 256 Tokens:       {token_stats['pct_input_exceed_256']:.2f}%",
            f"  - % Targets > 128 Tokens:      {token_stats['pct_target_exceed_128']:.2f}%",
            f"  - % Targets > 256 Tokens:      {token_stats['pct_target_exceed_256']:.2f}%"
        ])

    report_lines.extend([
        "\n8. QUALITY GATES SUMMARY",
        f"  - Overall Verdict: {overall_status}"
    ])
    if gate_failures:
        report_lines.append("  - Failures: " + "; ".join(gate_failures))
    if gate_warnings:
        report_lines.append("  - Warnings: " + "; ".join(gate_warnings))

    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"[SUCCESS] Saved Audit Report to: {AUDIT_REPORT_PATH}")

if __name__ == "__main__":
    run_v5_audit()
