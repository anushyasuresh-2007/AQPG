"""
apply_targeted_tnsb_sync.py
Targeted, surgical, idempotent synchronization script for:
- TNSB Class 12 Computer Science
- TNSB Class 10 Social Science

SAFETY CHARACTERISTICS:
1. Genuinely read-only --dry-run: No ORM objects added, no flush(), zero INSERT/UPDATE/DELETE.
2. Complete catalog matching (board, academic_year, class, subject_name).
3. Conflict & Inconsistency detection: Aborts on conflicting legacy records, multiple matches, unrecognized classes, or duplicate units/topics.
4. Resilient audit logging: Distinguishes staged IDs from confirmed committed IDs.
   Handles audit file writing failure after commit with explicit recovery metadata.
5. Multi-table foreign key inspection for rollback: Checks questions, question_options, generated_papers,
   and verifies exact parent-child hierarchy across subjects, units, and topics.
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Set

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.board import Board
from app.models.generated_paper import GeneratedPaper
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit
from app.services.curriculum.base import SubjectData
from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter


class SyncSafetyError(Exception):
    """Raised when any safety pre-condition, ambiguity, conflict, or constraint check fails."""
    pass


def validate_and_get_target_subjects(importer: TamilNaduBoardImporter, academic_year_code: str) -> List[SubjectData]:
    """Fetch curriculum and extract strictly the two target subjects, validating internal consistency."""
    cat = importer.fetch_curriculum(academic_year=academic_year_code)
    targets = [
        s for s in cat.subjects
        if (s.subject_name == "Computer Science" and s.class_number == 12) or
           (s.subject_name == "Social Science" and s.class_number == 10)
    ]
    if len(targets) != 2:
        raise SyncSafetyError(
            f"Expected exactly 2 target subjects from importer, found {len(targets)}: "
            f"{[f'{s.subject_name} (Class {s.class_number})' for s in targets]}"
        )

    # Validate no duplicate units or topics in target definition
    for s_data in targets:
        seen_units: Set[str] = set()
        seen_unit_numbers: Set[int] = set()
        for u in s_data.units:
            norm_u = u.unit_name.strip().lower()
            if norm_u in seen_units:
                raise SyncSafetyError(f"Duplicate unit '{u.unit_name}' in importer data for {s_data.subject_name}.")
            seen_units.add(norm_u)
            if u.unit_number:
                if u.unit_number in seen_unit_numbers:
                    raise SyncSafetyError(f"Duplicate unit_number {u.unit_number} in {s_data.subject_name}.")
                seen_unit_numbers.add(u.unit_number)

            seen_topics: Set[str] = set()
            for t in u.topics:
                norm_t = t.topic_name.strip().lower()
                if norm_t in seen_topics:
                    raise SyncSafetyError(f"Duplicate topic '{t.topic_name}' under unit '{u.unit_name}' for {s_data.subject_name}.")
                seen_topics.add(norm_t)

    return targets


def execute_targeted_sync(
    db: Session,
    dry_run: bool = True,
    audit_log_dir: Optional[str] = None,
) -> Dict[str, any]:
    """
    Execute targeted synchronization with full transactional safety.
    If dry_run is True:
      - 100% read-only: does NOT add ORM objects, does NOT call flush(), issues ZERO writes.
      - Calculates proposed changes purely from queried catalog state and importer data.
    If dry_run is False:
      - Runs within a strict database transaction.
      - Records staged IDs, commits the transaction, and writes an audit log.
      - If commit fails, transaction is rolled back and no success audit is written.
      - If writing audit file fails after commit, returns recovery metadata with committed IDs.
    """
    print("=" * 80)
    print(f"TARGETED TNSB CURRICULUM SYNC — MODE: {'DRY RUN (READ ONLY)' if dry_run else 'APPLY (TRANSACTIONAL WRITE)'}")
    print("=" * 80)

    # 1. Dynamic Prerequisite Resolution
    tnsb_boards = db.query(Board).filter(Board.code == "TNSB").all()
    if len(tnsb_boards) == 0:
        raise SyncSafetyError("Prerequisite missing: Board 'TNSB' not found in database.")
    if len(tnsb_boards) > 1:
        raise SyncSafetyError(f"Ambiguity detected: Found {len(tnsb_boards)} boards with code 'TNSB'.")
    tnsb_board = tnsb_boards[0]

    current_years = (
        db.query(AcademicYear)
        .filter(AcademicYear.board_id == tnsb_board.id, AcademicYear.is_current == True)
        .all()
    )
    if len(current_years) == 0:
        raise SyncSafetyError(f"Prerequisite missing: No current AcademicYear found for board '{tnsb_board.code}'.")
    if len(current_years) > 1:
        raise SyncSafetyError(f"Ambiguity detected: Found {len(current_years)} current AcademicYears for '{tnsb_board.code}'.")
    acad_year = current_years[0]

    classes = db.query(AcademicClass).filter(AcademicClass.board_id == tnsb_board.id).all()
    class_map: Dict[int, AcademicClass] = {}
    recognized_classes: Set[str] = set()
    for c in classes:
        if c.class_number:
            if c.class_number in class_map:
                raise SyncSafetyError(f"Ambiguity detected: Multiple AcademicClass records for class_number {c.class_number}.")
            class_map[c.class_number] = c
            recognized_classes.add(str(c.class_number))
        if c.class_code:
            recognized_classes.add(c.class_code)

    if 10 not in class_map or 12 not in class_map:
        raise SyncSafetyError(f"Prerequisite missing: AcademicClass for 10 or 12 missing for board '{tnsb_board.code}'.")

    # 2. Extract and validate importer targets
    importer = TamilNaduBoardImporter()
    targets = validate_and_get_target_subjects(importer, acad_year.year_code)

    # 3. Snapshot pre-sync counts
    pre_sub_count = db.query(Subject).count()
    pre_unit_count = db.query(Unit).count()
    pre_topic_count = db.query(Topic).count()

    print(f"Pre-sync catalog state: {pre_sub_count} subjects, {pre_unit_count} units, {pre_topic_count} topics.")

    # 4. Read-only Analysis (Both modes calculate this without mutating state)
    proposed_subject_inserts: List[Tuple[str, str, int]] = []
    skipped_subjects: List[Tuple[int, str, str]] = []
    proposed_unit_inserts: List[Tuple[str, str, int]] = []
    proposed_topic_inserts: List[Tuple[str, str]] = []

    target_subject_plans: List[Dict[str, any]] = []

    for s_data in targets:
        c_obj = class_map[s_data.class_number]

        # Scope matching
        same_name_records = db.query(Subject).filter(
            Subject.board == tnsb_board.code,
            Subject.subject_name == s_data.subject_name,
        ).all()

        matched_subject: Optional[Subject] = None
        target_matches: List[Subject] = []

        for rec in same_name_records:
            # Check for unrecognized class
            if not rec.class_name or rec.class_name not in recognized_classes:
                raise SyncSafetyError(
                    f"Ambiguous legacy match: Record ID {rec.id} for '{rec.subject_name}' has unrecognized class_name '{rec.class_name}'. Aborting."
                )
            # Check for conflicting board_id
            if rec.board_id is not None and rec.board_id != tnsb_board.id:
                raise SyncSafetyError(
                    f"Ambiguous legacy match: Record ID {rec.id} for '{rec.subject_name}' has board_id {rec.board_id} conflicting with {tnsb_board.id}. Aborting."
                )
            # Check for conflicting academic_year_id
            if rec.academic_year_id is not None and rec.academic_year_id != acad_year.id:
                raise SyncSafetyError(
                    f"Ambiguous legacy match: Record ID {rec.id} for '{rec.subject_name}' has academic_year_id {rec.academic_year_id} conflicting with {acad_year.id}. Aborting."
                )
            # Check if record belongs to target class
            is_target_class = (rec.class_name in [str(s_data.class_number), c_obj.class_code]) or (rec.class_id == c_obj.id)
            if is_target_class:
                if rec.class_id is not None and rec.class_id != c_obj.id:
                    raise SyncSafetyError(
                        f"Ambiguous legacy match: Record ID {rec.id} for '{rec.subject_name}' has class_id {rec.class_id} conflicting with target class {c_obj.id}. Aborting."
                    )
                target_matches.append(rec)

        if len(target_matches) > 1:
            raise SyncSafetyError(
                f"Ambiguous match: Found {len(target_matches)} records matching {s_data.subject_name} for Class {s_data.class_number}. Aborting."
            )

        if target_matches:
            matched_subject = target_matches[0]

        if matched_subject:
            skipped_subjects.append((matched_subject.id, matched_subject.subject_name, matched_subject.class_name))
            existing_unit_map = {u.unit_name.strip().lower(): u for u in matched_subject.units}
            for u_idx, u_data in enumerate(s_data.units, start=1):
                norm_u = u_data.unit_name.strip().lower()
                if norm_u not in existing_unit_map:
                    proposed_unit_inserts.append((s_data.subject_name, u_data.unit_name, u_data.unit_number or u_idx))
                    for t_idx, t_data in enumerate(u_data.topics, start=1):
                        proposed_topic_inserts.append((u_data.unit_name, t_data.topic_name))
                else:
                    existing_u = existing_unit_map[norm_u]
                    existing_topic_names = {t.topic_name.strip().lower() for t in existing_u.topics}
                    for t_idx, t_data in enumerate(u_data.topics, start=1):
                        norm_t = t_data.topic_name.strip().lower()
                        if norm_t not in existing_topic_names:
                            proposed_topic_inserts.append((u_data.unit_name, t_data.topic_name))
        else:
            proposed_subject_inserts.append((s_data.subject_name, str(s_data.class_number), len(s_data.units)))
            for u_idx, u_data in enumerate(s_data.units, start=1):
                proposed_unit_inserts.append((s_data.subject_name, u_data.unit_name, u_data.unit_number or u_idx))
                for t_idx, t_data in enumerate(u_data.topics, start=1):
                    proposed_topic_inserts.append((u_data.unit_name, t_data.topic_name))

        target_subject_plans.append({
            "subject_data": s_data,
            "class_obj": c_obj,
            "matched_subject": matched_subject,
        })

    print("\n--- SUMMARY OF PROPOSED CHANGES ---")
    print(f"Subjects to INSERT: {len(proposed_subject_inserts)}")
    for s_name, c_name, u_count in proposed_subject_inserts:
        print(f"  + Subject: '{s_name}' (Class {c_name}) with {u_count} units")
    print(f"Subjects SKIPPED (Already Exist): {len(skipped_subjects)}")
    for sid, s_name, c_name in skipped_subjects:
        print(f"  = Subject ID {sid}: '{s_name}' (Class {c_name})")

    print(f"Units to INSERT: {len(proposed_unit_inserts)}")
    print(f"Topics to INSERT: {len(proposed_topic_inserts)}")
    print(f"Existing row updates: 0 (No existing rows will be modified)")
    print(f"Existing row deletes: 0 (No rows will be deleted)")

    report = {
        "mode": "dry_run" if dry_run else "apply",
        "pre_counts": {"subjects": pre_sub_count, "units": pre_unit_count, "topics": pre_topic_count},
        "proposed_subject_inserts": len(proposed_subject_inserts),
        "proposed_unit_inserts": len(proposed_unit_inserts),
        "proposed_topic_inserts": len(proposed_topic_inserts),
    }

    if dry_run:
        print("\n[DRY RUN COMPLETE] Zero ORM objects added, zero flush() called, zero writes issued.")
        return report

    # 5. APPLY MODE: Transactional execution
    staged_subject_ids: List[int] = []
    staged_unit_ids: List[int] = []
    staged_topic_ids: List[int] = []

    try:
        for plan in target_subject_plans:
            s_data: SubjectData = plan["subject_data"]
            c_obj: AcademicClass = plan["class_obj"]
            subject_obj: Optional[Subject] = plan["matched_subject"]

            if not subject_obj:
                subject_obj = Subject(
                    subject_name=s_data.subject_name,
                    class_name=str(s_data.class_number),
                    board=tnsb_board.code,
                    board_id=tnsb_board.id,
                    academic_year_id=acad_year.id,
                    class_id=c_obj.id,
                    subject_code=s_data.subject_code,
                    subject_type="core",
                    source_url=s_data.source_url,
                    active=True,
                    last_synced_at=datetime.utcnow(),
                )
                db.add(subject_obj)
                db.flush()
                staged_subject_ids.append(subject_obj.id)

            existing_units = {u.unit_name.strip().lower(): u for u in subject_obj.units}
            for u_idx, u_data in enumerate(s_data.units, start=1):
                norm_u = u_data.unit_name.strip().lower()
                if norm_u not in existing_units:
                    unit_obj = Unit(
                        subject_id=subject_obj.id,
                        unit_name=u_data.unit_name,
                        unit_number=u_data.unit_number or u_idx,
                        source_url=u_data.source_url or s_data.source_url,
                        active=True,
                    )
                    db.add(unit_obj)
                    db.flush()
                    staged_unit_ids.append(unit_obj.id)
                    existing_units[norm_u] = unit_obj
                else:
                    unit_obj = existing_units[norm_u]

                if u_data.topics:
                    existing_topics = {t.topic_name.strip().lower(): t for t in unit_obj.topics}
                    for t_idx, t_data in enumerate(u_data.topics, start=1):
                        norm_t = t_data.topic_name.strip().lower()
                        if norm_t not in existing_topics:
                            topic_obj = Topic(
                                unit_id=unit_obj.id,
                                topic_name=t_data.topic_name,
                                topic_number=t_data.topic_number or t_idx,
                                active=True,
                                created_at=datetime.utcnow(),
                            )
                            db.add(topic_obj)
                            db.flush()
                            staged_topic_ids.append(topic_obj.id)
                            existing_topics[norm_t] = topic_obj

        if len(staged_subject_ids) != 2:
            raise SyncSafetyError(f"Apply aborted: Expected exactly 2 staged subjects, got {len(staged_subject_ids)}.")
        if len(staged_unit_ids) != 10:
            raise SyncSafetyError(f"Apply aborted: Expected exactly 10 staged units, got {len(staged_unit_ids)}.")
        if len(staged_topic_ids) != 23:
            raise SyncSafetyError(f"Apply aborted: Expected exactly 23 staged topics, got {len(staged_topic_ids)}.")

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"\n[APPLY FAILED] Transaction rolled back due to error: {e}")
        raise SyncSafetyError(f"Database transaction failed and was rolled back: {e}") from e

    committed_subject_ids = staged_subject_ids
    committed_unit_ids = staged_unit_ids
    committed_topic_ids = staged_topic_ids

    report["committed_subject_ids"] = committed_subject_ids
    report["committed_unit_ids"] = committed_unit_ids
    report["committed_topic_ids"] = committed_topic_ids
    report["db_committed"] = True

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    audit_filename = f"targeted_tnsb_sync_audit_{timestamp}.json"
    audit_filepath = os.path.join(audit_log_dir or ".", audit_filename)

    audit_payload = {
        "status": "COMMITTED",
        "timestamp_utc": datetime.utcnow().isoformat() + "Z",
        "board": "TNSB",
        "academic_year": acad_year.year_code,
        "committed_subject_ids": committed_subject_ids,
        "committed_unit_ids": committed_unit_ids,
        "committed_topic_ids": committed_topic_ids,
        "row_counts": {
            "subjects_committed": len(committed_subject_ids),
            "units_committed": len(committed_unit_ids),
            "topics_committed": len(committed_topic_ids),
        },
    }

    try:
        with open(audit_filepath, "w", encoding="utf-8") as f:
            json.dump(audit_payload, f, indent=2)
        print(f"\n[APPLY SUCCESSFUL] Transaction committed and audit log saved to: {audit_filepath}")
        report["audit_file"] = audit_filepath
    except (IOError, OSError) as audit_err:
        print("\n" + "!" * 80)
        print("CRITICAL ALERT: Database transaction was successfully COMMITTED, but writing the audit log file failed!")
        print(f"File write error: {audit_err}")
        print("EXACT COMMITTED PRIMARY KEYS RECOVERY DATA:")
        print(json.dumps(audit_payload, indent=2))
        print("RECOVERY ACTION: Save the above JSON payload manually as your audit file for future reference.")
        print("!" * 80)
        report["audit_file"] = None
        report["audit_write_error"] = str(audit_err)

    return report


def inspect_rollback_safety(db: Session, audit_filepath: str) -> Dict[str, any]:
    """
    Validate audit structure, relationships, and check all dependent tables:
    - questions (subject_id, unit_id, topic_id)
    - question_options (via question_id)
    - generated_papers (subject_id)
    - internal hierarchy integrity across subjects, units, and topics.
    Does NOT execute deletion.
    """
    if not os.path.exists(audit_filepath):
        raise SyncSafetyError(f"Audit file not found: {audit_filepath}")

    try:
        with open(audit_filepath, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
    except json.JSONDecodeError as jde:
        raise SyncSafetyError(f"Audit file is malformed or corrupted JSON: {jde}")

    sub_ids = audit_data.get("committed_subject_ids", audit_data.get("created_subject_ids", []))
    unit_ids = audit_data.get("committed_unit_ids", audit_data.get("created_unit_ids", []))
    topic_ids = audit_data.get("committed_topic_ids", audit_data.get("created_topic_ids", []))
    board_code = audit_data.get("board")

    if board_code != "TNSB":
        raise SyncSafetyError(f"Audit record board mismatch: Expected 'TNSB', found '{board_code}'.")
    if not isinstance(sub_ids, list) or len(sub_ids) != 2 or len(set(sub_ids)) != 2:
        raise SyncSafetyError(f"Invalid audit data: Expected exactly 2 unique committed subject IDs, found {len(sub_ids)}.")
    if not isinstance(unit_ids, list) or len(unit_ids) != 10 or len(set(unit_ids)) != 10:
        raise SyncSafetyError(f"Invalid audit data: Expected exactly 10 unique committed unit IDs, found {len(unit_ids)}.")
    if not isinstance(topic_ids, list) or len(topic_ids) != 23 or len(set(topic_ids)) != 23:
        raise SyncSafetyError(f"Invalid audit data: Expected exactly 23 unique committed topic IDs, found {len(topic_ids)}.")

    # Dynamically resolve prerequisites
    tnsb_board = db.query(Board).filter(Board.code == "TNSB").first()
    if not tnsb_board:
        raise SyncSafetyError("Database mismatch: Board 'TNSB' not found.")
    acad_year = db.query(AcademicYear).filter(AcademicYear.board_id == tnsb_board.id, AcademicYear.is_current == True).first()
    if not acad_year:
        raise SyncSafetyError("Database mismatch: Current AcademicYear for 'TNSB' not found.")

    classes = db.query(AcademicClass).filter(AcademicClass.board_id == tnsb_board.id).all()
    c10 = next((c for c in classes if c.class_number == 10), None)
    c12 = next((c for c in classes if c.class_number == 12), None)
    if not c10 or not c12:
        raise SyncSafetyError("Database mismatch: Classes 10 or 12 missing for TNSB.")

    # Validate exact target subject identity
    found_cs = False
    found_soc = False
    for sid in sub_ids:
        s = db.query(Subject).filter(Subject.id == sid).first()
        if not s:
            raise SyncSafetyError(f"Database mismatch: Subject ID {sid} not found in database.")
        if s.board != "TNSB" or s.board_id != tnsb_board.id:
            raise SyncSafetyError(f"Database mismatch: Subject ID {sid} board association is not TNSB.")
        if s.academic_year_id != acad_year.id:
            raise SyncSafetyError(f"Database mismatch: Subject ID {sid} academic_year_id {s.academic_year_id} does not match {acad_year.id}.")

        if s.subject_name == "Computer Science" and s.subject_code in ("TN-12-CS", "019", "519") and s.class_id == c12.id:
            found_cs = True
        elif s.subject_name == "Social Science" and s.subject_code in ("TN-10-SOC", "005") and s.class_id == c10.id:
            found_soc = True
        else:
            raise SyncSafetyError(
                f"Unexpected subject record ID {sid}: '{s.subject_name}' ({s.subject_code}, class_id={s.class_id}). "
                f"Does not match exact target specifications."
            )

    if not found_cs or not found_soc:
        raise SyncSafetyError("Audit subject IDs do not contain both target subjects (CS Class 12 and Social Science Class 10).")

    # Validate unit relationships & ensure no other units exist for these subjects
    for uid in unit_ids:
        u = db.query(Unit).filter(Unit.id == uid).first()
        if not u:
            raise SyncSafetyError(f"Database mismatch: Unit ID {uid} not found in database.")
        if u.subject_id not in sub_ids:
            raise SyncSafetyError(f"Integrity violation: Unit ID {uid} belongs to subject {u.subject_id}, not in recorded IDs {sub_ids}.")

    extra_units = db.query(Unit).filter(Unit.subject_id.in_(sub_ids), ~Unit.id.in_(unit_ids)).count()
    if extra_units > 0:
        raise SyncSafetyError(f"Integrity violation: Found {extra_units} unrecorded units belonging to subjects {sub_ids}.")

    # Validate topic relationships & ensure no other topics exist for these units
    for tid in topic_ids:
        t = db.query(Topic).filter(Topic.id == tid).first()
        if not t:
            raise SyncSafetyError(f"Database mismatch: Topic ID {tid} not found in database.")
        if t.unit_id not in unit_ids:
            raise SyncSafetyError(f"Integrity violation: Topic ID {tid} belongs to unit {t.unit_id}, not in recorded IDs {unit_ids}.")

    extra_topics = db.query(Topic).filter(Topic.unit_id.in_(unit_ids), ~Topic.id.in_(topic_ids)).count()
    if extra_topics > 0:
        raise SyncSafetyError(f"Integrity violation: Found {extra_topics} unrecorded topics belonging to units {unit_ids}.")

    # Inspect all dependent tables
    q_sub = db.query(Question).filter(Question.subject_id.in_(sub_ids)).count()
    q_unit = db.query(Question).filter(Question.unit_id.in_(unit_ids)).count()
    q_topic = db.query(Question).filter(Question.topic_id.in_(topic_ids)).count()

    # QuestionOption check via question relationships
    q_opts = (
        db.query(QuestionOption)
        .join(Question)
        .filter(
            Question.subject_id.in_(sub_ids) |
            Question.unit_id.in_(unit_ids) |
            Question.topic_id.in_(topic_ids)
        )
        .count()
    )

    gp_sub = db.query(GeneratedPaper).filter(GeneratedPaper.subject_id.in_(sub_ids)).count()

    total_deps = q_sub + q_unit + q_topic + q_opts + gp_sub
    if total_deps > 0:
        raise SyncSafetyError(
            f"Rollback aborted: Found dependent records referencing recorded IDs "
            f"(Questions: {q_sub + q_unit + q_topic}, Options: {q_opts}, GeneratedPapers: {gp_sub})."
        )

    return {
        "status": "SAFE_TO_ROLLBACK",
        "sub_ids": sub_ids,
        "unit_ids": unit_ids,
        "topic_ids": topic_ids,
        "dependent_questions": 0,
        "dependent_options": 0,
        "dependent_generated_papers": 0,
    }


def rollback_targeted_sync(db: Session, audit_filepath: str, confirm: bool = False):
    """
    Safely inspect and optionally roll back recorded IDs if confirm is explicitly True.
    """
    print("=" * 80)
    print(f"TARGETED SYNC ROLLBACK INSPECTION — AUDIT FILE: {audit_filepath}")
    print("=" * 80)

    inspection = inspect_rollback_safety(db, audit_filepath)
    sub_ids = inspection["sub_ids"]
    unit_ids = inspection["unit_ids"]
    topic_ids = inspection["topic_ids"]

    print("[DEPENDENCY & RELATIONSHIP CHECK PASSED]")
    print(f"Verified: 0 dependent questions, 0 question options, 0 generated papers.")
    print(f"Hierarchy validated: 23 topics -> 10 units -> 2 subjects (TNSB).")

    if not confirm:
        print("[INSPECTION COMPLETE] Zero rows deleted. Pass --confirm-rollback to execute.")
        return

    try:
        db.query(Topic).filter(Topic.id.in_(topic_ids)).delete(synchronize_session=False)
        db.query(Unit).filter(Unit.id.in_(unit_ids)).delete(synchronize_session=False)
        db.query(Subject).filter(Subject.id.in_(sub_ids)).delete(synchronize_session=False)
        db.commit()
        print("[ROLLBACK COMPLETE] Deleted recorded IDs cleanly. Zero orphaned rows remain.")
    except Exception as e:
        db.rollback()
        raise SyncSafetyError(f"Rollback transaction failed and was rolled back: {e}") from e


def main():
    parser = argparse.ArgumentParser(description="Targeted TNSB Curriculum Sync for AQPG")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true", help="Run read-only dry-run simulation (never commits)")
    group.add_argument("--apply", action="store_true", help="Execute synchronization write transaction")
    group.add_argument("--rollback", type=str, help="Path to audit JSON file to execute exact-ID rollback")

    parser.add_argument("--confirm-write", action="store_true", help="Required confirmation flag for --apply")
    parser.add_argument("--confirm-rollback", action="store_true", help="Required confirmation flag for --rollback")
    parser.add_argument("--db-url", type=str, default=None, help="Explicit database URL override (for isolated testing)")
    parser.add_argument("--audit-dir", type=str, default=".", help="Directory to store audit log file")

    args = parser.parse_args()

    if args.db_url:
        engine = create_engine(args.db_url)
        SessionCls = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionCls()
    else:
        from app.database.database import SessionLocal
        db = SessionLocal()

    try:
        if args.dry_run:
            execute_targeted_sync(db, dry_run=True)
        elif args.apply:
            if not args.confirm_write:
                print("ERROR: --apply requires --confirm-write to prevent accidental execution.")
                sys.exit(1)
            execute_targeted_sync(db, dry_run=False, audit_log_dir=args.audit_dir)
        elif args.rollback:
            rollback_targeted_sync(db, audit_filepath=args.rollback, confirm=args.confirm_rollback)
    finally:
        db.close()


if __name__ == "__main__":
    main()
