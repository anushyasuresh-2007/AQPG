"""Official Tamil Nadu State Board Curriculum Importer for Academic Sessions (e.g. 2026-27)."""

from typing import List, Optional

from app.services.curriculum.base import (
    BaseCurriculumImporter,
    BoardCurriculumData,
    SubjectData,
    TopicData,
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
                    UnitData(unit_number=1, unit_name="Unit 1 - World Wars & Modern History", topics=[
                        TopicData(topic_name="Outbreak of World War I and Its Aftermath"),
                        TopicData(topic_name="The World between two World Wars (Fascism & Nazism)"),
                        TopicData(topic_name="World War II and The World after World War II"),
                        TopicData(topic_name="Social and Religious Reform Movements in 19th Century"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Freedom Movement in Tamil Nadu & India", topics=[
                        TopicData(topic_name="Early Revolts against British Rule in Tamil Nadu (Palayakkarars)"),
                        TopicData(topic_name="Anti-Colonial Movements and Birth of Nationalism"),
                        TopicData(topic_name="Nationalism: Gandhian Phase (Non-Cooperation & Civil Disobedience)"),
                        TopicData(topic_name="Freedom Struggle in Tamil Nadu (Bharati, VOC, Rajaji)"),
                        TopicData(topic_name="Social Transformation in Tamil Nadu (Self-Respect Movement & Justice Party)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Geography of India & Tamil Nadu (Physical, Climate, Agriculture)", topics=[
                        TopicData(topic_name="India - Location, Relief and Drainage"),
                        TopicData(topic_name="Climate and Natural Vegetation of India"),
                        TopicData(topic_name="India - Agriculture (Crops & Irrigation)"),
                        TopicData(topic_name="India - Resources and Industries"),
                        TopicData(topic_name="Physical and Human Geography of Tamil Nadu"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Indian Constitution, Central & State Government", topics=[
                        TopicData(topic_name="Indian Constitution: Preamble, Fundamental Rights & Duties"),
                        TopicData(topic_name="Central Government: President, Prime Minister & Parliament"),
                        TopicData(topic_name="State Government: Governor, Chief Minister & Legislature"),
                        TopicData(topic_name="India's Foreign Policy and International Relations"),
                    ]),
                    UnitData(unit_number=5, unit_name="Unit 5 - Economics (GDP, Growth, Globalization & Food Security)", topics=[
                        TopicData(topic_name="Gross Domestic Product and its Growth: an Introduction"),
                        TopicData(topic_name="Globalization and Trade (MNCs & WTO)"),
                        TopicData(topic_name="Food Security and Nutrition (PDS & Agricultural Policy)"),
                        TopicData(topic_name="Government and Taxes (Direct & Indirect Taxes, GST)"),
                        TopicData(topic_name="Industrial Clusters in Tamil Nadu"),
                    ]),
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
                    UnitData(unit_number=1, unit_name="Unit 1 - Prose and Poetry (Textual Analysis)", topics=[
                        TopicData(topic_name="His First Flight (Liam O'Flaherty)"),
                        TopicData(topic_name="The Night the Ghost Got In (James Thurber)"),
                        TopicData(topic_name="Empowered Women Navigating the World"),
                        TopicData(topic_name="The Attic (Satyajit Ray)"),
                        TopicData(topic_name="Tech Bloomers"),
                        TopicData(topic_name="Life (Henry Van Dyke)"),
                        TopicData(topic_name="The Grumble Family (L.M. Montgomery)"),
                        TopicData(topic_name="I am Every Woman (Rakhi Nariani Shirke)"),
                        TopicData(topic_name="The Secret of the Machines (Rudyard Kipling)"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Supplementary Reading", topics=[
                        TopicData(topic_name="The Tempest (Tales from Shakespeare)"),
                        TopicData(topic_name="Zigzag (Asha Nehemiah)"),
                        TopicData(topic_name="The Story of Mulan"),
                        TopicData(topic_name="The Aged Mother (Matsuo Basho)"),
                        TopicData(topic_name="A Dilemma (Silas Weir Mitchell)"),
                        TopicData(topic_name="The Little Hero of Holland"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Applied Grammar and Vocabulary", topics=[
                        TopicData(topic_name="Modals and Semi-Modals"),
                        TopicData(topic_name="Active and Passive Voice"),
                        TopicData(topic_name="Direct and Indirect Speech"),
                        TopicData(topic_name="Prepositional Phrases and Conjunctions"),
                        TopicData(topic_name="Degrees of Comparison and Tenses"),
                        TopicData(topic_name="Phrasal Verbs, Idioms and Affixes"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Writing Skills (Letters, Reports, Summaries)", topics=[
                        TopicData(topic_name="Formal and Informal Letter Writing"),
                        TopicData(topic_name="Notice Writing and Message Drafting"),
                        TopicData(topic_name="Report Writing and Speech Writing"),
                        TopicData(topic_name="Picture Comprehension and Advertisement Making"),
                        TopicData(topic_name="Summary Writing and Note-Making"),
                    ]),
                ],
            ),

            # =================================================================
            # CLASS 12 (Higher Secondary)
            # =================================================================
            SubjectData(
                subject_name="English",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-ENG",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Prose Analysis", topics=[
                        TopicData(topic_name="Two Gentlemen of Verona (A.J. Cronin)"),
                        TopicData(topic_name="A Nice Cup of Tea (George Orwell)"),
                        TopicData(topic_name="In Celebration of Being Alive (Dr. Christian Barnard)"),
                        TopicData(topic_name="The Summit (Edmund Hillary)"),
                        TopicData(topic_name="The Chair (Ki. Rajanarayanan)"),
                        TopicData(topic_name="On the Rule of the Road (A.G. Gardiner)"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Poetry Appreciation", topics=[
                        TopicData(topic_name="The Castle (Edwin Muir)"),
                        TopicData(topic_name="Our Casuarina Tree (Toru Dutt)"),
                        TopicData(topic_name="All the World’s a Stage (William Shakespeare)"),
                        TopicData(topic_name="Ulysses (Alfred Tennyson)"),
                        TopicData(topic_name="A Father to his Son (Carl Sandburg)"),
                        TopicData(topic_name="Incident of the French Camp (Robert Browning)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Supplementary Reader Stories", topics=[
                        TopicData(topic_name="God Sees the Truth, but Waits (Leo Tolstoy)"),
                        TopicData(topic_name="Life of Pi (Yann Martel)"),
                        TopicData(topic_name="The Hour of Truth (Percival Wilde)"),
                        TopicData(topic_name="The Midnight Visitor (Robert Arthur)"),
                        TopicData(topic_name="All Summer in a Day (Ray Bradbury)"),
                        TopicData(topic_name="Remember Caesar (Gordon Daviot)"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Grammar, Vocabulary and Advanced Writing", topics=[
                        TopicData(topic_name="Question Tags and Relative Clauses"),
                        TopicData(topic_name="Conditional Clauses (If clauses)"),
                        TopicData(topic_name="Reported Speech and Inversion"),
                        TopicData(topic_name="Job Application Letter with Bio-Data / Resume"),
                        TopicData(topic_name="Article and Report Writing"),
                        TopicData(topic_name="Note-Making and Summarizing"),
                    ]),
                ],
            ),
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
            SubjectData(
                subject_name="Biology",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-BIO",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Reproduction in Organisms & Sexual Reproduction in Flowering Plants"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Human Reproduction & Reproductive Health"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Principles and Molecular Basis of Inheritance"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Evolution, Human Health and Diseases"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Biotechnology: Principles and Applications"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Organisms and Populations, Ecosystem & Environmental Issues"),
                ],
            ),
            SubjectData(
                subject_name="Economics",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-ECO",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Introduction to Macro Economics & National Income"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Theories of Employment and Income"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Monetary Economics, Banking and Inflation"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Fiscal Economics & Public Finance"),
                    UnitData(unit_number=5, unit_name="Unit 5 - International Economics & Trade"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Fiscal Planning and Development Economics in India"),
                ],
            ),
            SubjectData(
                subject_name="Commerce",
                class_name="Class XII",
                class_number=12,
                subject_code="TN-12-COM",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Principles and Functions of Management"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Financial Markets & Capital Market"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Human Resource Management (Recruitment & Training)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Marketing & Consumer Protection Act"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Company Law, Secretarial Practice & Business Ethics"),
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
