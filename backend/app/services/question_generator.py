"""Service for assembling question papers via Question Bank first, AI hybrid generation, deduplication, and persistent storage."""

import datetime
import hashlib
import json
import random
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


from sqlalchemy.orm import Session

from app.models.academic_class import AcademicClass
from app.models.bloom import Bloom
from app.models.board import Board
from app.models.generated_paper import GeneratedPaper
from app.models.question import Question
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit
from app.services.ai.base import AIQuestionPrompt
from app.services.ai.generator_factory import get_ai_generator


def clean_generated_question_text(text: str) -> str:
    """Clean question text by stripping parenthetical metadata like (Unit 1 - AP), (Chapter 3), or (Variation 49)."""
    if not text:
        return ""
    cleaned = re.sub(r"\s*\([^)]*(?:unit|chapter|variation)[^)]*\)", "", text, flags=re.IGNORECASE)
    return cleaned.strip()


def normalize_text_for_comparison(text: str) -> str:
    """Normalize question text for similarity/duplicate checking."""
    text = clean_generated_question_text(text)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def compute_question_hash(text: str) -> str:
    """Compute deterministic MD5 hash for exact duplicate detection."""
    norm = normalize_text_for_comparison(text)
    return hashlib.md5(norm.encode("utf-8")).hexdigest()


def compute_structural_hash(text: str) -> str:
    """Compute structural hash by normalizing numeric constants to placeholders to detect template repetition."""
    norm = normalize_text_for_comparison(text)
    struct_norm = re.sub(r"\d+(\.\d+)?", "#NUM", norm)
    struct_norm = re.sub(r"[²³⁴⁵⁶⁷⁸⁹]", "^#NUM", struct_norm)
    return hashlib.md5(struct_norm.encode("utf-8")).hexdigest()


def is_near_duplicate(candidate_text: str, existing_texts: Iterable[str], threshold: float = 0.75) -> bool:
    """Detect whether candidate_text is identical or a near-duplicate of any existing question text.

    Identifies:
    1. Exact textual duplicates after normalization.
    2. Substring inclusions (such as generic contextual suffixes or prefix padding).
    3. High token-set overlap between candidate and prior questions.
    """
    if not candidate_text:
        return False
    c_norm = normalize_text_for_comparison(candidate_text)
    if not c_norm:
        return False

    STOP_WORDS = {
        "the", "a", "an", "and", "or", "of", "in", "to", "for", "with", "on", "at",
        "by", "from", "as", "is", "are", "was", "were", "that", "this", "it", "its",
        "their", "describe", "explain", "state", "define"
    }
    c_words = set(re.findall(r"\b[a-z]{3,}\b", c_norm)) - STOP_WORDS
    if not c_words:
        return False

    for existing in existing_texts:
        if not existing:
            continue
        e_norm = normalize_text_for_comparison(existing)
        if not e_norm:
            continue
        if c_norm == e_norm:
            return True
        # Direct substring containment for longer strings (detects appended suffixes)
        if len(c_norm) >= 25 and len(e_norm) >= 25:
            if c_norm in e_norm or e_norm in c_norm:
                return True
        e_words = set(re.findall(r"\b[a-z]{3,}\b", e_norm)) - STOP_WORDS
        if not e_words:
            continue
        common = len(c_words & e_words)
        min_len = min(len(c_words), len(e_words))
        if min_len > 0 and (common / min_len) >= threshold:
            return True
        union = len(c_words | e_words)
        if union > 0 and (common / union) >= 0.65:
            return True

    return False


def classify_unit_category(
    unit_name: str,
    unit_description: Optional[str] = None,
    topics_list: Optional[List[str]] = None,
) -> str:
    """Classify requested unit context into a canonical mathematics curriculum category."""
    context_items = [unit_name.lower()]
    if unit_description:
        context_items.append(unit_description.lower())
    if topics_list:
        context_items.extend([t.lower() for t in topics_list])

    ctx = " ".join(context_items)

    # Programming and Computer Science context guard - not a mathematics unit category
    if any(w in ctx for w in ["python", "computer science", "mysql", "programming", "sql", "code", "software"]):
        return "OTHER"

    # 1. Vectors & 3D Geometry
    if any(w in ctx for w in ["vector", "vectors", "three dimensional", "3d geometry", "direction cosines", "direction ratios"]):
        return "VECTORS_3D"

    # 2. Coordinate Geometry (check before generic geometry)
    if any(w in ctx for w in ["coordinate", "cartesian", "section formula", "distance formula", "collinear"]):
        return "COORDINATE_GEOMETRY"

    # 3. Relations and Functions (check before general trigonometry to properly categorize combined Unit 1 names like "Unit 1 - Relations and Functions & Inverse Trigonometry")
    if any(w in ctx for w in ["relation", "relations", "function", "functions", "bijective", "equivalence relation", "injective", "surjective", "domain and range", "inverse trig", "inverse trigonometric"]) or re.search(r"\b(sets?)\b", ctx):
        return "RELATIONS_FUNCTIONS"

    # 4. Trigonometry
    if any(w in ctx for w in ["trigonometry", "trigonometric", "heights and distances", "heights & distances", "elevation", "depression"]):
        return "TRIGONOMETRY"

    # 5. Statistics & Probability
    if any(w in ctx for w in ["statistic", "statistics", "probability", "frequency", "mean", "median", "mode", "ogive", "data handling"]):
        return "STATISTICS_PROBABILITY"

    # 6. Mensuration
    if any(w in ctx for w in ["mensuration", "surface area", "surface areas", "volume", "volumes", "sector", "segment of a circle", "area related to circles"]):
        return "MENSURATION"

    # 7. Numbers & Sequences / Real Numbers & AP & GP (use word boundaries so 'chapter', 'applications', 'shapes' do not trigger 'ap')
    num_terms = [
        "arithmetic progression", "real number", "real numbers",
        "number system", "number systems", "sequence", "sequences",
        "numbers and sequences", "geometric progression", "series", "hcf", "lcm",
        "euclid", "modular arithmetic", "prime factorization"
    ]
    if any(w in ctx for w in num_terms) or re.search(r"\b(ap|a\.p\.|g\.p\.)\b", ctx):
        return "NUMBERS_SEQUENCES"

    # 8. Pure Geometry / Circles / Triangles / Specific Geometric Theorems
    if any(w in ctx for w in ["geometry", "circle", "circles", "triangle", "triangles", "similarity", "similar triangles", "tangent", "basic proportionality theorem", "thales theorem", "pythagoras"]):
        return "GEOMETRY"

    # 8b. Matrices and Determinants
    if any(w in ctx for w in ["matrix", "matrices", "determinant", "determinants", "cramer", "rank of a matrix", "rank of matrix"]):
        if not any(w in ctx for w in ["quadratic", "quadratics", "polynomial", "polynomials"]):
            return "MATRICES_DETERMINANTS"

    # 9. Algebra / Quadratics / Polynomials / Linear Equations
    if any(w in ctx for w in ["quadratic", "quadratics", "polynomial", "polynomials", "algebra", "algebraic", "linear equation", "linear equations", "equation", "matrix", "matrices"]):
        return "ALGEBRA_QUADRATICS"

    # 10. Linear Programming
    if any(w in ctx for w in ["linear programming", "lpp", "feasible region", "objective function", "constraints", "corner points"]):
        return "LINEAR_PROGRAMMING"

    # 11. Calculus / Derivatives / Integrals
    if any(w in ctx for w in ["calculus", "differential", "derivative", "derivatives", "integral", "integrals", "continuity", "differentiability"]):
        return "CALCULUS"

    return "OTHER"


def get_question_signatures(question_text: str) -> Set[str]:
    """Detect domain/category signatures present in the question text."""
    q_lower = question_text.lower()
    signatures = set()

    # Quadratic / Pure Algebra signatures
    quad_terms = [
        "quadratic formula",
        "quadratic equation",
        "quadratic",
        "nature of roots",
        "b² - 4ac",
        "b^2 - 4ac",
        "b²-4ac",
        "discriminant",
        "equal roots",
        "real and equal roots",
        "zeroes of the polynomial",
        "zeros of the polynomial",
        "zeroes of polynomial",
        "zeros of polynomial",
        "zeroes of a polynomial",
        "zeros of a polynomial",
        "polynomial",
        "polynomials",
        "linear equation",
        "linear equations",
        "system of linear equations",
        "simultaneous equations",
        "two-digit number",
        "two digit number",
    ]
    if any(term in q_lower for term in quad_terms) or re.search(r"x[²^2]\s*[\+\-]\s*\d+x", q_lower) or re.search(r"solve.*x[²^2]", q_lower) or re.search(r"roots of.*x[²^2]", q_lower):
        signatures.add("ALGEBRA_QUADRATICS")

    # Matrices and Determinants signatures
    mat_terms = [
        "matrix", "matrices", "determinant", "determinants", "inverse of matrix",
        "matrix inversion", "adjoint", "identity matrix", "rank of a matrix", "rank of matrix",
        "row echelon", "cramer's rule", "singular matrix", "symmetric matrix", "skew-symmetric",
        "square matrices", "matrix multiplication", "elementary row operations"
    ]
    if any(term in q_lower for term in mat_terms) or re.search(r"\bdet\s*\(", q_lower) or re.search(r"\badj\s*\(", q_lower):
        signatures.add("MATRICES_DETERMINANTS")

    # Speed & Motion / River Boat signatures
    speed_terms = [
        "speed of the stream", "speed of stream", "motor boat", "motorboat",
        "upstream", "downstream", "still water"
    ]
    if any(term in q_lower for term in speed_terms):
        signatures.add("SPEED_DISTANCE")

    # Trigonometry signatures
    trig_terms = [
        "sin θ", "cos θ", "tan θ", "cot θ", "sec θ", "cosec θ",
        "sin(", "cos(", "tan(", "sin²", "cos²", "tan²",
        "angle of elevation", "angle of depression",
        "trigonometric", "height of tower", "height of chimney", "height of building"
    ]
    if any(term in q_lower for term in trig_terms):
        signatures.add("TRIGONOMETRY")

    # Coordinate Geometry signatures
    coord_terms = [
        "coordinate", "coordinates", "distance between the points",
        "section formula", "divides the line segment", "collinear",
        "midpoint of", "cartesian plane", "x-axis", "y-axis"
    ]
    if any(term in q_lower for term in coord_terms):
        signatures.add("COORDINATE_GEOMETRY")

    # Statistics & Probability signatures
    stats_terms = [
        "frequency distribution", "mean of", "median of", "mode of",
        "probability of", "die is thrown", "dice are thrown",
        "coin is tossed", "drawn at random"
    ]
    if any(term in q_lower for term in stats_terms):
        signatures.add("STATISTICS_PROBABILITY")

    # Mensuration signatures
    mens_terms = [
        "surface area", "curved surface area", "total surface area",
        "volume of", "cylinder", "cone", "sphere", "hemisphere",
        "frustum", "sector of a circle", "segment of a circle",
        "radius of base", "scooping out"
    ]
    if any(term in q_lower for term in mens_terms):
        signatures.add("MENSURATION")

    # Pure Geometry signatures
    geom_terms = [
        "basic proportionality theorem", "thales theorem", "pythagoras theorem",
        "tangent to a circle", "tangents drawn from", "concentric circles",
        "similar triangles", "ratio of areas of two similar triangles",
        "lengths of tangents", "chord of a circle", "angle subtended",
        "cyclic quadrilateral", "radius of the circle", "hypotenuse",
        "in a right triangle", "rhombus", "subtends an angle", "alternate segment theorem"
    ]
    if any(term in q_lower for term in geom_terms):
        signatures.add("GEOMETRY")

    # Vectors & 3D Geometry signatures
    vec_terms = [
        "vector", "vectors", "unit vector", "magnitude of vector",
        "dot product", "cross product", "scalar product", "vector product",
        "direction cosines", "direction ratios", "perpendicular vectors",
        "collinear vectors", "projection of vector", "angle between vectors",
        "vector equation", "cartesian equation of the line"
    ]
    if any(term in q_lower for term in vec_terms) or re.search(r"\bvec\b", q_lower) or re.search(r"\|\s*a\s*×\s*b\s*\|", q_lower):
        signatures.add("VECTORS_3D")

    # Numbers & Sequences signatures
    num_terms = [
        "arithmetic progression", "a.p.", "common difference",
        "n-th term", "nth term", "hcf and lcm", "hcf of", "lcm of",
        "prove that √", "is irrational", "is an irrational number",
        "geometric progression", "g.p.", "common ratio", "geometric series",
        "sum of first", "sum of the ap", "sum of an ap", "term of the ap", "term of an ap",
        "euclid's division", "euclid division", "euclid's lemma", "prime factorization", "prime factors",
        "modular arithmetic", "congruence", "general term of the sequence", "term of the sequence", "numbers and sequences"
    ]
    if any(term in q_lower for term in num_terms) or re.search(r"\ba_n\b", q_lower) or re.search(r"\bs_n\b", q_lower):
        signatures.add("NUMBERS_SEQUENCES")

    # Relations & Functions signatures
    rel_terms = [
        "relation r", "relation on", "relation in", "equivalence relation", "equivalence class",
        "reflexive", "symmetric", "transitive", "empty relation", "universal relation",
        "function f:", "function f", "function g", "functions f", "functions g", "f(x)", "g(x)", "h(x)",
        "injective", "surjective", "bijective", "one-one", "one to one", "many-one", "many to one",
        "onto", "into function", "one-one and onto", "identity function", "constant function", "mapping",
        "composition of functions", "composite function", "g o f", "f o g", "(g o f)", "(f o g)",
        "inverse function", "inverse of f", "f⁻¹", "f^-1", "invertible",
        "domain and range", "domain of", "codomain", "range of",
        "inverse trigonometric", "inverse trig", "principal value", "sin⁻¹", "cos⁻¹", "tan⁻¹", "sin^-1", "cos^-1", "tan^-1"
    ]
    if any(term in q_lower for term in rel_terms) or re.search(r"\bf\s*:\s*[a-z0-9_]+\s*->", q_lower) or re.search(r"\bf\s*\(\s*x\s*\)", q_lower):
        signatures.add("RELATIONS_FUNCTIONS")

    # Linear Programming signatures
    lp_terms = [
        "linear programming", "feasible region", "objective function",
        "corner point", "corner points", "maximize z", "minimize z",
        "bounded feasible", "optimal value", "constraints"
    ]
    if any(term in q_lower for term in lp_terms) or re.search(r"z\s*=\s*\d+x\s*\+\s*\d+y", q_lower):
        signatures.add("LINEAR_PROGRAMMING")

    # Calculus signatures
    calc_terms = [
        "dy/dx", "integral", "integrals", "derivative", "derivatives",
        "differentiate", "differential equation", "rate of change",
        "maxima and minima", "continuity", "differentiable", "indefinite integral",
        "definite integral", "evaluating the integral", "∫"
    ]
    if any(term in q_lower for term in calc_terms) or re.search(r"\bdy/dx\b", q_lower) or re.search(r"\bf'\s*\(\s*x\s*\)", q_lower):
        signatures.add("CALCULUS")

    return signatures


def validate_unit_relevance(
    question_text: str,
    unit_name: str,
    unit_description: Optional[str] = None,
    topics_list: Optional[List[str]] = None,
    subject_name: Optional[str] = None,
) -> bool:
    """Post-generation gate checking whether question text is topically related to assigned unit."""
    if not question_text or not question_text.strip():
        return False

    clean_q = clean_generated_question_text(question_text)
    if not clean_q:
        return False

    # Gate against generic placeholder question templates derived only from unit titles
    clean_q_lower = clean_q.lower()
    FORBIDDEN_GENERIC_PATTERNS = [
        r"\blist the main components and key terms\b",
        r"\bstate the foundational .*? governing\b",
        r"\bstate the foundational\b",
        r"\bdetailed academic explanation covering key\b",
        r"\bstate the central theme, poetic devices, or textual context\b",
        r"\bidentify the literary techniques and narrative perspectives\b",
        r"\bdefine the key vocabulary and grammatical rules\b",
        r"\bdefine\s+unit\s+\d+\b",
        r"\bmention any three key attributes or factors\b",
        r"\bname the primary classifications or categories\b",
        r"\bapply the core literary themes and character values\b",
        r"\bdemonstrate how the grammatical rules and stylistic structures\b",
        r"\bapply the learned methods of\b",
        r"\bshow how the theoretical rules of\b",
        r"\bformulate a practical implementation plan applying the techniques\b",
        r"\banalyze the psychological development, emotional conflicts\b",
        r"\bcompare and contrast the contrasting perspectives or cultural contexts\b",
        r"\bdeconstruct the symbolism, imagery, and structural motifs\b",
        r"\banalyze the advantages, limitations, and operational trade-offs\b",
        r"\bcritically evaluate the moral message and universal relevance\b",
        r"\bassess the effectiveness of the narrative resolution\b",
        r"\bevaluate the effectiveness and practical significance\b",
        r"\bexplain the central themes, character motivations, and narrative progression\b",
        r"\bdescribe how key conflicts in unit\b",
        r"\bexplain the core principles and concepts\b",
        r"\bdescribe the main processes and features associated with\b",
        r"\bdiscuss the operational principles and theoretical foundations\b",
        r"\boutline the functional lifecycle and primary behaviors\b",
        r"\bstructural architecture\b",
        r"\boptimization techniques\b",
        r"\bbroader theoretical systems\b",
        r"\btheoretical systems\b",
        r"\bhyperparameter optimization\b",
        r"\bgradient descent\b",
        r"\bturbofan\b",
        r"\baerodynamic performance\b",
        r"\bpropulsion systems?\b",
        r"\bvehicle routing\b",
        r"\bsystemic architecture\b",
        r"\barchitectural paradigms\b",
        r"\bunderlying theoretical frameworks\b",
        r"\bfoundational theoretical systems\b",
    ]
    if any(re.search(pat, clean_q_lower) for pat in FORBIDDEN_GENERIC_PATTERNS):
        return False

    search_context = [unit_name.lower()]
    if subject_name:
        search_context.append(subject_name.lower())
    if unit_description:
        search_context.append(unit_description.lower())
    if topics_list:
        search_context.extend([t.lower() for t in topics_list])
    context_str = " ".join(search_context)

    s_clean = (subject_name or "").lower()

    # Cross-domain leak prevention:
    # 1. Computer science / ML terminology leaking into non-CS subjects
    if not any(cs in s_clean for cs in ["computer", "informatics", "information technology", "programming", "python", "data"]):
        if any(term in clean_q_lower for term in [
            "hyperparameter", "gradient descent", "neural network", "backpropagation",
            "sql query", "select * from", "binary search tree", "sorting algorithm",
            "convolutional neural", "random forest", "support vector machine", "cross-entropy",
            "route optimization algorithms", "fleet management"
        ]):
            return False

    # 2. Aerospace / advanced mechanical engineering leaking into standard school subjects
    if any(term in clean_q_lower for term in [
        "turbofan", "aerodynamic performance", "propulsion system", "airfoil",
        "thrust-to-weight", "mach number", "computational fluid dynamics", "wind tunnel testing"
    ]):
        return False

    # 3. If subject is Language (English, Tamil, Hindi), reject mathematical formulas / chemistry / CS
    if any(lang in s_clean for lang in ["english", "tamil", "hindi", "language"]):
        if any(term in clean_q_lower for term in [
            "dy/dx", "matrix", "determinant", "sin θ", "cos θ", "tan θ",
            "quadratic equation", "polynomial", "stoichiometry", "titration",
            "newton's second law", "resistors in parallel"
        ]):
            return False

    # 4. If subject is Humanities (History, Political Science, Geography), reject pure math / coding
    if any(hum in s_clean for hum in ["history", "political", "geography"]):
        if any(term in clean_q_lower for term in [
            "dy/dx", "integral", "derivative", "algorithm", "python", "sql"
        ]):
            return False

    # Explicit non-mathematics subjects (Computer Science, Physics, Chemistry, etc.) are never gated by math signatures
    if subject_name and not any(
        m in s_clean
        for m in ["math", "algebra", "geometry", "calculus", "trigonometry", "statistic"]
    ):
        return True

    requested_category = classify_unit_category(unit_name, unit_description, topics_list)
    question_signatures = get_question_signatures(clean_q)

    # If question exhibits domain-specific mathematical signatures:
    if question_signatures:
        if requested_category != "OTHER":
            # The requested unit's category MUST match one of the detected question signatures
            is_matched = requested_category in question_signatures
            if not is_matched:
                if requested_category == "ALGEBRA_QUADRATICS" and "MATRICES_DETERMINANTS" in question_signatures and any(w in context_str for w in ["matrix", "matrices", "determinant"]):
                    is_matched = True
                elif requested_category == "MATRICES_DETERMINANTS" and "ALGEBRA_QUADRATICS" in question_signatures and any(w in context_str for w in ["algebra", "quadratic", "polynomial"]):
                    is_matched = True
            if not is_matched:
                return False
        else:
            # For unclassified units (OTHER), only enforce math exclusions if context indicates Mathematics
                if "ALGEBRA_QUADRATICS" in question_signatures and not any(w in context_str for w in ["quadratic", "algebra", "polynomial", "equation"]):
                    return False
                if "TRIGONOMETRY" in question_signatures and not any(w in context_str for w in ["trigonometry", "height", "distance", "triangle"]):
                    return False
                if "STATISTICS_PROBABILITY" in question_signatures and not any(w in context_str for w in ["statistic", "probability", "data", "frequency"]):
                    return False
                if "COORDINATE_GEOMETRY" in question_signatures and not any(w in context_str for w in ["coordinate", "cartesian"]):
                    return False
                if "MENSURATION" in question_signatures and not any(w in context_str for w in ["mensuration", "surface area", "volume"]):
                    return False
                if "MATRICES_DETERMINANTS" in question_signatures and not any(w in context_str for w in ["matrix", "matrices", "determinant", "rank"]):
                    return False
                if "VECTORS_3D" in question_signatures and not any(w in context_str for w in ["vector", "vectors", "three dimensional", "3d"]):
                    return False
                if "LINEAR_PROGRAMMING" in question_signatures and not any(w in context_str for w in ["linear programming", "lpp", "linear"]):
                    return False
                if "CALCULUS" in question_signatures and not any(w in context_str for w in ["calculus", "differential", "derivative", "integral"]):
                    return False

    return True


def _find_exact_question_subset(
    questions: List[Question],
    required_marks: int,
    preferred_difficulty: Optional[str] = None,
    target_count: Optional[int] = None,
) -> Optional[List[Question]]:
    """
    Combinatorial subset search: Find a subset of questions whose marks total exactly the target required marks.
    Prioritizes matching preferred difficulty and target count.
    """
    if required_marks <= 0:
        return []
    if not questions:
        return None

    def question_sort_key(q: Question):
        diff_score = 0
        if preferred_difficulty and q.difficulty.lower() == preferred_difficulty.lower():
            diff_score = 2
        elif q.difficulty.lower() == "medium":
            diff_score = 1
        return (diff_score, -q.marks, -q.id)

    ordered_questions = sorted(questions, key=question_sort_key, reverse=True)
    memo: Dict[Tuple[int, int], Optional[List[int]]] = {}

    def dfs(index: int, remaining_marks: int) -> Optional[List[int]]:
        if remaining_marks == 0:
            return []
        if index >= len(ordered_questions):
            return None

        key = (index, remaining_marks)
        if key in memo:
            return memo[key]

        question = ordered_questions[index]
        if question.marks <= remaining_marks:
            take_result = dfs(index + 1, remaining_marks - question.marks)
            if take_result is not None:
                res = [index] + take_result
                memo[key] = res
                return res

        skip_result = dfs(index + 1, remaining_marks)
        memo[key] = skip_result
        return skip_result

    selected_indexes = dfs(0, required_marks)
    if selected_indexes is None:
        return None

    return [ordered_questions[i] for i in selected_indexes]


def generate_question_paper(
    db: Session,
    subject_id: int,
    selected_units: List[int],
    total_marks: int,
    bloom_distribution: Dict[str, int],
    number_of_questions: Optional[int] = None,
    difficulty: Optional[str] = "medium",
    source_mode: Optional[str] = "hybrid",  # "bank", "ai", "hybrid"
    use_ai: Optional[bool] = None,
    user_id: Optional[int] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
    board_id: Optional[int] = None,
    class_id: Optional[int] = None,
    stream_id: Optional[int] = None,
    max_marks_per_question: Optional[int] = None,
    assessment_mode: Optional[str] = "board",
    is_custom_assessment: bool = False,
) -> Dict[str, Any]:
    """
    Generate an examination paper combining approved Question Bank content, AI hybrid synthesis,
    exact mark balancing, and persistent record storage.
    """
    if use_ai is True:
        source_mode = "ai"
    elif use_ai is False and source_mode == "ai":
        source_mode = "bank"

    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        raise ValueError("Subject not found")

    # Determine canonical subject board code
    subject_board_code = None
    if subject.board_id:
        try:
            from app.models.board import Board
            b_rec = db.query(Board).filter(Board.id == subject.board_id).first()
            if b_rec and getattr(b_rec, "board_code", None) and isinstance(b_rec.board_code, str):
                subject_board_code = b_rec.board_code.upper()
        except Exception:
            pass
    if not subject_board_code and subject.board and isinstance(subject.board, str):
        subject_board_code = subject.board.upper()

    # Determine requested board code
    requested_board_code = None
    if board_id:
        try:
            from app.models.board import Board
            req_b_rec = db.query(Board).filter(Board.id == board_id).first()
            if req_b_rec and getattr(req_b_rec, "board_code", None) and isinstance(req_b_rec.board_code, str):
                requested_board_code = req_b_rec.board_code.upper()
        except Exception:
            pass
    if not requested_board_code and board and isinstance(board, str):
        requested_board_code = board.upper()

    # Validate board compatibility
    if board_id and subject.board_id:
        if subject.board_id != board_id:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to board ID {board_id}")
    elif requested_board_code and subject_board_code:
        if requested_board_code != subject_board_code:
            raise ValueError(f"Subject '{subject.subject_name}' belongs to board '{subject_board_code}', not '{requested_board_code}'")
    elif board and subject.board and isinstance(subject.board, str) and subject.board.lower() != board.lower():
        raise ValueError(f"Subject '{subject.subject_name}' does not belong to board '{board}'")

    # Determine canonical subject class name
    subject_class_code = None
    if subject.class_id:
        try:
            from app.models.academic_class import AcademicClass
            c_rec = db.query(AcademicClass).filter(AcademicClass.id == subject.class_id).first()
            if c_rec and getattr(c_rec, "class_code", None) and isinstance(c_rec.class_code, str):
                subject_class_code = c_rec.class_code
        except Exception:
            pass
    if not subject_class_code and subject.class_name and isinstance(subject.class_name, str):
        subject_class_code = subject.class_name

    if class_id and subject.class_id:
        if subject.class_id != class_id:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to class ID {class_id}")
    elif class_name and subject_class_code:
        roman_map = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6", "vii": "7", "viii": "8", "ix": "9", "x": "10", "xi": "11", "xii": "12"}
        req_c = class_name.lower().replace("class", "").strip()
        sub_c = subject_class_code.lower().replace("class", "").strip()
        req_c = roman_map.get(req_c, req_c)
        sub_c = roman_map.get(sub_c, sub_c)
        if req_c != sub_c:
            raise ValueError(f"Subject '{subject.subject_name}' does not belong to class '{class_name}'")

    resolved_board = requested_board_code or subject_board_code or board or subject.board or "CBSE"
    resolved_class = class_name or subject_class_code or subject.class_name or "10"
    if not resolved_class.lower().startswith("class"):
        resolved_class = f"Class {resolved_class}"
    raw_acad = getattr(subject, "academic_year", "2026-27")
    resolved_academic_year = raw_acad if isinstance(raw_acad, str) and raw_acad else "2026-27"

    # Load syllabus units
    available_units = db.query(Unit).filter(Unit.subject_id == subject_id).all()
    unit_map = {u.id: u for u in available_units}

    if selected_units:
        unit_ids_to_use = [uid for uid in selected_units if uid in unit_map]
        if not unit_ids_to_use:
            raise ValueError("Selected units are invalid or do not belong to the selected subject")
    else:
        unit_ids_to_use = [u.id for u in available_units]


    unit_names_list = [unit_map[uid].unit_name for uid in unit_ids_to_use if uid in unit_map]
    unit_names_str = ", ".join(unit_names_list) if unit_names_list else "All Syllabus Units"

    # Validate Bloom distribution percentages
    active_bloom_inputs = {k: v for k, v in bloom_distribution.items() if v > 0}
    sum_bloom_pct = sum(active_bloom_inputs.values())
    if sum_bloom_pct != 100:
        raise ValueError("Bloom distribution percentages must total 100")


    bloom_records = db.query(Bloom).all()
    bloom_by_name = {b.level_name.lower(): b for b in bloom_records}

    targets = []
    for b_name, pct in active_bloom_inputs.items():
        matching_bloom = bloom_by_name.get(b_name.lower())
        if not matching_bloom:
            matching_bloom = Bloom(level_name=b_name)
            db.add(matching_bloom)
            db.flush()
            bloom_by_name[b_name.lower()] = matching_bloom

        norm_pct = round((pct / sum_bloom_pct) * 100)
        raw_marks = (norm_pct / 100.0) * total_marks
        integer_marks = int(raw_marks)
        remainder = raw_marks - integer_marks
        targets.append({
            "name": b_name,
            "matching_bloom": matching_bloom,
            "percentage": norm_pct,
            "allocated_marks": integer_marks,
            "remainder": remainder,
        })

    # Largest Remainder Method for exact total marks
    current_allocated = sum(t["allocated_marks"] for t in targets)
    marks_shortage = total_marks - current_allocated
    if marks_shortage > 0:
        targets_by_remainder = sorted(targets, key=lambda x: x["remainder"], reverse=True)
        for i in range(marks_shortage):
            targets_by_remainder[i % len(targets_by_remainder)]["allocated_marks"] += 1

    # Authoritative paper-format rules and marks allocation validation
    from app.services.exam_blueprints import (
        get_allowed_marks_for_format,
        validate_paper_allocation_feasibility,
    )
    is_custom = bool(
        is_custom_assessment
        or (assessment_mode and assessment_mode.strip().lower() == "custom")
        or (resolved_board and resolved_board.strip().upper() in ("CUSTOM", "OTHER"))
    )
    min_allowed_mark, max_allowed_mark, allowed_marks = get_allowed_marks_for_format(
        board=resolved_board,
        class_name=resolved_class,
        subject_name=subject.subject_name,
        subject_code=getattr(subject, "subject_code", None),
        max_marks_limit=max_marks_per_question,
        is_custom_assessment=is_custom,
    )
    format_desc = f"{'Custom' if is_custom else resolved_board} {resolved_class} {subject.subject_name} format"
    validate_paper_allocation_feasibility(
        total_marks=total_marks,
        bloom_distribution=bloom_distribution,
        number_of_questions=number_of_questions,
        min_allowed_mark=min_allowed_mark,
        max_allowed_mark=max_allowed_mark,
        format_description=format_desc,
    )

    selected_questions: List[Dict[str, Any]] = []
    used_question_hashes: Set[str] = set()
    used_structural_hashes: Set[str] = set()
    used_question_texts: Set[str] = set()
    used_question_ids: Set[int] = set()
    shortages: List[Dict[str, Any]] = []

    # Build curriculum context map for selected units
    unit_curriculum_context = {}
    for uid, u in unit_map.items():
        topics = db.query(Topic).filter(Topic.unit_id == u.id, Topic.active == True).order_by(Topic.topic_number.asc()).all()
        topic_names = [t.topic_name for t in topics]
        unit_curriculum_context[uid] = {
            "unit": u,
            "description": u.description or "",
            "topics": topic_names,
        }

    # =========================================================================
    # STEP 1: QUERY APPROVED QUESTION BANK (unless source_mode == 'ai')
    # =========================================================================
    if source_mode != "ai":
        raw_eligible_questions = (
            db.query(Question)
            .filter(Question.subject_id == subject_id)
            .filter(Question.unit_id.in_(unit_ids_to_use))
            .filter(Question.status == "approved")
            .filter(Question.active == True)
            .all()
        )

        cleaned_bank_text_map: Dict[int, str] = {}
        questions_by_bloom: Dict[int, List[Question]] = {}
        seen_bank_hashes: Set[str] = set()

        for q in raw_eligible_questions:
            q_unit = unit_map.get(q.unit_id)
            if not q_unit:
                continue

            u_ctx = unit_curriculum_context.get(q.unit_id, {})
            u_desc = u_ctx.get("description")
            u_topics = u_ctx.get("topics")

            clean_text = clean_generated_question_text(q.question_text)
            if not clean_text:
                continue

            # Validate that question text actually matches assigned unit's curriculum
            if not validate_unit_relevance(clean_text, q_unit.unit_name, u_desc, u_topics, subject.subject_name):
                continue

            q_h = compute_question_hash(clean_text)
            s_h = compute_structural_hash(clean_text)

            # Pre-filter exact and near duplicates within the bank candidate pool
            if (q_h in used_question_hashes) or (s_h in used_structural_hashes) or (q_h in seen_bank_hashes) or is_near_duplicate(clean_text, used_question_texts):
                continue

            seen_bank_hashes.add(q_h)
            cleaned_bank_text_map[q.id] = clean_text
            questions_by_bloom.setdefault(q.bloom_level_id, []).append(q)

        for target in targets:
            req_marks = target["allocated_marks"]
            bloom_obj = target["matching_bloom"]

            if req_marks <= 0:
                continue

            available_for_bloom = [
                q for q in questions_by_bloom.get(bloom_obj.id, [])
                if q.id not in used_question_ids
                and compute_question_hash(cleaned_bank_text_map.get(q.id, q.question_text)) not in used_question_hashes
            ]

            subset = _find_exact_question_subset(
                questions=available_for_bloom,
                required_marks=req_marks,
                preferred_difficulty=difficulty,
            )

            if subset is not None:
                for q in subset:
                    c_text = cleaned_bank_text_map.get(q.id, clean_generated_question_text(q.question_text))
                    q_h = compute_question_hash(c_text)
                    s_h = compute_structural_hash(c_text)
                    used_question_ids.add(q.id)
                    used_question_hashes.add(q_h)
                    used_structural_hashes.add(s_h)
                    used_question_texts.add(c_text)
                    selected_questions.append({
                        "question_id": q.id,
                        "question": c_text,
                        "marks": q.marks,
                        "bloom": bloom_obj.level_name,
                        "difficulty": q.difficulty,
                        "question_type": q.question_type or "Short Answer",
                        "unit_id": q.unit_id,
                        "unit_name": unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name,
                        "topic_name": (u_topics[0] if u_topics else unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name),
                        "board": resolved_board,
                        "class_name": resolved_class,
                        "academic_year": resolved_academic_year,
                        "subject": subject.subject_name,
                        "answer": q.answer,
                        "explanation": q.explanation,
                        "source": q.source or "Question Bank",
                        "source_reference": f"{resolved_board} Prescribed Curriculum",
                        "validation_status": "verified",
                    })
            else:
                # Calculate what subset or partial marks we can take
                partial_sum = 0
                partial_qs = []
                for q in sorted(available_for_bloom, key=lambda x: -x.marks):
                    if partial_sum + q.marks <= req_marks:
                        partial_sum += q.marks
                        partial_qs.append(q)

                for q in partial_qs:
                    c_text = cleaned_bank_text_map.get(q.id, clean_generated_question_text(q.question_text))
                    q_h = compute_question_hash(c_text)
                    s_h = compute_structural_hash(c_text)
                    used_question_ids.add(q.id)
                    used_question_hashes.add(q_h)
                    used_structural_hashes.add(s_h)
                    used_question_texts.add(c_text)
                    selected_questions.append({
                        "question_id": q.id,
                        "question": c_text,
                        "marks": q.marks,
                        "bloom": bloom_obj.level_name,
                        "difficulty": q.difficulty,
                        "question_type": q.question_type or "Short Answer",
                        "unit_id": q.unit_id,
                        "unit_name": unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name,
                        "topic_name": (u_topics[0] if u_topics else unit_map.get(q.unit_id, Unit(unit_name="Unit")).unit_name),
                        "board": resolved_board,
                        "class_name": resolved_class,
                        "academic_year": resolved_academic_year,
                        "subject": subject.subject_name,
                        "answer": q.answer,
                        "explanation": q.explanation,
                        "source": q.source or "Question Bank",
                        "source_reference": f"{resolved_board} Prescribed Curriculum",
                        "validation_status": "verified",
                    })

                missing_marks = req_marks - partial_sum
                shortages.append({
                    "target": target,
                    "bloom_obj": bloom_obj,
                    "missing_marks": missing_marks,
                })

        # If legacy call without AI enabled and shortages exist
        if shortages and use_ai is not True and source_mode == "bank":
            raise ValueError(f"Insufficient approved questions in question bank for {subject.subject_name}")

    # =========================================================================
    # STEP 2: AI SYNTHESIS FOR SHORTAGES (Hybrid or Full AI mode)
    # =========================================================================
    if source_mode == "ai":
        shortages = [{
            "target": t,
            "bloom_obj": t["matching_bloom"],
            "missing_marks": t["allocated_marks"],
        } for t in targets if t["allocated_marks"] > 0]

    if shortages:
        if use_ai is False:
            raise ValueError(f"Insufficient approved questions in question bank for {subject.subject_name}")

        ai_generator = get_ai_generator()
        unit_cycle = 0

        # If number_of_questions is given, allocate exact question counts per target bloom
        shortage_bloom_names = {s["bloom_obj"].level_name for s in shortages}
        shortage_targets = [t for t in targets if t["name"] in shortage_bloom_names]
        
        q_alloc_map = {}
        if number_of_questions:
            remaining_q_count = number_of_questions - len(selected_questions)
            if remaining_q_count <= 0:
                remaining_q_count = len(shortage_targets)
            
            # Distribute remaining_q_count among shortage targets respecting min and max question bounds
            import math
            min_q_per_target = {
                s["bloom_obj"].level_name: max(1, math.ceil(s["missing_marks"] / max_allowed_mark))
                for s in shortages
            }
            max_q_per_target = {
                s["bloom_obj"].level_name: max(1, s["missing_marks"] // min_allowed_mark)
                for s in shortages
            }

            total_short_marks = sum(s["missing_marks"] for s in shortages)
            q_items = []
            for s in shortages:
                b_name = s["bloom_obj"].level_name
                pct = (s["missing_marks"] / max(1, total_short_marks))
                raw_q = pct * remaining_q_count
                int_q = int(raw_q)
                rem_q = raw_q - int_q
                clamped_q = max(min_q_per_target[b_name], min(max_q_per_target[b_name], int_q))
                q_items.append({
                    "bloom_name": b_name,
                    "int_q": clamped_q,
                    "rem_q": rem_q,
                    "min_q": min_q_per_target[b_name],
                    "max_q": max_q_per_target[b_name],
                })
            
            curr_q = sum(qi["int_q"] for qi in q_items)
            diff_q = remaining_q_count - curr_q
            if diff_q > 0:
                q_items.sort(key=lambda x: x["rem_q"], reverse=True)
                for _ in range(diff_q):
                    eligible = [qi for qi in q_items if qi["int_q"] < qi["max_q"]]
                    if eligible:
                        eligible[0]["int_q"] += 1
                        q_items.remove(eligible[0])
                        q_items.append(eligible[0])
                    else:
                        q_items[0]["int_q"] += 1
            elif diff_q < 0:
                q_items.sort(key=lambda x: x["rem_q"])
                for _ in range(abs(diff_q)):
                    eligible = [qi for qi in q_items if qi["int_q"] > qi["min_q"]]
                    if eligible:
                        eligible[0]["int_q"] -= 1
                        q_items.remove(eligible[0])
                        q_items.append(eligible[0])
                    else:
                        if q_items[0]["int_q"] > 1:
                            q_items[0]["int_q"] -= 1

            q_alloc_map = {qi["bloom_name"]: qi["int_q"] for qi in q_items}

        for s in shortages:
            bloom_obj = s["bloom_obj"]
            rem_marks = s["missing_marks"]
            target_bloom_q = q_alloc_map.get(bloom_obj.level_name)
            if target_bloom_q and target_bloom_q >= 1:
                base_m = rem_marks // target_bloom_q
                rem_m = rem_marks % target_bloom_q
                mark_splits = [base_m + (1 if i < rem_m else 0) for i in range(target_bloom_q)]
            else:
                # Standard secondary board decomposition (marks strictly 1 to 5)
                mark_splits = []
                curr_rem = rem_marks
                while curr_rem > 0:
                    if curr_rem >= 5:
                        if curr_rem == 6:
                            mark_splits.extend([3, 3])
                            curr_rem -= 6
                        elif curr_rem == 7:
                            mark_splits.extend([4, 3])
                            curr_rem -= 7
                        elif curr_rem == 8:
                            mark_splits.extend([5, 3])
                            curr_rem -= 8
                        elif curr_rem == 9:
                            mark_splits.extend([5, 4])
                            curr_rem -= 9
                        else:
                            mark_splits.append(5)
                            curr_rem -= 5
                    elif curr_rem == 4:
                        mark_splits.append(4)
                        curr_rem -= 4
                    elif curr_rem == 3:
                        mark_splits.append(3)
                        curr_rem -= 3
                    elif curr_rem == 2:
                        mark_splits.append(2)
                        curr_rem -= 2
                    elif curr_rem == 1:
                        mark_splits.append(1)
                        curr_rem -= 1
            mark_splits = [m for m in mark_splits if m > 0]

            for q_mark in mark_splits:
                if q_mark < min_allowed_mark or q_mark > max_allowed_mark:
                    raise ValueError(
                        f"Unsupported marks-per-question value ({q_mark} marks) for {resolved_board} "
                        f"{resolved_class} {subject.subject_name}. Supported marks range is "
                        f"{min_allowed_mark} to {max_allowed_mark} marks."
                    )
                if q_mark >= 5:
                    q_type = "Long Answer" if "math" not in subject.subject_name.lower() else "Numerical"
                elif q_mark >= 3:
                    q_type = "Short Answer" if "math" not in subject.subject_name.lower() else "Numerical"
                elif q_mark == 2:
                    q_type = "Very Short Answer"
                else:
                    q_type = "MCQ"

                # Dynamic candidate units starting from unit_cycle
                candidate_unit_ids = [
                    unit_ids_to_use[(unit_cycle + offset) % len(unit_ids_to_use)]
                    for offset in range(len(unit_ids_to_use))
                ]

                # Candidate Bloom levels: requested level first, then adjacent compatible fallback levels
                # Target Bloom level for this slot
                bloom_candidates = [bloom_obj.level_name]

                gen_res = None
                assigned_unit = None
                attempt_excludes = [q["question"] for q in selected_questions if "question" in q]

                for try_bloom in bloom_candidates:
                    if gen_res:
                        break
                    for cand_unit_id in candidate_unit_ids:
                        if gen_res:
                            break
                        curr_context = unit_curriculum_context[cand_unit_id]
                        cand_unit = curr_context["unit"]
                        cand_desc = curr_context["description"]
                        cand_topics = curr_context["topics"]

                        prompt = AIQuestionPrompt(
                            board=resolved_board,
                            class_name=resolved_class,
                            subject_name=subject.subject_name,
                            unit_name=cand_unit.unit_name,
                            topic_name=cand_topics[0] if cand_topics else None,
                            marks=q_mark,
                            difficulty=difficulty or "medium",
                            bloom_level=try_bloom,
                            question_type=q_type,
                            unit_description=cand_desc,
                            topics_list=cand_topics,
                            exclude_texts=attempt_excludes,
                        )

                        for attempt in range(12):
                            prompt.exclude_texts = attempt_excludes
                            candidate = ai_generator.generate_question(prompt)
                            if not candidate or not candidate.question_text:
                                from app.services.ai.generator_factory import OfflineFallbackProvider
                                fallback_prov = OfflineFallbackProvider()
                                candidate = fallback_prov.generate_question(prompt)

                            if not candidate or not candidate.question_text:
                                break  # Advance to next candidate unit if pool is exhausted for this unit and bloom

                            # Validate model answer is present, non-empty, and not a generic placeholder
                            cand_ans = str(candidate.answer or "").strip()
                            if not cand_ans:
                                continue
                            ans_lower = cand_ans.lower()
                            if any(p in ans_lower for p in [
                                "detailed academic explanation covering key terms",
                                "detailed academic explanation covering key concepts",
                                "factual recall of authorial intent, textual characters",
                                "authoritative historical dates, constitutional articles",
                                "detailed literary and linguistic application addressing key themes",
                                "comprehensive social science analysis applying institutional mechanisms",
                                "detailed solution applying the foundational rules",
                                "in-depth literary analysis examining character arcs",
                                "critical evaluation of literary themes, moral dilemmas",
                                "evaluative assessment of policy outcomes",
                                "evaluative assessment or constructive framework",
                                "comprehensive literary explanation detailing character development",
                                "comprehensive social science explanation detailing institutional mechanisms",
                            ]):
                                continue

                            q_text = clean_generated_question_text(candidate.question_text)
                            if not q_text:
                                continue

                            q_h = compute_question_hash(q_text)
                            s_h = compute_structural_hash(q_text)

                            # Reject exact and near duplicates
                            if (q_h in used_question_hashes) or (s_h in used_structural_hashes) or is_near_duplicate(q_text, used_question_texts):
                                attempt_excludes.append(q_text)
                                continue

                            # Validate unit relevance gate
                            if not validate_unit_relevance(q_text, cand_unit.unit_name, cand_desc, cand_topics, subject.subject_name):
                                attempt_excludes.append(q_text)
                                continue

                            # Validate Bloom's Taxonomy cognitive level gate
                            from app.services.bloom_service import validate_bloom_level
                            lang_ctx = "hindi" if "hindi" in subject.subject_name.lower() else None
                            is_valid_bloom, detected_level, reason = validate_bloom_level(q_text, bloom_obj.level_name, language=lang_ctx)

                            if not is_valid_bloom:
                                attempt_excludes.append(q_text)
                                continue

                            gen_res = candidate
                            gen_res.question_text = q_text
                            used_question_hashes.add(q_h)
                            used_structural_hashes.add(s_h)
                            used_question_texts.add(q_text)
                            assigned_unit = cand_unit
                            unit_cycle += 1
                            break

                if not gen_res:
                    raise ValueError(
                        f"Unable to generate additional distinct, unit-aligned questions for subject '{subject.subject_name}' "
                        f"without repetition. The question pool and distinct templates for "
                        f"cognitive level '{bloom_obj.level_name}' are exhausted. "
                        f"Please broaden the unit selection, adjust requested marks, or provide external AI credentials."
                    )

                # Persist new AI question into Question Bank with deduplication to prevent DB bloat
                existing_q = None
                try:
                    cand_q = (
                        db.query(Question)
                        .filter(
                            Question.subject_id == subject.id,
                            Question.question_text == gen_res.question_text,
                            Question.status == "draft",
                        )
                        .first()
                    )
                    if isinstance(cand_q, Question):
                        existing_q = cand_q
                except Exception:
                    existing_q = None

                if existing_q:
                    final_q = existing_q
                    if not final_q.answer and gen_res.answer:
                        final_q.answer = gen_res.answer
                    if not final_q.explanation and gen_res.explanation:
                        final_q.explanation = gen_res.explanation
                else:
                    new_q = Question(
                        subject_id=subject.id,
                        unit_id=assigned_unit.id,
                        bloom_level_id=bloom_obj.id,
                        board_id=subject.board_id or board_id,
                        class_id=subject.class_id or class_id,
                        question_text=gen_res.question_text,
                        question_type=gen_res.question_type or q_type,
                        marks=q_mark,
                        difficulty=gen_res.difficulty or difficulty or "medium",
                        answer=gen_res.answer,
                        explanation=gen_res.explanation,
                        numerical_data=gen_res.numerical_data,
                        application_context=gen_res.application_context,
                        source="AI Synthesized",
                        source_type="ai",
                        is_ai_generated=True,
                        approved=False,
                        status="draft",
                        active=True,
                    )
                    db.add(new_q)
                    db.flush()
                    final_q = new_q

                selected_questions.append({
                    "question_id": final_q.id,
                    "question": final_q.question_text,
                    "marks": q_mark,
                    "bloom": bloom_obj.level_name,
                    "difficulty": final_q.difficulty or difficulty or "medium",
                    "question_type": final_q.question_type or q_type,
                    "unit_id": assigned_unit.id,
                    "unit_name": assigned_unit.unit_name,
                    "topic_name": prompt.topic_name or ((unit_curriculum_context.get(assigned_unit.id, {}).get("topics") or [assigned_unit.unit_name])[0]),
                    "board": resolved_board,
                    "class_name": resolved_class,
                    "academic_year": resolved_academic_year,
                    "subject": subject.subject_name,
                    "answer": final_q.answer or gen_res.answer,
                    "explanation": final_q.explanation or gen_res.explanation,
                    "source": "AI Synthesized",
                    "source_reference": f"{resolved_board} Prescribed Curriculum",
                    "validation_status": "draft",
                })



        db.commit()

    # Sort questions by Section & Marks
    def section_rank(q):
        m = q["marks"]
        if m <= 1:
            return (1, m)
        elif m <= 2:
            return (2, m)
        elif m <= 4:
            return (3, m)
        else:
            return (4, m)

    selected_questions.sort(key=section_rank)

    # Compute Blueprint Summary Table
    blueprint_summary = []
    for target in targets:
        b_name = target["matching_bloom"].level_name
        req_m = target["allocated_marks"]
        gen_m = sum(q["marks"] for q in selected_questions if q["bloom"] == b_name)
        gen_c = len([q for q in selected_questions if q["bloom"] == b_name])
        blueprint_summary.append({
            "bloom": b_name,
            "required_percentage": target["percentage"],
            "required_marks": req_m,
            "generated_marks": gen_m,
            "generated_questions": gen_c,
        })

    # Resolve examination blueprint (official board pattern or pedagogical custom pattern)
    from app.services.exam_blueprints import get_exam_blueprint, build_custom_paper_blueprint

    official_bp = get_exam_blueprint(
        board_code=resolved_board,
        class_name=resolved_class,
        subject_name=subject.subject_name,
        subject_code=getattr(subject, "subject_code", None),
    )
    if official_bp and official_bp.total_marks == total_marks:
        is_official_pattern = True
        duration_minutes = official_bp.duration_minutes
        source_ref = official_bp.source_reference
        general_instructions = official_bp.general_instructions
    else:
        is_official_pattern = False
        custom_bp = build_custom_paper_blueprint(
            board_code=resolved_board,
            class_name=resolved_class,
            subject_name=subject.subject_name,
            total_marks=total_marks,
            target_questions_count=len(selected_questions),
        )
        duration_minutes = custom_bp.duration_minutes
        source_ref = custom_bp.source_reference
        general_instructions = custom_bp.general_instructions

    # Create persistent GeneratedPaper record
    paper_uuid = f"QP-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    paper_title = f"{resolved_board} {resolved_class} - {subject.subject_name} Examination"

    db_paper = GeneratedPaper(
        paper_id=paper_uuid,
        user_id=user_id,
        board_id=subject.board_id or board_id,
        class_id=subject.class_id or class_id,
        subject_id=subject.id,
        title=paper_title,
        board_name=resolved_board,
        class_name=resolved_class,
        subject_name=subject.subject_name,
        unit_names=unit_names_str,
        total_marks=total_marks,
        total_questions=len(selected_questions),
        difficulty=difficulty.capitalize() if difficulty else "Medium",
        source=source_mode.capitalize(),
        questions_data=json.dumps(selected_questions),
        blueprint_summary=json.dumps(blueprint_summary),
        status="saved",
    )
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)

    return {
        "paper_id": paper_uuid,
        "id": db_paper.id,
        "title": paper_title,
        "total_marks": total_marks,
        "total_questions": len(selected_questions),
        "duration_minutes": duration_minutes,
        "is_official_pattern": is_official_pattern,
        "source_reference": source_ref,
        "general_instructions": general_instructions,
        "questions": selected_questions,
        "subject_name": subject.subject_name,
        "board": resolved_board,
        "class_name": resolved_class,
        "unit_names": unit_names_str,
        "blueprint_summary": blueprint_summary,
        "source": source_mode.capitalize(),
    }
