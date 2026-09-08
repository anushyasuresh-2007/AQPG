"""
clean_reasoning.py
Preprocessing script for GSM8K reasoning datasets (main_train.csv, main_test.csv, socratic_train.csv, socratic_test.csv)
"""

import os
import re
import json
import pandas as pd

def extract_math_formulas(answer_text: str) -> list[str]:
    """Extracts formulas inside <<...>> delimiters."""
    if not answer_text:
        return []
    return re.findall(r'<<(.*?)>>', answer_text)

def parse_gsm8k_answer(raw_answer: str, is_socratic: bool = False):
    """
    Parses GSM8K answer into final numeric answer, step-by-step explanation, and extracted formulas.
    """
    if not raw_answer:
        return "", "", []
        
    formulas = extract_math_formulas(raw_answer)
    
    parts = raw_answer.split("####")
    if len(parts) == 2:
        explanation = parts[0].strip()
        final_ans = parts[1].strip()
    else:
        explanation = raw_answer.strip()
        final_ans = raw_answer.strip()
        
    # Clean <<...>> tags from explanation for human-readable text
    cleaned_explanation = re.sub(r'<<.*?>>', '', explanation)
    cleaned_explanation = re.sub(r'  +', ' ', cleaned_explanation).strip()
    
    return final_ans, cleaned_explanation, formulas

def clean_reasoning_csv(filepath: str) -> list[dict]:
    """Cleans a single GSM8K reasoning CSV file."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    df = pd.read_csv(filepath)
    fname = os.path.basename(filepath)
    is_socratic = "socratic" in fname.lower()
    
    records = []
    
    for idx, row in df.iterrows():
        q_text = str(row['question']).strip() if pd.notnull(row['question']) else ""
        raw_ans = str(row['answer']).strip() if pd.notnull(row['answer']) else ""
        
        if not q_text:
            continue
            
        final_ans, explanation, formulas = parse_gsm8k_answer(raw_ans, is_socratic=is_socratic)
        
        num_steps = len(formulas)
        if num_steps <= 2:
            difficulty = "medium"
            marks = 3
        else:
            difficulty = "hard"
            marks = 4
            
        num_data_json = json.dumps({"formulas": formulas, "step_count": num_steps}) if formulas else None
        
        record = {
            "source_dataset": "gsm8k_reasoning",
            "source_file": fname,
            "question": q_text,
            "answer": final_ans,
            "context": None,
            "options": None,
            "subject": "Mathematics",
            "chapter": "Arithmetic & Quantitative Reasoning",
            "unit": None,
            "topic": "Word Problems & Calculation",
            "board": None,
            "class_level": None,
            "bloom_level": "Apply" if num_steps <= 2 else "Analyze",
            "difficulty": difficulty,
            "question_type": "Numerical",
            "marks": marks,
            "explanation": explanation,
            "numerical_data": num_data_json
        }
        records.append(record)
        
    print(f"[clean_reasoning_csv] Processed {len(records)} records from {filepath}")
    return records

def clean_all_reasoning(extracted_dir: str) -> list[dict]:
    reasoning_dir = os.path.join(extracted_dir, "reasoning")
    files = [
        os.path.join(reasoning_dir, "main_train.csv"),
        os.path.join(reasoning_dir, "main_test.csv"),
        os.path.join(reasoning_dir, "socratic_train.csv"),
        os.path.join(reasoning_dir, "socratic_test.csv"),
    ]
    
    records = []
    for fpath in files:
        if os.path.exists(fpath):
            records.extend(clean_reasoning_csv(fpath))
            
    print(f"[clean_all_reasoning] Total Reasoning records: {len(records)}")
    return records

if __name__ == "__main__":
    extracted = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\extracted"
    res = clean_all_reasoning(extracted)
    print(f"Sample Reasoning clean record: {res[0] if res else 'None'}")
