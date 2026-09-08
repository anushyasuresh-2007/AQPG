# Phase 15 Source Provenance, Licensing & Normalization Mapping

This document specifies the exact mapping rules, provenance verification, and schema normalization protocols for Phase 15.

---

## 1. Upstream Source Registry

| Raw File | Primary Source | License | Verified | Provenance URL | Standard Coverage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `openstax_physics_raw.json` | OpenStax University & College Physics | CC BY 4.0 | Yes | [OpenStax Science](https://openstax.org/subjects/science) | Mechanics, Thermo, Electromagnetism, Optics, Modern Physics |
| `mmlu_stem_expanded_raw.json` | MMLU STEM Subsets | MIT License | Yes | [HuggingFace cais/mmlu](https://huggingface.co/datasets/cais/mmlu) | High School & Senior Secondary Physics, Chemistry, Math, Biology |
| `ai2_arc_grounded_raw.json` | AI2 ARC Benchmark | CC BY-SA 4.0 | Yes | [HuggingFace allenai/ai2_arc](https://huggingface.co/datasets/allenai/ai2_arc) | Grade 9 & Grade 10 Secondary Science |
| `science_benchmarks_raw.json` | SciQ & OpenBookQA | CC BY-NC 3.0 / Apache 2.0 | Yes | [HuggingFace allenai/sciq](https://huggingface.co/datasets/allenai/sciq) | General Science, Chemistry, Physics, Biology |
| `ncert_exemplar_class9_12_raw.json`| NCERT Exemplar & Benchmark | CC BY-NC 4.0 | Yes | [NCERT Official Portal](https://ncert.nic.in) | Class 9–12 CBSE Official Exemplar |
| `gsm8k_reasoning_all.csv` | OpenAI GSM8K | MIT License | Yes | [GitHub GSM8K](https://github.com/openai/grade-school-math) | Mathematical Reasoning & Numerical Word Problems |
| `eduqg_train_val.json` | OpenStax EduQG | CC BY 4.0 | Yes | [OpenStax Textbooks](https://openstax.org) | Higher Education & Secondary Curriculum |
| `blooms_taxonomy_dataset.csv` | Kaggle Bloom Benchmark | Public Domain | Yes | [Kaggle Benchmark](https://www.kaggle.com) | Cognitive Skill Progression |

---

## 2. Deterministic Mapping Rules

### A. Subject Mapping
- `Physics`: Mechanics, Thermodynamics, Waves & Optics, Electromagnetism, Modern Physics, Astronomy, Electrical Engineering.
- `Mathematics`: Arithmetic, Algebra, Geometry, Calculus, Mathematical Reasoning.
- `Chemistry`: Stoichiometry, Organic/Inorganic Chemistry, Chemical Reactions, Thermodynamics.
- `Biology`: Cellular Biology, Genetics, Ecology, Anatomy, Physiology.
- `General Science`: Integrated Secondary Natural Science.
- `Social Science`: Sociology, Psychology.
- `Business & Law`: Business, Accounting, Legal Studies.
- `History & Civics`: History, Government, Civics.
- `UNKNOWN`: Unspecified / Generic Prompts.

### B. Class Grounding Mapping
- `Class 9`: Grade 9 standard (ARC-Challenge, MMLU Elementary Math, NCERT Class 9).
- `Class 10`: Secondary Grade 10 science standard (ARC-Challenge Secondary, NCERT Class 10 Exemplar).
- `Class 11`: High School STEM standard (MMLU High School Physics/Chem/Math/Bio, OpenStax Mechanics/Thermo, NCERT Class 11).
- `Class 12`: Senior Secondary STEM standard (MMLU College Physics/Chem/Math, OpenStax Electromagnetism/Optics/Modern Physics, NCERT Class 12).
- `UNKNOWN`: Retained when single-grade alignment cannot be established from source structure.

### C. Board Grounding Mapping
- `CBSE`: NCERT Exemplar materials.
- `State Board`: Explicit State Board materials.
- `OpenStax Academic`: OpenStax textbook corpora.
- `Public Benchmark`: GSM8K, SciQ, AI2 ARC, MMLU, OpenBookQA.
- `UNKNOWN`: Unspecified.
