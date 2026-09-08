"""Curriculum synchronization coordinator and CLI runner for official board syllabi."""

import argparse
import sys
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.database.database import Base, SessionLocal, engine
from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.board import Board
from app.models.curriculum_sync_log import CurriculumSyncLog
from app.models.stream import Stream
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit
from app.services.curriculum.base import BaseCurriculumImporter, CurriculumSyncResult
from app.services.curriculum.cbse_importer import CBSEImporter
from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter

AVAILABLE_IMPORTERS: Dict[str, BaseCurriculumImporter] = {
    "cbse": CBSEImporter(),
    "tnsb": TamilNaduBoardImporter(),
    "tn": TamilNaduBoardImporter(),
}


def sync_board_curriculum(
    db: Session,
    board_key: str = "cbse",
    academic_year_code: str = "2026-27",
    target_classes: Optional[List[int]] = None,
) -> CurriculumSyncResult:
    """
    Synchronize the official board curriculum into the database catalog idempotently.
    Updates existing records and creates new subjects, units, and topics without duplicates.
    """
    importer = AVAILABLE_IMPORTERS.get(board_key.strip().lower())
    if not importer:
        raise ValueError(f"No importer registered for board key: '{board_key}'. Available: {list(AVAILABLE_IMPORTERS.keys())}")

    # Fetch official parsed curriculum data
    curriculum_data = importer.fetch_curriculum(academic_year=academic_year_code, target_classes=target_classes)

    # 1. Ensure Board record exists
    board = db.query(Board).filter(Board.code == curriculum_data.board_code).first()
    if not board:
        board = Board(
            code=curriculum_data.board_code,
            name=curriculum_data.board_name,
            state=curriculum_data.state,
            website_url=curriculum_data.source_url,
            description=f"Official curriculum data sourced from {curriculum_data.source_name}",
        )
        db.add(board)
        db.flush()

    # 2. Ensure AcademicYear record exists
    acad_year = (
        db.query(AcademicYear)
        .filter(AcademicYear.board_id == board.id, AcademicYear.year_code == curriculum_data.academic_year)
        .first()
    )
    if not acad_year:
        acad_year = AcademicYear(
            board_id=board.id,
            year_code=curriculum_data.academic_year,
            is_current=True,
        )
        db.add(acad_year)
        db.flush()

    # Cache existing classes, streams, subjects, and units
    existing_classes = {c.class_number: c for c in db.query(AcademicClass).filter(AcademicClass.board_id == board.id).all()}
    
    subjects_created = 0
    subjects_updated = 0
    units_created = 0
    units_updated = 0
    classes_synced_set = set()

    for sub_data in curriculum_data.subjects:
        classes_synced_set.add(sub_data.class_name)

        # 3. Ensure AcademicClass exists
        c_obj = existing_classes.get(sub_data.class_number)
        if not c_obj:
            c_obj = AcademicClass(
                board_id=board.id,
                class_code=sub_data.class_name,
                class_number=sub_data.class_number,
            )
            db.add(c_obj)
            db.flush()
            existing_classes[sub_data.class_number] = c_obj

        # 4. Ensure Stream exists if specified
        stream_id = None
        if sub_data.stream_name:
            stream_obj = (
                db.query(Stream)
                .filter(Stream.class_id == c_obj.id, Stream.stream_name == sub_data.stream_name)
                .first()
            )
            if not stream_obj:
                stream_obj = Stream(class_id=c_obj.id, stream_name=sub_data.stream_name)
                db.add(stream_obj)
                db.flush()
            stream_id = stream_obj.id

        # 5. Ensure Subject exists (match on subject_name + class_id + academic_year_id or board)
        subject_record = (
            db.query(Subject)
            .filter(
                Subject.board_id == board.id,
                Subject.academic_year_id == acad_year.id,
                Subject.class_id == c_obj.id,
                Subject.subject_name == sub_data.subject_name,
            )
            .first()
        )

        if not subject_record:
            # Check legacy matching record without board_id
            legacy = (
                db.query(Subject)
                .filter(
                    Subject.subject_name == sub_data.subject_name,
                    Subject.class_name == str(sub_data.class_number),
                )
                .first()
            )
            if legacy:
                subject_record = legacy
                subject_record.board_id = board.id
                subject_record.academic_year_id = acad_year.id
                subject_record.class_id = c_obj.id
                subject_record.stream_id = stream_id
                subject_record.subject_code = sub_data.subject_code
                subject_record.source_url = sub_data.source_url
                subject_record.last_synced_at = datetime.utcnow()
                subjects_updated += 1
            else:
                subject_record = Subject(
                    subject_name=sub_data.subject_name,
                    class_name=str(sub_data.class_number),
                    board=board.code,
                    board_id=board.id,
                    academic_year_id=acad_year.id,
                    class_id=c_obj.id,
                    stream_id=stream_id,
                    subject_code=sub_data.subject_code,
                    source_url=sub_data.source_url,
                    last_synced_at=datetime.utcnow(),
                )
                db.add(subject_record)
                db.flush()
                subjects_created += 1
        else:
            subject_record.subject_code = sub_data.subject_code
            subject_record.source_url = sub_data.source_url
            subject_record.last_synced_at = datetime.utcnow()
            subjects_updated += 1

        # 6. Ensure Units exist
        existing_units = {u.unit_name.strip().lower(): u for u in subject_record.units}

        for u_data in sub_data.units:
            norm_unit_name = u_data.unit_name.strip().lower()
            unit_record = existing_units.get(norm_unit_name)

            if not unit_record:
                unit_record = Unit(
                    subject_id=subject_record.id,
                    unit_name=u_data.unit_name,
                    unit_number=u_data.unit_number,
                    source_url=u_data.source_url or sub_data.source_url,
                )
                db.add(unit_record)
                db.flush()
                existing_units[norm_unit_name] = unit_record
                units_created += 1
            else:
                unit_record.unit_number = u_data.unit_number
                units_updated += 1

            # 7. Ensure Topics exist if provided
            if u_data.topics:
                existing_topics = {t.topic_name.strip().lower() for t in unit_record.topics}
                for t_data in u_data.topics:
                    if t_data.topic_name.strip().lower() not in existing_topics:
                        topic_record = Topic(
                            unit_id=unit_record.id,
                            topic_name=t_data.topic_name,
                            topic_number=t_data.topic_number,
                            description=t_data.description,
                        )
                        db.add(topic_record)

    # 8. Record Sync Log
    classes_str = ", ".join(sorted(classes_synced_set))
    sync_log = CurriculumSyncLog(
        board_code=board.code,
        academic_year=acad_year.year_code,
        classes_synced=classes_str,
        subjects_count=subjects_created + subjects_updated,
        units_count=units_created + units_updated,
        status="success",
        details=f"Synced {subjects_created} new subjects, {subjects_updated} updated subjects, {units_created} new units.",
        source_url=curriculum_data.source_url,
    )
    db.add(sync_log)
    db.commit()

    return CurriculumSyncResult(
        board_code=board.code,
        academic_year=acad_year.year_code,
        classes_synced=sorted(list(classes_synced_set)),
        subjects_created=subjects_created,
        subjects_updated=subjects_updated,
        units_created=units_created,
        units_updated=units_updated,
        status="success",
        message=f"Successfully synchronized {board.code} {academic_year_code} curriculum ({classes_str}).",
    )


def main():
    """CLI entrypoint for curriculum synchronization."""
    parser = argparse.ArgumentParser(description="Synchronize official board curriculum into AQPG database.")
    parser.add_argument("--board", default="cbse", help="Board code: 'cbse' or 'tnsb'")
    parser.add_argument("--year", default="2026-27", help="Academic session year (default: '2026-27')")
    parser.add_argument("--classes", nargs="*", type=int, help="Optional class numbers (e.g. 10 12)")

    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        print(f"Starting curriculum synchronization for Board='{args.board.upper()}', Year='{args.year}'...")
        res = sync_board_curriculum(db, board_key=args.board, academic_year_code=args.year, target_classes=args.classes)
        print(f"Status: {res.status.upper()}")
        print(f"Result: {res.message}")
        print(f"Subjects: {res.subjects_created} created, {res.subjects_updated} updated.")
        print(f"Units: {res.units_created} created, {res.units_updated} updated.")
        print("Curriculum sync complete!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
