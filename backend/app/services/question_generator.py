"""Service for assembling question papers via Question Bank first, AI hybrid generation, deduplication, and persistent storage."""

import datetime
import hashlib
import json
import random
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple


from sqlalchemy.orm import Session

from app.models.academic_class import AcademicClass
from app.models.bloom import Bloom
from app.models.board import Board
from app.models.generated_paper import GeneratedPaper
from app.models.question import Question
from app.models.subject import Subject
from app.models.unit import Unit
from app.services.ai.base import AIQuestionPrompt
from app.services.ai.generator_factory import get_ai_generator


def normalize_text_for_comparison(text: str) -> str:
    """Normalize question text for similarity/duplicate checking."""
    # Strip any ending unit/chapter parenthetical tags e.g. (Unit 1 - Matrices) or (Chapter 3)
    text = re.sub(r"\s*\([^)]*(?:unit|chapter)[^)]*\)\s*$", "", text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def compute_question_hash(text: str) -> str:
    """Compute deterministic MD5 hash for exact duplicate detection."""
    norm = normalize_text_for_comparison(text)
    return hashlib.md5(norm.encode("utf-8")).hexdigest()


def _find_exact_question_subset(
    questions: List[Question],
    required_marks: int,
    preferred_difficulty: Optional[str] = None,
    target_count: Optional[int] = None,
) -> Optional[List[Question]]:
    """
    Combinatorial subset search: Find a subset of questions whose marks total exactly the target required marks.
    Prioritizes matching preferred difficulty and target count.
    """
    if required_marks <= 0:
        return []
    if not questions:
        return None

    def question_sort_key(q: Question):
        diff_score = 0
        if preferred_difficulty and q.difficulty.lower() == preferred_difficulty.lower():
            diff_score = 2
        elif q.difficulty.lower() == "medium":
            diff_score = 1
        return (diff_score, -q.marks, random.random())

    ordered_questions = sorted(questions, key=question_sort_key, reverse=True)
    memo: Dict[Tuple[int, int], Optional[List[int]]] = {}

    def dfs(index: int, remaining_marks: int) -> Optional[List[int]]:
        if remaining_marks == 0:
            return []
        if index >= len(ordered_questions):
            return None

        key = (index, remaining_marks)
        if key in memo:
            return memo[key]

        question = ordered_questions[index]
        if question.marks <= remaining_marks:
            take_result = dfs(index + 1, remaining_marks - question.marks)
            if take_result is not None:
                res = [index] + take_result
                memo[key] = res
                return res

        skip_result = dfs(index + 1, remaining_marks)
        memo[key] = skip_result
        return skip_result

    selected_indexes = dfs(0, required_marks)
    if selected_indexes is None:
        return None

    return [ordered_questions[i] for i in selected_indexes]


def generate_question_paper(
    db: Session,
    subject_id: int,
    selected_units: List[int],
    total_marks: int,
    bloom_distribution: Dict[str, int],
    number_of_questions: Optional[int] = None,
    difficulty: Optional[str] = "medium",
    source_mode: Optional[str] = "hybrid",  # "bank", "ai", "hybrid"
    use_ai: Optional[bool] = None,
    user_id: Optional[int] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    board_id: Optional[int] = None,
    class_id: Optional[int] = None,
    stream_id: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Generate an examination paper combining approved Question Bank content, AI hybrid synthesis,
    exact mark balancing, and persistent record storage.
    """
    if use_ai is True:
        source_mode = "ai"
    elif use_ai is False and source_mode == "ai":
        source_mode = "bank"

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise ValueError("Subject not found")

    # Validate board and class if explicitly provided
    if board_id and subject.board_id:
        if subject.board_id != board_id:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to board ID {board_id}")
    elif board and subject.board and subject.board.lower() != board.lower():
        raise ValueError(f"Subject '{subject.subject_name}' does not belong to board '{board}'")

    if class_id and subject.class_id:
        if subject.class_id != class_id:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to class ID {class_id}")
    elif class_name and subject.class_name:
        roman_map = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10", "xi": "11", "xii": "12"}
        req_c = class_name.lower().replace("class", "").strip()
        sub_c = subject.class_name.lower().replace("class", "").strip()
        req_c = roman_map.get(req_c, req_c)
        sub_c = roman_map.get(sub_c, sub_c)
        if req_c != sub_c:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to class '{class_name}'")

    resolved_board = board or subject.board or "CBSE"
    resolved_class = class_name or subject.class_name or "10"
    if not resolved_class.lower().startswith("class"):
        resolved_class = f"Class {resolved_class}"

    # Load syllabus units
    available_units = db.query(Unit).filter(Unit.subject_id == subject_id).all()
    unit_map = {u.id: u for u in available_units}

    if selected_units:
        unit_ids_to_use = [uid for uid in selected_units if uid in unit_map]
        if not unit_ids_to_use:
            raise ValueError("Selected units are invalid or do not belong to the selected subject")
    else:
        unit_ids_to_use = [u.id for u in available_units]


    unit_names_list = [unit_map[uid].unit_name for uid in unit_ids_to_use if uid in unit_map]
    unit_names_str = ", ".join(unit_names_list) if unit_names_list else "All Syllabus Units"

    # Validate Bloom distribution percentages
    active_bloom_inputs = {k: v for k, v in bloom_distribution.items() if v > 0}
    sum_bloom_pct = sum(active_bloom_inputs.values())
    if sum_bloom_pct != 100:
        raise ValueError("Bloom distribution percentages must total 100")


    bloom_records = db.query(Bloom).all()
    bloom_by_name = {b.level_name.lower(): b for b in bloom_records}

    targets = []
    for b_name, pct in active_bloom_inputs.items():
        matching_bloom = bloom_by_name.get(b_name.lower())
        if not matching_bloom:
            matching_bloom = Bloom(level_name=b_name)
            db.add(matching_bloom)
            db.flush()
            bloom_by_name[b_name.lower()] = matching_bloom

        norm_pct = round((pct / sum_bloom_pct) * 100)
        raw_marks = (norm_pct / 100.0) * total_marks
        integer_marks = int(raw_marks)
        remainder = raw_marks - integer_marks
        targets.append({
            "name": b_name,
            "matching_bloom": matching_bloom,
            "percentage": norm_pct,
            "allocated_marks": integer_marks,
            "remainder": remainder,
        })

    # Largest Remainder Method for exact total marks
    current_allocated = sum(t["allocated_marks"] for t in targets)
    marks_shortage = total_marks - current_allocated
    if marks_shortage > 0:
        targets_by_remainder = sorted(targets, key=lambda x: x["remainder"], reverse=True)
        for i in range(marks_shortage):
            targets_by_remainder[i % len(targets_by_remainder)]["allocated_marks"] += 1

    selected_questions: List[Dict[str, Any]] = []
    used_question_hashes: Set[str] = set()
    used_question_ids: Set[int] = set()
    shortages: List[Dict[str, Any]] = []

    # =========================================================================
    # STEP 1: QUERY APPROVED QUESTION BANK (unless source_mode == 'ai')
    # =========================================================================
    if source_mode != "ai":
        eligible_questions = (
            db.query(Question)
            .filter(Question.subject_id == subject_id)
            .filter(Question.unit_id.in_(unit_ids_to_use))
            .filter(Question.status == "approved")
            .filter(Question.active == True)
            .all()
        )

        questions_by_bloom: Dict[int, List[Question]] = {}
        for q in eligible_questions:
            questions_by_bloom.setdefault(q.bloom_level_id, []).append(q)

        for target in targets:
            req_marks = target["allocated_marks"]
            bloom_obj = target["matching_bloom"]

            if req_marks <= 0:
                continue

            available_for_bloom = [
                q for q in questions_by_bloom.get(bloom_obj.id, [])
                if q.id not in used_question_ids
            ]

            subset = _find_exact_question_subset(
                questions=available_for_bloom,
                required_marks=req_marks,
                preferred_difficulty=difficulty,
            )

            if subset is not None:
                for q in subset:
                    used_question_ids.add(q.id)
                    used_question_hashes.add(compute_question_hash(q.question_text))
                    selected_questions.append({
                        "question_id": q.id,
                        "question": q.question_text,
                        "marks": q.marks,
                        "bloom": bloom_obj.level_name,
                        "difficulty": q.difficulty,
                        "question_type": q.question_type or "Short Answer",
                        "unit_id": q.unit_id,
                        "unit_name": unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name,
                        "answer": q.answer,
                        "explanation": q.explanation,
                        "source": q.source or "Question Bank",
                    })
            else:
                # Calculate what subset or partial marks we can take
                partial_sum = 0
                partial_qs = []
                for q in sorted(available_for_bloom, key=lambda x: -x.marks):
                    if partial_sum + q.marks <= req_marks:
                        partial_sum += q.marks
                        partial_qs.append(q)

                for q in partial_qs:
                    used_question_ids.add(q.id)
                    used_question_hashes.add(compute_question_hash(q.question_text))
                    selected_questions.append({
                        "question_id": q.id,
                        "question": q.question_text,
                        "marks": q.marks,
                        "bloom": bloom_obj.level_name,
                        "difficulty": q.difficulty,
                        "question_type": q.question_type or "Short Answer",
                        "unit_id": q.unit_id,
                        "unit_name": unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name,
                        "answer": q.answer,
                        "explanation": q.explanation,
                        "source": q.source or "Question Bank",
                    })

                missing_marks = req_marks - partial_sum
                shortages.append({
                    "target": target,
                    "bloom_obj": bloom_obj,
                    "missing_marks": missing_marks,
                })

        # If legacy call without AI enabled and shortages exist
        if shortages and use_ai is not True and source_mode == "bank":
            raise ValueError(f"Insufficient approved questions in question bank for {subject.subject_name}")

    # =========================================================================
    # STEP 2: AI SYNTHESIS FOR SHORTAGES (Hybrid or Full AI mode)
    # =========================================================================
    if source_mode == "ai":
        shortages = [{
            "target": t,
            "bloom_obj": t["matching_bloom"],
            "missing_marks": t["allocated_marks"],
        } for t in targets if t["allocated_marks"] > 0]

    if shortages:
        if use_ai is False:
            raise ValueError(f"Insufficient approved questions in question bank for {subject.subject_name}")

        ai_generator = get_ai_generator()
        unit_cycle = 0

        # If number_of_questions is given, allocate exact question counts per target bloom
        shortage_bloom_names = {s["bloom_obj"].level_name for s in shortages}
        shortage_targets = [t for t in targets if t["name"] in shortage_bloom_names]
        
        q_alloc_map = {}
        if number_of_questions:
            remaining_q_count = number_of_questions - len(selected_questions)
            if remaining_q_count <= 0:
                remaining_q_count = len(shortage_targets)
            
            # Distribute remaining_q_count among shortage targets
            total_short_marks = sum(s["missing_marks"] for s in shortages)
            q_items = []
            for s in shortages:
                pct = (s["missing_marks"] / max(1, total_short_marks))
                raw_q = pct * remaining_q_count
                int_q = int(raw_q)
                rem_q = raw_q - int_q
                q_items.append({"bloom_name": s["bloom_obj"].level_name, "int_q": max(1, int_q), "rem_q": rem_q})
            
            curr_q = sum(qi["int_q"] for qi in q_items)
            diff_q = remaining_q_count - curr_q
            if diff_q > 0:
                q_items.sort(key=lambda x: x["rem_q"], reverse=True)
                for i in range(diff_q):
                    q_items[i % len(q_items)]["int_q"] += 1
            elif diff_q < 0:
                q_items.sort(key=lambda x: x["rem_q"])
                for i in range(abs(diff_q)):
                    if q_items[i % len(q_items)]["int_q"] > 1:
                        q_items[i % len(q_items)]["int_q"] -= 1

            q_alloc_map = {qi["bloom_name"]: qi["int_q"] for qi in q_items}

        for s in shortages:
            bloom_obj = s["bloom_obj"]
            rem_marks = s["missing_marks"]
            target_bloom_q = q_alloc_map.get(bloom_obj.level_name, max(1, round(rem_marks / 5)))

            if target_bloom_q <= 1:
                mark_splits = [rem_marks]
            else:
                base_m = rem_marks // target_bloom_q
                rem_m = rem_marks % target_bloom_q
                mark_splits = [base_m + (1 if i < rem_m else 0) for i in range(target_bloom_q)]
                mark_splits = [m for m in mark_splits if m > 0]

            for q_mark in mark_splits:
                if q_mark >= 5:
                    q_type = "Long Answer" if "math" not in subject.subject_name.lower() else "Numerical"
                elif q_mark >= 3:
                    q_type = "Short Answer" if "math" not in subject.subject_name.lower() else "Numerical"
                elif q_mark == 2:
                    q_type = "Very Short Answer"
                else:
                    q_type = "MCQ"

                assigned_unit_id = unit_ids_to_use[unit_cycle % len(unit_ids_to_use)]
                unit_cycle += 1
                assigned_unit = unit_map[assigned_unit_id]

                prompt = AIQuestionPrompt(
                    board=resolved_board,
                    class_name=resolved_class,
                    subject_name=subject.subject_name,
                    unit_name=assigned_unit.unit_name,
                    topic_name=None,
                    marks=q_mark,
                    difficulty=difficulty or "medium",
                    bloom_level=bloom_obj.level_name,
                    question_type=q_type,
                )

                gen_res = ai_generator.generate_question(prompt)
                if not gen_res:
                    from app.services.ai.generator_factory import OfflineFallbackProvider
                    gen_res = OfflineFallbackProvider().generate_question(prompt)

                q_hash = compute_question_hash(gen_res.question_text)
                if q_hash in used_question_hashes:
                    gen_res.question_text += f" (Variation {random.randint(10, 99)})"

                used_question_hashes.add(compute_question_hash(gen_res.question_text))

                # Persist new AI question into Question Bank for future reuse!
                new_q = Question(
                    subject_id=subject.id,
                    unit_id=assigned_unit.id,
                    bloom_level_id=bloom_obj.id,
                    board_id=subject.board_id or board_id,
                    class_id=subject.class_id or class_id,
                    question_text=gen_res.question_text,
                    question_type=gen_res.question_type or q_type,
                    marks=q_mark,
                    difficulty=gen_res.difficulty or difficulty or "medium",
                    answer=gen_res.answer,
                    explanation=gen_res.explanation,
                    numerical_data=gen_res.numerical_data,
                    application_context=gen_res.application_context,
                    source="AI Synthesized",
                    source_type="ai",
                    is_ai_generated=True,
                    approved=True,
                    status="approved",
                    active=True,
                )
                db.add(new_q)
                db.flush()

                selected_questions.append({
                    "question_id": new_q.id,
                    "question": new_q.question_text,
                    "marks": new_q.marks,
                    "bloom": bloom_obj.level_name,
                    "difficulty": new_q.difficulty,
                    "question_type": new_q.question_type,
                    "unit_id": assigned_unit.id,
                    "unit_name": assigned_unit.unit_name,
                    "answer": new_q.answer,
                    "explanation": new_q.explanation,
                    "source": "AI Synthesized",
                })



        db.commit()

    # Sort questions by Section & Marks
    def section_rank(q):
        m = q["marks"]
        if m <= 1:
            return (1, m)
        elif m <= 2:
            return (2, m)
        elif m <= 4:
            return (3, m)
        else:
            return (4, m)

    selected_questions.sort(key=section_rank)

    # Compute Blueprint Summary Table
    blueprint_summary = []
    for target in targets:
        b_name = target["matching_bloom"].level_name
        req_m = target["allocated_marks"]
        gen_m = sum(q["marks"] for q in selected_questions if q["bloom"] == b_name)
        gen_c = len([q for q in selected_questions if q["bloom"] == b_name])
        blueprint_summary.append({
            "bloom": b_name,
            "required_percentage": target["percentage"],
            "required_marks": req_m,
            "generated_marks": gen_m,
            "generated_questions": gen_c,
        })

    # Create persistent GeneratedPaper record
    paper_uuid = f"QP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    paper_title = f"{resolved_board} {resolved_class} - {subject.subject_name} Examination"

    db_paper = GeneratedPaper(
        paper_id=paper_uuid,
        user_id=user_id,
        board_id=subject.board_id or board_id,
        class_id=subject.class_id or class_id,
        subject_id=subject.id,
        title=paper_title,
        board_name=resolved_board,
        class_name=resolved_class,
        subject_name=subject.subject_name,
        unit_names=unit_names_str,
        total_marks=total_marks,
        total_questions=len(selected_questions),
        difficulty=difficulty.capitalize() if difficulty else "Medium",
        source=source_mode.capitalize(),
        questions_data=json.dumps(selected_questions),
        blueprint_summary=json.dumps(blueprint_summary),
        status="saved",
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)

    return {
        "paper_id": paper_uuid,
        "id": db_paper.id,
        "title": paper_title,
        "total_marks": total_marks,
        "total_questions": len(selected_questions),
        "questions": selected_questions,
        "subject_name": subject.subject_name,
        "board": resolved_board,
        "class_name": resolved_class,
        "unit_names": unit_names_str,
        "blueprint_summary": blueprint_summary,
        "source": source_mode.capitalize(),
    }
