"""
train_qg_model.py
Prepares training data and pipeline for fine-tuning FLAN-T5 on Question Generation.
"""

import os
import json
import pandas as pd

UNIFIED_JSONL = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"
QG_MODEL_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\backend\ml\models\qg_flan_t5"

def prepare_qg_training_dataset():
    os.makedirs(QG_MODEL_DIR, exist_ok=True)
    
    print("=" * 80)
    print("PREPARING QUESTION GENERATION (QG) TRAINING DATASET")
    print("=" * 80)
    
    records = []
    with open(UNIFIED_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))
            
    qg_samples = []
    
    for r in records:
        q_text = r.get("question", "").strip()
        if not q_text:
            continue
            
        subject = r.get("subject") or "General Science"
        bloom = r.get("bloom_level") or "Understand"
        q_type = r.get("question_type") or "Short Answer"
        context = r.get("context") or ""
        
        # Build structured input prompt for FLAN-T5
        if context:
            input_prompt = f"generate question: type={q_type}, subject={subject}, bloom={bloom}, context={context[:300]}"
        else:
            input_prompt = f"generate question: type={q_type}, subject={subject}, bloom={bloom}"
            
        target = q_text
        
        qg_samples.append({
            "input_text": input_prompt,
            "target_text": target,
            "subject": subject,
            "bloom_level": bloom,
            "question_type": q_type,
            "answer": r.get("answer"),
            "explanation": r.get("explanation")
        })
        
    print(f"Generated {len(qg_samples)} QG prompt-target training pairs!")
    
    output_path = os.path.join(QG_MODEL_DIR, "qg_train_dataset.jsonl")
    with open(output_path, "w", encoding="utf-8") as f:
        for sample in qg_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")
            
    meta_path = os.path.join(QG_MODEL_DIR, "qg_model_config.json")
    config = {
        "base_model": "google/flan-t5-base",
        "fallback_model": "google/flan-t5-small",
        "train_samples_count": len(qg_samples),
        "dataset_path": output_path
    }
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
        
    print(f"[SUCCESS] Saved QG training dataset to: {output_path}")
    print(f"[SUCCESS] Saved QG config to: {meta_path}")
    print("=" * 80)

if __name__ == "__main__":
    prepare_qg_training_dataset()
