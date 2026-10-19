"""
exam_blueprints.py
Authoritative board-specific examination blueprints and paper assembly validators
for CBSE and Tamil Nadu State Board (TNSB) (Classes 10 & 12).
"""

import math
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field


@dataclass
class BlueprintSection:
    section_name: str
    description: str
    question_type: str
    num_questions: int
    marks_per_question: int
    internal_choices: int = 0

    @property
    def total_marks(self) -> int:
        return self.num_questions * self.marks_per_question


@dataclass
class ExamBlueprint:
    board_code: str
    class_number: int
    subject_code: str
    subject_name: str
    academic_year: str
    total_marks: int
    duration_minutes: int
    sections: List[BlueprintSection]
    general_instructions: List[str] = field(default_factory=list)
    source_reference: str = ""

    def validate_totals(self) -> bool:
        sum_marks = sum(s.total_marks for s in self.sections)
        return sum_marks == self.total_marks


OFFICIAL_BLUEPRINTS: Dict[str, ExamBlueprint] = {
    # -------------------------------------------------------------------------
    # CBSE CLASS 10 (Secondary)
    # -------------------------------------------------------------------------
    "CBSE-10-041": ExamBlueprint(
        board_code="CBSE",
        class_number=10,
        subject_code="041",
        subject_name="Mathematics Standard",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A", "Multiple Choice Questions (including Assertion-Reason)", "MCQ", 20, 1),
            BlueprintSection("Section B", "Very Short Answer Type Questions", "Very Short Answer", 5, 2),
            BlueprintSection("Section C", "Short Answer Type Questions", "Short Answer", 6, 3),
            BlueprintSection("Section D", "Long Answer Type Questions", "Long Answer", 4, 5),
            BlueprintSection("Section E", "Case-Based Integrated Assessment Units", "Case-based", 3, 4),
        ],
        general_instructions=[
            "This question paper consists of 38 questions in 5 Sections.",
            "All Questions are compulsory. However, internal choices are provided in some questions.",
            "Section A consists of 20 Multiple Choice Questions carrying 1 mark each.",
            "Section B consists of 5 Very Short Answer questions carrying 2 marks each.",
            "Section C consists of 6 Short Answer questions carrying 3 marks each.",
            "Section D consists of 4 Long Answer questions carrying 5 marks each.",
            "Section E consists of 3 Case-Based integrated units of assessment (4 marks each).",
            "Use of calculators is not permitted.",
        ],
        source_reference="CBSE Academic Curriculum & Class X Sample Question Papers (SQP 2026-27)",
    ),
    "CBSE-10-086": ExamBlueprint(
        board_code="CBSE",
        class_number=10,
        subject_code="086",
        subject_name="Science",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A", "Objective Type & Assertion-Reasoning", "MCQ", 20, 1),
            BlueprintSection("Section B", "Very Short Answer Questions", "Very Short Answer", 6, 2),
            BlueprintSection("Section C", "Short Answer Questions", "Short Answer", 7, 3),
            BlueprintSection("Section D", "Long Answer Questions", "Long Answer", 3, 5),
            BlueprintSection("Section E", "Case-Based / Data-Based Assessment", "Case-based", 3, 4),
        ],
        general_instructions=[
            "This question paper consists of 39 questions in 5 sections.",
            "Section A comprises 20 objective type questions of 1 mark each.",
            "Section B comprises 6 Very Short questions of 2 marks each.",
            "Section C comprises 7 Short Answer questions of 3 marks each.",
            "Section D comprises 3 Long Answer questions of 5 marks each.",
            "Section E comprises 3 source-based/case-based units of 4 marks each.",
        ],
        source_reference="CBSE Class X Science SQP & Curriculum 2026-27",
    ),
    "CBSE-10-087": ExamBlueprint(
        board_code="CBSE",
        class_number=10,
        subject_code="087",
        subject_name="Social Science",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Section B", "Very Short Answer Type Questions", "Very Short Answer", 4, 2),
            BlueprintSection("Section C", "Short Answer Type Questions", "Short Answer", 5, 3),
            BlueprintSection("Section D", "Long Answer Type Questions", "Long Answer", 4, 5),
            BlueprintSection("Section E", "Case-Based Questions", "Case-based", 3, 4),
            BlueprintSection("Section F", "Map Skill Based Question", "Map-based", 1, 5),
        ],
        general_instructions=[
            "Question paper comprises six Sections – A, B, C, D, E and F with 37 questions.",
            "Section A: Questions 1 to 20 are MCQs of 1 mark each.",
            "Section B: Questions 21 to 24 are Very Short Answer questions carrying 2 marks each.",
            "Section C: Questions 25 to 29 are Short Answer questions carrying 3 marks each.",
            "Section D: Questions 30 to 33 are Long Answer questions carrying 5 marks each.",
            "Section E: Questions 34 to 36 are Case Based Questions with sub-questions (4 marks each).",
            "Section F: Question 37 is Map Skill based with two parts: 37a History (2 marks) and 37b Geography (3 marks).",
        ],
        source_reference="CBSE Class X Social Science SQP & Curriculum 2026-27",
    ),
    "CBSE-10-184": ExamBlueprint(
        board_code="CBSE",
        class_number=10,
        subject_code="184",
        subject_name="English Language and Literature",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A: Reading Skills", "Unseen Discursive & Case-based Passages", "Comprehension", 20, 1),
            BlueprintSection("Section B: Writing Skills & Grammar", "Grammar Transformations & Creative Writing Tasks", "Writing Task", 4, 5),
            BlueprintSection("Section C: Literature Textbooks", "First Flight & Footprints Without Feet Questions", "Short Answer", 8, 3),
            BlueprintSection("Section C: Long Literature", "Long Analytical/Theme Based Answers", "Long Answer", 4, 4),
        ],
        general_instructions=[
            "This paper is divided into three sections: Section A: Reading (20 marks), Section B: Writing & Grammar (20 marks), Section C: Literature (40 marks).",
            "All questions are compulsory. Follow prescribed word limits strictly.",
        ],
        source_reference="CBSE Class X English Language and Literature Curriculum 2026-27",
    ),
    "CBSE-10-402": ExamBlueprint(
        board_code="CBSE",
        class_number=10,
        subject_code="402",
        subject_name="Information Technology",
        academic_year="2026-27",
        total_marks=50,
        duration_minutes=120,
        sections=[
            BlueprintSection("Section A: Objective Type", "Employability and Subject Skills (MCQ, Fill in blanks, Direct)", "Objective", 24, 1),
            BlueprintSection("Section B: Short Answer", "Employability and Subject Specific Skills Short Answers", "Short Answer", 7, 2),
            BlueprintSection("Section B: Long Answer", "Subject Specific Competency and Application Questions", "Long Answer", 3, 4),
        ],
        general_instructions=[
            "Please read the instructions carefully.",
            "This question paper consists of 21 questions in two sections: Section A & Section B.",
            "Section A has Objective type questions (24 marks) with sub-questions of 1 mark each.",
            "Section B has Subjective type questions (26 marks): Short Answer (2 marks) and Long Answer (4 marks).",
            "Out of 21 questions, candidates must answer 15 questions in 2 hours.",
        ],
        source_reference="CBSE Department of Skill Education, Class X Information Technology (Subject Code 402) Blueprint 2026-27",
    ),

    # -------------------------------------------------------------------------
    # CBSE CLASS 12 (Senior Secondary)
    # -------------------------------------------------------------------------
    "CBSE-12-301": ExamBlueprint(
        board_code="CBSE",
        class_number=12,
        subject_code="301",
        subject_name="English Core",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A: Reading Skills", "Reading Comprehension Passages", "Comprehension", 22, 1),
            BlueprintSection("Section B: Creative Writing Skills", "Notices, Invitations, Letters & Articles/Reports", "Writing Task", 4, 4.5), # 18 marks total
            BlueprintSection("Section C: Literature Textbooks", "Flamingo & Vistas Reference to Context & Questions", "Short Answer", 10, 4),
        ],
        general_instructions=[
            "The question paper contains three sections: Reading (22 marks), Creative Writing (18 marks), Literature (40 marks).",
            "Adhere to word limits and neat presentation.",
        ],
        source_reference="CBSE Class XII English Core Curriculum 2026-27",
    ),
    "CBSE-12-041": ExamBlueprint(
        board_code="CBSE",
        class_number=12,
        subject_code="041",
        subject_name="Mathematics",
        academic_year="2026-27",
        total_marks=80,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Section B", "Very Short Answer Questions", "Very Short Answer", 5, 2),
            BlueprintSection("Section C", "Short Answer Questions", "Short Answer", 6, 3),
            BlueprintSection("Section D", "Long Answer Questions", "Long Answer", 4, 5),
            BlueprintSection("Section E", "Case-Based Integrated Assessments", "Case-based", 3, 4),
        ],
        general_instructions=[
            "This question paper contains 38 questions across 5 sections.",
            "Section A: 20 MCQs (1 mark each). Section B: 5 VSA (2 marks each).",
            "Section C: 6 SA (3 marks each). Section D: 4 LA (5 marks each).",
            "Section E: 3 Case Studies (4 marks each).",
        ],
        source_reference="CBSE Class XII Mathematics SQP & Curriculum 2026-27",
    ),
    "CBSE-12-042": ExamBlueprint(
        board_code="CBSE",
        class_number=12,
        subject_code="042",
        subject_name="Physics",
        academic_year="2026-27",
        total_marks=70,
        duration_minutes=180,
        sections=[
            BlueprintSection("Section A", "Multiple Choice Questions", "MCQ", 16, 1),
            BlueprintSection("Section B", "Short Answer Type-I Questions", "Very Short Answer", 5, 2),
            BlueprintSection("Section C", "Short Answer Type-II Questions", "Short Answer", 7, 3),
            BlueprintSection("Section D", "Case-Based Questions", "Case-based", 2, 4),
            BlueprintSection("Section E", "Long Answer Type Questions", "Long Answer", 3, 5),
        ],
        general_instructions=[
            "There are 33 questions in all. All questions are compulsory.",
            "Section A contains 16 questions of 1 mark each.",
            "Section B contains 5 questions of 2 marks each.",
            "Section C contains 7 questions of 3 marks each.",
            "Section D contains 2 case study questions of 4 marks each.",
            "Section E contains 3 long answer questions of 5 marks each.",
        ],
        source_reference="CBSE Class XII Physics SQP & Curriculum 2026-27",
    ),

    # -------------------------------------------------------------------------
    # TAMIL NADU STATE BOARD (TNSB) CLASS 10 (SSLC)
    # -------------------------------------------------------------------------
    "TNSB-10-MAT": ExamBlueprint(
        board_code="TNSB",
        class_number=10,
        subject_code="TN-10-MAT",
        subject_name="Mathematics",
        academic_year="2026-27",
        total_marks=100,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 14, 1),
            BlueprintSection("Part II", "2-Mark Short Answer Questions (Answer 10 out of 14)", "Short Answer", 10, 2),
            BlueprintSection("Part III", "5-Mark Problems & Theorems (Answer 10 out of 14)", "Medium Answer", 10, 5),
            BlueprintSection("Part IV", "8-Mark Practical Geometry & Graph Questions", "Long Answer", 2, 8),
        ],
        general_instructions=[
            "This question paper consists of four parts.",
            "Part I: 14 objective questions of 1 mark each.",
            "Part II: Answer 10 questions of 2 marks each (Question 28 is compulsory).",
            "Part III: Answer 10 questions of 5 marks each (Question 42 is compulsory).",
            "Part IV: Answer all questions choosing either of the alternatives (8 marks each).",
        ],
        source_reference="Tamil Nadu State Board SSLC Examination Model Question Pattern 2026-27",
    ),
    "TNSB-10-ENG": ExamBlueprint(
        board_code="TNSB",
        class_number=10,
        subject_code="TN-10-ENG",
        subject_name="English",
        academic_year="2026-27",
        total_marks=100,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Synonyms, Antonyms, Vocabulary & Grammar MCQs", "MCQ", 14, 1),
            BlueprintSection("Part II", "Prose, Poetry & Grammar Transformations", "Short Answer", 10, 2),
            BlueprintSection("Part III", "Prose Paragraphs, Poetry Quotes & Letter/Report Tasks", "Medium Answer", 10, 5),
            BlueprintSection("Part IV", "Supplementary Paragraph & Unseen Comprehension", "Long Answer", 2, 8),
        ],
        general_instructions=[
            "Part I: Choose the correct answer (Questions 1 to 14, 1 mark each).",
            "Part II: Answer 10 questions out of 14 (2 marks each).",
            "Part III: Answer 10 questions out of 14 (5 marks each).",
            "Part IV: Answer all questions (8 marks each).",
        ],
        source_reference="TNSCERT Class 10 General English Blueprint & Textbook 2026-27",
    ),
    "TNSB-10-SOC": ExamBlueprint(
        board_code="TNSB",
        class_number=10,
        subject_code="TN-10-SOC",
        subject_name="Social Science",
        academic_year="2026-27",
        total_marks=100,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 14, 1),
            BlueprintSection("Part II", "Short Answers across History, Geography, Civics, Economics", "Short Answer", 10, 2),
            BlueprintSection("Part III", "Detailed Explanations & Distinction Tables", "Medium Answer", 10, 5),
            BlueprintSection("Part IV", "Essay Questions & India/Tamil Nadu Map", "Long Answer", 2, 8),
        ],
        general_instructions=[
            "Answer all questions in Part I.",
            "Part II: Answer 10 questions (2 marks each; Q28 compulsory).",
            "Part III: Answer 10 questions (5 marks each; Q42 compulsory).",
            "Part IV: Answer questions of 8 marks each including Map drawing.",
        ],
        source_reference="TNSCERT Class 10 Social Science Blueprint 2026-27",
    ),
    # -------------------------------------------------------------------------
    # TAMIL NADU STATE BOARD (TNSB) CLASS 12 (Higher Secondary / +2)
    # -------------------------------------------------------------------------
    "TNSB-12-519": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="519",
        subject_name="Computer Science",
        academic_year="2026-27",
        total_marks=70,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 15, 1),
            BlueprintSection("Part II", "Short Answer Questions (Q24 Compulsory)", "Short Answer", 6, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q33 Compulsory)", "Short Answer", 6, 3),
            BlueprintSection("Part IV", "Either/Or Comprehensive Long Answer Questions", "Long Answer", 5, 5),
        ],
        general_instructions=[
            "Part I: Answer all 15 questions (1 mark each).",
            "Part II: Answer any 6 questions out of 9 (2 marks each; Question No. 24 is compulsory).",
            "Part III: Answer any 6 questions out of 9 (3 marks each; Question No. 33 is compulsory).",
            "Part IV: Answer all questions choosing either (a) or (b) (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Computer Science Blueprint & Curriculum 2026-27",
    ),
    "TNSB-12-541": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="541",
        subject_name="Mathematics",
        academic_year="2026-27",
        total_marks=90,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Part II", "Very Short Answer Questions (Q30 Compulsory)", "Very Short Answer", 7, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q40 Compulsory)", "Short Answer", 7, 3),
            BlueprintSection("Part IV", "Either/Or Long Answer Questions", "Long Answer", 7, 5),
        ],
        general_instructions=[
            "Part I: Answer all 20 questions (1 mark each).",
            "Part II: Answer any 7 questions out of 10 (2 marks each; Question No. 30 is compulsory).",
            "Part III: Answer any 7 questions out of 10 (3 marks each; Question No. 40 is compulsory).",
            "Part IV: Answer all questions choosing either (a) or (b) (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Mathematics Blueprint 2026-27",
    ),
    "TNSB-12-505": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="505",
        subject_name="Physics",
        academic_year="2026-27",
        total_marks=70,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 15, 1),
            BlueprintSection("Part II", "Short Answer Questions (Q24 Compulsory)", "Short Answer", 6, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q33 Compulsory)", "Short Answer", 6, 3),
            BlueprintSection("Part IV", "Either/Or Long Answer Questions", "Long Answer", 5, 5),
        ],
        general_instructions=[
            "Part I: Answer all 15 questions (1 mark each).",
            "Part II: Answer any 6 questions (2 marks each; Question No. 24 is compulsory).",
            "Part III: Answer any 6 questions (3 marks each; Question No. 33 is compulsory).",
            "Part IV: Answer all questions of either/or type (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Physics Blueprint 2026-27",
    ),
    "TNSB-12-507": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="507",
        subject_name="Chemistry",
        academic_year="2026-27",
        total_marks=70,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 15, 1),
            BlueprintSection("Part II", "Short Answer Questions (Q24 Compulsory)", "Short Answer", 6, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q33 Compulsory)", "Short Answer", 6, 3),
            BlueprintSection("Part IV", "Either/Or Long Answer Questions", "Long Answer", 5, 5),
        ],
        general_instructions=[
            "Part I: Answer all 15 questions (1 mark each).",
            "Part II: Answer any 6 questions (2 marks each; Question No. 24 is compulsory).",
            "Part III: Answer any 6 questions (3 marks each; Question No. 33 is compulsory).",
            "Part IV: Answer all questions of either/or type (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Chemistry Blueprint 2026-27",
    ),
    "TNSB-12-509": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="509",
        subject_name="Biology",
        academic_year="2026-27",
        total_marks=70,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions (Bio-Botany & Bio-Zoology)", "MCQ", 15, 1),
            BlueprintSection("Part II", "Short Answer Questions", "Short Answer", 6, 2),
            BlueprintSection("Part III", "Short Answer Questions", "Short Answer", 6, 3),
            BlueprintSection("Part IV", "Long Answer Explanations", "Long Answer", 5, 5),
        ],
        general_instructions=[
            "Question paper contains Section A (Bio-Botany, 35 marks) and Section B (Bio-Zoology, 35 marks).",
            "Total theory marks: 70 marks.",
        ],
        source_reference="TNSCERT Class 12 Biology Blueprint 2026-27",
    ),
    "TNSB-12-549": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="549",
        subject_name="Economics",
        academic_year="2026-27",
        total_marks=90,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Part II", "Very Short Answer Questions (Q30 Compulsory)", "Very Short Answer", 7, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q40 Compulsory)", "Short Answer", 7, 3),
            BlueprintSection("Part IV", "Either/Or Long Answer Questions", "Long Answer", 7, 5),
        ],
        general_instructions=[
            "Part I: Answer all 20 questions (1 mark each).",
            "Part II: Answer any 7 questions (2 marks each; Question No. 30 is compulsory).",
            "Part III: Answer any 7 questions (3 marks each; Question No. 40 is compulsory).",
            "Part IV: Answer all 7 either/or questions (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Economics Blueprint 2026-27",
    ),
    "TNSB-12-555": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="555",
        subject_name="Commerce",
        academic_year="2026-27",
        total_marks=90,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Part II", "Very Short Answer Questions (Q30 Compulsory)", "Very Short Answer", 7, 2),
            BlueprintSection("Part III", "Short Answer Questions (Q40 Compulsory)", "Short Answer", 7, 3),
            BlueprintSection("Part IV", "Either/Or Long Answer Questions", "Long Answer", 7, 5),
        ],
        general_instructions=[
            "Part I: Answer all 20 questions (1 mark each).",
            "Part II: Answer any 7 questions (2 marks each; Question No. 30 is compulsory).",
            "Part III: Answer any 7 questions (3 marks each; Question No. 40 is compulsory).",
            "Part IV: Answer all 7 either/or questions (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Commerce Blueprint 2026-27",
    ),
    "TNSB-12-557": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="557",
        subject_name="Accountancy",
        academic_year="2026-27",
        total_marks=90,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Multiple Choice Questions", "MCQ", 20, 1),
            BlueprintSection("Part II", "Very Short Answer & Simple Problems (Q30 Compulsory)", "Very Short Answer", 7, 2),
            BlueprintSection("Part III", "Short Answer Problems & Ledger Adjustments (Q40 Compulsory)", "Short Answer", 7, 3),
            BlueprintSection("Part IV", "Comprehensive Accounting Problems (Either/Or)", "Long Answer", 7, 5),
        ],
        general_instructions=[
            "Part I: Answer all 20 questions (1 mark each).",
            "Part II: Answer any 7 questions (2 marks each; Question No. 30 is compulsory).",
            "Part III: Answer any 7 questions (3 marks each; Question No. 40 is compulsory).",
            "Part IV: Answer all 7 either/or questions (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 Accountancy Blueprint 2026-27",
    ),
    "TNSB-12-003": ExamBlueprint(
        board_code="TNSB",
        class_number=12,
        subject_code="003",
        subject_name="English",
        academic_year="2026-27",
        total_marks=90,
        duration_minutes=180,
        sections=[
            BlueprintSection("Part I", "Synonyms, Antonyms & Grammar MCQs", "MCQ", 20, 1),
            BlueprintSection("Part II", "Poetry Appreciation & Grammar Transformations", "Very Short Answer", 7, 2),
            BlueprintSection("Part III", "Prose Reference to Context & Writing Tasks", "Short Answer", 7, 3),
            BlueprintSection("Part IV", "Paragraph Essays & Supplementary Comprehension", "Long Answer", 7, 5),
        ],
        general_instructions=[
            "Part I: Answer all 20 questions (1 mark each).",
            "Part II: Answer 7 questions (2 marks each).",
            "Part III: Answer 7 questions (3 marks each).",
            "Part IV: Answer 7 questions of either/or type (5 marks each).",
        ],
        source_reference="TNSCERT Class 12 General English Blueprint 2026-27",
    ),
}

# Aliases for official TNSB DGE Subject Codes (Class 10 SSLC)
OFFICIAL_BLUEPRINTS["TNSB-10-003"] = OFFICIAL_BLUEPRINTS["TNSB-10-MAT"]
OFFICIAL_BLUEPRINTS["TNSB-10-002"] = OFFICIAL_BLUEPRINTS["TNSB-10-ENG"]
OFFICIAL_BLUEPRINTS["TNSB-10-005"] = OFFICIAL_BLUEPRINTS["TNSB-10-SOC"]

# Aliases for official TNSB DGE Subject Codes (Class 12 Higher Secondary)
# Computer Science: official 519, shorthand 019, legacy TN-12-CS
OFFICIAL_BLUEPRINTS["TNSB-12-019"] = OFFICIAL_BLUEPRINTS["TNSB-12-519"]
OFFICIAL_BLUEPRINTS["TNSB-12-CS"] = OFFICIAL_BLUEPRINTS["TNSB-12-519"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-CS"] = OFFICIAL_BLUEPRINTS["TNSB-12-519"]

# Mathematics: official 541, shorthand 041, legacy TN-12-MAT
OFFICIAL_BLUEPRINTS["TNSB-12-041"] = OFFICIAL_BLUEPRINTS["TNSB-12-541"]
OFFICIAL_BLUEPRINTS["TNSB-12-MAT"] = OFFICIAL_BLUEPRINTS["TNSB-12-541"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-MAT"] = OFFICIAL_BLUEPRINTS["TNSB-12-541"]

# Physics: official 505, shorthand 005, legacy TN-12-PHY
OFFICIAL_BLUEPRINTS["TNSB-12-005"] = OFFICIAL_BLUEPRINTS["TNSB-12-505"]
OFFICIAL_BLUEPRINTS["TNSB-12-PHY"] = OFFICIAL_BLUEPRINTS["TNSB-12-505"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-PHY"] = OFFICIAL_BLUEPRINTS["TNSB-12-505"]

# Chemistry: official 507, shorthand 007, legacy TN-12-CHEM
OFFICIAL_BLUEPRINTS["TNSB-12-007"] = OFFICIAL_BLUEPRINTS["TNSB-12-507"]
OFFICIAL_BLUEPRINTS["TNSB-12-CHEM"] = OFFICIAL_BLUEPRINTS["TNSB-12-507"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-CHEM"] = OFFICIAL_BLUEPRINTS["TNSB-12-507"]

# Biology: official 509, shorthand 009, legacy TN-12-BIO
OFFICIAL_BLUEPRINTS["TNSB-12-009"] = OFFICIAL_BLUEPRINTS["TNSB-12-509"]
OFFICIAL_BLUEPRINTS["TNSB-12-BIO"] = OFFICIAL_BLUEPRINTS["TNSB-12-509"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-BIO"] = OFFICIAL_BLUEPRINTS["TNSB-12-509"]

# Economics: official 549, legacy TN-12-ECO
OFFICIAL_BLUEPRINTS["TNSB-12-ECO"] = OFFICIAL_BLUEPRINTS["TNSB-12-549"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-ECO"] = OFFICIAL_BLUEPRINTS["TNSB-12-549"]

# Commerce: official 555, legacy TN-12-COM
OFFICIAL_BLUEPRINTS["TNSB-12-COM"] = OFFICIAL_BLUEPRINTS["TNSB-12-555"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-COM"] = OFFICIAL_BLUEPRINTS["TNSB-12-555"]

# Accountancy: official 557, legacy TN-12-ACC
OFFICIAL_BLUEPRINTS["TNSB-12-ACC"] = OFFICIAL_BLUEPRINTS["TNSB-12-557"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-ACC"] = OFFICIAL_BLUEPRINTS["TNSB-12-557"]

# English: official 003, legacy TN-12-ENG
OFFICIAL_BLUEPRINTS["TNSB-12-ENG"] = OFFICIAL_BLUEPRINTS["TNSB-12-003"]
OFFICIAL_BLUEPRINTS["TNSB-12-TN-12-ENG"] = OFFICIAL_BLUEPRINTS["TNSB-12-003"]


SUBJECT_CANONICAL_DOMAINS = {
    # Mathematics
    "mathematics": "mathematics",
    "maths": "mathematics",
    "math": "mathematics",
    "standard mathematics": "mathematics",
    "mathematics standard": "mathematics",
    "basic mathematics": "mathematics",
    "mathematics basic": "mathematics",

    # Computer Science
    "computer science": "computer_science",
    "computer": "computer_science",
    "cs": "computer_science",
    "comp sci": "computer_science",
    "information technology": "computer_science",
    "it": "computer_science",

    # Physics
    "physics": "physics",
    "phy": "physics",

    # Chemistry
    "chemistry": "chemistry",
    "chem": "chemistry",

    # Biology / Life Sciences
    "biology": "biology",
    "bio": "biology",
    "bio botany": "biology",
    "bio zoology": "biology",
    "botany": "biology",
    "zoology": "biology",

    # General Science (Secondary Class 10 Science)
    "science": "science",
    "general science": "science",
    "sci": "science",

    # Social Science
    "social science": "social_science",
    "social studies": "social_science",
    "social": "social_science",
    "soc": "social_science",

    # English
    "english": "english",
    "general english": "english",
    "english core": "english",
    "english language and literature": "english",
    "english communicative": "english",
    "eng": "english",

    # Economics
    "economics": "economics",
    "eco": "economics",

    # Commerce / Business Studies
    "commerce": "commerce",
    "business studies": "commerce",
    "com": "commerce",

    # Accountancy
    "accountancy": "accountancy",
    "accounts": "accountancy",
    "acc": "accountancy",

    # Languages
    "tamil": "tamil",
    "hindi": "hindi",
}


def _normalize_subject_string(text: str) -> str:
    if not text:
        return ""
    import re
    t = text.lower().strip()
    t = re.sub(r"\b(class\s*\d+|xii|x|cbse|tnsb|tn|std\s*\d+)\b", " ", t)
    t = re.sub(r"[^\w\s]", " ", t)
    return " ".join(t.split())


def _are_subjects_compatible(name_a: str, name_b: str) -> bool:
    """Check whether two subject names are semantically compatible.

    Prevents false matches from substring collisions:
    - 'cs' inside 'mathematics'
    - 'science' inside 'social science'
    """
    if not name_a or not name_b:
        return False
    norm_a = _normalize_subject_string(name_a)
    norm_b = _normalize_subject_string(name_b)
    if not norm_a or not norm_b:
        return False
    if norm_a == norm_b:
        return True

    dom_a = SUBJECT_CANONICAL_DOMAINS.get(norm_a)
    dom_b = SUBJECT_CANONICAL_DOMAINS.get(norm_b)
    if dom_a and dom_b:
        return dom_a == dom_b
    if dom_a and not dom_b:
        return any(norm_b == k for k, v in SUBJECT_CANONICAL_DOMAINS.items() if v == dom_a)
    if dom_b and not dom_a:
        return any(norm_a == k for k, v in SUBJECT_CANONICAL_DOMAINS.items() if v == dom_b)

    tokens_a = set(norm_a.split())
    tokens_b = set(norm_b.split())
    return tokens_a == tokens_b


def get_exam_blueprint(
    board_code: str,
    class_number: Optional[Any] = None,
    subject_code: Optional[str] = None,
    subject_name: Optional[str] = None,
    class_name: Optional[Any] = None,
) -> Optional[ExamBlueprint]:
    """Retrieve verified examination blueprint for board, class, and subject."""
    b_norm = (board_code or "CBSE").upper().strip()
    raw_class = class_number if class_number is not None else class_name
    c_num: Optional[int] = None
    if raw_class is not None:
        if isinstance(raw_class, int):
            c_num = raw_class
        else:
            str_c = str(raw_class).lower()
            if "12" in str_c or "xii" in str_c:
                c_num = 12
            elif "10" in str_c or "x" in str_c:
                c_num = 10

    clean_code = subject_code.strip().upper() if subject_code else ""

    # When class context is missing, attempt unambiguous deduction from code or subject
    if c_num is None:
        if "12" in clean_code or "-12-" in clean_code or "XII" in clean_code:
            c_num = 12
        elif "10" in clean_code or "-10-" in clean_code or "-X-" in clean_code:
            c_num = 10
        elif b_norm == "TNSB" and clean_code in ("505", "507", "509", "519", "541", "549", "555", "557", "019", "041", "007", "009"):
            c_num = 12
        elif b_norm == "TNSB" and clean_code in ("002", "004"):
            c_num = 10
        elif b_norm == "CBSE" and clean_code in ("042", "043", "044", "083", "301"):
            c_num = 12
        elif b_norm == "CBSE" and clean_code in ("086", "087", "184", "402"):
            c_num = 10
        elif clean_code in ("003", "3", "03"):
            # Dual-use code: Class 10 Math vs Class 12 English
            if subject_name:
                sn = subject_name.lower()
                if any(w in sn for w in ["math", "mat"]):
                    c_num = 10
                elif any(w in sn for w in ["english", "eng"]):
                    c_num = 12
        elif clean_code in ("005", "5"):
            # Dual-use code: Class 10 Social Science vs Class 12 Physics
            if subject_name:
                sn = subject_name.lower()
                if any(w in sn for w in ["social", "soc"]):
                    c_num = 10
                elif any(w in sn for w in ["physic", "phy"]):
                    c_num = 12
        elif not clean_code and subject_name:
            sn = subject_name.lower()
            if any(w in sn for w in ["social", "soc"]):
                c_num = 10
            elif any(w in sn for w in ["physics", "chemistry", "biology", "computer science", "economics", "commerce", "accountancy"]):
                if b_norm == "TNSB":
                    c_num = 12

    # Do not silently default to Class 10 when class context is missing and ambiguous
    if c_num is None:
        return None

    # Search by exact or normalized subject_code if provided
    if clean_code:
        keys_to_try = [
            f"{b_norm}-{c_num}-{clean_code}",
            f"{b_norm}-{c_num}-{clean_code.split('-')[-1]}",
            clean_code,
        ]
        if b_norm == "TNSB":
            from app.services.curriculum.tn_board_importer import resolve_tnsb_subject_code
            resolved_code = resolve_tnsb_subject_code(clean_code, class_number=c_num, subject_name=subject_name)
            if resolved_code and resolved_code != clean_code:
                keys_to_try.extend([
                    f"TNSB-{c_num}-{resolved_code}",
                    resolved_code,
                ])
            elif not resolved_code:
                # Explicit conflict or unresolvable ambiguous code
                return None

        matched_bp = None
        for key in keys_to_try:
            if key in OFFICIAL_BLUEPRINTS:
                matched_bp = OFFICIAL_BLUEPRINTS[key]
                break

        if matched_bp:
            # If subject_name was also provided, reject conflicting code/name combinations
            if subject_name and not _are_subjects_compatible(subject_name, matched_bp.subject_name):
                return None
            return matched_bp

    # Search by subject_name matching
    if subject_name:
        for bp in OFFICIAL_BLUEPRINTS.values():
            if bp.board_code == b_norm and bp.class_number == c_num:
                if _are_subjects_compatible(subject_name, bp.subject_name):
                    return bp

    return None


def build_custom_paper_blueprint(
    board_code: str,
    class_name: str,
    subject_name: str,
    total_marks: int,
    target_questions_count: Optional[int] = None,
) -> ExamBlueprint:
    """
    Build a custom, pedagogically balanced examination blueprint when a teacher
    specifies custom total marks (e.g. 25, 40, 50, 60 marks).
    """
    tot = max(5, int(total_marks))
    duration_mins = max(30, min(180, round(tot * 2.25)))

    # Allocate balanced question distribution
    if tot <= 25:
        # Mini test / Unit test
        num_mcq = max(3, round(tot * 0.20))
        num_short = max(2, round(tot * 0.40 / 2))
        rem = tot - num_mcq - (num_short * 2)
        num_long = max(1, round(rem / 4)) if rem >= 4 else 0
        mcq_marks = tot - (num_short * 2) - (num_long * 4)

        sections = [
            BlueprintSection("Section A: Objective", "Foundational Concept MCQs", "MCQ", max(1, mcq_marks), 1),
            BlueprintSection("Section B: Short Answer", "Conceptual Reasoning & Calculations", "Short Answer", num_short, 2),
        ]
        if num_long > 0:
            sections.append(BlueprintSection("Section C: Descriptive", "Detailed Explanations & Applications", "Long Answer", num_long, 4))
    else:
        # Major examination / Term test
        num_mcq = max(5, round(tot * 0.20))
        num_vsa = max(3, round(tot * 0.20 / 2))
        num_sa = max(3, round(tot * 0.30 / 3))
        rem = tot - num_mcq - (num_vsa * 2) - (num_sa * 3)
        num_la = max(1, round(rem / 5)) if rem >= 5 else 0
        mcq_adj = tot - (num_vsa * 2) - (num_sa * 3) - (num_la * 5)

        sections = [
            BlueprintSection("Section A: Objective Type", "Multiple Choice & Objective Questions", "MCQ", max(1, mcq_adj), 1),
            BlueprintSection("Section B: Very Short Answer", "Direct Explanations & Formulas", "Very Short Answer", num_vsa, 2),
            BlueprintSection("Section C: Short Answer", "Structured Reasoning & Numericals", "Short Answer", num_sa, 3),
        ]
        if num_la > 0:
            sections.append(BlueprintSection("Section D: Long Answer", "Comprehensive Problem Solving & Analysis", "Long Answer", num_la, 5))

    c_str = str(class_name).lower()
    if "12" in c_str or "xii" in c_str:
        c_num = 12
    elif "10" in c_str or "x" in c_str:
        c_num = 10
    else:
        c_num = 12
    return ExamBlueprint(
        board_code=board_code.upper(),
        class_number=c_num,
        subject_code="CUSTOM",
        subject_name=subject_name,
        academic_year="2026-27",
        total_marks=tot,
        duration_minutes=duration_mins,
        sections=sections,
        general_instructions=[
            f"This custom examination paper carries a maximum of {tot} marks.",
            f"Allocated test duration: {duration_mins} minutes.",
            "All questions are compulsory unless internal choice is specified.",
        ],
        source_reference="Custom Examination Configuration",
    )


def get_allowed_marks_for_format(
    board: Optional[str] = None,
    class_name: Optional[Any] = None,
    subject_name: Optional[str] = None,
    subject_code: Optional[str] = None,
    max_marks_limit: Optional[int] = None,
    is_custom_assessment: bool = False,
) -> Tuple[int, int, Set[int]]:
    """
    Determine the supported (min_mark, max_mark, allowed_marks_set) for the given paper format.
    Respects authoritative official blueprints where available.

    In board-compliant mode (is_custom_assessment=False), requests cannot exceed official
    board format limits. max_marks_limit may only be used to specify a stricter ceiling,
    and attempting to exceed the official maximum raises a ValueError.

    In explicit custom assessment mode (is_custom_assessment=True), caller-configured
    max_marks_limit overrides board ceilings.
    """
    # 1. Determine official/standard blueprint boundaries
    bp = get_exam_blueprint(
        board_code=board or "CBSE",
        class_number=class_name,
        subject_code=subject_code,
        subject_name=subject_name,
    )
    if bp and bp.sections:
        section_marks = {int(math.ceil(s.marks_per_question)) for s in bp.sections if s.marks_per_question > 0}
        if section_marks:
            official_min = min(section_marks)
            official_max = max(section_marks)
            allowed_base_set = set(section_marks)
        else:
            official_min, official_max = 1, 5
            allowed_base_set = set(range(1, 6))
    else:
        # Paper-format rules when no exact blueprint is matched:
        b_norm = (board or "CBSE").upper().strip()
        c_str = str(class_name or "").lower()
        is_class_10 = "10" in c_str or "x" in c_str

        # Safe whole-word and normalized alias matching
        import re
        sn_low = (subject_name or "").lower().strip()
        words = set(re.findall(r"\b[a-z0-9]+\b", sn_low))
        norm_sn = _normalize_subject_string(subject_name)
        clean_code = (subject_code or "").strip().upper()

        is_it_subject = (
            "information technology" in norm_sn
            or "it" in words
            or clean_code in ("402", "IT")
        )
        is_cs_subject = (
            "computer science" in norm_sn
            or "computer" in words
            or "cs" in words
            or clean_code in ("083", "519", "019", "CS")
        )

        if b_norm == "CBSE" and is_class_10 and is_it_subject:
            # Official CBSE Class 10 Information Technology (402) blueprint
            official_min, official_max = 1, 4
            allowed_base_set = {1, 2, 4}
        elif b_norm == "TNSB" and is_class_10:
            # TNSB SSLC Class 10 permits 8-mark questions (e.g. geometry, essay, map)
            official_min, official_max = 1, 8
            allowed_base_set = set(range(1, 9))
        else:
            if any(w in sn_low for w in ["economic", "account", "business", "commerce"]):
                official_min, official_max = 1, 6
                allowed_base_set = set(range(1, 7))
            elif (
                any(w in sn_low for w in [
                    "math", "science", "physics", "chemistry", "biology", "english",
                    "social", "history", "geography", "civics", "political", "tamil", "hindi",
                    "informatics", "technology"
                ])
                or is_cs_subject
                or is_it_subject
            ):
                official_min, official_max = 1, 6
                allowed_base_set = set(range(1, 7))
            else:
                # Custom/unconstrained subjects without blueprint default to 10
                official_min, official_max = 1, 10
                allowed_base_set = set(range(1, 11))

    # 2. Handle custom-assessment mode vs board-compliant mode
    b_is_custom = (board or "").strip().upper() in ("CUSTOM", "OTHER")
    if is_custom_assessment or b_is_custom:
        # Custom-assessment mode: caller can configure any custom marks limit >= 1
        if max_marks_limit is not None and max_marks_limit >= 1:
            eff_min = min(1, official_min)
            return eff_min, max_marks_limit, set(range(eff_min, max_marks_limit + 1))
        return 1, 10, set(range(1, 11))

    # 3. Board-compliant mode: official board format limits are strictly enforced
    if max_marks_limit is not None and max_marks_limit >= 1:
        if max_marks_limit > official_max:
            format_name = f"{board or 'CBSE'} {class_name or ''} {subject_name or ''}".strip()
            raise ValueError(
                f"Requested max_marks_per_question ({max_marks_limit}) exceeds official {format_name} "
                f"limit ({official_max} marks). Board-compliant assessments cannot exceed official format limits. "
                f"Specify assessment_mode='custom' or is_custom_assessment=true to enable custom assessment overrides."
            )
        # Stricter ceiling allowed (e.g. quiz with max 3 marks under CBSE format)
        effective_max = min(max_marks_limit, official_max)
        allowed_set = {m for m in allowed_base_set if m <= effective_max}
        return official_min, effective_max, allowed_set

    return official_min, official_max, allowed_base_set


def validate_paper_allocation_feasibility(
    total_marks: int,
    bloom_distribution: Dict[str, int],
    number_of_questions: Optional[int] = None,
    min_allowed_mark: int = 1,
    max_allowed_mark: int = 6,
    format_description: str = "supported paper format",
    is_custom_assessment: bool = False,
) -> None:
    """
    Validate that total_marks, number_of_questions, Bloom distribution, and allowed marks per question
    form a feasible mathematical and pedagogical combination.
    Raises ValueError with a clear explanation if the combination is impossible.
    """
    if total_marks < 1:
        raise ValueError("total_marks must be at least 1")

    if not bloom_distribution:
        raise ValueError("bloom_distribution is required")

    active_blooms = {k: v for k, v in bloom_distribution.items() if v > 0}
    if sum(active_blooms.values()) != 100:
        raise ValueError("Bloom distribution percentages must total 100")

    if number_of_questions is None:
        return

    if number_of_questions < 1:
        raise ValueError("number_of_questions must be at least 1")

    # Overall marks boundaries
    min_possible_marks = number_of_questions * min_allowed_mark
    max_possible_marks = number_of_questions * max_allowed_mark

    if total_marks < min_possible_marks:
        raise ValueError(
            f"Impossible allocation: total_marks ({total_marks}) is less than the minimum required "
            f"({min_possible_marks} marks) for {number_of_questions} questions "
            f"(minimum {min_allowed_mark} mark per question in {format_description})."
        )

    if total_marks > max_possible_marks:
        raise ValueError(
            f"Impossible allocation: {total_marks} marks across {number_of_questions} questions exceeds the maximum "
            f"possible ({max_possible_marks} marks) for {format_description} "
            f"(maximum {max_allowed_mark} marks per question)."
        )

    # Per-Bloom distribution boundaries
    sum_pct = sum(active_blooms.values())
    raw_targets = []
    for b_name, pct in active_blooms.items():
        norm_pct = round((pct / sum_pct) * 100)
        raw_m = (norm_pct / 100.0) * total_marks
        int_m = int(raw_m)
        rem_m = raw_m - int_m
        raw_targets.append({"name": b_name, "marks": int_m, "rem": rem_m})

    shortage = total_marks - sum(t["marks"] for t in raw_targets)
    if shortage > 0:
        raw_targets.sort(key=lambda x: x["rem"], reverse=True)
        for i in range(shortage):
            raw_targets[i % len(raw_targets)]["marks"] += 1

    active_with_marks = [t for t in raw_targets if t["marks"] > 0]
    num_active_levels = len(active_with_marks)

    if number_of_questions < num_active_levels:
        raise ValueError(
            f"Impossible allocation: {number_of_questions} questions cannot satisfy {num_active_levels} "
            f"distinct Bloom taxonomy levels with non-zero allocation."
        )

    # In standard board assessments, simple recall ('Remember') questions are strictly limited to
    # at most 4 marks (MCQ, VSA, or SA). They cannot pedagogically receive 5 or more marks (Long Answer).
    level_max_map = {}
    for t in active_with_marks:
        if t["name"].lower() == "remember" and not is_custom_assessment:
            level_max_map[t["name"]] = min(max_allowed_mark, 4)
        else:
            level_max_map[t["name"]] = max_allowed_mark

    min_questions_needed = sum(math.ceil(t["marks"] / level_max_map[t["name"]]) for t in active_with_marks)
    max_questions_allowed = sum(t["marks"] // min_allowed_mark for t in active_with_marks)

    if number_of_questions < min_questions_needed:
        remember_target = next((t for t in active_with_marks if t["name"].lower() == "remember"), None)
        standard_min = sum(math.ceil(t["marks"] / max_allowed_mark) for t in active_with_marks)
        if remember_target and not is_custom_assessment and standard_min <= number_of_questions < min_questions_needed:
            rem_m = remember_target["marks"]
            raise ValueError(
                f"Impossible allocation: {number_of_questions} questions cannot satisfy the requested Bloom distribution "
                f"for {total_marks} marks. Foundational recall ('Remember') questions are allocated {rem_m} marks, "
                f"which cannot be satisfied without assigning 5 marks to a recall question (maximum 4 marks in {format_description}). "
                f"To resolve this conflict, please increase the question count to at least {min_questions_needed} questions, "
                f"reduce total marks, or adjust the Bloom distribution to assign higher weights to analytical levels (Apply, Analyze, Evaluate)."
            )
        raise ValueError(
            f"Impossible allocation: {number_of_questions} questions cannot satisfy the requested Bloom distribution "
            f"for {total_marks} marks under the format's limit of {max_allowed_mark} marks per question. "
            f"At least {min_questions_needed} questions are required."
        )

    if number_of_questions > max_questions_allowed:
        raise ValueError(
            f"Impossible allocation: {number_of_questions} questions exceeds the maximum question count "
            f"({max_questions_allowed}) possible with {total_marks} marks (minimum {min_allowed_mark} mark per question)."
        )
