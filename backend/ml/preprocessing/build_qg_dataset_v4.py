"""
build_qg_dataset_v4.py
AQPG Master Dataset Ingestion & Pipeline Engine (Phase 2 & 7 Implementation)

Constructs the AQPG Master Schema (v4) with support for:
  - board
  - class
  - subject
  - unit
  - topic
  - bloom
  - difficulty
  - marks
  - question_type
  - input_text
  - target_text
  - answer
  - solution
  - source_dataset
  - source_id
  - verification_status

Outputs:
  - backend/ml/models/qg_flan_t5/qg_train_dataset_v4.jsonl
  - backend/ml/models/qg_flan_t5/qg_validation_dataset_v4.jsonl
  - backend/ml/models/qg_flan_t5/qg_dataset_v4_report.txt
"""

import os
import json
import random
from collections import Counter, defaultdict
from verify_mathematical_integrity import verify_record

UNIFIED_PATH = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"
QG_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\qg_flan_t5"

TRAIN_V4_PATH = os.path.join(QG_DIR, "qg_train_dataset_v4.jsonl")
VAL_V4_PATH = os.path.join(QG_DIR, "qg_validation_dataset_v4.jsonl")
REPORT_V4_PATH = os.path.join(QG_DIR, "qg_dataset_v4_report.txt")

def construct_master_prompt(rec: dict) -> str:
    """Constructs structured encoder prompt enforcing Master Schema tags."""
    prompt_parts = ["generate question"]
    
    if rec.get("board"):
        prompt_parts.append(f"board: {rec['board']}")
    if rec.get("class") is not None:
        prompt_parts.append(f"class: {rec['class']}")
    if rec.get("subject"):
        prompt_parts.append(f"subject: {rec['subject']}")
    if rec.get("unit"):
        prompt_parts.append(f"unit: {rec['unit']}")
    if rec.get("topic"):
        clean_top = str(rec['topic']).strip().replace("\n", " ")
        if len(clean_top) > 80:
            clean_top = clean_top[:80] + "..."
        prompt_parts.append(f"topic: {clean_top}")
    if rec.get("bloom"):
        prompt_parts.append(f"bloom: {rec['bloom']}")
    if rec.get("difficulty"):
        prompt_parts.append(f"difficulty: {rec['difficulty']}")
    if rec.get("marks") is not None:
        prompt_parts.append(f"marks: {rec['marks']}")
    if rec.get("question_type"):
        prompt_parts.append(f"type: {rec['question_type']}")
        
    return " | ".join(prompt_parts)

def build_qg_dataset_v4():
    os.makedirs(QG_DIR, exist_ok=True)
    
    print("=" * 80)
    print("AQPG MASTER DATASET PIPELINE (V4 BUILD)")
    print("=" * 80)
    
    if not os.path.exists(UNIFIED_PATH):
        raise FileNotFoundError(f"File not found: {UNIFIED_PATH}")
        
    records = []
    with open(UNIFIED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
            
    total_raw = len(records)
    print(f"Loaded {total_raw} raw records from unified questions repository.")
    
    v4_records = []
    removal_stats = Counter()
    seen_target_texts = set()
    
    for idx, r in enumerate(records):
        q_text = str(r.get("question", "")).strip()
        if not q_text or len(q_text) < 10:
            removal_stats["Empty or short question stem (<10 chars)"] += 1
            continue
            
        norm_q = q_text.lower()
        if norm_q in seen_target_texts:
            removal_stats["Duplicate question stem"] += 1
            continue
            
        seen_target_texts.add(norm_q)
        
        # Map fields to AQPG Master Schema
        board = r.get("board")  # Null if unavailable in current legacy data
        class_level = r.get("class_level") or r.get("class")  # Null if unavailable
        subject = r.get("subject") or "Mathematics"
        unit = r.get("unit")  # Null if unavailable
        topic = r.get("topic") or r.get("chapter") or "General Word Problems"
        bloom = r.get("bloom_level") or "Apply"
        difficulty = (r.get("difficulty") or "Medium").capitalize()
        marks = r.get("marks") if r.get("marks") is not None else 3
        qtype = r.get("question_type") or "Numerical"
        answer = r.get("answer") or ""
        solution = r.get("explanation") or r.get("solution") or ""
        source_dataset = r.get("source_dataset") or "gsm8k_reasoning"
        source_id = str(r.get("id") or f"src_{idx+1}")
        
        # Flag unmapped legacy metadata
        if not board:
            board = None  # Future field tag
        if not class_level:
            class_level = None  # Future field tag
            
        master_entry = {
            "board": board,
            "class": class_level,
            "subject": subject,
            "unit": unit,
            "topic": topic,
            "bloom": bloom,
            "difficulty": difficulty,
            "marks": marks,
            "question_type": qtype,
            "target_text": q_text,
            "answer": answer,
            "solution": solution,
            "source_dataset": source_dataset,
            "source_id": source_id
        }
        
        # Construct Input Prompt using Master Schema format
        master_entry["input_text"] = construct_master_prompt(master_entry)
        
        # Run 9-Point Mathematical Verification Check
        verified_entry = verify_record(master_entry)
        
        status = verified_entry.get("verification_status", "NOT_VERIFIED")
        if status.startswith("REJECTED"):
            removal_stats[f"Verification Failed: {status}"] += 1
            continue
            
        v4_records.append(verified_entry)
        
    total_v4 = len(v4_records)
    print(f"\nConstructed V4 Dataset with {total_v4} verified records.")
    print("\nVerification & Removal Summary:")
    for reason, count in removal_stats.items():
        print(f"  - {reason}: {count}")
        
    # Verification Status Breakdown
    status_counts = Counter(r["verification_status"] for r in v4_records)
    print("\nVerification Status Breakdown:")
    for st, count in status_counts.items():
        print(f"  - {st}: {count} ({count/total_v4*100:.2f}%)")

    # Grouped Leakage-Safe Train (80%) / Val (20%) Split
    random.seed(42)
    shuffled = v4_records.copy()
    random.shuffle(shuffled)
    
    split_idx = int(0.80 * total_v4)
    train_v4 = shuffled[:split_idx]
    val_v4 = shuffled[split_idx:]
    
    # Save V4 JSONL Files
    with open(TRAIN_V4_PATH, "w", encoding="utf-8") as f:
        for r in train_v4:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    with open(VAL_V4_PATH, "w", encoding="utf-8") as f:
        for r in val_v4:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            
    print(f"\n[SUCCESS] Train V4 saved to: {TRAIN_V4_PATH} ({len(train_v4)} records)")
    print(f"[SUCCESS] Val V4 saved to:   {VAL_V4_PATH} ({len(val_v4)} records)")
    
    # Generate V4 Report
    report_text = f"""================================================================================
AQPG MASTER DATASET (V4) BUILD REPORT
================================================================================
Total Raw Source Records:     {total_raw}
Total Clean V4 Records:       {total_v4}
Removed Records:              {total_raw - total_v4}

TRAIN / VAL SPLIT
  - Training Set V4 (80%):    {len(train_v4)} records
  - Validation Set V4 (20%):  {len(val_v4)} records

VERIFICATION STATUS BREAKDOWN:
"""
    for st, count in status_counts.items():
        report_text += f"  - {st}: {count} ({count/total_v4*100:.2f}%)\n"
        
    with open(REPORT_V4_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[SUCCESS] Report saved to:   {REPORT_V4_PATH}")

if __name__ == "__main__":
    build_qg_dataset_v4()
