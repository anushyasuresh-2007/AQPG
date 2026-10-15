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
                q_text = math_q["q"]
                ans = math_q["a"]
            else:
                return None

        else:
            # Check authentic curriculum pool for all non-math subjects first (English, Science, Physics, Chemistry, CS, etc.)
            from app.services.ai.curriculum_pools import match_curriculum_question, normalize_text_for_comparison
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
                    unit_name=prompt.unit_name,
                    topic_name=prompt.topic_name,
                )

            # When the authentic curriculum pool is exhausted for STEM subjects
            # (Chemistry, Physics, Biology, and Computer Science):
            # Do NOT manufacture generic questions such as "State the foundational laws and definitions governing...".
            # Return None so that the caller cleanly reports actionable pool exhaustion.
            is_stem = any(k in subj for k in ["chem", "physic", "bio", "computer", "programming"]) or bool(re.search(r"\b(cs|ip|it)\b", subj))
            if is_stem:
                return None

            norm_excludes = {normalize_text_for_comparison(str(t)) for t in (prompt.exclude_texts or [])}
            b_clean = (prompt.bloom_level or "Understand").strip().title()

            # Dynamic curriculum-aligned templates for humanities, social sciences, and custom/mock subjects
            if b_clean == "Remember":
                if "english" in subj:
                    templates = [
                        f"State the central theme, poetic devices, or textual context established in {prompt.unit_name} ({prompt.topic_name or 'Prescribed Lessons'}).",
                        f"Identify the literary techniques and narrative perspectives employed by the author in {prompt.unit_name}.",
                        f"Define the key vocabulary and grammatical rules highlighted in {prompt.unit_name}.",
                    ]
                    ans = f"Factual recall of authorial intent, textual characters, poetic devices, and vocabulary from {prompt.unit_name}."
                elif "social" in subj or any(w in subj for w in ["history", "geography", "civic", "politic"]):
                    templates = [
                        f"State the historical causes, constitutional provisions, or geographical features defining {prompt.unit_name}.",
                        f"List the major milestones, treaties, or demographic indicators associated with {prompt.unit_name}.",
                        f"Define the institutional frameworks and core terminology established in {prompt.unit_name}.",
                    ]
                    ans = f"Authoritative historical dates, constitutional articles, geographical definitions, and economic indicators of {prompt.unit_name}."
                else:
                    templates = [
                        f"Define {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}) and state its primary characteristics.",
                        f"List the main components and key terms associated with {prompt.unit_name}.",
                        f"State the foundational definitions and rules governing {prompt.unit_name}.",
                        f"Mention any three key attributes or factors relevant to {prompt.unit_name}.",
                        f"Name the primary classifications or categories of {prompt.unit_name}.",
                    ]
                    ans = f"Detailed academic explanation covering key terms, foundational definitions, and attributes of {prompt.unit_name}."
            elif b_clean == "Apply":
                if "english" in subj:
                    templates = [
                        f"Apply the core literary themes and character values of {prompt.unit_name} ({prompt.topic_name or 'Core Text'}) to resolve a modern ethical dilemma.",
                        f"Draft a creative piece or formal composition applying the conventions prescribed in {prompt.unit_name}.",
                        f"Demonstrate how the grammatical rules and stylistic structures in {prompt.unit_name} apply to transform the given context.",
                        f"Apply the critical message of {prompt.unit_name} to compose an analytical reflection on human behavior.",
                    ]
                    ans = f"Detailed literary and linguistic application addressing key themes, character motivations, and conventions of {prompt.unit_name}."
                elif "social" in subj or any(w in subj for w in ["history", "geography", "civic", "politic"]):
                    templates = [
                        f"Apply the democratic principles and constitutional provisions of {prompt.unit_name} ({prompt.topic_name or 'Key Topics'}) to address a local community challenge.",
                        f"Demonstrate how the resource conservation and geographical techniques in {prompt.unit_name} can be implemented in a drought-affected region.",
                        f"Analyze how the historical lessons or economic frameworks in {prompt.unit_name} apply to mitigating contemporary socio-economic disparities.",
                        f"Illustrate how institutional governance mechanisms in {prompt.unit_name} apply to resolving a civic crisis.",
                    ]
                    ans = f"Comprehensive social science analysis applying institutional mechanisms, constitutional articles, or geographical methods of {prompt.unit_name}."
                else:
                    templates = [
                        f"Demonstrate how the principles of {prompt.unit_name} ({prompt.topic_name or 'Methods'}) are applied to solve a practical problem.",
                        f"Apply the learned methods of {prompt.unit_name} to illustrate a standard scenario.",
                        f"Show how the theoretical rules of {prompt.unit_name} can be implemented in a concrete case.",
                        f"Apply the operational procedure of {prompt.unit_name} to analyze the given system parameters.",
                        f"Illustrate with an appropriate example how {prompt.unit_name} is utilized to resolve an operational challenge.",
                        f"Formulate a practical implementation plan applying the techniques of {prompt.unit_name}.",
                    ]
                    ans = f"Detailed solution applying the foundational rules, formulas, and methods of {prompt.unit_name}."
            elif b_clean == "Analyze":
                if "english" in subj:
                    templates = [
                        f"Analyze the psychological development, emotional conflicts, and motivations of central figures in {prompt.unit_name}.",
                        f"Compare and contrast the contrasting perspectives or cultural contexts presented in {prompt.unit_name}.",
                        f"Deconstruct the symbolism, imagery, and structural motifs utilized in {prompt.unit_name}.",
                    ]
                    ans = f"In-depth literary analysis examining character arcs, stylistic motifs, and thematic significance in {prompt.unit_name}."
                elif "social" in subj or any(w in subj for w in ["history", "geography", "civic", "politic"]):
                    templates = [
                        f"Analyze the relationship and critical factors governing {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}).",
                        f"Compare and contrast the primary mechanisms or categories established in {prompt.unit_name}.",
                        f"Examine the underlying causes and differential outcomes in {prompt.unit_name}.",
                        f"Analyze the comparative advantages and operational differences found in {prompt.unit_name}.",
                    ]
                    ans = f"In-depth analysis examining key components, causal factors, and comparative features of {prompt.unit_name}."
                else:
                    templates = [
                        f"Analyze the relationship and critical factors governing {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}).",
                        f"Compare and contrast the primary mechanisms or categories established in {prompt.unit_name}.",
                        f"Examine the underlying causes and differential outcomes in {prompt.unit_name}.",
                        f"Analyze the advantages, limitations, and operational trade-offs in {prompt.unit_name}.",
                        f"Differentiate between the key structural aspects and dynamic properties of {prompt.unit_name}.",
                        f"Break down the functional dependencies and performance impacts in {prompt.unit_name}.",
                    ]
                    ans = f"In-depth analysis examining key components, causal factors, and comparative features of {prompt.unit_name}."
            elif b_clean in ("Evaluate", "Create"):
                if "english" in subj:
                    templates = [
                        f"Critically evaluate the moral message and universal relevance of {prompt.unit_name} in contemporary society.",
                        f"Assess the effectiveness of the narrative resolution in {prompt.unit_name} with textual evidence.",
                    ]
                    ans = f"Critical evaluation of literary themes, moral dilemmas, and narrative craft in {prompt.unit_name}."
                elif "social" in subj or any(w in subj for w in ["history", "geography", "civic", "politic"]):
                    templates = [
                        f"Evaluate the effectiveness and practical significance of policy frameworks in {prompt.unit_name}.",
                        f"Critically assess the validity and socio-political impact of historical movements in {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative assessment of policy outcomes, constitutional principles, and historical movements in {prompt.unit_name}."
                else:
                    templates = [
                        f"Evaluate the effectiveness and practical significance of {prompt.unit_name} in its specific domain.",
                        f"Critically assess the validity and impact of theoretical principles in {prompt.unit_name}.",
                        f"Formulate an evaluative argument defending the optimal configuration in {prompt.unit_name}.",
                        f"Synthesize an enhanced design proposal addressing the constraints of {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative assessment or constructive framework addressing the core challenges of {prompt.unit_name}."
            else:
                if "english" in subj:
                    templates = [
                        f"Explain the central themes, character motivations, and narrative progression in {prompt.unit_name}.",
                        f"Describe how key conflicts in {prompt.unit_name} develop and influence the characters.",
                    ]
                    ans = f"Comprehensive literary explanation detailing character development and central themes in {prompt.unit_name}."
                elif "social" in subj or any(w in subj for w in ["history", "geography", "civic", "politic"]):
                    templates = [
                        f"Explain the socio-political factors and institutional mechanisms governing {prompt.unit_name}.",
                        f"Describe the historical progression and structural significance of events in {prompt.unit_name}.",
                    ]
                    ans = f"Comprehensive social science explanation detailing institutional mechanisms and historical factors in {prompt.unit_name}."
                else:
                    templates = [
                        f"Explain the core principles and concepts of {prompt.unit_name} ({prompt.topic_name or 'Key Topics'}) and their practical significance.",
                        f"Describe the main processes and features associated with {prompt.unit_name}.",
                        f"Discuss the operational principles and theoretical foundations of {prompt.unit_name}.",
                        f"Explain how key mechanisms and components function within {prompt.unit_name}.",
                        f"Elaborate on the significance and practical roles of {prompt.unit_name} in its relevant domain.",
                        f"Outline the functional lifecycle and primary behaviors observed in {prompt.unit_name}.",
                    ]
                    ans = f"Detailed academic explanation covering key concepts, definitions, and applications of {prompt.unit_name}."

            unex_templates = [t for t in templates if normalize_text_for_comparison(t) not in norm_excludes]
            if unex_templates:
                q_text = random.choice(unex_templates)
            else:
                return None
        return GeneratedQuestionResult(
            question_text=q_text,
            answer=ans,
            explanation=f"Curriculum question for category '{category}'." if 'category' in locals() else f"Curriculum question for {prompt.board} {prompt.class_name} {prompt.subject_name} ({prompt.unit_name}).",
            question_type=q_type,
            marks=marks,
            difficulty=prompt.difficulty.lower(),
            bloom=b_lvl,
            unit_name=prompt.unit_name,
            topic_name=prompt.topic_name,
        )

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
