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
) -> str:
    """Generate high quality contextual mock questions tailored to Bloom level and marks."""
    bloom_lower = bloom_level.lower()
    
    templates_by_bloom = {
        "remember": [
            f"Define the key terminology and foundational concepts of '{unit}' in '{subject}'.",
            f"State the primary principles and laws governing '{unit}' in '{subject}'.",
            f"List and recall the standard characteristics associated with '{unit}'.",
            f"Identify the essential components that comprise '{unit}' in '{subject}'."
        ],
        "understand": [
            f"Explain the working principles and significance of '{unit}' within the study of '{subject}'.",
            f"Describe how '{unit}' functions and illustrate its role in '{subject}' with clear examples.",
            f"Summarize the core concepts of '{unit}' and explain their relevance to practical scenarios.",
            f"Compare and contrast the key mechanisms found in '{unit}' with adjacent topics in '{subject}'."
        ],
        "apply": [
            f"Demonstrate how to apply the techniques of '{unit}' to solve standard problems in '{subject}'.",
            f"Given a real-world scenario, illustrate the implementation of '{unit}' concepts in '{subject}'.",
            f"Apply the analytical methods taught in '{unit}' to calculate and derive key outcomes.",
            f"Construct a step-by-step practical procedure using the principles of '{unit}'."
        ],
        "analyze": [
            f"Critically analyze the performance advantages and trade-offs of '{unit}' in '{subject}'.",
            f"Examine the relationships between the various sub-components of '{unit}' under different constraints.",
            f"Deconstruct a complex problem in '{subject}' and analyze how '{unit}' provides an optimal solution.",
            f"Distinguish between theoretical expectations and practical challenges encountered in '{unit}'."
        ],
        "evaluate": [
            f"Evaluate the effectiveness and efficiency of methods used in '{unit}' for '{subject}'.",
            f"Assess the validity of common hypotheses regarding '{unit}' and justify your reasoning.",
            f"Critique the standard approaches in '{unit}' and recommend potential improvements."
        ],
        "create": [
            f"Design a novel architecture or solution leveraging the principles of '{unit}' in '{subject}'.",
            f"Formulate an integrated workflow combining '{unit}' with broader systems in '{subject}'.",
            f"Develop a structured proposal to address open challenges in '{unit}'."
        ]
    }

    # Default to understand if unknown bloom
    pool = templates_by_bloom.get(bloom_lower, templates_by_bloom["understand"])
    selected_template = pool[index % len(pool)]

    if textbook_context:
        snippet = textbook_context[:60] + "..." if len(textbook_context) > 60 else textbook_context
        selected_template = f"Based on reference context '{snippet}': " + selected_template

    return selected_template


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
    falls back to generating mock placeholder questions.
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
            return ["The Last Lesson", "Lost Spring", "Deep Water", "The Rattrap", "Indigo", "Poets and Pancakes", "The Interview", "Going Places", "Abdul and Zarina"]
        elif "math" in subject_name.lower():
            return ["Real Numbers", "Polynomials", "Pair of Linear Equations", "Quadratic Equations", "Arithmetic Progressions", "Triangles", "Coordinate Geometry", "Introduction to Trigonometry"]
        elif "science" in subject_name.lower():
            return ["Chemical Reactions and Equations", "Acids, Bases and Salts", "Metals and Non-metals", "Carbon and its Compounds", "Life Processes", "Control and Coordination"]
        else:
            return [f"Chapter 1: Intro to {subject_name}", f"Chapter 2: Core {subject_name}", f"Chapter 3: Advanced {subject_name}", f"Chapter 4: Practical Applications"]

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

