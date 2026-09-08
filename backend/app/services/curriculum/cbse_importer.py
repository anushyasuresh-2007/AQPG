"""Official CBSE Board Curriculum Importer for Academic Sessions (e.g. 2026-27)."""

from typing import List, Optional

from app.services.curriculum.base import (
    BaseCurriculumImporter,
    BoardCurriculumData,
    SubjectData,
    TopicData,
    UnitData,
)


class CBSEImporter(BaseCurriculumImporter):
    """Authoritative importer for Central Board of Secondary Education (CBSE) Academic Curriculum."""

    def get_board_code(self) -> str:
        return "CBSE"

    def get_board_name(self) -> str:
        return "Central Board of Secondary Education"

    def get_state(self) -> str:
        return "All India"

    def fetch_curriculum(
        self,
        academic_year: str = "2026-27",
        target_classes: Optional[List[int]] = None,
    ) -> BoardCurriculumData:
        source_url = f"https://cbseacademic.nic.in/curriculum_{academic_year.replace('-', '_')}.html"

        all_subjects: List[SubjectData] = [
            # =================================================================
            # CLASS 10 (Secondary)
            # =================================================================
            SubjectData(
                subject_name="Science",
                class_name="Class X",
                class_number=10,
                subject_code="086",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(
                        unit_number=1,
                        unit_name="Unit 1 - Chemical Substances: Nature and Behaviour",
                        topics=[
                            TopicData(topic_name="Chemical Reactions and Equations"),
                            TopicData(topic_name="Acids, Bases and Salts"),
                            TopicData(topic_name="Metals and Non-metals"),
                            TopicData(topic_name="Carbon and its Compounds"),
                        ],
                    ),
                    UnitData(
                        unit_number=2,
                        unit_name="Unit 2 - World of Living",
                        topics=[
                            TopicData(topic_name="Life Processes"),
                            TopicData(topic_name="Control and Coordination"),
                            TopicData(topic_name="How do Organisms Reproduce?"),
                            TopicData(topic_name="Heredity and Evolution"),
                        ],
                    ),
                    UnitData(
                        unit_number=3,
                        unit_name="Unit 3 - Natural Phenomena",
                        topics=[
                            TopicData(topic_name="Light - Reflection and Refraction"),
                            TopicData(topic_name="Human Eye and Colourful World"),
                        ],
                    ),
                    UnitData(
                        unit_number=4,
                        unit_name="Unit 4 - Effects of Current",
                        topics=[
                            TopicData(topic_name="Electricity and Ohm's Law"),
                            TopicData(topic_name="Magnetic Effects of Electric Current"),
                        ],
                    ),
                    UnitData(
                        unit_number=5,
                        unit_name="Unit 5 - Natural Resources & Environment",
                        topics=[
                            TopicData(topic_name="Our Environment & Ecosystems"),
                            TopicData(topic_name="Sustainable Natural Resource Management"),
                        ],
                    ),
                ],
            ),
            SubjectData(
                subject_name="Mathematics Standard",
                class_name="Class X",
                class_number=10,
                subject_code="041",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Number Systems (Real Numbers)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Algebra (Polynomials, Linear Equations, Quadratics, AP)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Coordinate Geometry"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Geometry (Triangles & Circles)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Trigonometry & Applications"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Mensuration (Areas Related to Circles, Surface Areas & Volumes)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Statistics and Probability"),
                ],
            ),
            SubjectData(
                subject_name="Social Science",
                class_name="Class X",
                class_number=10,
                subject_code="087",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - India and the Contemporary World - II (History)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Contemporary India - II (Geography)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Democratic Politics - II (Political Science)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Understanding Economic Development (Economics)"),
                ],
            ),
            SubjectData(
                subject_name="English Language and Literature",
                class_name="Class X",
                class_number=10,
                subject_code="184",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Reading Skills (Comprehension & Inference)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Writing Skills and Applied Grammar"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Language Through Literature (First Flight)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Supplementary Reader (Footprints Without Feet)"),
                ],
            ),
            SubjectData(
                subject_name="Information Technology",
                class_name="Class X",
                class_number=10,
                subject_code="402",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Employability Skills (Communication & Self Management)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Digital Documentation (Advanced)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Electronic Spreadsheet (Advanced)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Database Management System (RDBMS)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Web Applications and Security"),
                ],
            ),

            # =================================================================
            # CLASS 12 (Senior Secondary)
            # =================================================================
            SubjectData(
                subject_name="Physics",
                class_name="Class XII",
                class_number=12,
                subject_code="042",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Electrostatics (Electric Charges, Fields & Potential)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Current Electricity"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Magnetic Effects of Current and Magnetism"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Electromagnetic Induction and Alternating Currents"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Electromagnetic Waves"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Optics (Ray & Wave Optics)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Dual Nature of Radiation and Matter"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Atoms and Nuclei"),
                    UnitData(unit_number=9, unit_name="Unit 9 - Electronic Devices (Semiconductors)"),
                ],
            ),
            SubjectData(
                subject_name="Chemistry",
                class_name="Class XII",
                class_number=12,
                subject_code="043",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Solutions"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Electrochemistry"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Chemical Kinetics"),
                    UnitData(unit_number=4, unit_name="Unit 4 - The d- and f-Block Elements"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Coordination Compounds"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Haloalkanes and Haloarenes"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Alcohols, Phenols and Ethers"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Aldehydes, Ketones and Carboxylic Acids"),
                    UnitData(unit_number=9, unit_name="Unit 9 - Amines"),
                    UnitData(unit_number=10, unit_name="Unit 10 - Biomolecules"),
                ],
            ),
            SubjectData(
                subject_name="Biology",
                class_name="Class XII",
                class_number=12,
                subject_code="044",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Reproduction (Plant & Human Reproduction)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Genetics and Evolution (Inheritance & Molecular Basis)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Biology and Human Welfare (Health, Disease & Microbes)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Biotechnology: Principles, Processes and Applications"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Ecology and Environment (Organisms, Ecosystem, Biodiversity)"),
                ],
            ),
            SubjectData(
                subject_name="Mathematics",
                class_name="Class XII",
                class_number=12,
                subject_code="041",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Relations and Functions & Inverse Trigonometry"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Algebra (Matrices and Determinants)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Calculus (Continuity, Differentiability, Integrals & Differential Equations)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Vectors and Three-Dimensional Geometry"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Linear Programming"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Probability and Random Variables"),
                ],
            ),
            SubjectData(
                subject_name="Computer Science",
                class_name="Class XII",
                class_number=12,
                subject_code="083",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Computational Thinking and Programming - 2 (Python Advanced)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Computer Networks (Architecture, Protocols & Web)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Database Management (SQL & Python-DB Connectivity)"),
                ],
            ),
            SubjectData(
                subject_name="Economics",
                class_name="Class XII",
                class_number=12,
                subject_code="030",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - National Income and Related Aggregates"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Money and Banking"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Determination of Income and Employment"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Government Budget and the Economy"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Balance of Payments & Foreign Exchange"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Indian Economic Development (Development Experience 1947-90 & Reforms)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Current Challenges Facing Indian Economy"),
                ],
            ),
            SubjectData(
                subject_name="Business Studies",
                class_name="Class XII",
                class_number=12,
                subject_code="054",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Nature and Significance of Management"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Principles of Management & Business Environment"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Planning and Organizing"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Staffing, Directing and Controlling"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Financial Management and Financial Markets"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Marketing Management and Consumer Protection"),
                ],
            ),
            SubjectData(
                subject_name="Accountancy",
                class_name="Class XII",
                class_number=12,
                subject_code="055",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Accounting for Partnership Firms (Fundamentals & Reconstitution)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Accounting for Companies (Share Capital & Debentures)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Analysis of Financial Statements (Ratios & Cash Flow)"),
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
            source_name="CBSE Official Academic Curriculum Portal",
            source_url=source_url,
            subjects=all_subjects,
        )
