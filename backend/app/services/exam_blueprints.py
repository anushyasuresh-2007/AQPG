"""
exam_blueprints.py
Authoritative board-specific examination blueprints and paper assembly validators
for CBSE and Tamil Nadu State Board (TNSB) (Classes 10 & 12).
"""

from typing import Dict, Any, List, Optional
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
}


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
    if raw_class is None:
        c_num = 10
    elif isinstance(raw_class, int):
        c_num = raw_class
    else:
        str_c = str(raw_class).lower()
        if "12" in str_c or "xii" in str_c:
            c_num = 12
        else:
            c_num = 10

    # Search by exact subject_code if provided
    if subject_code:
        key = f"{b_norm}-{c_num}-{subject_code.strip()}"
        if key in OFFICIAL_BLUEPRINTS:
            return OFFICIAL_BLUEPRINTS[key]

    # Search by subject_name matching
    if subject_name:
        s_lower = subject_name.lower().strip()
        for bp in OFFICIAL_BLUEPRINTS.values():
            if bp.board_code == b_norm and bp.class_number == c_num:
                if bp.subject_name.lower() == s_lower or s_lower in bp.subject_name.lower() or bp.subject_name.lower() in s_lower:
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
