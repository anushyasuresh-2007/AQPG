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
            SubjectData(
                subject_name="Mathematics Basic",
                class_name="Class X",
                class_number=10,
                subject_code="241",
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
                subject_name="Hindi Course A",
                class_name="Class X",
                class_number=10,
                subject_code="002",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Kshitij Bhag-2 (Kavya Khand)", topics=[
                        TopicData(topic_name="Surdas ke Pad"),
                        TopicData(topic_name="Tulsidas - Ram-Lakshman-Parshuram Samvad"),
                        TopicData(topic_name="Jaishankar Prasad - Aatmakathya"),
                        TopicData(topic_name="Suryakant Tripathi Nirala - Utsah, At Nahi Rahi Hai"),
                        TopicData(topic_name="Nagarjun - Yeh Danturit Muskan, Fasal"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Kshitij Bhag-2 (Gadya Khand)", topics=[
                        TopicData(topic_name="Netaji Ka Chashma (Swayam Prakash)"),
                        TopicData(topic_name="Balgobin Bhagat (Ramvriksh Benipuri)"),
                        TopicData(topic_name="Lakhnavi Andaz (Yashpal)"),
                        TopicData(topic_name="Ek Kahani Yeh Bhi (Mannu Bhandari)"),
                        TopicData(topic_name="Naubatkhane Mein Ibadat (Yatindra Mishra)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Kritika Bhag-2 (Purak Pathyapustak)", topics=[
                        TopicData(topic_name="Mata Ka Aanchal (Shivpujan Sahay)"),
                        TopicData(topic_name="Sana-Sana Hath Jodi (Madhu Kankariya)"),
                        TopicData(topic_name="Main Kyon Likhta Hun? (Agyeya)"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Vyakaran Evam Rachnatmak Lekhan", topics=[
                        TopicData(topic_name="Rachna ke Aadhar par Vakya Bhed"),
                        TopicData(topic_name="Vachya (Kartrivachya, Karmavachya, Bhavavachya)"),
                        TopicData(topic_name="Pad Parichay"),
                        TopicData(topic_name="Alankar (Shlesh, Utpreksha, Atishyokti, Manavikarana)"),
                        TopicData(topic_name="Anuched Lekhan, Patra Lekhan, Vigyapan Lekhan"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Hindi Course B",
                class_name="Class X",
                class_number=10,
                subject_code="085",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Sparsh Bhag-2 (Padya Khand)", topics=[
                        TopicData(topic_name="Kabir - Sakhi"),
                        TopicData(topic_name="Meera - Pad"),
                        TopicData(topic_name="Maithili Sharan Gupt - Manushyata"),
                        TopicData(topic_name="Sumitranandan Pant - Parvat Pradesh Mein Pavas"),
                        TopicData(topic_name="Viren Dangwal - Top"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Sparsh Bhag-2 (Gadya Khand)", topics=[
                        TopicData(topic_name="Bade Bhai Sahab (Premchand)"),
                        TopicData(topic_name="Diary Ka Ek Panna (Sitaram Seksaria)"),
                        TopicData(topic_name="Tatara-Vamiro Katha (Lila Dhar Mandloi)"),
                        TopicData(topic_name="Ab Kahan Doosre Ke Dukh Se Dukhi Hone Wale (Nida Fazli)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Sanchayan Bhag-2 (Purak Pathyapustak)", topics=[
                        TopicData(topic_name="Harihar Kaka (Mithileshwar)"),
                        TopicData(topic_name="Sapnon Ke Se Din (Gurdial Singh)"),
                        TopicData(topic_name="Topi Shukla (Rahi Masoom Raza)"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Vyakaran Evam Rachnatmak Lekhan", topics=[
                        TopicData(topic_name="Padbandh"),
                        TopicData(topic_name="Rachna ke aadhar par vakya roopantaran"),
                        TopicData(topic_name="Samas (Tatpurush, Karmadharaya, Dvigu, Dvandva, Bahuvrihi)"),
                        TopicData(topic_name="Muhavare"),
                        TopicData(topic_name="Anuched Lekhan, Vigyapan, Soochna Lekhan, Laghukatha"),
                    ]),
                ],
            ),
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
            SubjectData(
                subject_name="English Core",
                class_name="Class XII",
                class_number=12,
                subject_code="301",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Reading Skills (Unseen Passages & Case Studies)", topics=[
                        TopicData(topic_name="Discursive Passage (Inference & Vocabulary)"),
                        TopicData(topic_name="Case-Based Factual Passage (Data Interpretation)"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Creative Writing Skills", topics=[
                        TopicData(topic_name="Short Writing Tasks: Notice Writing"),
                        TopicData(topic_name="Formal and Informal Invitations & Replies"),
                        TopicData(topic_name="Letters: Application for a Job with Bio-Data"),
                        TopicData(topic_name="Letters: Letter to the Editor"),
                        TopicData(topic_name="Article and Report Writing"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Literature: Flamingo (Prose and Poetry)", topics=[
                        TopicData(topic_name="The Last Lesson (Alphonse Daudet)"),
                        TopicData(topic_name="Lost Spring (Anees Jung)"),
                        TopicData(topic_name="Deep Water (William Douglas)"),
                        TopicData(topic_name="The Rattrap (Selma Lagerlöf)"),
                        TopicData(topic_name="Indigo (Louis Fischer)"),
                        TopicData(topic_name="My Mother at Sixty-Six (Kamala Das)"),
                        TopicData(topic_name="Keeping Quiet (Pablo Neruda)"),
                        TopicData(topic_name="A Thing of Beauty (John Keats)"),
                        TopicData(topic_name="Aunt Jennifer's Tigers (Adrienne Rich)"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Supplementary Reader: Vistas", topics=[
                        TopicData(topic_name="The Third Level (Jack Finney)"),
                        TopicData(topic_name="The Tiger King (Kalki)"),
                        TopicData(topic_name="Journey to the End of the Earth (Tishani Doshi)"),
                        TopicData(topic_name="The Enemy (Pearl S. Buck)"),
                        TopicData(topic_name="On the Face of It (Susan Hill)"),
                        TopicData(topic_name="Memories of Childhood (Zitkala-Sa & Bama)"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Informatics Practices",
                class_name="Class XII",
                class_number=12,
                subject_code="065",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Data Handling using Pandas and Data Visualization", topics=[
                        TopicData(topic_name="Pandas Series and DataFrame Operations"),
                        TopicData(topic_name="Data Visualization using Pyplot (Line, Bar, Histogram)"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Database Query using SQL", topics=[
                        TopicData(topic_name="SQL Aggregate Functions (SUM, AVG, MIN, MAX, COUNT)"),
                        TopicData(topic_name="SQL Clauses (GROUP BY, HAVING, ORDER BY)"),
                        TopicData(topic_name="SQL Joins (Equi-Join, Natural Join)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Introduction to Computer Networks", topics=[
                        TopicData(topic_name="Network Topologies and Network Types (LAN, MAN, WAN)"),
                        TopicData(topic_name="Network Protocols (HTTP, FTP, TCP/IP, DNS)"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Societal Impacts", topics=[
                        TopicData(topic_name="Digital Footprints, Etiquette and Cyber Safety"),
                        TopicData(topic_name="Data Protection, Intellectual Property Rights and Cyber Law"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Applied Mathematics",
                class_name="Class XII",
                class_number=12,
                subject_code="241",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Numbers, Quantification and Numerical Applications"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Algebra (Matrices and Determinants)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Calculus (Differentiation, Integration and Applications)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Probability Distributions"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Inferential Statistics"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Index Numbers and Time-based Data"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Financial Mathematics (Perpetuity, Sinking Funds, EMI, CAGR)"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Linear Programming"),
                ],
            ),
            SubjectData(
                subject_name="History",
                class_name="Class XII",
                class_number=12,
                subject_code="027",
                stream_name="Arts",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Themes in Indian History Part I (Ancient History)", topics=[
                        TopicData(topic_name="The Harappan Civilisation (Bricks, Beads and Bones)"),
                        TopicData(topic_name="Early States and Economies (Kings, Farmers and Towns)"),
                        TopicData(topic_name="Early Societies (Kinship, Caste and Class)"),
                        TopicData(topic_name="Cultural Developments (Thinkers, Beliefs and Buildings)"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Themes in Indian History Part II (Medieval History)", topics=[
                        TopicData(topic_name="Through the Eyes of Travellers (Al-Biruni, Ibn Battuta, Bernier)"),
                        TopicData(topic_name="Bhakti-Sufi Traditions"),
                        TopicData(topic_name="An Imperial Capital: Vijayanagara"),
                        TopicData(topic_name="Peasants, Zamindars and the State (Agrarian Society & Mughal Empire)"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Themes in Indian History Part III (Modern History)", topics=[
                        TopicData(topic_name="Colonialism and the Countryside (Exploring Official Archives)"),
                        TopicData(topic_name="Rebels and the Raj (1857 Revolt and Representations)"),
                        TopicData(topic_name="Mahatma Gandhi and the Nationalist Movement (Civil Disobedience & Beyond)"),
                        TopicData(topic_name="Framing the Constitution (The Beginning of a New Era)"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Political Science",
                class_name="Class XII",
                class_number=12,
                subject_code="028",
                stream_name="Arts",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Contemporary World Politics", topics=[
                        TopicData(topic_name="The End of Bipolarity"),
                        TopicData(topic_name="Contemporary Centres of Power"),
                        TopicData(topic_name="Contemporary South Asia"),
                        TopicData(topic_name="International Organizations (UN and agencies)"),
                        TopicData(topic_name="Security in the Contemporary World"),
                        TopicData(topic_name="Environment and Natural Resources & Globalisation"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Politics in India Since Independence", topics=[
                        TopicData(topic_name="Challenges of Nation-Building"),
                        TopicData(topic_name="Era of One-Party Dominance & Planned Development"),
                        TopicData(topic_name="India's External Relations"),
                        TopicData(topic_name="Challenges to and Restoration of the Congress System"),
                        TopicData(topic_name="The Crisis of Democratic Order & Democratic Resurgence"),
                        TopicData(topic_name="Regional Aspirations & Recent Developments in Indian Politics"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Geography",
                class_name="Class XII",
                class_number=12,
                subject_code="029",
                stream_name="Arts",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Fundamentals of Human Geography", topics=[
                        TopicData(topic_name="Human Geography: Nature and Scope"),
                        TopicData(topic_name="The World Population: Distribution, Density and Growth"),
                        TopicData(topic_name="Human Development Concepts"),
                        TopicData(topic_name="Primary, Secondary, Tertiary and Quaternary Activities"),
                        TopicData(topic_name="Transport, Communication and International Trade"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - India: People and Economy", topics=[
                        TopicData(topic_name="Population: Distribution, Density, Growth and Composition"),
                        TopicData(topic_name="Human Settlements and Urbanisation"),
                        TopicData(topic_name="Land, Water, Mineral and Energy Resources of India"),
                        TopicData(topic_name="Planning and Sustainable Development in Indian Context"),
                    ]),
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
