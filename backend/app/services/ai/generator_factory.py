"""AI Question Generator factory and multi-provider orchestrator with graceful fallback."""

import os
import random
import re
from typing import List, Optional

from app.core.config import settings
from app.services.ai.base import AIQuestionPrompt, BaseAIProvider, GeneratedQuestionResult
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAIProvider


class OfflineFallbackProvider(BaseAIProvider):
    """Generates rigorous, subject-specific questions when external AI API keys are not provided."""

    def is_available(self) -> bool:
        return True

    def generate_question(self, prompt: AIQuestionPrompt) -> Optional[GeneratedQuestionResult]:
        subj = prompt.subject_name.lower()
        u_lower = prompt.unit_name.lower()
        marks = prompt.marks
        b_lvl = prompt.bloom_level
        q_type = prompt.question_type

        from app.services.ai.curriculum_pools import normalize_text_for_comparison
        norm_excludes = {normalize_text_for_comparison(str(t)) for t in (prompt.exclude_texts or [])}


        # Subject-specific realistic questions
        if "math" in subj:
            from app.services.question_generator import classify_unit_category
            category = classify_unit_category(prompt.unit_name, prompt.unit_description, prompt.topics_list)

            from app.services.ai.curriculum_pools import get_math_curriculum_question
            math_q = get_math_curriculum_question(category, prompt.bloom_level, prompt.exclude_texts)
            if math_q:
                return GeneratedQuestionResult(
                    question_text=math_q["q"],
                    answer=math_q["a"],
                    explanation=f"Curriculum question for category '{category}'.",
                    question_type=q_type,
                    marks=marks,
                    difficulty=prompt.difficulty.lower(),
                    bloom=b_lvl,
                    unit_name=prompt.unit_name,
                    topic_name=prompt.topic_name,
                )
            return None

        else:
            # Check authentic curriculum pool for all non-math subjects (English, Science, Physics, Chemistry, CS, etc.)
            from app.services.ai.curriculum_pools import match_curriculum_question
            full_unit_desc = f"{prompt.unit_name} {prompt.topic_name or ''}".strip()
            matched_pool_q = match_curriculum_question(
                board=prompt.board,
                class_name=prompt.class_name,
                subject_name=prompt.subject_name,
                unit_name=full_unit_desc,
                bloom_level=prompt.bloom_level,
                marks=prompt.marks,
                exclude_texts=prompt.exclude_texts,
            )
            if matched_pool_q:
                return GeneratedQuestionResult(
                    question_text=matched_pool_q["q"],
                    answer=matched_pool_q["a"],
                    explanation=f"Authentic curriculum question matching {prompt.board} {prompt.class_name} {prompt.subject_name}.",
                    question_type=matched_pool_q.get("type", q_type),
                    marks=matched_pool_q.get("marks", marks),
                    difficulty=prompt.difficulty.lower(),
                    bloom=matched_pool_q.get("bloom", b_lvl),
                    unit_name=matched_pool_q.get("unit") or prompt.unit_name,
                    topic_name=prompt.topic_name,
                )

            # When the authentic curriculum pool is exhausted for any subject:
            # Do NOT manufacture generic templates or placeholder answers.
            # Return None so that the caller cleanly reports actionable pool exhaustion.
            return None

    def generate_batch(self, prompts: List[AIQuestionPrompt]) -> List[GeneratedQuestionResult]:
        return [self.generate_question(p) for p in prompts]


def get_ai_generator() -> BaseAIProvider:
    """Return configured AI Provider (Gemini, OpenAI, or Fallback)."""
    provider_name = (os.getenv("AI_PROVIDER") or getattr(settings, "AI_PROVIDER", "gemini")).lower()

    if provider_name in ("v17_2", "v17.2", "flan_t5_v17_2"):
        from app.services.ai.v17_2_inference_adapter import V17_2InferenceAdapter
        v17_2 = V17_2InferenceAdapter()
        if v17_2.is_available():
            return v17_2
        raise RuntimeError("V17.2 checkpoint is unavailable or failed integrity verification")


    if provider_name == "openai":
        provider = OpenAIProvider()
        if provider.is_available():
            return provider
    elif provider_name == "gemini":
        provider = GeminiProvider()
        if provider.is_available():
            return provider

    # Check both if primary not configured
    gemini = GeminiProvider()
    if gemini.is_available():
        return gemini

    openai = OpenAIProvider()
    if openai.is_available():
        return openai

    return OfflineFallbackProvider()
