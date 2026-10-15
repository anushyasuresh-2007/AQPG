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
from app.models import Subject, Unit, AcademicClass, Board, Bloom, Question
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
            ("chemistry_biomolecules", "Chemistry", "biomolecule"),
            ("cs_oop", "Computer Science", "object oriented"),
            ("cs_unit1", "Computer Science", "problem solving"),
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

    def test_25_marks_cs_unit1_problem_solving_functions(self):
        """Computer Science Unit 1 (Problem Solving & Functions in Python): 25-mark paper must have exact marks, zero duplicates, and genuine unit isolation."""
        target = self.targets["cs_unit1"]
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

        # Verify that all selected questions strictly belong to Unit 1 and not Unit 2 Core Python
        disallowed_keywords = ["read()", "readline()", "readlines()", "list comprehension", "append operation", "count_words"]
        for q in paper["questions"]:
            for kw in disallowed_keywords:
                self.assertNotIn(
                    kw.lower(),
                    q["question"].lower(),
                    f"Unit 2 keyword '{kw}' polluted Unit 1 paper: {q['question']}"
                )

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

    def test_curriculum_matching_cs_unit1_variants(self):
        """Curriculum pool matching for CS Unit 1 across naming variants, all 5 Bloom levels, and marks."""
        from app.services.ai.curriculum_pools import match_curriculum_question

        naming_variants = [
            "Unit 1 - Problem Solving Techniques & Functions in Python",
            "Problem Solving Techniques & Functions in Python",
            "Problem Solving Techniques",
            "Functions in Python",
            "Unit 1",
        ]
        bloom_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]
        marks_options = [2, 3, 4, 5]

        # Test each naming variant matches successfully
        for variant in naming_variants:
            matched = match_curriculum_question(
                board="TNSB",
                class_name="12",
                subject_name="Computer Science",
                unit_name=variant,
                bloom_level="Remember",
                marks=2,
            )
            self.assertIsNotNone(matched, f"Failed to match curriculum question for variant: '{variant}'")
            self.assertEqual(matched["board"], "TNSB")
            self.assertEqual(matched["class"], 12)
            self.assertIn("Problem Solving", matched["unit"])

        # Test all 5 Bloom levels match suitable questions
        for bl in bloom_levels:
            matched = match_curriculum_question(
                board="TNSB",
                class_name="12",
                subject_name="Computer Science",
                unit_name="Unit 1 - Problem Solving Techniques & Functions in Python",
                bloom_level=bl,
                marks=3 if bl in ("Understand", "Apply") else (2 if bl == "Remember" else 5),
            )
            self.assertIsNotNone(matched, f"Failed to match question for Bloom level: '{bl}'")

        # Test different marks values (2, 3, 4, 5)
        for m in marks_options:
            matched = match_curriculum_question(
                board="TNSB",
                class_name="12",
                subject_name="Computer Science",
                unit_name="Unit 1 - Problem Solving Techniques & Functions in Python",
                marks=m,
            )
            self.assertIsNotNone(matched, f"Failed to match question for marks: {m}")

    def test_25_marks_chemistry_unit10_biomolecules(self):
        """Chemistry Class 12 Unit 10 Biomolecules: 25-mark paper must have exact marks, zero duplicates, and genuine unit relevance."""
        target = self.targets["chemistry_biomolecules"]
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

        # Verify unit relevance: must contain valid biomolecule domain terms
        biomolecule_keywords = ["glucose", "protein", "peptide", "amino", "dna", "rna", "sugar", "nucleic", "vitamin", "anomer", "zwitterion", "denaturation"]
        found_relevant = False
        for q in paper["questions"]:
            q_text_low = q["question"].lower()
            if any(kw in q_text_low for kw in biomolecule_keywords):
                found_relevant = True
                break
        self.assertTrue(found_relevant, "Generated Biomolecules paper must contain authentic biomolecule terminology")

        # Disallow cross-unit contamination from unrelated chemistry units (e.g., Solutions, Electrochemistry)
        disallowed_keywords = ["raoult's law", "colligative property", "osmotic pressure", "nernst equation", "galvanic cell", "molar conductivity"]
        for q in paper["questions"]:
            for kw in disallowed_keywords:
                self.assertNotIn(
                    kw,
                    q["question"].lower(),
                    f"Cross-unit keyword '{kw}' polluted Biomolecules paper: {q['question']}"
                )

    def test_curriculum_matching_chemistry_biomolecules_variants(self):
        """Curriculum pool matching for Chemistry Biomolecules across naming variants, all 5 Bloom levels, and marks."""
        from app.services.ai.curriculum_pools import match_curriculum_question

        naming_variants = [
            "Unit 10 - Biomolecules",
            "Biomolecules",
            "Unit 10",
            "Unit 8 - Organic Nitrogen Compounds & Biomolecules",
        ]
        bloom_levels = ["Remember", "Understand", "Apply", "Analyze", "Evaluate"]
        marks_options = [1, 2, 3, 4, 5]

        # Test each naming variant matches successfully
        for variant in naming_variants:
            matched = match_curriculum_question(
                board="CBSE",
                class_name="12",
                subject_name="Chemistry",
                unit_name=variant,
                bloom_level="Understand",
                marks=3,
            )
            self.assertIsNotNone(matched, f"Failed to match curriculum question for variant: '{variant}'")
            self.assertEqual(matched["unit"], "Biomolecules")

        # Test all 5 Bloom levels match suitable questions
        for bl in bloom_levels:
            matched = match_curriculum_question(
                board="CBSE",
                class_name="12",
                subject_name="Chemistry",
                unit_name="Unit 10 - Biomolecules",
                bloom_level=bl,
                marks=3 if bl in ("Understand", "Apply") else (2 if bl == "Remember" else 5),
            )
            self.assertIsNotNone(matched, f"Failed to match question for Bloom level: '{bl}'")

        # Test different marks values (1, 2, 3, 4, 5)
        for m in marks_options:
            matched = match_curriculum_question(
                board="CBSE",
                class_name="12",
                subject_name="Chemistry",
                unit_name="Unit 10 - Biomolecules",
                marks=m,
            )
            self.assertIsNotNone(matched, f"Failed to match question for marks: {m}")

    def test_exhausted_pool_biomolecules_actionable_error_on_excessive_marks(self):
        """When mark target on single-unit Biomolecules exceeds distinct verified questions, must raise an actionable ValueError."""
        target = self.targets["chemistry_biomolecules"]
        self.assertIsNotNone(target["subject"])
        # Requesting a huge 150-mark paper on a single unit with strict bloom distribution exhausts distinct templates
        with self.assertRaises(ValueError) as ctx:
            generate_question_paper(
                db=self.db,
                subject_id=target["subject"].id,
                selected_units=[target["unit"].id],
                total_marks=150,
                bloom_distribution=self.DEFAULT_BLOOM_DIST,
                source_mode="ai",
                use_ai=True,
            )
        err_msg = str(ctx.exception)
        self.assertIn("exhausted", err_msg.lower())
        self.assertIn("broaden the unit selection", err_msg.lower())

    # =========================================================================
    # 5. POST-AUDIT TARGETED FIX REGRESSIONS
    # =========================================================================

    def test_subject_compatibility_collisions_and_aliases(self):
        """Fix 1 Regression: Prevent 'cs' inside 'mathematics' and 'science' inside 'social science' collisions."""
        from app.services.exam_blueprints import _are_subjects_compatible, get_exam_blueprint

        # Incompatible subjects must evaluate to False
        self.assertFalse(_are_subjects_compatible("Mathematics", "Computer Science"), "Math and CS must be incompatible.")
        self.assertFalse(_are_subjects_compatible("Maths", "CS"), "Maths and CS must be incompatible.")
        self.assertFalse(_are_subjects_compatible("Science", "Social Science"), "Science and Social Science must be incompatible.")
        self.assertFalse(_are_subjects_compatible("General Science", "Social Studies"), "Science and Social Studies must be incompatible.")

        # Compatible aliases must evaluate to True
        self.assertTrue(_are_subjects_compatible("Mathematics", "Maths"), "Mathematics and Maths must be compatible.")
        self.assertTrue(_are_subjects_compatible("CS", "Computer Science"), "CS and Computer Science must be compatible.")
        self.assertTrue(_are_subjects_compatible("Computer Science", "CS"), "Computer Science and CS must be compatible.")
        self.assertTrue(_are_subjects_compatible("Social Science", "Social Studies"), "Social Science and Social Studies must be compatible.")

        # Valid Class 10 and Class 12 blueprint lookups must be preserved
        bp_cs = get_exam_blueprint("TNSB", 12, "519", "Computer Science")
        self.assertIsNotNone(bp_cs)
        self.assertEqual(bp_cs.subject_code, "519")

        bp_phy = get_exam_blueprint("TNSB", 12, "505", "Physics")
        self.assertIsNotNone(bp_phy)
        self.assertEqual(bp_phy.subject_code, "505")

        bp_math10 = get_exam_blueprint("TNSB", 10, "003", "Mathematics")
        self.assertIsNotNone(bp_math10)
        self.assertEqual(bp_math10.subject_code, "TN-10-MAT")

        bp_eng12 = get_exam_blueprint("TNSB", 12, "003", "English")
        self.assertIsNotNone(bp_eng12)
        self.assertEqual(bp_eng12.subject_code, "003")

        # Incompatible code / subject combinations must fail safely
        bp_conflict = get_exam_blueprint("TNSB", 12, "519", "Mathematics")
        self.assertIsNone(bp_conflict, "Mathematics requested with CS code 519 must return None.")

        # Class 10 Science lookup must never silently match Social Science
        bp_sci = get_exam_blueprint("TNSB", 10, None, "Science")
        if bp_sci is not None:
            self.assertNotEqual(bp_sci.subject_name, "Social Science")

    def test_ai_generator_fallback_signature_and_no_generic_filler(self):
        """Fix 2 Regression: _get_mock_question_text does not raise TypeError and returns empty string instead of generic filler."""
        from app.services.ai_generator import _get_mock_question_text

        # 1. Valid authentic question retrieval with explicit board and class_name
        q_valid = _get_mock_question_text("Chemistry", "Biomolecules", "Remember", "medium", 2, board="TNSB", class_name="12")
        self.assertTrue(len(q_valid) > 0, "Must retrieve an authentic question.")
        self.assertNotIn("foundational definitions", q_valid.lower())

        # 2. Legacy callers without board and class_name must succeed with safe defaults
        q_legacy = _get_mock_question_text("Chemistry", "Biomolecules", "Remember", "medium", 2)
        self.assertTrue(len(q_legacy) > 0, "Legacy callers without board/class must succeed.")

        # 3. Non-existent pool question must return empty string rather than generic filler
        q_empty = _get_mock_question_text("NonExistentSubject", "NonExistentUnit", "Remember", "medium", 2)
        self.assertEqual(q_empty, "", "Must return empty string when no authentic question is available.")
        self.assertNotIn("foundational definitions", q_empty.lower())
        self.assertNotIn("laws and principles", q_empty.lower())

    def test_biomolecules_no_duplicates_and_enzyme_evaluation_distinctness(self):
        """Fix 3 Regression: Biomolecules has zero duplicate/near-duplicate pairs and distinct 5-mark questions."""
        from app.services.ai.curriculum_pools import CHEMISTRY_QUESTIONS

        bio_qs = [q for q in CHEMISTRY_QUESTIONS if q.get("unit") == "Biomolecules"]
        self.assertEqual(len(bio_qs), 22, f"Expected 22 Biomolecules questions, found {len(bio_qs)}")

        # Pairwise near-duplicate check across all 22 questions
        for i in range(len(bio_qs)):
            for j in range(i + 1, len(bio_qs)):
                qi = bio_qs[i]["q"]
                qj = bio_qs[j]["q"]
                self.assertFalse(
                    is_near_duplicate(qi, [qj], threshold=0.60),
                    f"Near-duplicate found between question {i+1} and {j+1}:\nQ1: {qi}\nQ2: {qj}"
                )

        # Verify replacement enzyme question exists and is distinct from protein hierarchy
        q_texts = [q["q"].lower() for q in bio_qs]
        has_enzyme = any("enzyme catalysis" in qt for qt in q_texts)
        has_protein_hierarchy = any("structural hierarchy of proteins" in qt for qt in q_texts)
        self.assertTrue(has_enzyme, "Biomolecules pool must contain the enzyme catalysis evaluation question.")
        self.assertTrue(has_protein_hierarchy, "Biomolecules pool must contain the protein hierarchy question.")

    def test_offline_fallback_provider_stops_generic_fabrication_on_exhaustion(self):
        """Fix 4 Regression: OfflineFallbackProvider returns None on pool exhaustion, never fabricates generic templates."""
        from app.services.ai.generator_factory import OfflineFallbackProvider
        from app.services.ai.curriculum_pools import CHEMISTRY_QUESTIONS

        prov = OfflineFallbackProvider()
        bio_q_texts = [q["q"] for q in CHEMISTRY_QUESTIONS if q.get("unit") == "Biomolecules"]

        # When all authentic questions are excluded, provider must return None
        p_exhausted = AIQuestionPrompt(
            board="TNSB",
            class_name="12",
            subject_name="Chemistry",
            unit_name="Biomolecules",
            topic_name="Biomolecules",
            question_type="Long Answer",
            bloom_level="Evaluate",
            marks=5,
            difficulty="Hard",
            exclude_texts=bio_q_texts,
        )
        res = prov.generate_question(p_exhausted)
        self.assertIsNone(res, "Provider must return None on pool exhaustion, not generic templates.")

        # When valid questions exist, provider must return authentic result
        p_valid = AIQuestionPrompt(
            board="TNSB",
            class_name="12",
            subject_name="Chemistry",
            unit_name="Biomolecules",
            topic_name="Biomolecules",
            question_type="Long Answer",
            bloom_level="Evaluate",
            marks=5,
            difficulty="Hard",
            exclude_texts=[],
        )
        res_valid = prov.generate_question(p_valid)
        self.assertIsNotNone(res_valid)
        self.assertNotIn("foundational laws and definitions governing", res_valid.question_text.lower())

    def test_ai_generated_questions_not_labelled_verified(self):
        """Fix 5 Regression: AI-generated questions in draft status must not be labelled validation_status='verified'."""
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
        ai_questions = [q for q in paper["questions"] if q.get("source") == "AI Synthesized"]
        self.assertTrue(len(ai_questions) > 0, "Expected at least one AI-synthesized question.")
        for q in ai_questions:
            self.assertNotEqual(
                q.get("validation_status"),
                "verified",
                f"AI-generated question {q['question_id']} must not be labelled 'verified': {q}",
            )
            self.assertEqual(
                q.get("validation_status"),
                "draft",
                f"AI-generated question {q['question_id']} should have validation_status='draft'",
            )
            # Verify persisted question in DB is also approved=False and status='draft'
            db_q = self.db.query(Question).filter(Question.id == q["question_id"]).first()
            self.assertIsNotNone(db_q)
            self.assertFalse(db_q.approved)
            self.assertEqual(db_q.status, "draft")


if __name__ == "__main__":
    unittest.main()
