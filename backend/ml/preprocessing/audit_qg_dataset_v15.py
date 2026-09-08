"""
audit_qg_dataset_v15.py
AQPG Phase 15 Forensic Audit, Quality Gates, Cross-Tabulation & Tokenization Engine.

Performs Comprehensive Audit across:
  - datasets/v15/qg_dataset_v15.jsonl (Master)
  - datasets/v15/qg_train_dataset_v15.jsonl (Train)
  - datasets/v15/qg_validation_dataset_v15.jsonl (Val)

Generates 8 Cross-Tabulation Matrices:
  1. Subject x Class
  2. Subject x Board
  3. Subject x Question Type
  4. Subject x Verification Status
  5. Class x Board
  6. Source x Subject
  7. Source x Class
  8. Source x License

Executes:
  - Exact & Normalized Target Overlap Analysis (Leakage Gate)
  - Exact & Normalized Prompt Overlap Analysis
  - Duplicate Prompt-Target Pair Detection
  - FLAN-T5-Small Tokenization Analysis (seed 42, 2000 samples)
  - Hard/Soft Quality Gates & Empirical Training Authorization Evaluation

Outputs:
  - datasets/v15/qg_dataset_v15_audit.json
  - datasets/v15/qg_dataset_v15_audit_report.txt
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
V15_DIR = os.path.join(DATASETS_DIR, "v15")

MASTER_V15_PATH = os.path.join(V15_DIR, "qg_dataset_v15.jsonl")
TRAIN_V15_PATH = os.path.join(V15_DIR, "qg_train_dataset_v15.jsonl")
VAL_V15_PATH = os.path.join(V15_DIR, "qg_validation_dataset_v15.jsonl")

AUDIT_JSON_PATH = os.path.join(V15_DIR, "qg_dataset_v15_audit.json")
AUDIT_REPORT_PATH = os.path.join(V15_DIR, "qg_dataset_v15_audit_report.txt")

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

def run_v15_audit():
    print("=" * 80)
    print("AQPG PHASE 15 DATASET FORENSIC AUDIT & TRAINING AUTHORIZATION GATE")
    print("=" * 80)
    
    train_records, train_errs = load_and_validate_jsonl(TRAIN_V15_PATH)
    val_records, val_errs = load_and_validate_jsonl(VAL_V15_PATH)
    
    json_errors = train_errs + val_errs
    total_records = len(train_records) + len(val_records)
    all_records = train_records + val_records
    
    print(f"Train Records Count: {len(train_records)}")
    print(f"Val Records Count:   {len(val_records)}")
    print(f"Total V15 Records:   {total_records}")
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
    license_dist = Counter(r.get("license", "UNKNOWN") for r in all_records)

    # 4. Cross-Tabulation Matrices (8 Matrices)
    matrix_sb_class = build_matrix(all_records, "subject", "class")
    matrix_sb_board = build_matrix(all_records, "subject", "board")
    matrix_sb_qtype = build_matrix(all_records, "subject", "question_type")
    matrix_sb_status = build_matrix(all_records, "subject", "verification_status")
    matrix_class_board = build_matrix(all_records, "class", "board")
    matrix_src_subject = build_matrix(all_records, "source_dataset", "subject")
    matrix_src_class = build_matrix(all_records, "source_dataset", "class")
    matrix_src_license = build_matrix(all_records, "source_dataset", "license")

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

    # 6. Quality Gates & Training Authorization Evaluation
    gate_failures = []
    gate_warnings = []
    
    if json_errors:
        gate_failures.append(f"Malformed JSON detected ({len(json_errors)} errors).")
    if norm_target_leakage > 0:
        gate_failures.append(f"Train/Val Target Question Leakage detected ({norm_target_leakage} overlapping targets).")
    if dup_pairs_count > 0:
        gate_failures.append(f"Duplicate prompt-target pairs present ({dup_pairs_count} pairs).")

    math_cnt = subject_dist.get("Mathematics", 0)
    phy_cnt = subject_dist.get("Physics", 0)
    chem_cnt = subject_dist.get("Chemistry", 0)

    math_pass = math_cnt >= 5000
    phy_pass = phy_cnt >= 5000
    chem_pass = chem_cnt >= 5000

    if not phy_pass:
        gate_failures.append(f"Physics Target Threshold Gap: {phy_cnt} < 5,000 target records.")
    if not chem_pass:
        gate_failures.append(f"Chemistry Target Threshold Gap: {chem_cnt} < 5,000 target records.")
    if not math_pass:
        gate_failures.append(f"Mathematics Target Threshold Gap: {math_cnt} < 5,000 target records.")

    c9_cnt = class_dist.get("Class 9", 0)
    c10_cnt = class_dist.get("Class 10", 0)
    c11_cnt = class_dist.get("Class 11", 0)
    c12_cnt = class_dist.get("Class 12", 0)

    c9_pass = c9_cnt >= 1000
    c10_pass = c10_cnt >= 1000
    c11_pass = c11_cnt >= 1000
    c12_pass = c12_cnt >= 1000

    if not c9_pass:
        gate_failures.append(f"Class 9 Threshold Gap: {c9_cnt} < 1,000 records.")
    if not c10_pass:
        gate_failures.append(f"Class 10 Threshold Gap: {c10_cnt} < 1,000 records.")
    if not c11_pass:
        gate_failures.append(f"Class 11 Threshold Gap: {c11_cnt} < 1,000 records.")
    if not c12_pass:
        gate_failures.append(f"Class 12 Threshold Gap: {c12_cnt} < 1,000 records.")

    unknown_class_cnt = class_dist.get("UNKNOWN", 0)
    unknown_board_cnt = board_dist.get("UNKNOWN", 0)
    unknown_unit_cnt = unit_dist.get("UNKNOWN", 0)

    all_gates_pass = (
        len(gate_failures) == 0 and
        math_pass and phy_pass and chem_pass and
        c9_pass and c10_pass and c11_pass and c12_pass and
        norm_target_leakage == 0 and dup_pairs_count == 0 and len(json_errors) == 0
    )

    overall_status = "PASS" if all_gates_pass else ("FAIL" if gate_failures else "WARN")

    # Readiness Verdict Decision Logic
    if all_gates_pass:
        readiness_verdict = "A. TRAINING AUTHORIZED"
    elif any("Malformed" in gf or "Leakage" in gf for gf in gate_failures):
        readiness_verdict = "C. DATA QUALITY FAILURE"
    else:
        readiness_verdict = "B. NEED MORE DATA"

    print("\n" + "=" * 80)
    print(f"AQPG PHASE 15 QUALITY GATES VERDICT: {overall_status}")
    print(f"EMPIRICAL READINESS VERDICT:       {readiness_verdict}")
    print("=" * 80)
    if gate_failures:
        print("GATE FAILURES:")
        for gf in gate_failures:
            print(f"  [FAIL] {gf}")
    if gate_warnings:
        print("GATE WARNINGS:")
        for gw in gate_warnings:
            print(f"  [WARN] {gw}")

    # Build JSON Audit Output
    audit_data = {
        "overall_status": overall_status,
        "readiness_verdict": readiness_verdict,
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
        "subject_thresholds": {
            "mathematics": {"count": math_cnt, "threshold": 5000, "pass": math_pass},
            "physics": {"count": phy_cnt, "threshold": 5000, "pass": phy_pass},
            "chemistry": {"count": chem_cnt, "threshold": 5000, "pass": chem_pass}
        },
        "class_thresholds": {
            "class_9": {"count": c9_cnt, "threshold": 1000, "pass": c9_pass},
            "class_10": {"count": c10_cnt, "threshold": 1000, "pass": c10_pass},
            "class_11": {"count": c11_cnt, "threshold": 1000, "pass": c11_pass},
            "class_12": {"count": c12_cnt, "threshold": 1000, "pass": c12_pass}
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
            "verification_status": dict(status_dist),
            "license": dict(license_dist)
        },
        "matrices": {
            "subject_x_class": matrix_sb_class,
            "subject_x_board": matrix_sb_board,
            "subject_x_question_type": matrix_sb_qtype,
            "subject_x_verification_status": matrix_sb_status,
            "class_x_board": matrix_class_board,
            "source_x_subject": matrix_src_subject,
            "source_x_class": matrix_src_class,
            "source_x_license": matrix_src_license
        },
        "token_stats": token_stats,
        "gate_failures": gate_failures,
        "gate_warnings": gate_warnings
    }

    with open(AUDIT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\n[SUCCESS] Saved Phase 15 Audit JSON to: {AUDIT_JSON_PATH}")

    # Build Text Audit Report
    report_lines = [
        "================================================================================",
        "AQPG PHASE 15 DATASET FORENSIC AUDIT REPORT",
        "================================================================================",
        f"OVERALL AUDIT VERDICT:    {overall_status}",
        f"EMPIRICAL READINESS:      {readiness_verdict}\n",
        "1. RECORD COUNTS & SYNTAX",
        f"  - Train Set (80%):      {len(train_records)}",
        f"  - Validation Set (20%): {len(val_records)}",
        f"  - Total V15 Records:    {total_records}",
        f"  - JSON Syntax Errors:   {len(json_errors)}\n",
        "2. DATA LEAKAGE & DUPLICATION",
        f"  - Exact Prompt Overlap:          {exact_prompt_leakage}",
        f"  - Exact Target Overlap:          {exact_target_leakage} (Goal: 0)",
        f"  - Normalized Target Overlap:     {norm_target_leakage} (Goal: 0)",
        f"  - Duplicate Prompt-Target Pairs: {dup_pairs_count} (Goal: 0)\n",
        "3. STEM SUBJECT BREAKDOWN",
        f"  - Mathematics:   {math_cnt} ({(math_cnt/total_records*100):.2f}%) [Threshold >=5,000: {'PASS' if math_pass else 'FAIL'}]",
        f"  - Physics:       {phy_cnt} ({(phy_cnt/total_records*100):.2f}%) [Threshold >=5,000: {'PASS' if phy_pass else 'FAIL'}]",
        f"  - Chemistry:     {chem_cnt} ({(chem_cnt/total_records*100):.2f}%) [Threshold >=5,000: {'PASS' if chem_pass else 'FAIL'}]",
        f"  - Biology:       {subject_dist.get('Biology', 0)} ({(subject_dist.get('Biology', 0)/total_records*100):.2f}%)",
        f"  - General Science:{subject_dist.get('General Science', 0)} ({(subject_dist.get('General Science', 0)/total_records*100):.2f}%)",
        f"  - Social Science:{subject_dist.get('Social Science', 0)} ({(subject_dist.get('Social Science', 0)/total_records*100):.2f}%)",
        f"  - Business & Law:{subject_dist.get('Business & Law', 0)} ({(subject_dist.get('Business & Law', 0)/total_records*100):.2f}%)",
        f"  - History/Civics:{subject_dist.get('History & Civics', 0)} ({(subject_dist.get('History & Civics', 0)/total_records*100):.2f}%)",
        f"  - UNKNOWN:       {subject_dist.get('UNKNOWN', 0)} ({(subject_dist.get('UNKNOWN', 0)/total_records*100):.2f}%)\n",
        "4. K-12 CLASS GROUNDING BREAKDOWN",
        f"  - Class 9:       {c9_cnt} ({(c9_cnt/total_records*100):.2f}%) [Threshold >=1,000: {'PASS' if c9_pass else 'FAIL'}]",
        f"  - Class 10:      {c10_cnt} ({(c10_cnt/total_records*100):.2f}%) [Threshold >=1,000: {'PASS' if c10_pass else 'FAIL'}]",
        f"  - Class 11:      {c11_cnt} ({(c11_cnt/total_records*100):.2f}%) [Threshold >=1,000: {'PASS' if c11_pass else 'FAIL'}]",
        f"  - Class 12:      {c12_cnt} ({(c12_cnt/total_records*100):.2f}%) [Threshold >=1,000: {'PASS' if c12_pass else 'FAIL'}]",
        f"  - Total Class 9-12:{total_records - unknown_class_cnt} ({((total_records - unknown_class_cnt)/total_records*100):.2f}%)",
        f"  - Class UNKNOWN: {unknown_class_cnt} ({(unknown_class_cnt/total_records*100):.2f}%)\n",
        "5. BOARD GROUNDING BREAKDOWN",
        f"  - CBSE:             {board_dist.get('CBSE', 0)}",
        f"  - State Board:      {board_dist.get('State Board', 0)}",
        f"  - OpenStax Academic:{board_dist.get('OpenStax Academic', 0)}",
        f"  - Public Benchmark: {board_dist.get('Public Benchmark', 0)}",
        f"  - UNKNOWN:          {unknown_board_cnt}\n",
        f"  - Unit UNKNOWN:     {unknown_unit_cnt} ({(unknown_unit_cnt/total_records*100):.2f}%)\n",
        "6. CROSS-TABULATION MATRICES:"
    ]

    report_lines.append("\nA. Subject x Class:")
    for sb, c_dict in matrix_sb_class.items():
        report_lines.append(f"  [{sb}]: {c_dict}")

    report_lines.append("\nB. Subject x Board:")
    for sb, b_dict in matrix_sb_board.items():
        report_lines.append(f"  [{sb}]: {b_dict}")

    report_lines.append("\nC. Subject x Question Type:")
    for sb, q_dict in matrix_sb_qtype.items():
        report_lines.append(f"  [{sb}]: {q_dict}")

    report_lines.append("\nD. Subject x Verification Status:")
    for sb, s_dict in matrix_sb_status.items():
        report_lines.append(f"  [{sb}]: {s_dict}")

    report_lines.append("\nE. Class x Board:")
    for cl, b_dict in matrix_class_board.items():
        report_lines.append(f"  [{cl}]: {b_dict}")

    report_lines.append("\nF. Source x Subject:")
    for src, sb_dict in matrix_src_subject.items():
        report_lines.append(f"  [{src}]: {sb_dict}")

    report_lines.append("\nG. Source x Class:")
    for src, cl_dict in matrix_src_class.items():
        report_lines.append(f"  [{src}]: {cl_dict}")

    report_lines.append("\nH. Source x License:")
    for src, lic_dict in matrix_src_license.items():
        report_lines.append(f"  [{src}]: {lic_dict}")

    if token_stats:
        report_lines.extend([
            "\n7. TOKENIZATION AUDIT (google/flan-t5-small)",
            f"  - Sample Size:                  {token_stats['sample_size']}",
            f"  - Input Tokens (Min / Max / Avg): {token_stats['input_min']} / {token_stats['input_max']} / {token_stats['input_avg']:.1f}",
            f"  - Target Tokens (Min / Max / Avg):{token_stats['target_min']} / {token_stats['target_max']} / {token_stats['target_avg']:.1f}",
            f"  - % Inputs > 128 Tokens:        {token_stats['pct_input_exceed_128']:.2f}%",
            f"  - % Inputs > 256 Tokens:        {token_stats['pct_input_exceed_256']:.2f}%",
            f"  - % Targets > 128 Tokens:       {token_stats['pct_target_exceed_128']:.2f}%",
            f"  - % Targets > 256 Tokens:       {token_stats['pct_target_exceed_256']:.2f}%"
        ])

    report_lines.extend([
        "\n8. QUALITY GATES & TRAINING AUTHORIZATION VERDICT",
        f"  - Quality Gate Status: {overall_status}",
        f"  - Final Verdict:        {readiness_verdict}"
    ])
    if gate_failures:
        report_lines.append("  - Failures: " + "; ".join(gate_failures))
    if gate_warnings:
        report_lines.append("  - Warnings: " + "; ".join(gate_warnings))

    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"[SUCCESS] Saved Phase 15 Audit Report to: {AUDIT_REPORT_PATH}")

if __name__ == "__main__":
    run_v15_audit()
