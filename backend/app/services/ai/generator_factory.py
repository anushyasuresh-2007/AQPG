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
            matched_pool_q = match_curriculum_question(
                board=prompt.board,
                class_name=prompt.class_name,
                subject_name=prompt.subject_name,
                unit_name=prompt.unit_name,
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

            norm_excludes = {normalize_text_for_comparison(str(t)) for t in (prompt.exclude_texts or [])}
            b_clean = (prompt.bloom_level or "Understand").strip().title()

            if "physic" in subj:
                if b_clean == "Remember":
                    templates = [
                        f"State the foundational laws and definitions governing {prompt.unit_name} ({prompt.topic_name or 'Core Principles'}).",
                        f"Define the key physical quantities and SI units associated with {prompt.unit_name}.",
                        f"List the primary characteristics and operational principles of {prompt.unit_name}.",
                    ]
                    ans = f"Authoritative physical definitions, SI units, and foundational laws of {prompt.unit_name}."
                elif b_clean == "Apply":
                    templates = [
                        f"Calculate the resulting physical quantities in a standard system governed by {prompt.unit_name} ({prompt.topic_name or 'Calculations'}).",
                        f"Determine the magnitude and direction of physical parameters applying the laws of {prompt.unit_name}.",
                        f"Apply the governing equations of {prompt.unit_name} to solve for unknown variables under given boundary conditions.",
                    ]
                    ans = f"Step-by-step mathematical calculation and procedural application of governing formulas in {prompt.unit_name}."
                elif b_clean == "Analyze":
                    templates = [
                        f"Analyze the relationship between varying physical parameters and their systemic impact in {prompt.unit_name}.",
                        f"Compare and contrast the behavior and operational characteristics of different configurations in {prompt.unit_name}.",
                        f"Examine the experimental observations and functional dependencies established in {prompt.unit_name}.",
                    ]
                    ans = f"In-depth physical analysis examining parameter dependencies, comparative states, and systemic behavior in {prompt.unit_name}."
                elif b_clean in ("Evaluate", "Create"):
                    templates = [
                        f"Evaluate the validity and practical significance of theoretical approximations used in {prompt.unit_name}.",
                        f"Critically assess the effectiveness and limitations of standard models describing {prompt.unit_name}.",
                        f"Justify the necessity of conservation principles and boundary conditions in {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative judgment and critical assessment of theoretical validity, model assumptions, and practical constraints in {prompt.unit_name}."
                else:
                    templates = [
                        f"Explain the physical principles and underlying mechanisms of {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}).",
                        f"Describe the working principle and physical significance of {prompt.unit_name} with relevant equations.",
                        f"Differentiate between the primary phenomena and operational states observed in {prompt.unit_name}.",
                    ]
                    ans = f"Conceptual explanation of underlying physical principles, working mechanisms, and governing equations of {prompt.unit_name}."

            elif "chem" in subj:
                if b_clean == "Remember":
                    templates = [
                        f"State the fundamental laws, definitions, and nomenclature rules associated with {prompt.unit_name}.",
                        f"Define the key chemical terms and thermodynamic parameters governing {prompt.unit_name}.",
                        f"List the primary reagents, reaction conditions, and products characteristic of {prompt.unit_name}.",
                    ]
                    ans = f"Authoritative chemical definitions, nomenclature, and foundational rules of {prompt.unit_name}."
                elif b_clean == "Apply":
                    templates = [
                        f"Write the balanced chemical equations and reaction steps for the transformations characteristic of {prompt.unit_name}.",
                        f"Calculate the quantitative parameters (yield, equilibrium, or cell potential) for chemical systems in {prompt.unit_name}.",
                        f"Apply the chemical principles of {prompt.unit_name} to predict the major products and intermediates of given reactions.",
                    ]
                    ans = f"Balanced chemical reactions, stoichiometry, and quantitative application of principles in {prompt.unit_name}."
                elif b_clean == "Analyze":
                    templates = [
                        f"Analyze the influence of electronic, steric, and thermodynamic factors on the reactivity trends in {prompt.unit_name}.",
                        f"Compare and contrast the chemical behavior and stability of different species or functional groups in {prompt.unit_name}.",
                        f"Examine the experimental evidence supporting the proposed mechanisms and rate laws in {prompt.unit_name}.",
                    ]
                    ans = f"Detailed chemical analysis examining electronic effects, thermodynamic stability, and reaction pathway mechanisms in {prompt.unit_name}."
                elif b_clean in ("Evaluate", "Create"):
                    templates = [
                        f"Evaluate the effectiveness and environmental sustainability of synthetic pathways and catalytic methods in {prompt.unit_name}.",
                        f"Critically assess the validity of theoretical models in explaining anomalous trends in {prompt.unit_name}.",
                        f"Justify the choice of specific reagents and reaction conditions over alternative routes in {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative assessment of synthetic efficiency, environmental green metrics, and theoretical model validity in {prompt.unit_name}."
                else:
                    templates = [
                        f"Explain the reaction mechanisms and electronic factors governing {prompt.unit_name} ({prompt.topic_name or 'Core Mechanisms'}).",
                        f"Describe the structural features, bonding characteristics, and physical properties of compounds in {prompt.unit_name}.",
                        f"Differentiate between competing pathways and molecular behaviors observed in {prompt.unit_name}.",
                    ]
                    ans = f"Comprehensive chemical explanation detailing mechanisms, bonding theories, and structural characteristics in {prompt.unit_name}."

            elif "computer" in subj or "programming" in subj or re.search(r"\b(cs|ip|it)\b", subj):
                if b_clean == "Remember":
                    templates = [
                        f"Define the primary syntax, data structures, and architectural principles of {prompt.unit_name}.",
                        f"State the key terminology, scoping rules, and execution constraints associated with {prompt.unit_name}.",
                        f"List the essential built-in methods, operators, and protocols supported in {prompt.unit_name}.",
                    ]
                    ans = f"Authoritative technical definitions, syntax rules, and architectural standards of {prompt.unit_name}."
                elif b_clean == "Apply":
                    templates = [
                        f"Write a Python program implementing the core computational logic prescribed in {prompt.unit_name}.",
                        f"Write a Python script to process and manipulate structured data applying the conventions of {prompt.unit_name}.",
                        f"Apply the algorithmic principles of {prompt.unit_name} to construct an efficient software solution.",
                    ]
                    ans = f"Functional code implementation and algorithmic solution executing specifications of {prompt.unit_name}."
                elif b_clean == "Analyze":
                    templates = [
                        f"Analyze the time and space complexity trade-offs of different implementations in {prompt.unit_name}.",
                        f"Compare and contrast the structural efficiency and execution paradigms utilized in {prompt.unit_name}.",
                        f"Examine the debugging techniques and error-handling mechanisms required to ensure robust execution in {prompt.unit_name}.",
                    ]
                    ans = f"Algorithmic analysis examining asymptotic complexity, structural paradigms, and robustness in {prompt.unit_name}."
                elif b_clean in ("Evaluate", "Create"):
                    templates = [
                        f"Evaluate the effectiveness and design robustness of object-oriented architectures versus procedural approaches in {prompt.unit_name}.",
                        f"Critically assess the security implications, data integrity risks, and optimization trade-offs in {prompt.unit_name}.",
                        f"Justify the selection of specific algorithmic strategies or data structures for large-scale problem solving in {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative judgment of architectural design, security posture, and computational efficiency in {prompt.unit_name}."
                else:
                    templates = [
                        f"Explain the core working mechanism, data flow, and memory organization of {prompt.unit_name}.",
                        f"Describe how computational components interact and maintain structural integrity in {prompt.unit_name}.",
                        f"Differentiate between alternative design patterns and execution strategies available in {prompt.unit_name}.",
                    ]
                    ans = f"Technical explanation of data structures, execution pipelines, and computational abstractions in {prompt.unit_name}."

            else:
                # Dynamic templates for remaining subjects (English, Social Science, Biology, Economics, Commerce, etc.) when pools are exhausted
                if b_clean == "Remember":
                    templates = [
                        f"Define {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}) and state its primary characteristics.",
                        f"List the main components and key terms associated with {prompt.unit_name}.",
                        f"State the foundational definitions and rules governing {prompt.unit_name}.",
                        f"Mention any three key attributes or factors relevant to {prompt.unit_name}.",
                        f"Name the primary classifications or categories of {prompt.unit_name}.",
                        f"Identify the fundamental assumptions underlying {prompt.unit_name}.",
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
                        ]
                        ans = f"Detailed solution applying the foundational rules, formulas, and methods of {prompt.unit_name}."
                elif b_clean == "Analyze":
                    templates = [
                        f"Analyze the relationship and critical factors governing {prompt.unit_name} ({prompt.topic_name or 'Core Concepts'}).",
                        f"Compare and contrast the primary mechanisms or categories established in {prompt.unit_name}.",
                        f"Examine the underlying causes and differential outcomes in {prompt.unit_name}.",
                        f"Analyze the comparative advantages and operational differences found in {prompt.unit_name}.",
                    ]
                    ans = f"In-depth analysis examining key components, causal factors, and comparative features of {prompt.unit_name}."
                elif b_clean in ("Evaluate", "Create"):
                    templates = [
                        f"Evaluate the effectiveness and practical significance of {prompt.unit_name} in its specific domain.",
                        f"Critically assess the validity and impact of theoretical principles in {prompt.unit_name}.",
                        f"Justify the necessity of key frameworks and methods established in {prompt.unit_name}.",
                        f"Assess the significance and consequences of core developments in {prompt.unit_name}.",
                    ]
                    ans = f"Evaluative assessment or constructive framework addressing the core challenges of {prompt.unit_name}."
                else:
                    templates = [
                        f"Explain the core principles and concepts of {prompt.unit_name} ({prompt.topic_name or 'Key Topics'}) and their practical significance.",
                        f"Describe the main processes and features associated with {prompt.unit_name}.",
                        f"Summarize the essential definitions, laws, and applications prescribed in {prompt.unit_name}.",
                        f"Illustrate the fundamental mechanism of {prompt.unit_name} with suitable explanations.",
                    ]
                    ans = f"Detailed academic explanation covering key concepts, definitions, and applications of {prompt.unit_name}."

            unex_templates = [t for t in templates if normalize_text_for_comparison(t) not in norm_excludes]
            if unex_templates:
                q_text = random.choice(unex_templates)
            else:
                # All distinct fallback templates for this cognitive level have been exhausted.
                # Do NOT pad or fabricate questions with superficial suffixes or (Part X) variants.
                return None


        return GeneratedQuestionResult(
            question_text=q_text,
            answer=ans,
            explanation=f"Generated for cognitive level '{b_lvl}' matching target difficulty '{prompt.difficulty}'.",
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
