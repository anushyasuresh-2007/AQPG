"""Official Tamil Nadu State Board Curriculum Importer for Academic Sessions (e.g. 2026-27)."""

from typing import Dict, List, Optional

from app.services.curriculum.base import (
    BaseCurriculumImporter,
    BoardCurriculumData,
    SubjectData,
    TopicData,
    UnitData,
)

# Authoritative DGE Tamil Nadu Subject Code Mapping & Compatibility Aliases
TNSB_ALIAS_TO_OFFICIAL_MAP: Dict[str, str] = {
    # Class 12 Higher Secondary (+2) Official DGE 500-Series
    "TN-12-CS": "519",
    "019": "519",
    "519": "519",
    "TN-12-MAT": "541",
    "041": "541",
    "541": "541",
    "TN-12-PHY": "505",
    "505": "505",
    "TN-12-CHEM": "507",
    "007": "507",
    "507": "507",
    "TN-12-BIO": "509",
    "009": "509",
    "509": "509",
    "TN-12-ECO": "549",
    "549": "549",
    "TN-12-COM": "555",
    "555": "555",
    "TN-12-ACC": "557",
    "557": "557",
    "TN-12-ENG": "003",
    # Class 10 SSLC Official DGE Codes
    "TN-10-ENG": "002",
    "002": "002",
    "TN-10-MAT": "003",
    "TN-10-SCI": "004",
    "004": "004",
    "TN-10-SOC": "005",
}


def resolve_tnsb_subject_code(
    code: str,
    class_number: Optional[int] = None,
    subject_name: Optional[str] = None,
) -> str:
    """Resolve any legacy or shorthand TNSB subject code to its verified official DGE code."""
    if not code:
        return ""
    clean = code.strip().upper()

    # Conflicting check if both code and subject_name are provided
    if subject_name:
        s_low = subject_name.lower().strip()
        code_to_expected = {
            "505": "physic",
            "PHY": "physic",
            "507": "chem",
            "CHE": "chem",
            "CHEM": "chem",
            "509": "bio",
            "BIO": "bio",
            "519": "computer",
            "CS": "computer",
            "019": "computer",
            "541": "math",
            "MAT": "math",
            "041": "math",
            "549": "econom",
            "ECO": "econom",
            "555": "commerc",
            "COM": "commerc",
            "557": "account",
            "ACC": "account",
            "002": "eng",
            "ENG": "eng",
            "004": "sci",
            "SCI": "sci",
            "SOC": "social",
        }
        for prefix, expected_sub in code_to_expected.items():
            if clean in (prefix, f"TN-12-{prefix}", f"TN-10-{prefix}"):
                if not any(w in s_low for w in [expected_sub, "general", "core"]):
                    return ""  # Reject conflict

    # Handle dual-use codes with class_number disambiguation
    if clean in ("005", "5"):
        # In Class 12 shorthand, 005 was Physics (official 505). In Class 10, 005 is Social Science.
        if class_number == 12:
            if subject_name and not any(w in subject_name.lower() for w in ["physic", "phy"]):
                return ""  # Conflict: 005 in Class 12 is Physics, but given subject is not Physics
            return "505"
        if class_number == 10:
            if subject_name and not any(w in subject_name.lower() for w in ["social", "soc"]):
                return ""  # Conflict: 005 in Class 10 is Social Science
            return "005"
        if subject_name:
            sn_lower = subject_name.lower()
            if any(w in sn_lower for w in ["physic", "phy"]):
                return "505"
            if any(w in sn_lower for w in ["social", "soc"]):
                return "005"
        # If class_number is missing and subject_name does not disambiguate, it is ambiguous
        return ""

    if clean in ("003", "3", "03"):
        # 003 is official for both Class 10 Mathematics and Class 12 English
        if class_number == 10:
            if subject_name and not any(w in subject_name.lower() for w in ["math", "mat"]):
                return ""  # Conflict: 003 in Class 10 is Mathematics
            return "003"
        if class_number == 12:
            if subject_name and not any(w in subject_name.lower() for w in ["english", "eng"]):
                return ""  # Conflict: 003 in Class 12 is English
            return "003"
        if subject_name:
            sn_lower = subject_name.lower()
            if any(w in sn_lower for w in ["math", "mat"]):
                return "003"
            if any(w in sn_lower for w in ["english", "eng"]):
                return "003"
        # If neither class nor subject is provided, code 003 is ambiguous between Math and English
        return ""

    if clean in TNSB_ALIAS_TO_OFFICIAL_MAP:
        resolved = TNSB_ALIAS_TO_OFFICIAL_MAP[clean]
        # Class mismatch check (e.g. TN-10-MAT with class_number=12)
        if "TN-10-" in clean and class_number == 12:
            return ""
        if "TN-12-" in clean and class_number == 10:
            return ""
        return resolved

    return clean


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
        source_url = f"https://scert.tnschools.gov.in/curriculum_{academic_year.replace('-', '_')}"

        all_subjects: List[SubjectData] = [
            # =================================================================
            # CLASS 10 (SSLC)
            # =================================================================
            SubjectData(
                subject_name="Tamil",
                class_name="Class X",
                class_number=10,
                subject_code="001",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Iyal 1: Mozhi (Annai Mozhiye, Tamizhsollvalam, Ezhuthu Chol)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Iyal 2: Iyarkai, Ezhil (Kaatre Vaa, Mullaippaattu, Thogainilai)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Iyal 3: Panpaadu (Virundhu Potrudhum, Kaasi Kaandam, Thogaanilai)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Iyal 4: Ariviyal, Thozhilnutpam (Seyaarkai Nunnarivu, Podhu Ilakkanam)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Iyal 5: Kalvi (Mozhipeyarppu Kalvi, Needhivenba, Thiruvilaiyaadal)"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Iyal 6: Kalai, Ilakkiyam (Nigazhkalai, Muthukumaraswami Pillaithamizh)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Iyal 7: Naagareegam, Thozhil (Sittragal, Er Puthithu, Silappathikaram)"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Iyal 8: Aram, Thathuvam (Sanga Ilakkiyam, Kaala Kaniyan, Yaappu)"),
                    UnitData(unit_number=9, unit_name="Unit 9 - Iyal 9: Manitham (Thembavani, Oruvan Irukiraan, Ani Ilakkanam)"),
                ],
            ),
            SubjectData(
                subject_name="Science",
                class_name="Class X",
                class_number=10,
                subject_code="004",
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
                subject_code="003",
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
                subject_code="005",
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
                subject_code="002",
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
                subject_code="003",
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
                subject_code="505",
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
                subject_code="507",
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
                subject_code="541",
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
                subject_code="519",
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
                subject_code="509",
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
                subject_code="549",
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
                subject_code="555",
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
            SubjectData(
                subject_name="Accountancy",
                class_name="Class XII",
                class_number=12,
                subject_code="557",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Accounts from Incomplete Records", topics=[
                        TopicData(topic_name="Meaning and Features of Incomplete Records"),
                        TopicData(topic_name="Statement of Affairs Method"),
                        TopicData(topic_name="Ascertaining Missing Figures through Total Debtors and Creditors"),
                    ]),
                    UnitData(unit_number=2, unit_name="Unit 2 - Accounts of Not-for-Profit Organisation", topics=[
                        TopicData(topic_name="Receipts and Payments Account"),
                        TopicData(topic_name="Income and Expenditure Account"),
                        TopicData(topic_name="Preparation of Balance Sheet for Not-for-Profit Entities"),
                    ]),
                    UnitData(unit_number=3, unit_name="Unit 3 - Accounts of Partnership Firms - Fundamentals", topics=[
                        TopicData(topic_name="Partnership Deed and Rules Applicable in Absence of Deed"),
                        TopicData(topic_name="Fixed and Fluctuating Capital Methods"),
                        TopicData(topic_name="Interest on Capital, Drawings and P&L Appropriation Account"),
                    ]),
                    UnitData(unit_number=4, unit_name="Unit 4 - Goodwill in Partnership Accounts", topics=[
                        TopicData(topic_name="Nature and Factors Determining Goodwill"),
                        TopicData(topic_name="Average Profit and Super Profit Methods"),
                        TopicData(topic_name="Capitalisation Method"),
                    ]),
                    UnitData(unit_number=5, unit_name="Unit 5 - Admission of a Partner", topics=[
                        TopicData(topic_name="Revaluation of Assets and Liabilities"),
                        TopicData(topic_name="Distribution of Accumulated Profits, Losses and Reserves"),
                        TopicData(topic_name="New Profit Sharing Ratio and Sacrificing Ratio"),
                        TopicData(topic_name="Adjustment of Goodwill on Admission"),
                    ]),
                    UnitData(unit_number=6, unit_name="Unit 6 - Retirement and Death of a Partner", topics=[
                        TopicData(topic_name="Gaining Ratio and New Profit Sharing Ratio"),
                        TopicData(topic_name="Revaluation and Settlement of Account of Retiring Partner"),
                        TopicData(topic_name="Settlement of Deceased Partner's Dues"),
                    ]),
                    UnitData(unit_number=7, unit_name="Unit 7 - Company Accounts (Issue of Shares)", topics=[
                        TopicData(topic_name="Share Capital and Issue of Shares at Par and Premium"),
                        TopicData(topic_name="Calls in Arrears, Calls in Advance and Pro-rata Allotment"),
                        TopicData(topic_name="Forfeiture and Re-issue of Shares"),
                    ]),
                    UnitData(unit_number=8, unit_name="Unit 8 - Financial Statement Analysis", topics=[
                        TopicData(topic_name="Significance and Limitations of Financial Statements"),
                        TopicData(topic_name="Comparative Statements Preparation"),
                        TopicData(topic_name="Common Size Statements Preparation"),
                    ]),
                    UnitData(unit_number=9, unit_name="Unit 9 - Ratio Analysis", topics=[
                        TopicData(topic_name="Liquidity Ratios (Current and Quick Ratio)"),
                        TopicData(topic_name="Solvency and Turnover Ratios"),
                        TopicData(topic_name="Profitability Ratios (Gross and Net Profit)"),
                    ]),
                    UnitData(unit_number=10, unit_name="Unit 10 - Computerised Accounting System - Tally", topics=[
                        TopicData(topic_name="Applications of Computers in Accounting and CAS Architecture"),
                        TopicData(topic_name="Creating Company, Groups and Ledgers in Tally"),
                        TopicData(topic_name="Voucher Entry and Generating Financial Reports"),
                    ]),
                ],
            ),
            SubjectData(
                subject_name="Tamil",
                class_name="Class XII",
                class_number=12,
                subject_code="001",
                stream_name="General",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Iyal 1: Uyirin Uyiraana (Ilam Thamizhe, Thannervilaatha Thamizh, Seyyul Ezhuthu)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Iyal 2: Perumazhai Kaalam (Nedunalvaadai, Naalvagai Poruthangal)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Iyal 3: Panpaadu (Virundhinar Illam, Kambaramayanam, Porul Kol)"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Iyal 4: Kalvi (Pathukappu Enbathu Kalviye, Thirkadugam, Yaappu)"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Iyal 5: Naadu (Padhai Maariya Payanam, Thembavani, Thirukkural)"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Iyal 6: Kalai (Sirukadhaiyin Thotram, Thiraipada Kalai, Silappathikaram)"),
                    UnitData(unit_number=7, unit_name="Unit 7 - Iyal 7: Naagareegam (Puranaanuru, Ilakkanam)"),
                    UnitData(unit_number=8, unit_name="Unit 8 - Iyal 8: Arivu (Gnanam, Rakshanya Yathrigam, Kootrilakkanam)"),
                ],
            ),
            SubjectData(
                subject_name="Botany",
                class_name="Class XII",
                class_number=12,
                subject_code="511",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Asexual and Sexual Reproduction in Plants"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Classical Genetics & Chromosomal Basis of Inheritance"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Principles and Processes of Biotechnology & Plant Tissue Culture"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Principles of Ecology, Ecosystem & Environmental Issues"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Plant Breeding and Biologically Useful Plants"),
                ],
            ),
            SubjectData(
                subject_name="Zoology",
                class_name="Class XII",
                class_number=12,
                subject_code="513",
                stream_name="Science",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Reproduction in Organisms & Human Reproduction"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Reproductive Health & Principles of Inheritance"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Molecular Genetics & Evolution"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Human Health and Diseases & Microbes in Human Welfare"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Applications of Biotechnology"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Organisms and Populations, Biodiversity & Environmental Issues"),
                ],
            ),
            SubjectData(
                subject_name="Business Mathematics and Statistics",
                class_name="Class XII",
                class_number=12,
                subject_code="551",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Applications of Matrices and Determinants"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Integral Calculus & Applications of Integration"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Differential Equations & Numerical Methods"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Probability Distributions & Random Variables"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Sampling Techniques and Statistical Inference"),
                    UnitData(unit_number=6, unit_name="Unit 6 - Applied Statistics & Operations Research"),
                ],
            ),
            SubjectData(
                subject_name="Computer Applications",
                class_name="Class XII",
                class_number=12,
                subject_code="520",
                stream_name="Commerce",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Multimedia and Desktop Publishing (PageMaker)"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Database Management System (DBMS & SQL)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Introduction to PHP & Server-Side Scripting"),
                    UnitData(unit_number=4, unit_name="Unit 4 - PHP MySQL Database Integration"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Computer Networks, E-Commerce and Cyber Security"),
                ],
            ),
            SubjectData(
                subject_name="History",
                class_name="Class XII",
                class_number=12,
                subject_code="545",
                stream_name="Arts",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Rise of Nationalism in British India & Early Resistance"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Gandhian Era, Anti-Colonial Movements & Partition"),
                    UnitData(unit_number=3, unit_name="Unit 3 - Reconstruction of Post-Colonial India & Socio-Economic Order"),
                    UnitData(unit_number=4, unit_name="Unit 4 - World Wars, Decolonisation and Cold War"),
                    UnitData(unit_number=5, unit_name="Unit 5 - Imperialism and Contemporary World History"),
                ],
            ),
            SubjectData(
                subject_name="Political Science",
                class_name="Class XII",
                class_number=12,
                subject_code="547",
                stream_name="Arts",
                source_url=source_url,
                units=[
                    UnitData(unit_number=1, unit_name="Unit 1 - Constitution of India & Fundamental Rights"),
                    UnitData(unit_number=2, unit_name="Unit 2 - Union Government (Legislature & Executive)"),
                    UnitData(unit_number=3, unit_name="Unit 3 - State Government & Local Governments"),
                    UnitData(unit_number=4, unit_name="Unit 4 - Indian Judiciary & Judicial Review"),
                    UnitData(unit_number=5, unit_name="Unit 5 - India's Foreign Policy and International Relations"),
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
