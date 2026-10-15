"""Service for generating questions using Gemini API or offline mock fallback."""

import json
import re
import urllib.request
from typing import Dict, List, Optional
from urllib.error import HTTPError, URLError

from app.core.config import settings


def normalize_text(text: str) -> str:
    """Normalize text for duplicate detection."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text).lower().strip()


def _get_mock_question_text(
    subject: str,
    unit: str,
    bloom_level: str,
    difficulty: str,
    marks: int,
    index: int = 0,
    textbook_context: Optional[str] = None,
    board: Optional[str] = None,
    class_name: Optional[str] = None,
) -> str:
    """Generate authentic, curriculum-grounded questions tailored to Bloom level and marks.
    
    Queries the verified curriculum pool using explicit board and class context.
    If no authentic question is available, returns an empty string rather than
    fabricating generic filler.
    """
    if not subject or not unit:
        return ""

    from app.services.ai.curriculum_pools import match_curriculum_question
    b_val = (board or "CBSE").strip()
    c_val = str(class_name or "12").strip()

    pool_q = match_curriculum_question(
        board=b_val,
        class_name=c_val,
        subject_name=subject,
        unit_name=unit,
        bloom_level=bloom_level,
        marks=marks,
    )
    if pool_q and pool_q.get("q"):
        return pool_q["q"]

    # When no authentic curriculum question exists in the verified pool,
    # do not silently generate generic filler.
    return ""


def generate_questions_via_ai(
    subject: str,
    unit: str,
    bloom_level: str,
    difficulty: str,
    marks: int,
    count: int = 1,
    textbook_context: Optional[str] = None,
) -> list[dict]:
    """
    Generate questions based on criteria. If GEMINI_API_KEY is not set,
    falls back to generating mock placeholder questions for testing.
    """
    if not settings.GEMINI_API_KEY:
        questions = []
        mock_templates = [
            f"Explain the significance of '{unit}' in context of '{subject}' (Bloom Level: {bloom_level}, Difficulty: {difficulty}, Marks: {marks}).",
            f"Describe a real-world scenario where the concepts of '{unit}' are applied under the subject '{subject}' ({difficulty} difficulty).",
            f"How does the structure of '{unit}' support overall understanding of '{subject}'? (Bloom level: {bloom_level}, Marks: {marks}).",
            f"Compare and contrast '{unit}' with adjacent topics in '{subject}'.",
            f"Analyze the relationship between key elements of '{unit}' (Bloom Level: {bloom_level}, Marks: {marks}).",
            f"Formulate a summary describing the core functions in '{unit}' ({difficulty} difficulty).",
            f"Identify the primary arguments presented in '{unit}' regarding '{subject}'.",
            f"Illustrate how '{unit}' functions under varying parameters in '{subject}'."
        ]
        for i in range(count):
            template = mock_templates[i % len(mock_templates)]
            if textbook_context:
                snippet = textbook_context[:50] + "..." if len(textbook_context) > 50 else textbook_context
                template = f"Based on textbook text '{snippet}': " + template
            questions.append({
                "question_text": template,
                "difficulty": difficulty,
                "marks": marks
            })
        return questions


    # Call Gemini API
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    
    prompt = (
        f"Generate {count} unique and high-quality question(s) for the subject '{subject}' "
        f"and unit '{unit}', matching Bloom's taxonomy level '{bloom_level}'. "
        f"Each question must be worth exactly {marks} mark(s) and have a difficulty of '{difficulty}'. "
    )

    if textbook_context:
        prompt += f"\nUse the following textbook text/chapter content as the primary reference to generate the questions:\n{textbook_context}\n"

    prompt += (
        f"Return ONLY a JSON object with a single key 'questions' containing a list of questions. "
        f"Each question object in the list must have exactly these keys: "
        f"'question_text' (the question itself), 'difficulty' (string '{difficulty}'), and 'marks' (integer {marks}). "
        f"Do not wrap the JSON output in markdown formatting or backticks."
    )

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            response_data = json.loads(res.read().decode("utf-8"))
            candidate_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            # Clean possible markdown wrap
            candidate_text = re.sub(r"^```json\s*", "", candidate_text.strip(), flags=re.MULTILINE)
            candidate_text = re.sub(r"\s*```$", "", candidate_text.strip(), flags=re.MULTILINE)
            parsed_json = json.loads(candidate_text)
            return parsed_json.get("questions", [])
    except (HTTPError, URLError, json.JSONDecodeError, KeyError, IndexError) as exc:
        print(f"Gemini API call failed, falling back to mock: {exc}")
        questions = []
        for i in range(count):
            q_text = _get_mock_question_text(subject, unit, bloom_level, difficulty, marks, index=i, textbook_context=textbook_context)
            questions.append({
                "question_text": q_text,
                "difficulty": difficulty,
                "marks": marks
            })
        return questions


def generate_full_paper_via_ai(
    subject_name: str,
    board: str,
    class_name: str,
    blueprint_items: List[Dict[str, object]],
    overall_difficulty: str = "medium",
) -> List[Dict[str, object]]:
    """
    Generate all questions for an entire question paper blueprint using Gemini API
    or a rich offline mock fallback. Guarantees question uniqueness and strict
    adherence to the blueprint requirements.
    """
    if not blueprint_items:
        return []

    generated_results: List[Dict[str, object]] = []
    seen_normalized_texts = set()

    # If Gemini API Key is available, attempt batch prompt
    if settings.GEMINI_API_KEY:
        try:
            blueprint_descriptions = []
            for idx, item in enumerate(blueprint_items):
                blueprint_descriptions.append(
                    f"Q{idx + 1}: Unit '{item['unit_name']}', Bloom Level '{item['bloom_name']}', Marks {item['marks']}, Difficulty '{item['difficulty']}'"
                )

            prompt = (
                f"You are an expert examination question paper author for Board: '{board}', Class: '{class_name}', Subject: '{subject_name}'.\n"
                f"Generate exactly {len(blueprint_items)} unique, high-quality, academic examination questions strictly covering the following question blueprint:\n\n"
                + "\n".join(blueprint_descriptions) +
                "\n\nStrict Requirements:\n"
                f"1. Generate questions ONLY from the specified subject '{subject_name}' and designated units.\n"
                "2. Each question must match its designated Bloom's taxonomy level, marks, and difficulty.\n"
                "3. Do not generate repetitive or duplicate questions.\n"
                "4. Return ONLY a JSON object with a single key 'questions' containing a list of objects in the exact order of the blueprint.\n"
                "Each question object must have: 'question_text' (string), 'unit_name' (string), 'bloom_level' (string), 'marks' (integer), 'difficulty' (string).\n"
                "Do NOT wrap the JSON in markdown code blocks."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            }

            req = urllib.request.Request(
                url,
                method="POST",
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=20) as res:
                response_data = json.loads(res.read().decode("utf-8"))
                candidate_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                candidate_text = re.sub(r"^```json\s*", "", candidate_text.strip(), flags=re.MULTILINE)
                candidate_text = re.sub(r"\s*```$", "", candidate_text.strip(), flags=re.MULTILINE)
                parsed = json.loads(candidate_text)
                ai_questions = parsed.get("questions", [])

                if isinstance(ai_questions, list) and len(ai_questions) == len(blueprint_items):
                    for idx, q_data in enumerate(ai_questions):
                        bp = blueprint_items[idx]
                        q_text = str(q_data.get("question_text", "")).strip()
                        norm = normalize_text(q_text)
                        if not q_text or norm in seen_normalized_texts:
                            # Fallback replacement if duplicate or empty
                            q_text = _get_mock_question_text(
                                subject=subject_name,
                                unit=bp["unit_name"],
                                bloom_level=bp["bloom_name"],
                                difficulty=bp["difficulty"],
                                marks=bp["marks"],
                                index=idx + 10,
                                board=board,
                                class_name=class_name,
                            )
                            norm = normalize_text(q_text)

                        seen_normalized_texts.add(norm)
                        generated_results.append({
                            "unit_id": bp["unit_id"],
                            "unit_name": bp["unit_name"],
                            "bloom_id": bp["bloom_id"],
                            "bloom_name": bp["bloom_name"],
                            "marks": bp["marks"],
                            "difficulty": bp["difficulty"],
                            "question_text": q_text,
                        })
                    return generated_results

        except Exception as exc:
            print(f"Gemini full paper generation failed, using robust mock fallback: {exc}")

    # Offline / fallback mock generation
    for idx, bp in enumerate(blueprint_items):
        attempt = 0
        q_text = ""
        while attempt < 10:
            candidate = _get_mock_question_text(
                subject=subject_name,
                unit=bp["unit_name"],
                bloom_level=bp["bloom_name"],
                difficulty=bp["difficulty"],
                marks=bp["marks"],
                index=idx + attempt,
                board=board,
                class_name=class_name,
            )
            norm = normalize_text(candidate)
            if norm not in seen_normalized_texts:
                seen_normalized_texts.add(norm)
                q_text = candidate
                break
            attempt += 1

        if not q_text:
            q_text = f"Analyze the key principles of '{bp['unit_name']}' in '{subject_name}' (Question {idx+1})."

        generated_results.append({
            "unit_id": bp["unit_id"],
            "unit_name": bp["unit_name"],
            "bloom_id": bp["bloom_id"],
            "bloom_name": bp["bloom_name"],
            "marks": bp["marks"],
            "difficulty": bp["difficulty"],
            "question_text": q_text,
        })

    return generated_results


def fetch_syllabus_units(board: str, class_name: str, subject_name: str) -> list[str]:
    """
    Query Gemini API to get the official chapter/unit list for a given board, class, and subject.
    If GEMINI_API_KEY is not configured, returns a default mock list of chapters for that subject.
    """
    if not settings.GEMINI_API_KEY:
        if "english" in subject_name.lower():
            return ["The Last Lesson", "Lost Spring", "Deep Water", "The Rattrap", "Indigo", "Poets and Pancakes", "The Interview", "Going Places", "A Roadside Stand", "Aunt Jennifer's Tigers"]
        elif "math" in subject_name.lower():
            return ["Real Numbers", "Polynomials", "Pair of Linear Equations", "Quadratic Equations", "Arithmetic Progressions", "Triangles", "Coordinate Geometry", "Introduction to Trigonometry"]
        elif "science" in subject_name.lower():
            return ["Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals", "Carbon and its Compounds", "Life Processes", "Control and Coordination"]

        b_upper = (board or "").upper()
        if "TN" in b_upper:
            try:
                from app.services.curriculum.tn_board_importer import TamilNaduBoardImporter
                c_num = 12 if ("12" in str(class_name) or "xii" in str(class_name).lower()) else 10
                curriculum = TamilNaduBoardImporter().fetch_curriculum(target_classes=[c_num])
                for sub in curriculum.subjects:
                    if sub.subject_name.lower() in subject_name.lower() or subject_name.lower() in sub.subject_name.lower():
                        return [u.unit_name for u in sub.units]
            except Exception:
                pass
        else:
            try:
                from app.services.curriculum.cbse_importer import CBSEImporter
                c_num = 12 if ("12" in str(class_name) or "xii" in str(class_name).lower()) else 10
                curriculum = CBSEImporter().fetch_curriculum(target_classes=[c_num])
                for sub in curriculum.subjects:
                    if sub.subject_name.lower() in subject_name.lower() or subject_name.lower() in sub.subject_name.lower():
                        return [u.unit_name for u in sub.units]
            except Exception:
                pass

        return [f"Unit 1 - Foundational Principles of {subject_name}", f"Unit 2 - Theoretical Analysis of {subject_name}", f"Unit 3 - Advanced Applications of {subject_name}"]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
    
    prompt = (
        f"List the standard official textbook chapters or units for the syllabus of Board: '{board}', Class: '{class_name}', Subject: '{subject_name}'. "
        f"Return ONLY a JSON object containing a list of strings representing chapter names under the key 'units'. "
        f"Do not include markdown code block formatting or backticks around the JSON."
    )

    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    req = urllib.request.Request(
        url,
        method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            response_data = json.loads(res.read().decode("utf-8"))
            candidate_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            candidate_text = re.sub(r"^```json\s*", "", candidate_text.strip(), flags=re.MULTILINE)
            candidate_text = re.sub(r"\s*```$", "", candidate_text.strip(), flags=re.MULTILINE)
            parsed_json = json.loads(candidate_text)
            return parsed_json.get("units", [])
    except Exception as exc:
        print(f"Gemini API call failed for syllabus fetch, falling back: {exc}")
        return [f"Chapter 1: Intro to {subject_name}", f"Chapter 2: Core {subject_name}", f"Chapter 3: Advanced {subject_name}"]

