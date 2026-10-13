"""
test_apply_targeted_tnsb_sync.py
Comprehensive unit tests verifying the behavior and safety of
backend/scripts/apply_targeted_tnsb_sync.py on an isolated in-memory SQLite database.
"""

import json
import os
import sys
import tempfile
from unittest.mock import patch
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.database import Base
from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.bloom import Bloom
from app.models.board import Board
from app.models.generated_paper import GeneratedPaper
from app.models.question import Question
from app.models.question_option import QuestionOption
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit
from app.services.curriculum.base import SubjectData, UnitData, TopicData
from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter
from scripts.apply_targeted_tnsb_sync import (
    SyncSafetyError,
    execute_targeted_sync,
    inspect_rollback_safety,
    rollback_targeted_sync,
    validate_and_get_target_subjects,
)


@pytest.fixture
def mock_db_and_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()

    for b_name in ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]:
        db.add(Bloom(level_name=b_name))

    cbse = Board(id=1, code="CBSE", name="Central Board of Secondary Education", state="National")
    tnsb = Board(id=2, code="TNSB", name="Tamil Nadu State Board of School Examination", state="Tamil Nadu")
    db.add_all([cbse, tnsb])
    db.flush()

    ay_cbse = AcademicYear(id=1, board_id=1, year_code="2026-27", is_current=True)
    ay_tnsb = AcademicYear(id=2, board_id=2, year_code="2026-27", is_current=True)
    db.add_all([ay_cbse, ay_tnsb])
    db.flush()

    c10_cbse = AcademicClass(id=1, board_id=1, class_code="Class X", class_number=10)
    c12_cbse = AcademicClass(id=2, board_id=1, class_code="Class XII", class_number=12)
    c10_tnsb = AcademicClass(id=3, board_id=2, class_code="Class X", class_number=10)
    c12_tnsb = AcademicClass(id=4, board_id=2, class_code="Class XII", class_number=12)
    db.add_all([c10_cbse, c12_cbse, c10_tnsb, c12_tnsb])
    db.flush()

    # Populate 16 live baseline subjects
    live_subjects = [
        (1, "Science", "10", "CBSE", 1, 1, 1, "086"),
        (2, "Mathematics Standard", "10", "CBSE", 1, 1, 1, "041"),
        (3, "Social Science", "10", "CBSE", 1, 1, 1, "087"),
        (4, "English Language and Literature", "10", "CBSE", 1, 1, 1, "184"),
        (5, "Information Technology", "10", "CBSE", 1, 1, 1, "402"),
        (6, "Physics", "12", "CBSE", 1, 1, 2, "042"),
        (7, "Chemistry", "12", "CBSE", 1, 1, 2, "043"),
        (8, "Biology", "12", "CBSE", 1, 1, 2, "044"),
        (9, "Mathematics", "12", "CBSE", 1, 1, 2, "041"),
        (10, "Computer Science", "12", "CBSE", 1, 1, 2, "083"),
        (11, "Economics", "12", "CBSE", 1, 1, 2, "030"),
        (12, "Business Studies", "12", "CBSE", 1, 1, 2, "054"),
        (13, "Accountancy", "12", "CBSE", 1, 1, 2, "055"),
        (14, "Mathematics", "10", "TNSB", 2, 2, 3, "TN-10-MAT"),
        (15, "English", "10", "TNSB", 2, 2, 3, "TN-10-ENG"),
        (16, "English", "12", "CBSE", 1, 1, 2, "301"),
    ]
    for sid, sname, cname, bcode, bid, yid, cid, scode in live_subjects:
        db.add(Subject(id=sid, subject_name=sname, class_name=cname, board=bcode, board_id=bid, academic_year_id=yid, class_id=cid, subject_code=scode))
    db.commit()

    yield db, engine
    db.close()


def test_dry_run_is_genuinely_read_only_with_sql_monitoring(mock_db_and_engine):
    """Monitor all SQL statements and assert that dry-run emits zero INSERT, UPDATE, or DELETE."""
    db, engine = mock_db_and_engine
    executed_statements = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        cleaned = statement.strip().upper()
        executed_statements.append(cleaned)

    event.listen(engine, "before_cursor_execute", before_cursor_execute)

    pre_subjects = db.query(Subject).count()
    pre_units = db.query(Unit).count()
    pre_topics = db.query(Topic).count()

    report = execute_targeted_sync(db, dry_run=True)

    event.remove(engine, "before_cursor_execute", before_cursor_execute)

    assert report["mode"] == "dry_run"
    assert report["proposed_subject_inserts"] == 2
    assert report["proposed_unit_inserts"] == 10
    assert report["proposed_topic_inserts"] == 23

    # Assert database counts remain strictly unchanged
    assert db.query(Subject).count() == pre_subjects
    assert db.query(Unit).count() == pre_units
    assert db.query(Topic).count() == pre_topics

    # Assert NO mutating SQL statements were executed at all!
    for stmt in executed_statements:
        assert not stmt.startswith("INSERT"), f"Dry-run executed mutating statement: {stmt}"
        assert not stmt.startswith("UPDATE"), f"Dry-run executed mutating statement: {stmt}"
        assert not stmt.startswith("DELETE"), f"Dry-run executed mutating statement: {stmt}"


def test_apply_mode_inserts_exact_counts_and_preserves_cbse(mock_db_and_engine):
    """Verify that apply mode inserts exactly 2 subjects, 10 units, 23 topics, and leaves CBSE unchanged."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)

        assert report["mode"] == "apply"
        assert report["db_committed"] is True
        assert len(report["committed_subject_ids"]) == 2
        assert len(report["committed_unit_ids"]) == 10
        assert len(report["committed_topic_ids"]) == 23

        # Assert database counts
        assert db.query(Subject).count() == 18
        assert db.query(Unit).count() == 10
        assert db.query(Topic).count() == 23

        # Assert CBSE Mathematics (ID 2) and CBSE CS (ID 10) untouched
        cbse_math = db.query(Subject).filter(Subject.id == 2).first()
        assert cbse_math.board == "CBSE" and cbse_math.subject_name == "Mathematics Standard"

        cbse_cs = db.query(Subject).filter(Subject.id == 10).first()
        assert cbse_cs.board == "CBSE" and cbse_cs.subject_name == "Computer Science"

        # Assert audit log file exists and contains committed status
        audit_file = report["audit_file"]
        assert os.path.exists(audit_file)
        with open(audit_file, "r", encoding="utf-8") as f:
            audit_data = json.load(f)
        assert audit_data["status"] == "COMMITTED"
        assert audit_data["row_counts"]["subjects_committed"] == 2
        assert audit_data["row_counts"]["units_committed"] == 10
        assert audit_data["row_counts"]["topics_committed"] == 23


def test_idempotent_reapplication(mock_db_and_engine):
    """Verify that re-running apply when records exist creates zero additional rows."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        sub_count = db.query(Subject).count()

        # Re-run dry-run
        second_report = execute_targeted_sync(db, dry_run=True)
        assert second_report["proposed_subject_inserts"] == 0
        assert second_report["proposed_unit_inserts"] == 0
        assert second_report["proposed_topic_inserts"] == 0
        assert db.query(Subject).count() == sub_count


def test_commit_failure_rolls_back_and_does_not_emit_audit_log(mock_db_and_engine):
    """Verify that if database commit fails, the transaction rolls back cleanly and no audit log is emitted."""
    db, _ = mock_db_and_engine
    pre_sub_count = db.query(Subject).count()

    with tempfile.TemporaryDirectory() as tmpdir:
        with patch.object(db, "commit", side_effect=RuntimeError("Simulated DB commit error")):
            with pytest.raises(SyncSafetyError, match="Database transaction failed and was rolled back"):
                execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)

        # Assert rollback
        assert db.query(Subject).count() == pre_sub_count
        # Assert no audit files created in tmpdir
        assert len(os.listdir(tmpdir)) == 0


def test_audit_file_failure_handles_committed_transaction_gracefully(mock_db_and_engine):
    """Verify that if audit file writing fails after DB commit, committed metadata is returned."""
    db, _ = mock_db_and_engine
    pre_sub_count = db.query(Subject).count()

    # Pass an invalid directory to trigger write error
    invalid_dir = os.path.join(tempfile.gettempdir(), "non_existent_dir_aqpg_test", "sub")
    report = execute_targeted_sync(db, dry_run=False, audit_log_dir=invalid_dir)

    assert report["db_committed"] is True
    assert len(report["committed_subject_ids"]) == 2
    assert report["audit_file"] is None
    assert "audit_write_error" in report
    # The DB commit did succeed
    assert db.query(Subject).count() == pre_sub_count + 2


def test_inconsistent_legacy_match_aborts(mock_db_and_engine):
    """Verify that an inconsistent legacy record causes immediate abort."""
    db, _ = mock_db_and_engine
    # Add an inconsistent legacy subject with wrong class_id
    bad_legacy = Subject(
        id=99,
        subject_name="Computer Science",
        class_name="12",
        board="TNSB",
        board_id=2,
        academic_year_id=2,
        class_id=999,  # Conflicts with class_id 4
    )
    db.add(bad_legacy)
    db.commit()

    with pytest.raises(SyncSafetyError, match="conflicting with target class"):
        execute_targeted_sync(db, dry_run=True)


def test_unrecognized_class_on_same_name_record_aborts(mock_db_and_engine):
    """Verify that a same-name legacy record with unrecognized class_name aborts."""
    db, _ = mock_db_and_engine
    bad_legacy = Subject(
        id=98,
        subject_name="Computer Science",
        class_name="UNKNOWN_OR_CORRUPT",
        board="TNSB",
    )
    db.add(bad_legacy)
    db.commit()

    with pytest.raises(SyncSafetyError, match="unrecognized class_name"):
        execute_targeted_sync(db, dry_run=True)


def test_duplicate_units_or_topics_in_importer_aborts():
    """Verify that duplicate units or topics in target definition cause an abort."""
    importer = TamilNaduBoardImporter()
    with patch.object(importer, "fetch_curriculum") as mock_fetch:
        from app.services.curriculum.base import BoardCurriculumData
        mock_fetch.return_value = BoardCurriculumData(
            board_code="TNSB",
            board_name="TN Board",
            state="TN",
            source_name="TNSCERT",
            source_url="https://www.tnscert.org",
            academic_year="2026-27",
            subjects=[
                SubjectData(
                    subject_name="Computer Science",
                    class_name="Class XII",
                    class_number=12,
                    subject_code="TN-12-CS",
                    units=[
                        UnitData(unit_number=1, unit_name="Unit 1 - Python Basics"),
                        UnitData(unit_number=2, unit_name="Unit 1 - Python Basics"),  # Duplicate
                    ]
                ),
                SubjectData(
                    subject_name="Social Science",
                    class_name="Class X",
                    class_number=10,
                    subject_code="TN-10-SOC",
                    units=[UnitData(unit_number=1, unit_name="Unit 1 - History")]
                ),
            ]
        )
        with pytest.raises(SyncSafetyError, match="Duplicate unit"):
            validate_and_get_target_subjects(importer, "2026-27")


def test_tampered_or_malformed_audit_json_aborts_rollback(mock_db_and_engine):
    """Verify that malformed or tampered audit JSON files cause rollback to abort."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        bad_json = os.path.join(tmpdir, "bad.json")
        with open(bad_json, "w") as f:
            f.write("{ invalid json")
        with pytest.raises(SyncSafetyError, match="malformed or corrupted"):
            inspect_rollback_safety(db, bad_json)

        wrong_board = os.path.join(tmpdir, "wrong_board.json")
        with open(wrong_board, "w") as f:
            json.dump({"board": "CBSE", "committed_subject_ids": [1, 2]}, f)
        with pytest.raises(SyncSafetyError, match="board mismatch"):
            inspect_rollback_safety(db, wrong_board)


def test_rollback_rejects_inconsistent_subject_identity(mock_db_and_engine):
    """Verify that rollback rejects subjects that do not match exact CS Class 12 / Social Science Class 10 identity."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        audit_file = report["audit_file"]

        # Tamper subject: change subject name
        sub_id = report["committed_subject_ids"][0]
        s = db.query(Subject).filter(Subject.id == sub_id).first()
        s.subject_name = "Wrong Subject Name"
        db.commit()

        with pytest.raises(SyncSafetyError, match="Does not match exact target specifications"):
            inspect_rollback_safety(db, audit_file)


def test_unexpected_dependent_foreign_keys_in_questions_aborts_rollback(mock_db_and_engine):
    """Verify that dependent Question records cause rollback to abort."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        audit_file = report["audit_file"]
        created_sub_id = report["committed_subject_ids"][0]
        created_unit_id = report["committed_unit_ids"][0]

        # Simulate user question referencing newly created subject and unit
        bloom = db.query(Bloom).first()
        db.add(Question(
            subject_id=created_sub_id,
            unit_id=created_unit_id,
            question_text="Sample question",
            marks=2,
            bloom_level_id=bloom.id,
        ))
        db.commit()

        with pytest.raises(SyncSafetyError, match="Rollback aborted: Found dependent records"):
            inspect_rollback_safety(db, audit_file)


def test_unexpected_dependent_foreign_keys_in_question_options_aborts_rollback(mock_db_and_engine):
    """Verify that dependent QuestionOption records cause rollback to abort."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        audit_file = report["audit_file"]
        created_sub_id = report["committed_subject_ids"][0]
        created_unit_id = report["committed_unit_ids"][0]

        bloom = db.query(Bloom).first()
        q = Question(
            subject_id=created_sub_id,
            unit_id=created_unit_id,
            question_text="Sample MCQ question",
            marks=1,
            bloom_level_id=bloom.id,
        )
        db.add(q)
        db.flush()
        db.add(QuestionOption(
            question_id=q.id,
            option_label="A",
            option_text="Option text",
            is_correct=True,
        ))
        db.commit()

        with pytest.raises(SyncSafetyError, match="Rollback aborted: Found dependent records"):
            inspect_rollback_safety(db, audit_file)


def test_unexpected_dependent_foreign_keys_in_generated_papers_aborts_rollback(mock_db_and_engine):
    """Verify that dependent GeneratedPaper records cause rollback to abort."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        audit_file = report["audit_file"]
        created_sub_id = report["committed_subject_ids"][0]

        # Simulate generated paper referencing newly created subject
        db.add(GeneratedPaper(
            paper_id="TEST-QP-01",
            subject_id=created_sub_id,
            title="Sample Paper",
            board_name="TNSB",
            class_name="12",
            subject_name="Computer Science",
            total_marks=50,
            total_questions=10,
            questions_data="[]",
        ))
        db.commit()

        with pytest.raises(SyncSafetyError, match="Rollback aborted: Found dependent records"):
            inspect_rollback_safety(db, audit_file)


def test_rollback_succeeds_when_clean(mock_db_and_engine):
    """Verify that confirmed rollback cleans up exactly the recorded IDs."""
    db, _ = mock_db_and_engine
    with tempfile.TemporaryDirectory() as tmpdir:
        report = execute_targeted_sync(db, dry_run=False, audit_log_dir=tmpdir)
        audit_file = report["audit_file"]

        assert db.query(Subject).count() == 18

        # Execute confirmed rollback
        rollback_targeted_sync(db, audit_filepath=audit_file, confirm=True)

        assert db.query(Subject).count() == 16
        assert db.query(Unit).count() == 0
        assert db.query(Topic).count() == 0
