"""AQPG V17.1 Model Local Inference Adapter.

Provides a safe, read-only inference interface for the fine-tuned V17.1 FLAN-T5 model.
Enforces strict read-only guarantees:
- Never trains
- Never modifies checkpoints or datasets
- Never downloads remote models (local_files_only=True)
- Fails safely with explicit RuntimeError if V17.1 local weights are not present
"""

import os
from typing import Any, Dict, List, Optional

from app.services.ai.base import AIQuestionPrompt, BaseAIProvider, GeneratedQuestionResult

REQUIRED_CHECKPOINT_FILES = [
    "config.json",
    ["model.safetensors", "pytorch_model.bin"],
]

DEFAULT_V17_1_PATHS = [
    "backend/ml/models/checkpoints/flan_t5_v17/best_model",
    "backend/ml/models/checkpoints/flan_t5_v17",
    "backend/ml/models/checkpoints/flan_t5_v17_1",
    "phase21_v17_gpu_training_output",
]


class V17_1InferenceAdapter(BaseAIProvider):
    """Read-only inference adapter for AQPG V17.1 FLAN-T5 question generation model."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize adapter and locate V17.1 checkpoint directory if present."""
        self.model_path = model_path or self._resolve_default_model_path()
        self.tokenizer = None
        self.model = None
        self._is_loaded = False

    def _resolve_default_model_path(self) -> Optional[str]:
        """Find local V17.1 model directory if valid weights exist."""
        cwd = os.getcwd()
        for rel_path in DEFAULT_V17_1_PATHS:
            abs_path = os.path.abspath(os.path.join(cwd, rel_path))
            if self._verify_checkpoint_integrity(abs_path):
                return abs_path
        return None

    def _verify_checkpoint_integrity(self, path: str) -> bool:
        """Verify that directory exists and contains complete model files."""
        if not os.path.exists(path) or not os.path.isdir(path):
            return False

        for req in REQUIRED_CHECKPOINT_FILES:
            if isinstance(req, list):
                if not any(os.path.exists(os.path.join(path, f)) for f in req):
                    return False
            else:
                if not os.path.exists(os.path.join(path, req)):
                    return False
        return True

    def is_available(self) -> bool:
        """Return True only if a valid V17.1 model path with weight files is present."""
        if not self.model_path:
            return False
        return self._verify_checkpoint_integrity(self.model_path)

    def load_model(self) -> bool:
        """Load local V17.1 tokenizer and model using HuggingFace transformers with local_files_only=True."""
        if not self.is_available():
            raise RuntimeError(
                "V17.1 local model weights are not available. No inference was performed."
            )

        if self._is_loaded:
            return True

        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                self.model_path,
                local_files_only=True,
            )
            self.model.eval()
            self._is_loaded = True
            return True
        except Exception as exc:
            self._is_loaded = False
            raise RuntimeError(
                f"Failed to load V17.1 local model weights from '{self.model_path}': {exc}"
            ) from exc

    def unload_model(self) -> None:
        """Unload model from memory if loaded."""
        self.model = None
        self.tokenizer = None
        self._is_loaded = False

    def generate_question(
        self,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = "medium",
        question_type: Optional[str] = "Conceptual",
        marks: Optional[int] = 2,
        bloom_level: Optional[str] = "Understand",
        additional_context: Optional[str] = None,
        prompt: Optional[AIQuestionPrompt] = None,
    ) -> GeneratedQuestionResult:
        """
        Generate a question using V17.1 local model.
        Fails safely if V17.1 weights are absent.
        """
        if not self.is_available():
            raise RuntimeError(
                "V17.1 local model weights are not available. No inference was performed."
            )

        if not self._is_loaded:
            self.load_model()

        if prompt is not None:
            subj = prompt.subject_name
            top = prompt.topic_name or prompt.unit_name
            diff = prompt.difficulty
            q_type = prompt.question_type
            m = prompt.marks
            b_lvl = prompt.bloom_level
            ctx = getattr(prompt, "additional_context", None)
        else:
            subj = subject or "Science"
            top = topic or "General"
            diff = difficulty or "medium"
            q_type = question_type or "Conceptual"
            m = marks if marks is not None else 2
            b_lvl = bloom_level or "Understand"
            ctx = additional_context

        prompt_text = f"generate question | subject: {subj} | topic: {top} | class: Class 10 | difficulty: {diff} | marks: {m} | type: {q_type} | bloom: {b_lvl}"
        if ctx:
            prompt_text += f" | context: {ctx}"

        import torch

        inputs = self.tokenizer(prompt_text, return_tensors="pt", max_length=256, truncation=True)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=64,
                num_beams=1,
                do_sample=False,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return GeneratedQuestionResult(
            question_text=generated_text,
            answer="",
            explanation=f"Generated by V17.1 local model checkpoint at {self.model_path}",
            question_type=q_type,
            marks=m,
            difficulty=diff,
            bloom=b_lvl,
            unit_name=top,
            topic_name=top,
        )

    def generate_batch(self, prompts: List[AIQuestionPrompt]) -> List[GeneratedQuestionResult]:
        """Generate multiple questions for a list of prompts."""
        return [self.generate_question(prompt=p) for p in prompts]
