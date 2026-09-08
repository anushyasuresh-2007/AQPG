"""
build_qg_dataset_v2.py
Re-prepares and quality-filters the Question Generation (QG) dataset for FLAN-T5.
Constructs controlled input prompts using exact source metadata fields.
Calculates and reports prompt collision metrics accurately.

Outputs:
  - backend/ml/models/qg_flan_t5/qg_train_dataset_backup.jsonl (backup)
  - backend/ml/models/qg_flan_t5/qg_train_dataset_v2.jsonl (80% train)
  - backend/ml/models/qg_flan_t5/qg_validation_dataset_v2.jsonl (20% validation)
  - backend/ml/models/qg_flan_t5/qg_preprocessing_report.txt (audit report)
"""

import os
import shutil
import json
import random
import pandas as pd
from collections import Counter

UNIFIED_PATH = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"
QG_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\qg_flan_t5"

ORIGINAL_QG_PATH = os.path.join(QG_DIR, "qg_train_dataset.jsonl")
BACKUP_QG_PATH = os.path.join(QG_DIR, "qg_train_dataset_backup.jsonl")

TRAIN_V2_PATH = os.path.join(QG_DIR, "qg_train_dataset_v2.jsonl")
VAL_V2_PATH = os.path.join(QG_DIR, "qg_validation_dataset_v2.jsonl")
REPORT_PATH = os.path.join(QG_DIR, "qg_preprocessing_report.txt")

def process_qg_dataset_v2():
    os.makedirs(QG_DIR, exist_ok=True)
    
    print("=" * 80)
    print("STEP 1: CREATING BACKUP OF ORIGINAL QG DATASET")
    print("=" * 80)
    
    if os.path.exists(ORIGINAL_QG_PATH):
        shutil.copyfile(ORIGINAL_QG_PATH, BACKUP_QG_PATH)
        print(f"[SUCCESS] Created backup at: {BACKUP_QG_PATH}")
    else:
        print(f"[INFO] Original file {ORIGINAL_QG_PATH} not found. Skipping backup copy.")
        
    print("\n" + "=" * 80)
    print("STEP 2 & 3: READING UNIFIED DATASET & BUILDING CONTROLLED PROMPTS")
    print("=" * 80)
    
    if not os.path.exists(UNIFIED_PATH):
        raise FileNotFoundError(f"[ERROR] Unified dataset not found at: {UNIFIED_PATH}")
        
    raw_records = []
    with open(UNIFIED_PATH, "r", encoding="utf-8") as f:
        for line in f:
            raw_records.append(json.loads(line))
            
    print(f"Loaded {len(raw_records)} raw records from {UNIFIED_PATH}")
    
    processed_samples = []
    removal_reasons = Counter()
    seen_targets = set()
    seen_prompt_target_pairs = set()
    
    for idx, r in enumerate(raw_records):
        target_q = str(r.get("question", "")).strip()
        
        # Quality Filter 1: Empty or extremely short target
        if not target_q or len(target_q) < 5:
            removal_reasons["Empty or trivial target question"] += 1
            continue
            
        # Quality Filter 2: Duplicate Target Question (Exact string)
        norm_target = target_q.lower()
        if norm_target in seen_targets:
            removal_reasons["Duplicate target question"] += 1
            continue
            
        # Extract Actual Metadata (DO NOT INVENT VALUES)
        board = str(r.get("board")).strip() if r.get("board") else "unknown"
        class_level = str(r.get("class_level")).strip() if r.get("class_level") else "unknown"
        subject = str(r.get("subject")).strip() if r.get("subject") else "unknown"
        
        # Topic / Unit / Chapter
        topic = str(r.get("topic")).strip() if r.get("topic") else ""
        if not topic and r.get("chapter"):
            topic = str(r.get("chapter")).strip()
        if not topic:
            topic = "unknown"
            
        bloom = str(r.get("bloom_level")).strip() if r.get("bloom_level") else "unknown"
        difficulty = str(r.get("difficulty")).strip() if r.get("difficulty") else "unknown"
        marks = str(r.get("marks")).strip() if r.get("marks") is not None else "unknown"
        q_type = str(r.get("question_type")).strip() if r.get("question_type") else "unknown"
        
        # Context snippet (clean newlines and whitespace)
        raw_context = r.get("context")
        if raw_context and isinstance(raw_context, str) and raw_context.strip():
            context = raw_context.strip().replace("\n", " ").replace("\r", " ")
            context = " ".join(context.split())[:300]
        else:
            context = "unknown"
            
        # Build Rich Controlled Input Prompt String
        prompt_parts = [
            "generate question",
            f"board: {board}",
            f"class: {class_level}",
            f"subject: {subject}",
            f"topic: {topic}",
            f"bloom: {bloom}",
            f"difficulty: {difficulty}",
            f"marks: {marks}",
            f"type: {q_type}"
        ]
        
        if context != "unknown":
            prompt_parts.append(f"context: {context}")
            
        input_prompt = " | ".join(prompt_parts)
        
        # Check duplicate prompt-target pairs
        pair_key = (input_prompt, norm_target)
        if pair_key in seen_prompt_target_pairs:
            removal_reasons["Duplicate prompt-target pair"] += 1
            continue
            
        seen_targets.add(norm_target)
        seen_prompt_target_pairs.add(pair_key)
        
        sample_obj = {
            "id": idx + 1,
            "input_text": input_prompt,
            "target_text": target_q,
            "board": board,
            "class_level": class_level,
            "subject": subject,
            "topic": topic,
            "bloom_level": bloom,
            "difficulty": difficulty,
            "marks": marks,
            "question_type": q_type,
            "has_context": context != "unknown",
            "answer": r.get("answer"),
            "explanation": r.get("explanation"),
            "source_dataset": r.get("source_dataset")
        }
        processed_samples.append(sample_obj)
        
    print(f"\nFinal Quality-Filtered QG Samples: {len(processed_samples)}")
    print("Removal Breakdown:")
    for k, v in removal_reasons.items():
        print(f"  - {k}: {v}")
        
    print("\n" + "=" * 80)
    print("STEP 5: PROMPT COLLISION ANALYSIS")
    print("=" * 80)
    
    total_final = len(processed_samples)
    final_df = pd.DataFrame(processed_samples)
    
    unique_prompts = final_df['input_text'].nunique()
    dup_prompts = total_final - unique_prompts
    collision_rate = (dup_prompts / total_final * 100) if total_final > 0 else 0.0
    
    unique_targets = final_df['target_text'].nunique()
    dup_targets = total_final - unique_targets
    
    print(f"Total Final Samples:    {total_final}")
    print(f"Unique Input Prompts:   {unique_prompts}")
    print(f"Duplicate Prompts:      {dup_prompts}")
    print(f"Prompt Collision Rate:  {collision_rate:.4f}%")
    print(f"Unique Target Questions:{unique_targets}")
    print(f"Duplicate Targets:      {dup_targets}")
    
    print("\n" + "=" * 80)
    print("STEP 7: TRAIN / VALIDATION DYNAMIC SPLIT (80% / 20%)")
    print("=" * 80)
    
    # Shuffle with fixed seed for zero leakage
    random.seed(42)
    shuffled_samples = processed_samples.copy()
    random.shuffle(shuffled_samples)
    
    split_idx = int(0.80 * total_final)
    train_samples = shuffled_samples[:split_idx]
    val_samples = shuffled_samples[split_idx:]
    
    print(f"Train Set Size (80%): {len(train_samples)}")
    print(f"Val Set Size (20%):   {len(val_samples)}")
    
    # Verify zero data leakage
    train_targets = set(s['target_text'].lower() for s in train_samples)
    val_targets = set(s['target_text'].lower() for s in val_samples)
    leakage_count = len(train_targets.intersection(val_targets))
    print(f"Target Question Leakage between Train and Val: {leakage_count} (Expected 0)")
    
    print("\n" + "=" * 80)
    print("STEP 8: SAVING OUTPUT FILES")
    print("=" * 80)
    
    with open(TRAIN_V2_PATH, "w", encoding="utf-8") as f:
        for s in train_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"[SUCCESS] Saved train set v2 to: {TRAIN_V2_PATH}")
    
    with open(VAL_V2_PATH, "w", encoding="utf-8") as f:
        for s in val_samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    print(f"[SUCCESS] Saved validation set v2 to: {VAL_V2_PATH}")
    
    # Generate Distributions for Audit Report
    def get_dist_dict(df, col):
        return df[col].value_counts(dropna=False).to_dict()
        
    bloom_dist = get_dist_dict(final_df, 'bloom_level')
    qtype_dist = get_dist_dict(final_df, 'question_type')
    diff_dist = get_dist_dict(final_df, 'difficulty')
    marks_dist = get_dist_dict(final_df, 'marks')
    subject_dist = get_dist_dict(final_df, 'subject')
    class_dist = get_dist_dict(final_df, 'class_level')
    board_dist = get_dist_dict(final_df, 'board')
    
    report_lines = [
        "================================================================================",
        "QUESTION GENERATION (QG) PREPROCESSING & AUDIT REPORT (V2)",
        "Target Architecture: google/flan-t5-base / flan-t5-small",
        "================================================================================\n",
        "1. FILE LOCATIONS",
        f"  - Source Unified Dataset:  {UNIFIED_PATH}",
        f"  - Original QG Dataset:     {ORIGINAL_QG_PATH}",
        f"  - Backup QG Dataset:       {BACKUP_QG_PATH}",
        f"  - Train Set V2 (80%):      {TRAIN_V2_PATH}",
        f"  - Val Set V2 (20%):        {VAL_V2_PATH}\n",
        "2. DATASET FILTERING STATS",
        f"  - Original Raw Records:    {len(raw_records)}",
        f"  - Final Clean QG Samples:  {total_final}",
        f"  - Removed Records Total:   {len(raw_records) - total_final}\n",
        "  Removal Reasons Breakdown:"
    ]
    
    for k, v in removal_reasons.items():
        report_lines.append(f"    * {k}: {v}")
        
    report_lines.extend([
        "\n3. PROMPT COLLISION & LEAKAGE ANALYSIS",
        f"  - Total Final Samples:     {total_final}",
        f"  - Unique Input Prompts:    {unique_prompts}",
        f"  - Duplicate Input Prompts: {dup_prompts}",
        f"  - Prompt Collision Rate:   {collision_rate:.4f}%",
        f"  - Unique Target Questions: {unique_targets}",
        f"  - Duplicate Targets:       {dup_targets}",
        f"  - Train/Val Target Leak:   {leakage_count}\n",
        "4. TRAIN / VALIDATION SPLIT METRICS",
        f"  - Training Set Size:       {len(train_samples)} ({len(train_samples)/total_final*100:.2f}%)",
        f"  - Validation Set Size:     {len(val_samples)} ({len(val_samples)/total_final*100:.2f}%)\n",
        "5. CATEGORICAL DISTRIBUTIONS IN FINAL QG DATASET\n",
        "Bloom Taxonomy Distribution:"
    ])
    
    for k, v in bloom_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nQuestion Type Distribution:")
    for k, v in qtype_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nDifficulty Distribution:")
    for k, v in diff_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nMarks Distribution:")
    for k, v in marks_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nSubject Distribution:")
    for k, v in subject_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")
        
    report_lines.append("\nClass Level Distribution:")
    for k, v in class_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")

    report_lines.append("\nBoard Distribution:")
    for k, v in board_dist.items():
        report_lines.append(f"  - {k}: {v} ({v/total_final*100:.2f}%)")

    report_text = "\n".join(report_lines)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"[SUCCESS] Saved preprocessing report to: {REPORT_PATH}")

    print("\n" + "=" * 80)
    print("STEP 9: VALIDATING 20 RANDOM SAMPLE PROMPTS")
    print("=" * 80)
    
    sample_20 = random.sample(processed_samples, min(20, len(processed_samples)))
    for idx, s in enumerate(sample_20):
        print(f"\n--- SAMPLE {idx + 1} ---")
        print(f"INPUT:\n{s['input_text']}")
        print(f"TARGET:\n{s['target_text']}")
        if s['answer']:
            print(f"ANSWER: {s['answer']}")

if __name__ == "__main__":
    process_qg_dataset_v2()
