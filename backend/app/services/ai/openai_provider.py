"""OpenAI GPT Provider implementation."""

import json
import os
import re
from typing import List, Optional

import httpx

from app.core.config import settings
from app.services.ai.base import AIQuestionPrompt, BaseAIProvider, GeneratedQuestionResult
from app.services.ai.prompt_builder import build_subject_specific_system_prompt


class OpenAIProvider(BaseAIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY") or getattr(settings, "OPENAI_API_KEY", "")

    def is_available(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def generate_question(self, prompt: AIQuestionPrompt) -> Optional[GeneratedQuestionResult]:
        if not self.is_available():
            return None

        system_prompt = build_subject_specific_system_prompt(prompt)
        url = "https://api.openai.com/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "messages": [
                {"role": "system", "content": "You are a master examination author that outputs raw JSON strictly conforming to user schema."},
                {"role": "user", "content": system_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }

        try:
            with httpx.Client(timeout=25.0) as client:
                res = client.post(url, json=payload, headers=headers)
                if res.status_code != 200:
                    return None

                data = res.json()
                raw_text = data["choices"][0]["message"]["content"]
                parsed = json.loads(raw_text)

                return GeneratedQuestionResult(
                    question_text=parsed.get("question_text", "Question content"),
                    answer=parsed.get("answer", "Answer"),
                    explanation=parsed.get("explanation"),
                    question_type=parsed.get("question_type", prompt.question_type),
                    marks=int(parsed.get("marks", prompt.marks)),
                    difficulty=parsed.get("difficulty", prompt.difficulty).lower(),
                    bloom=parsed.get("bloom", prompt.bloom_level),
                    unit_name=prompt.unit_name,
                    topic_name=prompt.topic_name,
                    numerical_data=parsed.get("numerical_data"),
                    application_context=parsed.get("application_context"),
                )
        except Exception:
            return None

    def generate_batch(self, prompts: List[AIQuestionPrompt]) -> List[GeneratedQuestionResult]:
        results = []
        for p in prompts:
            res = self.generate_question(p)
            if res:
                results.append(res)
        return results
