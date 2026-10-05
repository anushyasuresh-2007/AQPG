"""AQPG V17.2 Model Local Inference Adapter.

Provides a safe, read-only inference interface for the fine-tuned V17.2 FLAN-T5 model.
Enforces strict read-only guarantees:
- Never trains
- Never modifies checkpoints or datasets
- Never downloads remote models (local_files_only=True)
- Fails safely with explicit RuntimeError if V17.2 local weights are not present
"""

import hashlib
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import torch

from app.services.ai.base import AIQuestionPrompt, BaseAIProvider, GeneratedQuestionResult

EXPECTED_V17_2_FILE_HASHES = {
    "config.json": "8175ff688ac72a8aeb00416a323fb536a51f25b3e4b28eea48ab9efaee3047cd",
    "generation_config.json": "196b3297c73e8b686aa1c3bc1fe99b17362ddd682354a710a6f07c697eb6e273",
    "model.safetensors": "e2cfed7ba5fd44ea31c67e352985e42072fb6532ce96222769b573530d3b4954",
    "special_tokens_map.json": "65d84a9271d68f1230ab99518c00f0f7eaef95c7b363001595ba6fa662d434b1",
    "tokenizer.json": "8c3804f01b141a4f28649b2ff899f7eb3bedad28fd898f8c38b7dbc70db700bf",
    "tokenizer_config.json": "ebc3fede7a53346b49346d8e8fbb7d664b9b448f559660c36195bb19e2d5eaaa",
}

DEFAULT_V17_2_PATHS = [
    "backend/ml/models/checkpoints/flan_t5_v17_2/best_model",
    "backend/ml/models/checkpoints/flan_t5_v17_2",
]


def verify_v17_2_checkpoint(path: str) -> bool:
    """Verify the exact approved V17.2 checkpoint files and hashes."""
    checkpoint = Path(path)
    if not checkpoint.is_dir():
        return False

    for filename, expected_hash in EXPECTED_V17_2_FILE_HASHES.items():
        file_path = checkpoint / filename
        if not file_path.is_file():
            return False

        digest = hashlib.sha256()
        try:
            with file_path.open("rb") as artifact:
                for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
                    digest.update(chunk)
        except OSError:
            return False

        if digest.hexdigest() != expected_hash:
            return False

    return True


class V17_2InferenceAdapter(BaseAIProvider):
    """Read-only inference adapter for AQPG V17.2 FLAN-T5 question generation model."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize adapter and locate V17.2 checkpoint directory if present."""
        self.model_path = model_path or self._resolve_default_model_path()
        self.tokenizer = None
        self.model = None
        self._is_loaded = False

    def _resolve_default_model_path(self) -> Optional[str]:
        """Find local V17.2 model directory if valid weights exist."""
        # 0. Try explicit environment variable V17_2_MODEL_PATH if specified
        env_path = os.getenv("V17_2_MODEL_PATH")
        if env_path:
            abs_env_path = os.path.abspath(env_path)
            return abs_env_path if self._verify_checkpoint_integrity(abs_env_path) else None

        # 1. Try relative to __file__
        file_dir = os.path.dirname(os.path.abspath(__file__))
        rel_to_file = os.path.abspath(os.path.join(file_dir, "../../../ml/models/checkpoints/flan_t5_v17_2/best_model"))
        if self._verify_checkpoint_integrity(rel_to_file):
            return rel_to_file

        rel_to_file_parent = os.path.abspath(os.path.join(file_dir, "../../../ml/models/checkpoints/flan_t5_v17_2"))
        if self._verify_checkpoint_integrity(rel_to_file_parent):
            return rel_to_file_parent

        # 2. Try relative to CWD
        cwd = os.getcwd()
        for rel_path in DEFAULT_V17_2_PATHS:
            abs_path = os.path.abspath(os.path.join(cwd, rel_path))
            if self._verify_checkpoint_integrity(abs_path):
                return abs_path
        return None

    def _verify_checkpoint_integrity(self, path: str) -> bool:
        """Verify that the exact approved V17.2 checkpoint is present."""
        return bool(path) and verify_v17_2_checkpoint(path)

    def is_available(self) -> bool:
        """Return True only if a valid V17.2 model path with weight files is present."""
        if not self.model_path:
            return False
        return self._verify_checkpoint_integrity(self.model_path)

    def load_model(self) -> bool:
        """Load local V17.2 tokenizer and model using HuggingFace transformers with local_files_only=True."""
        if not self.is_available():
            raise RuntimeError(
                f"V17.2 local model weights are not available at path '{self.model_path}'. No inference was performed."
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
                f"Failed to load V17.2 local model weights from '{self.model_path}': {exc}"
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
        difficulty: str = "Medium",
        marks: int = 3,
        question_type: str = "Conceptual",
        bloom_level: str = "Understand",
        prompt: Optional[AIQuestionPrompt] = None,
    ) -> GeneratedQuestionResult:
        """Generate a question using V17.2 local model."""
        if not self._is_loaded:
            self.load_model()

        if prompt is not None:
            subj = prompt.subject_name
            topics_str = ", ".join(prompt.topics_list) if getattr(prompt, "topics_list", None) else (prompt.topic_name or "")
            top = f"{prompt.unit_name} - {topics_str}" if topics_str else prompt.unit_name
            diff = prompt.difficulty
            q_type = prompt.question_type
            m = prompt.marks
            b_lvl = prompt.bloom_level
            cls_lvl = getattr(prompt, "class_name", "Class 10")
            unit_n = prompt.unit_name
        else:
            subj = subject or "Science"
            top = topic or "General Science"
            diff = difficulty
            q_type = question_type
            m = marks
            b_lvl = bloom_level
            cls_lvl = "Class 10"
            unit_n = top

        # Canonical 8-tag V17.2 Prompt Format
        prompt_text = (
            f"generate question | subject: {subj} | topic: {top} | class: {cls_lvl} | "
            f"difficulty: {diff} | marks: {m} | type: {q_type} | bloom: {b_lvl}"
        )

        inputs = self.tokenizer(prompt_text, return_tensors="pt", max_length=256, truncation=True)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=128,
            )

        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        return GeneratedQuestionResult(
            question_text=generated_text,
            answer=f"Reference answer for {q_type} question on {top}.",
            explanation=f"Generated by V17.2 local model checkpoint at {self.model_path}",
            question_type=q_type,
            marks=m,
            difficulty=diff,
            bloom=b_lvl,
            unit_name=unit_n,
            topic_name=top,
        )

    def generate_batch(self, prompts: List[AIQuestionPrompt]) -> List[GeneratedQuestionResult]:
        """Generate multiple questions for a list of prompts."""
        return [self.generate_question(prompt=p) for p in prompts]
