"""
audit_qg_dataset_v4.py
AQPG V4 Dataset Forensic Audit, Quality Gates, Tokenization & Control Condition Validation Engine.

Performs 23 Forensic Checks, Tokenization Analysis (google/flan-t5-small), Control Tag Rate Calculation,
and Quality Gate PASS/WARN/FAIL evaluation across qg_train_dataset_v4.jsonl and qg_validation_dataset_v4.jsonl.

Outputs:
  - backend/ml/models/qg_flan_t5/qg_dataset_v4_audit.json
  - backend/ml/models/qg_flan_t5/qg_dataset_v4_audit_report.txt
"""

import os
import sys
import re
import json
import random
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple

# Safe PyTorch & Transformers loading
torch_lib = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\.venv\lib\site-packages\torch\lib"
if os.path.exists(torch_lib):
    try:
        os.add_dll_directory(torch_lib)
    except Exception:
        pass
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from transformers import AutoTokenizer

QG_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\qg_flan_t5"
TRAIN_V4_PATH = os.path.join(QG_DIR, "qg_train_dataset_v4.jsonl")
VAL_V4_PATH = os.path.join(QG_DIR, "qg_validation_dataset_v4.jsonl")

AUDIT_JSON_PATH = os.path.join(QG_DIR, "qg_dataset_v4_audit.json")
AUDIT_REPORT_PATH = os.path.join(QG_DIR, "qg_dataset_v4_audit_report.txt")

TOKENIZER_MODEL = "google/flan-t5-small"

def normalize_text(text: str) -> str:
    """Normalize text for leakage & duplicate checks."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())

def load_and_validate_jsonl(filepath: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Loads JSONL file and validates JSON syntax per line."""
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

def extract_control_tags(input_prompt: str) -> Dict[str, str]:
    """Extracts control tags from formatted prompt."""
    tags = {}
    if not input_prompt:
        return tags
    parts = input_prompt.split("|")
    for part in parts:
        part = part.strip()
        if ":" in part:
            k, v = part.split(":", 1)
            tags[k.strip().lower()] = v.strip()
    return tags

def run_forensic_audit():
    print("=" * 80)
    print("AQPG V4 DATASET FORENSIC AUDIT & QUALITY GATES")
    print("=" * 80)
    
    # 1 & 2: Load & Validate JSON Syntax
    train_records, train_json_errs = load_and_validate_jsonl(TRAIN_V4_PATH)
    val_records, val_json_errs = load_and_validate_jsonl(VAL_V4_PATH)
    
    json_errors = train_json_errs + val_json_errs
    total_records = len(train_records) + len(val_records)
    
    print(f"Train Records Count: {len(train_records)}")
    print(f"Val Records Count:   {len(val_records)}")
    print(f"Total V4 Records:    {total_records}")
    print(f"JSON Syntax Errors:  {len(json_errors)}")
    
    all_records = train_records + val_records
    
    # 3 & 4: Required Fields & Empty Inputs/Targets
    required_fields = ["input_text", "target_text", "answer", "subject", "topic", "bloom", "difficulty", "marks", "question_type", "source_dataset", "source_id"]
    missing_required_counts = Counter()
    empty_input_count = 0
    empty_target_count = 0
    
    for r in all_records:
        inp = str(r.get("input_text") or "").strip()
        tgt = str(r.get("target_text") or "").strip()
        if not inp:
            empty_input_count += 1
        if not tgt:
            empty_target_count += 1
            
        for f in required_fields:
            if f not in r or r[f] is None or str(r[f]).strip() == "":
                missing_required_counts[f] += 1

    # 5 & 6: Duplicate Detection
    seen_pair_keys = set()
    dup_pairs_count = 0
    for r in all_records:
        pair_key = (r.get("input_text", ""), r.get("target_text", ""))
        if pair_key in seen_pair_keys:
            dup_pairs_count += 1
        else:
            seen_pair_keys.add(pair_key)
            
    # 7, 8, 9, 10: Train / Validation Leakage Analysis
    train_exact_prompts = set(r.get("input_text", "") for r in train_records)
    val_exact_prompts = set(r.get("input_text", "") for r in val_records)
    exact_prompt_leakage = len(train_exact_prompts.intersection(val_exact_prompts))
    
    train_norm_prompts = set(normalize_text(r.get("input_text", "")) for r in train_records)
    val_norm_prompts = set(normalize_text(r.get("input_text", "")) for r in val_records)
    norm_prompt_leakage = len(train_norm_prompts.intersection(val_norm_prompts))
    
    train_exact_targets = set(r.get("target_text", "") for r in train_records)
    val_exact_targets = set(r.get("target_text", "") for r in val_records)
    exact_target_leakage = len(train_exact_targets.intersection(val_exact_targets))
    
    train_norm_targets = set(normalize_text(r.get("target_text", "")) for r in train_records)
    val_norm_targets = set(normalize_text(r.get("target_text", "")) for r in val_records)
    norm_target_leakage = len(train_norm_targets.intersection(val_norm_targets))
    
    # 11-21: Distribution Analysis
    source_dist = Counter(r.get("source_dataset", "unknown") for r in all_records)
    subject_dist = Counter(r.get("subject", "unspecified") for r in all_records)
    topic_dist = Counter(r.get("topic", "unspecified") for r in all_records)
    unit_dist = Counter(r.get("unit") if r.get("unit") is not None else "MISSING" for r in all_records)
    class_dist = Counter(str(r.get("class")) if r.get("class") is not None else "MISSING" for r in all_records)
    board_dist = Counter(str(r.get("board")) if r.get("board") is not None else "MISSING" for r in all_records)
    bloom_dist = Counter(r.get("bloom", "unspecified") for r in all_records)
    diff_dist = Counter(r.get("difficulty", "unspecified") for r in all_records)
    marks_dist = Counter(str(r.get("marks")) for r in all_records)
    qtype_dist = Counter(r.get("question_type", "unspecified") for r in all_records)
    status_dist = Counter(r.get("verification_status", "unspecified") for r in all_records)
    
    # 22: Numerical Answer Presence
    num_ans_count = sum(1 for r in all_records if r.get("answer") and any(c.isdigit() for c in str(r["answer"])))
    
    # 23: Input Control Tag Presence
    control_fields = ["subject", "topic", "unit", "class", "board", "bloom", "difficulty", "marks", "question_type"]
    tag_presence_counts = Counter()
    for r in all_records:
        tags = extract_control_tags(r.get("input_text", ""))
        for cf in control_fields:
            if cf in tags and tags[cf] not in ["none", "unspecified", "null"]:
                tag_presence_counts[cf] += 1
                
    tag_presence_rates = {cf: (tag_presence_counts[cf] / total_records * 100) if total_records > 0 else 0.0 for cf in control_fields}

    # TOKENIZATION ANALYSIS (google/flan-t5-small)
    print("\nLoading tokenizer for tokenization analysis:", TOKENIZER_MODEL)
    try:
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_MODEL)
    except Exception as e:
        print(f"Warning: Could not load tokenizer ({e}). Tokenization analysis skipped.")
        tokenizer = None
        
    token_stats = {}
    if tokenizer:
        subject_samples = defaultdict(list)
        for r in all_records:
            sb = r.get("subject", "Mathematics")
            subject_samples[sb].append(r)
            
        for sb, s_recs in subject_samples.items():
            inp_lens = []
            tgt_lens = []
            sample_subset = random.sample(s_recs, min(1000, len(s_recs)))
            for r in sample_subset:
                inp_t = len(tokenizer.encode(r.get("input_text", "")))
                tgt_t = len(tokenizer.encode(r.get("target_text", "")))
                inp_lens.append(inp_t)
                tgt_lens.append(tgt_t)
                
            token_stats[sb] = {
                "sample_count": len(sample_subset),
                "input_min": min(inp_lens) if inp_lens else 0,
                "input_max": max(inp_lens) if inp_lens else 0,
                "input_avg": sum(inp_lens)/len(inp_lens) if inp_lens else 0,
                "target_min": min(tgt_lens) if tgt_lens else 0,
                "target_max": max(tgt_lens) if tgt_lens else 0,
                "target_avg": sum(tgt_lens)/len(tgt_lens) if tgt_lens else 0,
                "pct_above_256": (sum(1 for x in inp_lens if x > 256) / len(inp_lens) * 100) if inp_lens else 0,
                "pct_above_384": (sum(1 for x in inp_lens if x > 384) / len(inp_lens) * 100) if inp_lens else 0,
                "pct_above_512": (sum(1 for x in inp_lens if x > 512) / len(inp_lens) * 100) if inp_lens else 0,
            }

    # QUALITY GATES EVALUATION (PASS / WARN / FAIL)
    gate_failures = []
    gate_warnings = []
    
    if json_errors:
        gate_failures.append(f"Malformed JSON detected ({len(json_errors)} errors).")
    if empty_input_count > 0 or empty_target_count > 0:
        gate_failures.append(f"Empty input ({empty_input_count}) or target ({empty_target_count}) fields detected.")
    if norm_target_leakage > 0:
        gate_failures.append(f"Train/Val Target Question Leakage detected ({norm_target_leakage} overlapping targets).")
    if dup_pairs_count > total_records * 0.05:
        gate_failures.append(f"Excessive duplicate prompt-target pairs ({dup_pairs_count} pairs).")

    # Domain Presence Checks
    has_math = subject_dist.get("Mathematics", 0) > 0
    has_physics = subject_dist.get("Physics", 0) > 0
    has_chemistry = subject_dist.get("Chemistry", 0) > 0
    has_class_data = any(k != "MISSING" for k in class_dist.keys())
    has_board_data = any(k != "MISSING" for k in board_dist.keys())
    has_unit_data = any(k != "MISSING" for k in unit_dist.keys())

    if not has_physics or not has_chemistry:
        gate_warnings.append("Multi-subject imbalance: Physics or Chemistry data is missing in current V4 dataset.")
    if not has_class_data or not has_board_data or not has_unit_data:
        gate_warnings.append("Supervision gap: Class, Board, or Unit metadata is missing from active records.")

    overall_status = "FAIL" if gate_failures else ("WARN" if gate_warnings else "PASS")
    
    print("\n" + "=" * 80)
    print(f"AQPG V4 QUALITY GATES VERDICT: {overall_status}")
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
        "required_field_missing": dict(missing_required_counts),
        "empty_input_count": empty_input_count,
        "empty_target_count": empty_target_count,
        "duplicate_pairs_count": dup_pairs_count,
        "leakage": {
            "exact_prompt_overlap": exact_prompt_leakage,
            "normalized_prompt_overlap": norm_prompt_leakage,
            "exact_target_overlap": exact_target_leakage,
            "normalized_target_overlap": norm_target_leakage
        },
        "domain_presence": {
            "Mathematics": has_math,
            "Physics": has_physics,
            "Chemistry": has_chemistry,
            "Class": has_class_data,
            "Board": has_board_data,
            "Unit": has_unit_data
        },
        "control_tag_presence_rates": tag_presence_rates,
        "distributions": {
            "source_dataset": dict(source_dist),
            "subject": dict(subject_dist),
            "bloom": dict(bloom_dist),
            "difficulty": dict(diff_dist),
            "marks": dict(marks_dist),
            "question_type": dict(qtype_dist),
            "verification_status": dict(status_dist),
            "class": dict(class_dist),
            "board": dict(board_dist),
            "unit": dict(unit_dist)
        },
        "token_stats": token_stats,
        "gate_failures": gate_failures,
        "gate_warnings": gate_warnings
    }

    with open(AUDIT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_data, f, indent=2)
    print(f"\nSaved audit JSON to: {AUDIT_JSON_PATH}")

    # Build Text Audit Report
    report_lines = [
        "================================================================================",
        "AQPG V4 DATASET FORENSIC AUDIT REPORT",
        "================================================================================",
        f"OVERALL STATUS: {overall_status}\n",
        "1. RECORD COUNTS & JSON SYNTAX",
        f"  - Train Set:         {len(train_records)}",
        f"  - Validation Set:    {len(val_records)}",
        f"  - Total V4 Records:  {total_records}",
        f"  - JSON Syntax Errors:{len(json_errors)}\n",
        "2. DATA LEAKAGE ANALYSIS",
        f"  - Exact Prompt Overlap:      {exact_prompt_leakage}",
        f"  - Normalized Prompt Overlap: {norm_prompt_leakage}",
        f"  - Exact Target Overlap:      {exact_target_leakage}",
        f"  - Normalized Target Overlap: {norm_target_leakage} (Goal: 0)\n",
        "3. ACTUAL DOMAIN & CURRICULUM DATA PRESENCE",
        f"  - Mathematics Data: {has_math} ({subject_dist.get('Mathematics', 0)} records)",
        f"  - Physics Data:     {has_physics} ({subject_dist.get('Physics', 0)} records)",
        f"  - Chemistry Data:   {has_chemistry} ({subject_dist.get('Chemistry', 0)} records)",
        f"  - Class Data:       {has_class_data}",
        f"  - Board Data:       {has_board_data}",
        f"  - Unit Data:        {has_unit_data}\n",
        "4. CONTROL TAG PRESENCE RATES IN INPUT PROMPTS:"
    ]
    for tag, rate in tag_presence_rates.items():
        report_lines.append(f"  - {tag}: {rate:.2f}%")

    if not has_class_data or not has_board_data or not has_unit_data:
        report_lines.append("\n  [EXPLICIT REPORT]: Architecture supports this control, but the current dataset does not provide sufficient supervision.")

    report_lines.extend([
        "\n5. CATEGORICAL DISTRIBUTIONS IN V4",
        "\nVerification Status Distribution:"
    ])
    for k, v in status_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_records*100:.2f}%)")
        
    report_lines.append("\nBloom Taxonomy Distribution:")
    for k, v in bloom_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_records*100:.2f}%)")

    report_lines.extend([
        "\n6. TOKENIZATION STATS (google/flan-t5-small)"
    ])
    for sb, ts in token_stats.items():
        report_lines.append(f"  [{sb}] Input Tokens (Avg: {ts['input_avg']:.1f}, Max: {ts['input_max']}) | Target Tokens (Avg: {ts['target_avg']:.1f}, Max: {ts['target_max']})")

    report_lines.extend([
        "\n7. QUALITY GATES VERDICT SUMMARY",
        f"  - Status: {overall_status}"
    ])
    if gate_failures:
        report_lines.append("  Failures: " + "; ".join(gate_failures))
    if gate_warnings:
        report_lines.append("  Warnings: " + "; ".join(gate_warnings))

    with open(AUDIT_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(f"Saved audit report text to: {AUDIT_REPORT_PATH}")
    return audit_data

if __name__ == "__main__":
    run_forensic_audit()
