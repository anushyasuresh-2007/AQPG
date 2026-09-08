"""
clean_eduqg.py
Preprocessing script for EduQG datasets (eduqg_llm_formatted.csv, eduqg_train.json, eduqg_val.json)
"""

import os
import json
import pandas as pd

BLOOM_INT_MAP = {
    1: "Remember",
    2: "Understand",
    3: "Apply",
    4: "Analyze",
    "1": "Remember",
    "2": "Understand",
    "3": "Apply",
    "4": "Analyze"
}

def clean_eduqg_csv(filepath: str) -> list[dict]:
    """Cleans eduqg_llm_formatted.csv"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    df = pd.read_csv(filepath)
    records = []
    
    for idx, row in df.iterrows():
        prompt = str(row['prompt']).strip() if pd.notnull(row['prompt']) else ""
        if not prompt:
            continue
            
        opt_A = str(row['A']).strip() if pd.notnull(row['A']) else ""
        opt_B = str(row['B']).strip() if pd.notnull(row['B']) else ""
        opt_C = str(row['C']).strip() if pd.notnull(row['C']) else ""
        opt_D = str(row['D']).strip() if pd.notnull(row['D']) else ""
        opt_E = str(row['E']).strip() if pd.notnull(row['E']) else ""
        
        options_dict = {
            "A": opt_A, "B": opt_B, "C": opt_C, "D": opt_D, "E": opt_E
        }
        # Filter out empty options
        options = {k: v for k, v in options_dict.items() if v}
        
        ans_letter = str(row['answer']).strip() if pd.notnull(row['answer']) else ""
        ans_text = options.get(ans_letter, ans_letter)
        
        record = {
            "source_dataset": "eduqg",
            "source_file": os.path.basename(filepath),
            "question": prompt,
            "answer": ans_text,
            "context": None,
            "options": options,
            "subject": "General Studies / Business",
            "chapter": None,
            "unit": None,
            "topic": None,
            "board": None,
            "class_level": None,
            "bloom_level": None,
            "difficulty": "easy",
            "question_type": "MCQ",
            "marks": 1,
            "explanation": None,
            "numerical_data": None
        }
        records.append(record)
        
    print(f"[clean_eduqg_csv] Processed {len(records)} records from {filepath}")
    return records

def clean_eduqg_json(filepath: str) -> list[dict]:
    """Cleans eduqg_train.json or eduqg_val.json"""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
        
    with open(filepath, "r", encoding="utf-8") as f:
        docs = json.load(f)
        
    records = []
    fname = os.path.basename(filepath)
    
    for doc in docs:
        bname = doc.get("bname", "")
        formatted_subject = bname.replace("_", " ").title() if bname else None
        chapter = doc.get("chapter", None)
        summary = doc.get("summary", "").strip()
        chapter_text = doc.get("chapter_text", "").strip()
        
        for q_item in doc.get("questions", []):
            q_info = q_item.get("question", {})
            q_text = ""
            choices = []
            
            if isinstance(q_info, dict):
                q_text = q_info.get("question_text") or q_info.get("normal_format") or q_info.get("cloze_format") or ""
                choices = q_info.get("question_choices", [])
            elif isinstance(q_info, str):
                q_text = q_info
                
            q_text = q_text.strip()
            if not q_text:
                continue
                
            a_info = q_item.get("answer", {})
            ans_text = ""
            if isinstance(a_info, dict):
                ans_text = a_info.get("ans_text", "")
            elif isinstance(a_info, str):
                ans_text = a_info
                
            bloom_raw = q_item.get("bloom")
            bloom_level = BLOOM_INT_MAP.get(bloom_raw, None) if bloom_raw is not None else None
            
            hl_context = q_item.get("hl_context", "") or q_item.get("hl_sentences", "") or summary or chapter_text[:500]
            # Clean context highlight tokens (<hl>)
            hl_context = hl_context.replace("<hl>", "").replace("  ", " ").strip()
            
            options_dict = None
            if choices and isinstance(choices, list):
                q_type = "MCQ"
                labels = ["A", "B", "C", "D", "E", "F"]
                options_dict = {labels[i]: str(choice).strip() for i, choice in enumerate(choices) if i < len(labels)}
                marks = 1
                difficulty = "easy"
            elif q_info.get("cloze_format") and not choices:
                q_type = "Very Short Answer"
                marks = 1
                difficulty = "easy"
            else:
                q_type = "Short Answer"
                marks = 2
                difficulty = "medium"
                
            if bloom_level in ["Apply", "Analyze"]:
                difficulty = "medium"
                if q_type == "Short Answer":
                    q_type = "Application Based"
                    marks = 3
                    
            record = {
                "source_dataset": "eduqg",
                "source_file": fname,
                "question": q_text,
                "answer": ans_text,
                "context": hl_context if hl_context else None,
                "options": options_dict,
                "subject": formatted_subject,
                "chapter": f"Chapter {chapter}" if chapter else None,
                "unit": None,
                "topic": summary[:100] if summary else None,
                "board": None,
                "class_level": None,
                "bloom_level": bloom_level,
                "difficulty": difficulty,
                "question_type": q_type,
                "marks": marks,
                "explanation": None,
                "numerical_data": None
            }
            records.append(record)
            
    print(f"[clean_eduqg_json] Processed {len(records)} records from {filepath}")
    return records

def clean_all_eduqg(extracted_dir: str) -> list[dict]:
    csv_path = os.path.join(extracted_dir, "eduqg", "eduqg_llm_formatted.csv")
    train_json = os.path.join(extracted_dir, "eduqg", "eduqg_train.json")
    val_json = os.path.join(extracted_dir, "eduqg", "eduqg_val.json")
    
    records = []
    if os.path.exists(csv_path):
        records.extend(clean_eduqg_csv(csv_path))
    if os.path.exists(train_json):
        records.extend(clean_eduqg_json(train_json))
    if os.path.exists(val_json):
        records.extend(clean_eduqg_json(val_json))
        
    print(f"[clean_all_eduqg] Total EduQG records: {len(records)}")
    return records

if __name__ == "__main__":
    extracted = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\extracted"
    res = clean_all_eduqg(extracted)
    print(f"Sample EduQG clean record: {res[0] if res else 'None'}")
