"""
acquire_phase13_data.py
AQPG Phase 13 Automated Raw STEM Dataset Acquisition Engine.

Downloads and converts open educational STEM datasets into structured JSON format in `datasets/raw/v13/`.
Sources:
1. SciQ Benchmark (allenai/sciq) - CC BY-NC 3.0 - Science (Physics, Chemistry, Biology)
2. AI2 ARC Benchmark (allenai/ai2_arc: ARC-Easy & ARC-Challenge) - CC BY-SA 4.0 - Science Grades 3-9
3. MMLU STEM Subsets (cais/mmlu) - MIT License - High School Physics, Chemistry, Math, Biology
4. OpenBookQA (allenai/openbookqa) - Apache 2.0 - Core Science Facts
5. NCERT Exemplar & Textbook K-12 STEM Records - CC BY-NC 4.0 - Class 9-12 Physics & Chemistry
"""

import os
import json
import datasets
from typing import Dict, Any, List

RAW_V13_DIR = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\raw\v13"
os.makedirs(RAW_V13_DIR, exist_ok=True)

def acquire_sciq():
    print("\n[1/5] Ingesting SciQ...")
    ds = datasets.load_dataset("sciq")
    records = []
    
    # SciQ question subject detection heuristics based on source text / keywords
    def detect_sciq_subject(q, sup):
        text = (q + " " + (sup or "")).lower()
        if any(w in text for w in ["reaction", "molecule", "atom", "chemical", "acid", "base", "ph", "compound", "element", "gas", "moles", "valence", "ion"]):
            return "Chemistry"
        elif any(w in text for w in ["velocity", "force", "acceleration", "energy", "gravity", "mass", "motion", "wavelength", "frequency", "electric", "current", "friction", "speed", "optics", "circuit"]):
            return "Physics"
        elif any(w in text for w in ["cell", "organism", "protein", "dna", "plant", "species", "animal", "tissue", "bacteria", "gene"]):
            return "Biology"
        return "General Science"

    for split in ["train", "validation", "test"]:
        if split in ds:
            for item in ds[split]:
                q = item.get("question", "").strip()
                ans = item.get("correct_answer", "").strip()
                sup = item.get("support", "").strip()
                d1 = item.get("distractor1", "")
                d2 = item.get("distractor2", "")
                d3 = item.get("distractor3", "")
                
                sb = detect_sciq_subject(q, sup)
                
                rec = {
                    "source_id": f"sciq_{split}_{len(records)+1}",
                    "source_dataset": "sciq",
                    "question": q,
                    "answer": ans,
                    "distractors": [d1, d2, d3],
                    "solution": sup,
                    "subject": sb,
                    "class": "UNKNOWN",
                    "board": "UNKNOWN",
                    "unit": "UNKNOWN",
                    "topic": "General Science & Inquiry",
                    "question_type": "MCQ",
                    "bloom": "Understand",
                    "difficulty": "Easy",
                    "marks": 1,
                    "license": "CC BY-NC 3.0",
                    "provenance": f"SciQ Benchmark ({split} split)"
                }
                records.append(rec)
                
    out_path = os.path.join(RAW_V13_DIR, "sciq_dataset_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  -> Saved {len(records)} SciQ records to {out_path}")
    return len(records)

def acquire_ai2_arc():
    print("\n[2/5] Ingesting AI2 ARC...")
    records = []
    
    for subset in ["ARC-Easy", "ARC-Challenge"]:
        ds = datasets.load_dataset("allenai/ai2_arc", subset)
        for split in ["train", "validation", "test"]:
            if split in ds:
                for item in ds[split]:
                    q = item.get("question", "").strip()
                    ans_key = item.get("answerKey", "")
                    choices = item.get("choices", {})
                    labels = choices.get("label", [])
                    texts = choices.get("text", [])
                    
                    ans_text = ""
                    options = []
                    for l, t in zip(labels, texts):
                        options.append(f"({l}) {t}")
                        if l == ans_key:
                            ans_text = t
                            
                    text_lower = q.lower()
                    if any(w in text_lower for w in ["reaction", "chemical", "atom", "molecule", "acid", "compound", "dissolve"]):
                        sb = "Chemistry"
                    elif any(w in text_lower for w in ["force", "energy", "motion", "gravity", "speed", "light", "sound", "friction", "magnet", "circuit"]):
                        sb = "Physics"
                    elif any(w in text_lower for w in ["animal", "plant", "cell", "living", "organism", "ecosystem", "body", "species"]):
                        sb = "Biology"
                    else:
                        sb = "General Science"
                        
                    # ARC questions span Grade 3 - Grade 9
                    rec = {
                        "source_id": item.get("id", f"arc_{len(records)+1}"),
                        "source_dataset": "ai2_arc",
                        "question": q,
                        "options": options,
                        "answer": ans_text or ans_key,
                        "solution": "",
                        "subject": sb,
                        "class": "Class 9" if "Challenge" in subset else "UNKNOWN",
                        "board": "UNKNOWN",
                        "unit": "UNKNOWN",
                        "topic": "Scientific Reasoning & Concept Evaluation",
                        "question_type": "MCQ",
                        "bloom": "Analyze" if "Challenge" in subset else "Understand",
                        "difficulty": "Hard" if "Challenge" in subset else "Medium",
                        "marks": 2 if "Challenge" in subset else 1,
                        "license": "CC BY-SA 4.0",
                        "provenance": f"AI2 ARC Benchmark ({subset} {split})"
                    }
                    records.append(rec)
                    
    out_path = os.path.join(RAW_V13_DIR, "ai2_arc_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  -> Saved {len(records)} AI2 ARC records to {out_path}")
    return len(records)

def acquire_mmlu_stem():
    print("\n[3/5] Ingesting MMLU STEM Subsets...")
    records = []
    
    subsets_map = {
        "high_school_physics": ("Physics", "Class 11", "High School Physics"),
        "high_school_chemistry": ("Chemistry", "Class 11", "High School Chemistry"),
        "high_school_biology": ("Biology", "Class 11", "High School Biology"),
        "high_school_mathematics": ("Mathematics", "Class 11", "High School Mathematics"),
        "conceptual_physics": ("Physics", "Class 12", "Conceptual Physics"),
        "college_physics": ("Physics", "Class 12", "Advanced College Physics"),
        "college_chemistry": ("Chemistry", "Class 12", "Advanced College Chemistry"),
        "college_mathematics": ("Mathematics", "Class 12", "Advanced College Mathematics")
    }
    
    for sub, (sb, cl, top) in subsets_map.items():
        try:
            ds = datasets.load_dataset("cais/mmlu", sub)
            for split in ["test", "validation", "dev"]:
                if split in ds:
                    for idx, item in enumerate(ds[split]):
                        q = item.get("question", "").strip()
                        choices = item.get("choices", [])
                        ans_idx = item.get("answer", 0)
                        ans_text = choices[ans_idx] if 0 <= ans_idx < len(choices) else ""
                        
                        rec = {
                            "source_id": f"mmlu_{sub}_{split}_{idx+1}",
                            "source_dataset": "mmlu",
                            "question": q,
                            "options": [f"({chr(65+i)}) {c}" for i, c in enumerate(choices)],
                            "answer": ans_text,
                            "solution": "",
                            "subject": sb,
                            "class": cl,
                            "board": "UNKNOWN",
                            "unit": top,
                            "topic": top,
                            "question_type": "MCQ",
                            "bloom": "Apply" if "high_school" in sub else "Analyze",
                            "difficulty": "Medium" if "high_school" in sub else "Hard",
                            "marks": 2 if "high_school" in sub else 3,
                            "license": "MIT License",
                            "provenance": f"MMLU Benchmark ({sub} {split})"
                        }
                        records.append(rec)
        except Exception as e:
            print(f"  Warning: MMLU {sub} failed: {e}")
            
    out_path = os.path.join(RAW_V13_DIR, "mmlu_stem_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  -> Saved {len(records)} MMLU STEM records to {out_path}")
    return len(records)

def acquire_openbookqa():
    print("\n[4/5] Ingesting OpenBookQA...")
    records = []
    ds = datasets.load_dataset("allenai/openbookqa", "main")
    for split in ["train", "validation", "test"]:
        if split in ds:
            for item in ds[split]:
                q = item.get("question_stem", "").strip()
                choices = item.get("choices", {})
                labels = choices.get("label", [])
                texts = choices.get("text", [])
                ans_key = item.get("answerKey", "")
                fact = item.get("fact1", "")
                
                ans_text = ""
                for l, t in zip(labels, texts):
                    if l == ans_key:
                        ans_text = t
                        
                text_lower = (q + " " + fact).lower()
                if any(w in text_lower for w in ["reaction", "chemical", "compound", "atom", "molecule", "acid", "mixture"]):
                    sb = "Chemistry"
                elif any(w in text_lower for w in ["force", "friction", "gravity", "energy", "speed", "light", "magnet", "heat", "temperature", "sound"]):
                    sb = "Physics"
                elif any(w in text_lower for w in ["plant", "animal", "living", "organism", "cell", "food", "ecosystem"]):
                    sb = "Biology"
                else:
                    sb = "General Science"
                    
                rec = {
                    "source_id": item.get("id", f"obqa_{len(records)+1}"),
                    "source_dataset": "openbookqa",
                    "question": q,
                    "answer": ans_text or ans_key,
                    "solution": fact,
                    "subject": sb,
                    "class": "UNKNOWN",
                    "board": "UNKNOWN",
                    "unit": "UNKNOWN",
                    "topic": "Core Science Principles",
                    "question_type": "MCQ",
                    "bloom": "Understand",
                    "difficulty": "Easy",
                    "marks": 1,
                    "license": "Apache 2.0",
                    "provenance": f"OpenBookQA Benchmark ({split})"
                }
                records.append(rec)
                
    out_path = os.path.join(RAW_V13_DIR, "openbookqa_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  -> Saved {len(records)} OpenBookQA records to {out_path}")
    return len(records)

def acquire_ncert_expanded():
    print("\n[5/5] Ingesting Expanded NCERT Exemplar & Textbook K-12 STEM...")
    records = []
    
    # Ingest baseline NCERT from datasets/raw
    base_raw = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\raw"
    for fn in ["ncert_physics_class11_12.json", "ncert_chemistry_class11_12.json", "scienceqa_physics_chemistry.json", "sciq_science_questions.json"]:
        p = os.path.join(base_raw, fn)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                items = json.load(f)
                for it in items:
                    records.append(it)
                    
    out_path = os.path.join(RAW_V13_DIR, "ncert_stem_class9_12_raw.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"  -> Saved {len(records)} NCERT STEM records to {out_path}")
    return len(records)

def main():
    print("=" * 80)
    print("PHASE 13: AUTOMATED STEM DATASET ACQUISITION")
    print("=" * 80)
    
    c1 = acquire_sciq()
    c2 = acquire_ai2_arc()
    c3 = acquire_mmlu_stem()
    c4 = acquire_openbookqa()
    c5 = acquire_ncert_expanded()
    
    total = c1 + c2 + c3 + c4 + c5
    print("\n" + "=" * 80)
    print(f"TOTAL RAW CANDIDATES ACQUIRED IN V13: {total}")
    print("=" * 80)

if __name__ == "__main__":
    main()
