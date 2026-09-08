"""Official Tamil Nadu State Board Curriculum Importer for Academic Sessions (e.g. 2026-27)."""

from typing import List, Optional

from app.services.curriculum.base import (
    BaseCurriculumImporter,
    BoardCurriculumData,
    SubjectData,
    UnitData,
)


class TamilNaduBoardImporter(BaseCurriculumImporter):
    """Authoritative importer for Tamil Nadu State Board of School Examination (TNSB / Samacheer Kalvi)."""

    def get_board_code(self) -> str:
        return "TNSB"

    def get_board_name(self) -> str:
        return "Tamil Nadu State Board of School Examination"

    def get_state(self) -> str:
        return "Tamil Nadu"

    def fetch_curriculum(
        self,
        academic_year: str = "2026-27",
        target_classes: Optional[List[int]] = None,
    ) -> BoardCurriculumData:
        source_url = f"https://www.tnscert.org/curriculum_{academic_year.replace('-', '_')}"

        all_subjects: List[SubjectData] = [
            # =================================================================
            # CLASS 10 (SSLC)
            # =================================================================
            SubjectData(
                subject_name="Science",
                class_name="Class X",
                class_number=10,
                subject_code="TN-10-SCI",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Laws of Motion & Optics (Physics)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Thermal Physics, Electricity & Acoustics (Physics)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Nuclear Physics (Physics)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Periodic Classification & Solutions (Chemistry)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Types of Chemical Reactions, Carbon & its Compounds (Chemistry)"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Plant Anatomy & Physiology (Biology)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Structural Organisation of Animals & Human Organ Systems (Biology)"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Reproduction in Plants and Animals (Biology)"),
                    UnitData(unit_number=9, unit_name="Unit 9 - Genetics & Origin of Life (Biology)"),
                    UnitData(unit_number=10, unit_name="Unit 10 - Environmental Management & Sustainable Ecology (Biology)"),
                ],
            ),
            SubjectData(
                subject_name="Mathematics",
                class_name="Class X",
                class_number=10,
                subject_code="TN-10-MAT",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Relations and Functions"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Numbers and Sequences"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Algebra (Polynomials, Quadratics & Matrices)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Geometry (Similarity, Theorems & Circles)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Coordinate Geometry"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Trigonometry & Heights/Distances"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Mensuration (Surface Areas and Volumes)"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Statistics and Probability"),
                ],
            ),
            SubjectData(
                subject_name="Social Science",
                class_name="Class X",
                class_number=10,
                subject_code="TN-10-SOC",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - World Wars & Modern History"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Freedom Movement in Tamil Nadu & India"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Geography of India & Tamil Nadu (Physical, Climate, Agriculture)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Indian Constitution, Central & State Government"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Economics (GDP, Growth, Globalization & Food Security)"),
                ],
            ),
            SubjectData(
                subject_name="English",
                class_name="Class X",
                class_number=10,
                subject_code="TN-10-ENG",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Prose and Poetry (Textual Analysis)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Supplementary Reading"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Applied Grammar and Vocabulary"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Writing Skills (Letters, Reports, Summaries)"),
                ],
            ),

            # =================================================================
            # CLASS 12 (Higher Secondary)
            # =================================================================
            SubjectData(
                subject_name="Physics",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-PHY",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Electrostatics"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Current Electricity"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Magnetism and Magnetic Effects of Electric Current"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Electromagnetic Induction and Alternating Current"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Electromagnetic Waves & Wave Optics"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Ray Optics"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Dual Nature of Radiation and Matter"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Atomic and Nuclear Physics"),
                    UnitData(unit_number=9, unit_name="Unit 9 - Semiconductor Electronics & Communication"),
                ],
            ),
            SubjectData(
                subject_name="Chemistry",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-CHE",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Metallurgy & p-Block Elements"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Transition and Inner Transition Elements"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Coordination Chemistry"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Solid State & Chemical Kinetics"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Ionic Equilibrium & Electrochemistry"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Hydroxy Compounds and Ethers"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Carbonyl Compounds & Carboxylic Acids"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Organic Nitrogen Compounds & Biomolecules"),
                ],
            ),
            SubjectData(
                subject_name="Mathematics",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-MAT",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Applications of Matrices and Determinants"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Complex Numbers & Theory of Equations"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Inverse Trigonometric Functions & 2D Analytical Geometry"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Vector Algebra"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Differential & Integral Calculus Applications"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Differential Equations & Probability Distributions"),
                ],
            ),
            SubjectData(
                subject_name="Computer Science",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-CS",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Problem Solving Techniques & Functions in Python"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Core Python (Control Structures, Functions, Strings, Collections)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Object Oriented Programming with Python (Classes & Methods)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Database Concepts & Structured Query Language (SQL)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Python-MySQL Integration & Data Manipulation"),
                ],
            ),
        ]

        if target_classes:
            all_subjects = [s for s in all_subjects if s.class_number in target_classes]

        return BoardCurriculumData(
            board_code=self.get_board_code(),
            board_name=self.get_board_name(),
            state=self.get_state(),
            academic_year=academic_year,
            source_name="Tamil Nadu State Council of Educational Research and Training (TNSCERT)",
            source_url=source_url,
            subjects=all_subjects,
        )
