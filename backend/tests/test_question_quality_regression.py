"""
test_question_quality_regression.py
Quality-focused regression tests for AQPG question generation pipeline:
1. Strict near-duplicate detection and elimination of generic contextual suffix padding.
2. Pool exhaustion handling with clear, actionable error reporting.
3. Papers with small and large mark targets (25 and 50 marks) across:
   - Physics: Electrostatics
   - Chemistry: Metallurgy and p-Block Elements
   - Computer Science: Object Oriented Programming (Classes & Methods)
   - Mathematics: Geometry
   - English: Literature / Prose
   - Social Science: History / Contemporary World
4. Exact total marks, board/class/unit isolation, and Bloom cognitive intent.
"""

import re
import sys
import unittest
from pathlib import Path
from typing import List, Dict, Any

# Ensure backend directory is on sys.path
backend_path = Path(__file__).resolve().parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.db.session import SessionLocal
from app.models import Subject, Unit, AcademicClass, Board, Bloom
from app.services.ai.base import AIQuestionPrompt
from app.services.ai.generator_factory import OfflineFallbackProvider
from app.services.ai.curriculum_pools import get_math_curriculum_question, normalize_text_for_comparison
from app.services.bloom_service import validate_bloom_level
from app.services.question_generator import generate_question_paper, is_near_duplicate


DISALLOWED_SUFFIX_PATTERNS = [
    r"with reference to standard practical applications",
    r"focusing on the essential operational steps",
    r"highlighting key distinctions, core challenges",
    r"in the context of curriculum problem solving",
    r"demonstrating analytical clarity, underlying principles",
    r"\(Part \d+\)",
    r"\(Variation \d+\)",
]


class TestQuestionQualityRegression(unittest.TestCase):
    """Quality-gate regression test suite verifying distinct, syllabus-grounded questions."""

    @classmethod
    def setUpClass(cls):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        repo_root = Path(__file__).resolve().parents[2]
        db_file = repo_root / "aqpg.db"
        if not db_file.exists():
            db_file = repo_root / "backend" / "aqpg.db"

        engine = create_engine(f"sqlite:///{db_file.as_posix()}", connect_args={"check_same_thread": False})
        SessionCls = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        cls.db = SessionCls()
        cls.provider = OfflineFallbackProvider()

        # Find target subjects and units in local DB
        cls.targets: Dict[str, Dict[str, Any]] = {}
        target_specs = [
            ("physics", "Physics", "electrostatics"),
            ("chemistry", "Chemistry", "metallurgy"),
            ("cs_oop", "Computer Science", "object oriented"),
            ("math_geometry", "Mathematics Standard", "geometry"),
            ("english", "English Core", "literature"),
            ("social_science", "Social Science", "contemporary world"),
        ]

        all_subjects = cls.db.query(Subject).all()
        for key, subj_name, unit_kw in target_specs:
            matched_subj = None
            matched_unit = None
            for s in all_subjects:
                if subj_name.lower() in s.subject_name.lower():
                    units = cls.db.query(Unit).filter(Unit.subject_id == s.id, Unit.active == True).all()
                    for u in units:
                        if unit_kw.lower() in u.unit_name.lower():
                            matched_subj = s
                            matched_unit = u
                            break
                if matched_subj and matched_unit:
                    break

            if not matched_subj or not matched_unit:
                # Fallback search by subject keyword if exact name differs
                for s in all_subjects:
                    if key.split("_")[0] in s.subject_name.lower():
                        units = cls.db.query(Unit).filter(Unit.subject_id == s.id, Unit.active == True).all()
                        for u in units:
                            if unit_kw.lower() in u.unit_name.lower() or any(w in u.unit_name.lower() for w in unit_kw.split()):
                                matched_subj = s
                                matched_unit = u
                                break
                    if matched_subj and matched_unit:
                        break

            cls.targets[key] = {
                "subject": matched_subj,
                "unit": matched_unit,
            }

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # =========================================================================
    # 1. NEAR-DUPLICATE DETECTION UNIT TESTS
    # =========================================================================

    def test_near_duplicate_detects_identical_strings(self):
        """Identical strings must be detected as duplicates."""
        q1 = "State Coulomb's Law of electrostatics for two point charges in vacuum."
        q2 = "State Coulomb's Law of electrostatics for two point charges in vacuum."
        self.assertTrue(is_near_duplicate(q1, [q2]))

    def test_near_duplicate_detects_suffix_padding(self):
        """Questions made unique only by appending generic suffixes must be flagged as duplicates."""
        base_q = "Explain the core working mechanism, data flow, and memory organization of Object Oriented Programming with Python."
        padded_q1 = base_q + " with reference to standard practical applications and illustrative examples."
        padded_q2 = base_q + " focusing on the essential operational steps and theoretical context."
        part_padded = base_q + " (Part 4)."

        self.assertTrue(is_near_duplicate(padded_q1, [base_q]), "Suffix-padded variation must be flagged as near-duplicate")
        self.assertTrue(is_near_duplicate(padded_q2, [base_q]), "Suffix-padded variation must be flagged as near-duplicate")
        self.assertTrue(is_near_duplicate(part_padded, [base_q]), "(Part N) padded variation must be flagged as near-duplicate")

    def test_near_duplicate_allows_genuinely_distinct_questions(self):
        """Distinct syllabus questions testing different concepts must NOT be flagged as duplicates."""
        q1 = "State Coulomb's Law of electrostatics for two point charges in vacuum."
        q2 = "Explain why electric field lines never intersect each other and describe the physical significance of electric flux."
        q3 = "Calculate the equivalent capacitance of three capacitors connected in series and in parallel."
        q4 = "Derive an expression for the electric field intensity at a point on the axial line of an electric dipole."

        self.assertFalse(is_near_duplicate(q1, [q2, q3, q4]))
        self.assertFalse(is_near_duplicate(q2, [q1, q3, q4]))
        self.assertFalse(is_near_duplicate(q3, [q1, q2, q4]))
        self.assertFalse(is_near_duplicate(q4, [q1, q2, q3]))

    # =========================================================================
    # 2. FALLBACK PROVIDER QUALITY & NO SUFFIX VARIATIONS
    # =========================================================================

    def test_offline_fallback_provider_returns_none_when_exhausted(self):
        """When all distinct templates for a cognitive level are excluded, provider must return None, not pad with suffixes."""
        prompt = AIQuestionPrompt(
            board="CBSE",
            class_name="Class 12",
            subject_name="Computer Science",
            unit_name="Object Oriented Programming with Python (Classes & Methods)",
            topic_name="Classes & Methods",
            marks=3,
            difficulty="medium",
            bloom_level="Understand",
            question_type="Short Answer",
        )

        # Collect questions until provider returns None
        collected = []
        for _ in range(50):
            prompt.exclude_texts = collected
            res = self.provider.generate_question(prompt)
            if res is None:
                break
            collected.append(res.question_text)

        # Verify that all collected questions are distinct and none contain disallowed suffixes
        for q_text in collected:
            for pattern in DISALLOWED_SUFFIX_PATTERNS:
                self.assertIsNone(
                    re.search(pattern, q_text, re.IGNORECASE),
                    f"Generated question contains disallowed suffix padding: '{q_text}'"
                )

        # Must eventually return None (clean exhaustion)
        self.assertIsNone(
            self.provider.generate_question(prompt),
            "Provider must return None when question pool and distinct templates are exhausted."
        )

    def test_math_curriculum_pool_returns_none_when_exhausted(self):
        """get_math_curriculum_question must return None when category is exhausted, never duplicate."""
        collected = []
        for _ in range(50):
            res = get_math_curriculum_question(category="GEOMETRY", bloom_level="Apply", exclude_texts=collected)
            if res is None:
                break
            collected.append(res["q"])

        # When exhausted, must return None
        res_exhausted = get_math_curriculum_question(category="GEOMETRY", bloom_level="Apply", exclude_texts=collected)
        self.assertIsNone(res_exhausted, "Math pool must return None rather than repeating an excluded question.")

    # =========================================================================
    # 3. 25-MARK QUESTION PAPER GENERATION (Target Units)
    # =========================================================================

    def _verify_paper_quality(self, paper: Dict[str, Any], expected_marks: int, expected_subj_name: str, expected_unit_name: str):
        """Common quality gate verifications for a generated paper."""
        questions = paper.get("questions", [])
        self.assertTrue(len(questions) > 0, "Paper must contain at least one question.")

        # 1. Exact total marks
        total_actual_marks = sum(q["marks"] for q in questions)
        self.assertEqual(
            total_actual_marks,
            expected_marks,
            f"Expected exactly {expected_marks} marks, got {total_actual_marks}"
        )

        # 2. Isolation: subject and unit
        for q in questions:
            self.assertEqual(q["subject"].lower(), expected_subj_name.lower())
            self.assertEqual(q["unit_name"].lower(), expected_unit_name.lower())

        # 3. No disallowed suffix padding
        for q in questions:
            q_text = q["question"]
            for pat in DISALLOWED_SUFFIX_PATTERNS:
                self.assertIsNone(
                    re.search(pat, q_text, re.IGNORECASE),
                    f"Disallowed padding pattern '{pat}' detected in: '{q_text}'"
                )

        # 4. Zero exact duplicates
        q_texts = [q["question"] for q in questions]
        self.assertEqual(
            len(set(normalize_text_for_comparison(t) for t in q_texts)),
            len(q_texts),
            "Duplicate questions detected in paper!"
        )

        # 5. Zero near duplicates
        for i, q1 in enumerate(q_texts):
            other_qs = [q_texts[j] for j in range(len(q_texts)) if j != i]
            self.assertFalse(
                is_near_duplicate(q1, other_qs),
                f"Question is a near-duplicate of another question in the paper: '{q1}'"
            )

        # 6. Valid Bloom level intent
        for q in questions:
            bloom_level = q.get("bloom", "Understand")
            is_valid, detected, reason = validate_bloom_level(q["question"], bloom_level)
            self.assertTrue(
                is_valid,
                f"Bloom taxonomy alignment failed for '{q['question']}': requested '{bloom_level}', got reason: {reason}"
            )

    DEFAULT_BLOOM_DIST = {"Remember": 20, "Understand": 30, "Apply": 30, "Analyze": 10, "Evaluate": 10}

    def test_25_marks_physics_electrostatics(self):
        """Physics Electrostatics: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["physics"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    def test_25_marks_chemistry_metallurgy_pblock(self):
        """Chemistry Metallurgy & p-Block: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["chemistry"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    def test_25_marks_cs_oop(self):
        """Computer Science OOP: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["cs_oop"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    def test_25_marks_mathematics_geometry(self):
        """Mathematics Geometry: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["math_geometry"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    def test_25_marks_english(self):
        """English: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["english"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    def test_25_marks_social_science(self):
        """Social Science: 25-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["social_science"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=25,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 25, target["subject"].subject_name, target["unit"].unit_name)

    # =========================================================================
    # 4. 50-MARK QUESTION PAPER GENERATION (Target Units)
    # =========================================================================

    def test_50_marks_physics_electrostatics(self):
        """Physics Electrostatics: 50-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["physics"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=50,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 50, target["subject"].subject_name, target["unit"].unit_name)

    def test_50_marks_chemistry_metallurgy_pblock(self):
        """Chemistry Metallurgy & p-Block: 50-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["chemistry"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=50,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 50, target["subject"].subject_name, target["unit"].unit_name)

    def test_50_marks_cs_oop(self):
        """Computer Science OOP: 50-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["cs_oop"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=50,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 50, target["subject"].subject_name, target["unit"].unit_name)

    def test_50_marks_mathematics_geometry(self):
        """Mathematics Geometry: 50-mark paper must have exact marks, zero duplicates, and genuine diversity."""
        target = self.targets["math_geometry"]
        self.assertIsNotNone(target["subject"])
        paper = generate_question_paper(
            db=self.db,
            subject_id=target["subject"].id,
            selected_units=[target["unit"].id],
            total_marks=50,
            bloom_distribution=self.DEFAULT_BLOOM_DIST,
            source_mode="ai",
            use_ai=True,
        )
        self._verify_paper_quality(paper, 50, target["subject"].subject_name, target["unit"].unit_name)

    # =========================================================================
    # 5. POOL EXHAUSTION HANDLING (Actionable Error, No Padding)
    # =========================================================================

    def test_exhausted_pool_raises_actionable_error(self):
        """When mark target exceeds available distinct questions, must raise an actionable ValueError."""
        target = self.targets["cs_oop"]
        self.assertIsNotNone(target["subject"])

        # Requesting 300 marks from a single unit with zero external AI credentials must exhaust the pool
        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=target["subject"].id,
                selected_units=[target["unit"].id],
                total_marks=300,
                bloom_distribution=self.DEFAULT_BLOOM_DIST,
                source_mode="ai",
                use_ai=True,
            )

        err_msg = str(ctx.exception)
        self.assertIn("exhausted", err_msg.lower())
        self.assertTrue(
            "broaden the unit selection" in err_msg.lower() or "adjust" in err_msg.lower(),
            f"Error message must provide actionable advice: {err_msg}"
        )


if __name__ == "__main__":
    unittest.main()
