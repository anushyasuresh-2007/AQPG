"""
build_unified_dataset.py
Combines cleaned records from all extracted datasets (Bloom, EduQG, Reasoning) into a unified dataset matching the unified schema.
Outputs:
  - datasets/unified/unified_questions.jsonl
  - datasets/unified/unified_questions.csv
"""

import os
import json
import pandas as pd
from clean_bloom import clean_bloom_dataset
from clean_eduqg import clean_all_eduqg
from clean_reasoning import clean_all_reasoning

EXTRACTED_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\extracted"
OUTPUT_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified"

def build_unified_dataset():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("=" * 80)
    print("STARTING UNIFIED DATASET AGGREGATION & DEDUPLICATION")
    print("=" * 80)
    
    all_records = []
    
    # 1. Clean Bloom Dataset
    bloom_path = os.path.join(EXTRACTED_DIR, "bloom", "blooms_taxonomy_dataset.csv")
    if os.path.exists(bloom_path):
        all_records.extend(clean_bloom_dataset(bloom_path))
        
    # 2. Clean EduQG Datasets
    all_records.extend(clean_all_eduqg(EXTRACTED_DIR))
    
    # 3. Clean Reasoning Datasets
    all_records.extend(clean_all_reasoning(EXTRACTED_DIR))
    
    print(f"\nTotal raw records before deduplication: {len(all_records)}")
    
    # Deduplication based on question text (case-insensitive & whitespace trimmed)
    seen_questions = set()
    unique_records = []
    dedup_count = 0
    
    for idx, rec in enumerate(all_records):
        rec["id"] = idx + 1
        q_norm = str(rec["question"]).strip().lower()
        
        # We allow duplicate questions if options or answers differ, but flag exact string matches within the same dataset
        dedup_key = (rec["source_dataset"], q_norm)
        if dedup_key in seen_questions:
            dedup_count += 1
            continue
            
        seen_questions.add(dedup_key)
        unique_records.append(rec)
        
    print(f"Removed {dedup_count} exact duplicate records within dataset sources.")
    print(f"Total unique unified records: {len(unique_records)}")
    
    # Write JSONL
    jsonl_path = os.path.join(OUTPUT_DIR, "unified_questions.jsonl")
    with open(jsonl_path, "w", encoding="utf-8") as f:
        for rec in unique_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"\n[SUCCESS] Saved unified JSONL to: {jsonl_path}")
    
    # Write CSV
    csv_path = os.path.join(OUTPUT_DIR, "unified_questions.csv")
    df = pd.DataFrame(unique_records)
    # Format dictionary columns as JSON strings for CSV compatibility
    if "options" in df.columns:
        df["options"] = df["options"].apply(lambda x: json.dumps(x) if isinstance(x, dict) else x)
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[SUCCESS] Saved unified CSV to: {csv_path}")
    
    # Print Summary Statistics
    print("\n" + "=" * 80)
    print("UNIFIED DATASET SUMMARY AUDIT")
    print("=" * 80)
    print("Record breakdown by Source Dataset:")
    print(df["source_dataset"].value_counts().to_string())
    print("\nRecord breakdown by Question Type:")
    print(df["question_type"].value_counts().to_string())
    print("\nRecord breakdown by Bloom Level:")
    print(df["bloom_level"].value_counts(dropna=False).to_string())
    print("=" * 80)
    
    return unique_records

if __name__ == "__main__":
    build_unified_dataset()
