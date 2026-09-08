"""Subject-specific prompt builder for pedagogical, curriculum-aligned question generation."""

from app.services.ai.base import AIQuestionPrompt


def build_subject_specific_system_prompt(prompt: AIQuestionPrompt) -> str:
    """Build deep, subject-specific pedagogical instructions."""
    subj = prompt.subject_name.lower()
    class_str = prompt.class_name.lower()

    # Determine age bracket
    try:
        class_num = int("".join([c for c in class_str if c.isdigit()]))
    except Exception:
        class_num = 10

    subject_guidelines = ""

    if "math" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: MATHEMATICS
- Prioritize numerical problem solving, step-by-step equation solutions, algebraic manipulation, and geometric reasoning.
- For Apply/Analyze: Provide concrete numerical values (e.g. "Solve 2x² - 5x + 2 = 0", "Find the sum of first 20 terms of AP: 3, 7, 11...").
- DO NOT generate purely trivial theory like "What is a quadratic equation?". Provide solvable mathematical problems.
- In 'answer', provide the complete step-by-step mathematical working and final value.
"""
    elif "physic" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: PHYSICS
- Prioritize formula application, numerical calculations with SI units, circuit analysis, optical ray parameters, and mechanics.
- Example: "A 5 kg object is accelerated from rest to 10 m/s in 5 seconds. Calculate the net force acting on it."
- For Apply/Analyze: Give explicit given parameters, formulas required, and unit conversions.
- In 'answer', provide the step-by-step derivation or numerical calculation with final units.
"""
    elif "chem" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: CHEMISTRY
- Prioritize balanced chemical equations, stoichiometry, mole calculations, organic reaction mechanisms, and acid-base equilibrium.
- Example: "Calculate the number of moles in 18 g of water" or "Write the balanced chemical equation for the reaction of iron with steam."
- In 'answer', provide balanced reactions, molecular masses, and chemical explanations.
"""
    elif "bio" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: BIOLOGY
- Prioritize physiological processes, genetics crosses (Mendelian ratios), anatomical functions, and assertion-reason relationships.
- For Apply/Analyze: Include real-life physiological scenarios or comparative structural analysis.
- In 'answer', provide key anatomical terms, pathways, and physiological rationale.
"""
    elif "computer" in subj or "information technology" in subj or "cs" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: COMPUTER SCIENCE / IT
- Prioritize programming questions (Python code snippets, output prediction, syntax error debugging, SQL queries, relational keys).
- In 'answer', provide exact code solutions, SQL query syntax, or line-by-line output trace.
"""
    elif "english" in subj or "language" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: ENGLISH / LANGUAGES
- Prioritize grammar applications, sentence transformations, vocabulary in context, reading comprehension, and structured writing tasks.
"""
    elif "social" in subj or "history" in subj or "geography" in subj or "civics" in subj or "economics" in subj:
        subject_guidelines = """
SUBJECT SPECIALIZATION: SOCIAL SCIENCE
- Prioritize source-based analytical questions, cause-and-effect reasoning, constitutional principles, economic development metrics (GDP, HDI), and geographical explanations.
"""
    else:
        subject_guidelines = """
SUBJECT SPECIALIZATION: GENERAL ACADEMICS
- Ensure rigorous, age-appropriate conceptual and application-based questions aligned with the syllabus unit.
"""

    age_guidelines = ""
    if class_num <= 5:
        age_guidelines = """
AGE LEVEL: PRIMARY (Class 1 to 5)
- Use simple, friendly vocabulary.
- Focus on real-life observation, daily activities, visual/concrete concepts, and basic numbers.
"""
    elif class_num <= 8:
        age_guidelines = """
AGE LEVEL: MIDDLE SCHOOL (Class 6 to 8)
- Focus on foundational principles, structured 2-to-3 step problems, and scientific terminology.
"""
    else:
        age_guidelines = """
AGE LEVEL: SECONDARY & SENIOR SECONDARY (Class 9 to 12)
- Strict adherence to official board standards.
- High rigor: include multi-step numericals, analytical derivations, case-study questions, and comprehensive explanations.
"""

    return f"""You are a master examination paper author and curriculum specialist for {prompt.board}.
{age_guidelines}
{subject_guidelines}

Generate a single examination question with the following specifications:
- Board: {prompt.board}
- Class: {prompt.class_name}
- Subject: {prompt.subject_name}
- Unit: {prompt.unit_name}
- Topic: {prompt.topic_name or 'General Unit Concept'}
- Marks: {prompt.marks}
- Difficulty: {prompt.difficulty.upper()}
- Bloom Taxonomy: {prompt.bloom_level}
- Target Question Type: {prompt.question_type}

Output MUST be a valid JSON object with EXACTLY these keys:
{{
  "question_text": "The complete, clear question text.",
  "question_type": "{prompt.question_type}",
  "marks": {prompt.marks},
  "difficulty": "{prompt.difficulty.lower()}",
  "bloom": "{prompt.bloom_level}",
  "answer": "Complete, correct model answer with step-by-step working where applicable.",
  "explanation": "Scoring rubric and pedagogical explanation.",
  "numerical_data": "Optional calculation details or null",
  "application_context": "Optional real-world context or null"
}}
Return ONLY raw JSON. No markdown backticks, no markdown formatting.
"""
