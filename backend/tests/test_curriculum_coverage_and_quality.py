"""
test_curriculum_coverage_and_quality.py
Regression test suite for comprehensive curriculum coverage and question quality:
1. Subject retrieval normalization across boards (CBSE, TNSB) and class name conventions ("Class X" vs "10", "Class XII" vs "12").
2. Official DGE subject code resolution for Tamil Nadu State Board subjects.
3. Importer completeness for CBSE and TNSB curricula.
4. Question relevance validation gating against generic phrases:
   "structural architecture", "optimization techniques", "broader theoretical systems",
   "hyperparameter optimization", "gradient descent", "turbofan", "propulsion systems".
5. Prevention of cross-domain jargon leaks (e.g., ML / aerospace / SQL into Biology, History, English, Tamil).
"""

import unittest
from pathlib import Path
import sys

backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.db.session import SessionLocal
from app.crud.subject import get_subjects
from app.schemas.subject import SubjectResponse
from app.services.curriculum.cbse_importer import CBSEImporter
from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter, resolve_tnsb_subject_code
from app.services.question_generator import validate_unit_relevance
from app.services.ai.curriculum_pools import match_curriculum_question
from app.services.bloom_service import validate_bloom_level


class TestCurriculumCoverageAndQuality(unittest.TestCase):
    """Regression test suite for curriculum coverage and question generation quality."""

    @classmethod
    def setUpClass(cls):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        repo_root = Path(__file__).resolve().parents[2]
        db_file = repo_root / "aqpg.db"
        if not db_file.exists():
            db_file = repo_root / "backend" / "aqpg.db"

        engine = create_engine(f"sqlite:///{db_file.as_posix()}", connect_args={"check_same_thread": False})
        Session = sessionmaker(bind=engine)
        cls.db = Session()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_subject_retrieval_supports_both_class_naming_conventions(self):
        """Querying subjects by 'Class X' or '10' must return the exact same subjects."""
        # CBSE Class 10
        cbse_x = get_subjects(self.db, board_code="CBSE", class_name="Class X")
        cbse_10 = get_subjects(self.db, board_code="CBSE", class_name="10")
        self.assertGreater(len(cbse_x), 0, "CBSE Class X query must return subjects")
        self.assertEqual({s.id for s in cbse_x}, {s.id for s in cbse_10},
                         "Class X and 10 queries for CBSE must return identical subject IDs")

        # CBSE Class 12
        cbse_xii = get_subjects(self.db, board_code="CBSE", class_name="Class XII")
        cbse_12 = get_subjects(self.db, board_code="CBSE", class_name="12")
        self.assertGreater(len(cbse_xii), 0, "CBSE Class XII query must return subjects")
        self.assertEqual({s.id for s in cbse_xii}, {s.id for s in cbse_12},
                         "Class XII and 12 queries for CBSE must return identical subject IDs")

        # TNSB Class 12
        tnsb_xii = get_subjects(self.db, board_code="TNSB", class_name="Class XII")
        tnsb_12 = get_subjects(self.db, board_code="TNSB", class_name="12")
        self.assertGreater(len(tnsb_xii), 0, "TNSB Class XII query must return subjects")
        self.assertEqual({s.id for s in tnsb_xii}, {s.id for s in tnsb_12},
                         "Class XII and 12 queries for TNSB must return identical subject IDs")

    def test_tnsb_subject_code_resolution(self):
        """TNSB subject codes must resolve legacy codes to official DGE 3-digit series."""
        # Class 12 Physics (005 -> 505)
        self.assertEqual(resolve_tnsb_subject_code("005", class_number=12, subject_name="Physics"), "505")
        # Class 12 Mathematics (041 -> 541)
        self.assertEqual(resolve_tnsb_subject_code("041", class_number=12, subject_name="Mathematics"), "541")
        # Class 12 Chemistry (007 -> 507)
        self.assertEqual(resolve_tnsb_subject_code("007", class_number=12, subject_name="Chemistry"), "507")
        # Class 12 Biology (009 -> 509)
        self.assertEqual(resolve_tnsb_subject_code("009", class_number=12, subject_name="Biology"), "509")
        # Class 12 Computer Science (019 -> 519)
        self.assertEqual(resolve_tnsb_subject_code("019", class_number=12, subject_name="Computer Science"), "519")

    def test_cbse_importer_contains_mandatory_subjects(self):
        """CBSE importer must contain foundational core subjects for Classes 10 and 12."""
        importer = CBSEImporter()
        cbse_data = importer.fetch_curriculum("2026-27")
        cbse_sub_names = {s.subject_name for s in cbse_data.subjects}

        # Class 10 mandatory subjects
        self.assertIn("Mathematics Standard", cbse_sub_names)
        self.assertIn("Science", cbse_sub_names)
        self.assertIn("Social Science", cbse_sub_names)
        self.assertIn("English Language and Literature", cbse_sub_names)
        self.assertIn("Information Technology", cbse_sub_names)
        self.assertIn("Mathematics Basic", cbse_sub_names)
        self.assertIn("Hindi Course A", cbse_sub_names)

        # Class 12 mandatory subjects
        self.assertIn("Mathematics", cbse_sub_names)
        self.assertIn("Physics", cbse_sub_names)
        self.assertIn("Chemistry", cbse_sub_names)
        self.assertIn("Biology", cbse_sub_names)
        self.assertIn("Computer Science", cbse_sub_names)
        self.assertIn("Economics", cbse_sub_names)
        self.assertIn("Business Studies", cbse_sub_names)
        self.assertIn("Accountancy", cbse_sub_names)
        self.assertIn("Informatics Practices", cbse_sub_names)
        self.assertIn("History", cbse_sub_names)
        self.assertIn("Political Science", cbse_sub_names)

    def test_tnsb_importer_contains_mandatory_subjects(self):
        """TNSB importer must contain foundational subjects including Tamil, Commerce, and Sciences."""
        importer = TamilNaduBoardImporter()
        tn_data = importer.fetch_curriculum("2026-27")
        tn_sub_names = {s.subject_name for s in tn_data.subjects}

        # Class 10
        self.assertIn("Tamil", tn_sub_names)
        self.assertIn("English", tn_sub_names)
        self.assertIn("Mathematics", tn_sub_names)
        self.assertIn("Science", tn_sub_names)
        self.assertIn("Social Science", tn_sub_names)

        # Class 12
        self.assertIn("Tamil", tn_sub_names)
        self.assertIn("Physics", tn_sub_names)
        self.assertIn("Chemistry", tn_sub_names)
        self.assertIn("Biology", tn_sub_names)
        self.assertIn("Botany", tn_sub_names)
        self.assertIn("Zoology", tn_sub_names)
        self.assertIn("Computer Science", tn_sub_names)
        self.assertIn("Computer Applications", tn_sub_names)
        self.assertIn("Accountancy", tn_sub_names)
        self.assertIn("Commerce", tn_sub_names)
        self.assertIn("Economics", tn_sub_names)
        self.assertIn("Business Mathematics and Statistics", tn_sub_names)
        self.assertIn("History", tn_sub_names)
        self.assertIn("Political Science", tn_sub_names)

    def test_rejection_of_forbidden_generic_phrases(self):
        """Questions containing generic and non-syllabus placeholder phrases must be rejected."""
        forbidden_questions = [
            "Explain the structural architecture of the system in detail.",
            "Analyze the optimization techniques used in this process.",
            "Critically evaluate the broader theoretical systems governing this unit.",
            "Formulate an algorithm for hyperparameter optimization.",
            "Compare batch gradient descent and stochastic gradient descent in neural networks.",
            "Create a propulsion system concept that integrates turbofan engines and aerodynamic performance.",
            "Evaluate the vehicle routing heuristics in fleet management.",
        ]

        for fq in forbidden_questions:
            is_valid = validate_unit_relevance(
                question_text=fq,
                unit_name="Unit 1 - Life Processes",
                subject_name="Biology",
            )
            self.assertFalse(is_valid, f"Validator failed to reject forbidden generic phrase in: '{fq}'")

    def test_cross_domain_leak_rejection(self):
        """Domain-inappropriate questions (ML, SQL, engineering) must be rejected for school subjects."""
        # Machine learning leaking into Biology
        self.assertFalse(validate_unit_relevance(
            question_text="Evaluate the cross-entropy loss function used to train deep neural networks.",
            unit_name="Unit 2 - Genetics and Evolution",
            subject_name="Biology",
        ))

        # Turbofan engineering leaking into Chemistry
        self.assertFalse(validate_unit_relevance(
            question_text="Analyze the aerodynamic performance and airfoil lift of next-generation turbofan blades.",
            unit_name="Unit 3 - Electrochemistry",
            subject_name="Chemistry",
        ))

        # Calculus formula leaking into English Literature
        self.assertFalse(validate_unit_relevance(
            question_text="Find the derivative dy/dx for the given polynomial function.",
            unit_name="Unit 2 - Poetry",
            subject_name="English",
        ))

        # SQL query leaking into History
        self.assertFalse(validate_unit_relevance(
            question_text="Write an SQL query with SELECT * FROM to extract records.",
            unit_name="Unit 1 - The Harappan Civilisation",
            subject_name="History",
        ))

    def test_authentic_curriculum_retrieval(self):
        """Authentic curriculum pools must return high-quality questions for supported subjects."""
        # Tamil Class 10
        tn_q = match_curriculum_question(
            board="TNSB",
            class_name="Class 10",
            subject_name="Tamil",
            unit_name="Iyal 1",
            bloom_level="Understand",
        )
        self.assertIsNotNone(tn_q, "Must retrieve authentic Tamil Class 10 question")
        self.assertIn("அன்னை மொழியே", tn_q["q"])

        # Hindi Class 10
        hi_q = match_curriculum_question(
            board="CBSE",
            class_name="Class 10",
            subject_name="Hindi Course A",
            unit_name="Kshitij",
            bloom_level="Understand",
        )
        self.assertIsNotNone(hi_q, "Must retrieve authentic Hindi Class 10 question")
        self.assertIn("सूरदास", hi_q["q"])


if __name__ == "__main__":
    unittest.main()
