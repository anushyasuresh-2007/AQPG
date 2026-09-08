"""
seed_questions_from_unified.py
Seeds the MySQL / SQLite database with unified questions from datasets/unified/unified_questions.jsonl.
Preserves existing database structure and existing questions without dropping tables.
"""

import sys
import os
import json
from sqlalchemy.orm import Session

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database.database import engine, Base, SessionLocal
from app.models.bloom import Bloom
from app.models.subject import Subject
from app.models.unit import Unit
from app.models.question import Question
from app.models.question_option import QuestionOption

UNIFIED_JSONL = r"C:\Users\Divya\OneDrive\Desktop\AQPG\datasets\unified\unified_questions.jsonl"

BLOOM_LEVELS = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]

def seed_database(limit: int = 2000):
    print("=" * 80)
    print("SEEDING DATABASE WITH UNIFIED QUESTION BANK")
    print("=" * 80)
    
    try:
        Base.metadata.create_all(bind=engine)
        print("[SUCCESS] Database tables verified / created successfully.")
    except Exception as e:
        print(f"[WARNING] Database connection issue: {e}")
        
    db: Session = SessionLocal()
    
    try:
        # 1. Seed Bloom Levels
        bloom_map = {}
        for b_name in BLOOM_LEVELS:
            existing_b = db.query(Bloom).filter(Bloom.level_name == b_name).first()
            if not existing_b:
                existing_b = Bloom(level_name=b_name)
                db.add(existing_b)
                db.commit()
                db.refresh(existing_b)
            bloom_map[b_name.lower()] = existing_b.id
            bloom_map[b_name] = existing_b.id
            
        print(f"[SUCCESS] Verified Bloom Levels in DB: {list(bloom_map.keys())}")
        
        # 2. Cache Subjects and Units
        subject_map = {}
        unit_map = {}
        
        def get_or_create_subject(name: str) -> int:
            s_name = (name or "General Studies").strip()
            if s_name in subject_map:
                return subject_map[s_name]
                
            s = db.query(Subject).filter(Subject.subject_name == s_name).first()
            if not s:
                s = Subject(
                    subject_name=s_name,
                    class_name="Class 10",
                    board="CBSE",
                    subject_code=s_name[:10].upper().replace(" ", "_"),
                    subject_type="core",
                    active=True
                )
                db.add(s)
                db.commit()
                db.refresh(s)
            subject_map[s_name] = s.id
            return s.id
            
        def get_or_create_unit(subject_id: int, unit_title: str) -> int:
            u_name = (unit_title or "General Unit").strip()
            key = (subject_id, u_name)
            if key in unit_map:
                return unit_map[key]
                
            u = db.query(Unit).filter(Unit.subject_id == subject_id, Unit.unit_name == u_name).first()
            if not u:
                u = Unit(
                    subject_id=subject_id,
                    unit_name=u_name,
                    unit_number=1,
                    description=f"Unit: {u_name}",
                    active=True
                )
                db.add(u)
                db.commit()
                db.refresh(u)
            unit_map[key] = u.id
            return u.id
            
        # 3. Load Records from JSONL
        records = []
        with open(UNIFIED_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                records.append(json.loads(line))
                
        print(f"Loaded {len(records)} unified records from JSONL file.")
        
        inserted_q_count = 0
        skipped_count = 0
        
        import_records = records[:limit] if limit else records
        print(f"Seeding up to {len(import_records)} questions into database...")
        
        for idx, r in enumerate(import_records):
            q_text = str(r.get("question", "")).strip()
            if not q_text:
                continue
                
            existing = db.query(Question).filter(Question.question_text == q_text).first()
            if existing:
                skipped_count += 1
                continue
                
            subj_id = get_or_create_subject(r.get("subject"))
            unit_id = get_or_create_unit(subj_id, r.get("chapter") or "General Chapter")
            
            b_level_str = r.get("bloom_level") or "Understand"
            bloom_id = bloom_map.get(b_level_str, bloom_map.get("Understand"))
            
            num_data = r.get("numerical_data")
            if isinstance(num_data, dict):
                num_data = json.dumps(num_data)
                
            q_obj = Question(
                subject_id=subj_id,
                unit_id=unit_id,
                bloom_level_id=bloom_id,
                question_text=q_text,
                question_type=r.get("question_type") or "Short Answer",
                marks=r.get("marks") or 1,
                difficulty=(r.get("difficulty") or "medium").lower(),
                answer=r.get("answer"),
                explanation=r.get("explanation"),
                numerical_data=num_data,
                application_context=r.get("context"),
                source=r.get("source_dataset") or "Unified AQPG Dataset",
                source_type="imported",
                is_ai_generated=False,
                approved=True,
                status="approved",
                active=True
            )
            db.add(q_obj)
            db.commit()
            db.refresh(q_obj)
            
            # Options for MCQ
            options_data = r.get("options")
            if options_data:
                if isinstance(options_data, str):
                    try:
                        options_data = json.loads(options_data)
                    except:
                        options_data = None
                        
                if isinstance(options_data, dict):
                    correct_ans = (r.get("answer") or "").strip()
                    for opt_label, opt_text in options_data.items():
                        is_correct = (opt_text.strip() == correct_ans) or (opt_label.strip() == correct_ans)
                        opt_obj = QuestionOption(
                            question_id=q_obj.id,
                            option_label=opt_label,
                            option_text=opt_text,
                            is_correct=is_correct
                        )
                        db.add(opt_obj)
                    db.commit()
                    
            inserted_q_count += 1
            if inserted_q_count % 500 == 0:
                print(f"Progress: Inserted {inserted_q_count} questions...")
                
        print("\n" + "=" * 80)
        print(f"DATABASE SEEDING COMPLETED")
        print(f"Successfully inserted: {inserted_q_count} new questions")
        print(f"Skipped duplicates: {skipped_count}")
        print("=" * 80)
        
    except Exception as e:
        print(f"[ERROR] Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database(limit=2000)
