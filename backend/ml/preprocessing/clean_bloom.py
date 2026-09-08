"""
clean_bloom.py
Preprocessing script for blooms_taxonomy_dataset.csv
"""

import os
import pandas as pd

BLOOM_MAP = {
    "BT1": "Remember",
    "BT2": "Understand",
    "BT3": "Apply",
    "BT4": "Analyze",
    "BT5": "Evaluate",
    "BT6": "Create"
}

def clean_bloom_dataset(raw_filepath: str) -> list[dict]:
    """
    Cleans blooms_taxonomy_dataset.csv and returns records matching the unified schema.
    """
    if not os.path.exists(raw_filepath):
        raise FileNotFoundError(f"File not found: {raw_filepath}")
        
    df = pd.read_csv(raw_filepath)
    cleaned_records = []
    
    for idx, row in df.iterrows():
        q_text = str(row['Questions']).strip() if pd.notnull(row['Questions']) else ""
        raw_cat = str(row['Category']).strip() if pd.notnull(row['Category']) else ""
        
        if not q_text:
            continue
            
        bloom_level = BLOOM_MAP.get(raw_cat, raw_cat)
        
        # Determine default difficulty & question_type based on Bloom level
        if bloom_level in ["Remember", "Understand"]:
            q_type = "Short Answer"
            difficulty = "easy"
            marks = 1
        elif bloom_level in ["Apply", "Analyze"]:
            q_type = "Application Based"
            difficulty = "medium"
            marks = 2
        else:
            q_type = "Long Answer"
            difficulty = "hard"
            marks = 4
            
        record = {
            "source_dataset": "bloom_taxonomy",
            "source_file": os.path.basename(raw_filepath),
            "question": q_text,
            "answer": None,
            "context": None,
            "options": None,
            "subject": None,
            "chapter": None,
            "unit": None,
            "topic": None,
            "board": None,
            "class_level": None,
            "bloom_level": bloom_level,
            "difficulty": difficulty,
            "question_type": q_type,
            "marks": marks,
            "explanation": None,
            "numerical_data": None
        }
        cleaned_records.append(record)
        
    print(f"[clean_bloom] Processed {len(cleaned_records)} records from {raw_filepath}")
    return cleaned_records

if __name__ == "__main__":
    filepath = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\extracted\bloom\blooms_taxonomy_dataset.csv"
    res = clean_bloom_dataset(filepath)
    print(f"Sample clean record: {res[0] if res else 'None'}")
