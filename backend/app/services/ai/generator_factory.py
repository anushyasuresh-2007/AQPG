"""AI Question Generator factory and multi-provider orchestrator with graceful fallback."""

import os
import random
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

        # Subject-specific realistic questions
        if "math" in subj:
            # Check unit category for unit-grounded fallback templates
            if "coordinate" in u_lower:
                if marks <= 2:
                    p1 = (random.randint(1, 5), random.randint(1, 5))
                    p2 = (p1[0] + 3, p1[1] + 4)
                    q_text = f"Find the distance between the points A({p1[0]}, {p1[1]}) and B({p2[0]}, {p2[1]}) in the coordinate plane."
                    ans = f"Distance d = √[({p2[0]}-{p1[0]})² + ({p2[1]}-{p1[1]})²] = √(3² + 4²) = √25 = 5 units."
                elif marks <= 4:
                    q_text = f"Find the coordinates of the point P which divides the line segment joining A(-1, 7) and B(4, -3) in the ratio 2:3 internally."
                    ans = f"Using Section Formula x = (m1*x2 + m2*x1)/(m1+m2) = (2*4 + 3*-1)/5 = 1, y = (2*-3 + 3*7)/5 = 3. Point P is (1, 3)."
                else:
                    q_text = f"Determine the ratio in which the line 2x + y - 4 = 0 divides the line segment joining the points A(2, -2) and B(3, 7)."
                    ans = f"Let ratio be k:1. Point on line is P((3k+2)/(k+1), (7k-2)/(k+1)). Substituting into line equation gives k = 2/9."

            elif any(w in u_lower for w in ["trigonometry", "height", "distance"]):
                if marks <= 2:
                    q_text = f"Evaluate the trigonometric expression: 2 tan²(45°) + cos²(30°) - sin²(60°)."
                    ans = f"2(1)² + (√3/2)² - (√3/2)² = 2 + 3/4 - 3/4 = 2."
                elif marks <= 4:
                    q_text = f"A tower stands vertically on the ground. From a point on the ground 15 m away from the foot of the tower, the angle of elevation of the top of the tower is 60°. Find the height of the tower."
                    ans = f"tan(60°) = h / 15 => √3 = h / 15 => h = 15√3 m ≈ 25.98 m."
                else:
                    q_text = f"Prove the trigonometric identity: (sin θ - 2 sin³ θ) / (2 cos³ θ - cos θ) = tan θ."
                    ans = f"LHS = sin θ(1 - 2 sin² θ) / cos θ(2 cos² θ - 1) = tan θ(cos 2θ / cos 2θ) = tan θ = RHS."

            elif any(w in u_lower for w in ["statistic", "probability", "data"]):
                if marks <= 2:
                    q_text = f"A die is thrown once. Find the probability of getting a prime number."
                    ans = f"Total outcomes = 6. Prime numbers = {{2, 3, 5}} (3 outcomes). P(prime) = 3/6 = 1/2."
                elif marks <= 4:
                    q_text = f"A box contains 90 discs numbered 1 to 90. If one disc is drawn at random from the box, find the probability that it bears a two-digit number."
                    ans = f"Total outcomes = 90. Two-digit numbers = 10 to 90 (81 outcomes). P(two-digit) = 81/90 = 9/10."
                else:
                    q_text = f"Find the mean of the following frequency distribution: Class intervals 0-10, 10-20, 20-30, 30-40, 40-50 with frequencies 5, 8, 15, 12, 10 respectively."
                    ans = f"Using ∑(f*x)/∑f: Midpoints x = 5, 15, 25, 35, 45. ∑(f*x) = 25+120+375+420+450 = 1390. ∑f = 50. Mean = 1390/50 = 27.8."

            elif any(w in u_lower for w in ["quadratic", "algebra", "polynomial", "equation"]):
                if marks <= 2:
                    val_x = random.randint(2, 9)
                    val_a = random.choice([2, 3, 4, 5])
                    val_b = random.randint(1, 12)
                    q_text = f"Find the zeros of the linear polynomial {val_a}x - {val_b} and verify the result."
                    ans = f"{val_a}x - {val_b} = 0 => x = {val_b}/{val_a}."
                elif marks <= 4:
                    quads = [
                        {"eq": "x² - 5x + 6 = 0", "ans": "x = 2 or x = 3", "d": "25 - 24 = 1"},
                        {"eq": "2x² - 5x + 2 = 0", "ans": "x = 2 or x = 1/2", "d": "25 - 16 = 9"},
                        {"eq": "x² - 7x + 12 = 0", "ans": "x = 3 or x = 4", "d": "49 - 48 = 1"},
                        {"eq": "x² - 8x + 15 = 0", "ans": "x = 3 or x = 5", "d": "64 - 60 = 4"},
                    ]
                    selected = random.choice(quads)
                    q_text = f"Solve the quadratic equation {selected['eq']} using the quadratic formula and state the nature of roots."
                    ans = f"Using x = [-b ± √(b² - 4ac)] / 2a, D = {selected['d']} > 0. Roots are real and distinct: {selected['ans']}."
                else:
                    q_text = f"The sum of the reciprocals of Rehman's ages 3 years ago and 5 years from now is 1/3. Find his present age."
                    ans = f"Let present age be x. 1/(x-3) + 1/(x+5) = 1/3 => x² - 4x - 21 = 0 => (x-7)(x+3) = 0 => x = 7 years."

            elif any(w in u_lower for w in ["number", "sequence", "progression", "arithmetic", "real"]):
                if marks <= 2:
                    q_text = f"Find the HCF and LCM of 96 and 404 using the prime factorization method."
                    ans = f"96 = 2⁵ * 3, 404 = 2² * 101. HCF = 2² = 4. LCM = (96 * 404) / 4 = 9696."
                elif marks <= 4:
                    q_text = f"Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18..."
                    ans = f"First term a = 3, common difference d = 5. a_20 = a + 19d = 3 + 19(5) = 3 + 95 = 98."
                else:
                    q_text = f"Prove that √5 is an irrational number using the method of contradiction."
                    ans = f"Assume √5 = a/b co-prime. 5b² = a² => 5 divides a. Let a = 5c => 5b² = 25c² => b² = 5c² => 5 divides b. Contradicts co-prime assumption. Thus √5 is irrational."

            elif any(w in u_lower for w in ["circle", "similarity", "theorem"]):
                if marks <= 2:
                    q_text = f"State the Basic Proportionality Theorem (Thales Theorem) for triangles."
                    ans = f"If a line is drawn parallel to one side of a triangle to intersect the other two sides in distinct points, the other two sides are divided in the same ratio."
                elif marks <= 4:
                    q_text = f"Prove that the lengths of tangents drawn from an external point to a circle are equal."
                    ans = f"Let PA and PB be tangents from P to circle O. In △OAP and △OBP: OA = OB (radii), OP = OP (common), ∠OAP = ∠OBP = 90°. RHS congruence => PA = PB."
                else:
                    q_text = f"State and prove Pythagoras Theorem for a right-angled triangle."
                    ans = f"Statement: In a right triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides. Proof via similar triangles △ABD ~ △ABC and △CBD ~ △ABC."

            elif any(w in u_lower for w in ["mensuration", "surface area", "volume"]):
                if marks <= 2:
                    q_text = f"Find the area of a sector of a circle of radius 6 cm if the central angle is 60°."
                    ans = f"Area = (θ/360°) * π * r² = (60/360) * (22/7) * 36 = 18.86 cm²."
                elif marks <= 4:
                    q_text = f"A solid is in the shape of a cone standing on a hemisphere with both their radii being equal to 1 cm and the height of the cone is equal to its radius. Find the volume of the solid in terms of π."
                    ans = f"Volume = V_cone + V_hemisphere = (1/3)πr²h + (2/3)πr³ = (1/3)π(1)³ + (2/3)π(1)³ = π cm³."
                else:
                    q_text = f"A wooden article was made by scooping out a hemisphere from each end of a solid cylinder of height 10 cm and base radius 3.5 cm. Find the total surface area of the article."
                    ans = f"TSA = CSA of cylinder + 2 * CSA of hemisphere = 2πrh + 2*(2πr²) = 2πr(h + 2r) = 2*(22/7)*3.5*(10 + 7) = 374 cm²."

            elif any(w in u_lower for w in ["relation", "function", "set"]):
                if marks <= 2:
                    q_text = f"Determine whether the relation R in the set Z of integers defined by R = {{(x,y): x - y is an integer}} is reflexive and symmetric."
                    ans = f"Reflexive: x - x = 0 (integer) => (x,x) ∈ R. Symmetric: if x - y = k, y - x = -k (integer) => (y,x) ∈ R. Both hold."
                else:
                    q_text = f"Show that the function f: R -> R defined by f(x) = 3x + 2 is one-one and onto (bijective)."
                    ans = f"One-one: f(x1)=f(x2) => 3x1+2=3x2+2 => x1=x2. Onto: For any y ∈ R, x = (y-2)/3 ∈ R such that f(x)=y."

            else:
                # Unmapped math unit: return Controlled Fallback Failure rather than generating an unrelated quadratic question!
                return None

        elif "physic" in subj:
            if marks <= 2:
                forces = [10, 15, 20, 25, 30]
                disps = [2, 3, 4, 5, 8]
                f = random.choice(forces)
                d = random.choice(disps)
                q_text = f"State the formula for work done and calculate the work when a force of {f} N displaces a body by {d} m in the direction of force ({prompt.unit_name})."
                ans = f"Work W = F * d = {f} N * {d} m = {f * d} Joules."
            elif marks <= 4:
                phys_short = [
                    {"mass": 5, "v": 20, "t": 4, "f": 25, "ke": 1000},
                    {"mass": 2, "v": 10, "t": 2, "f": 10, "ke": 100},
                    {"mass": 10, "v": 30, "t": 5, "f": 60, "ke": 4500},
                    {"mass": 4, "v": 16, "t": 4, "f": 16, "ke": 512},
                ]
                selected = random.choice(phys_short)
                q_text = f"A body of mass {selected['mass']} kg is accelerated from rest to {selected['v']} m/s in a time interval of {selected['t']} seconds. Calculate the net force and kinetic energy acquired ({prompt.unit_name})."
                ans = f"Acceleration a = v/t = {selected['v']}/{selected['t']} = {selected['v']/selected['t']} m/s². Force F = m*a = {selected['mass']}*{selected['v']/selected['t']} = {selected['f']} N. KE = 0.5*m*v² = {selected['ke']} J."
            else:
                phys_long = [
                    {"r": 20, "i": 15, "t": 2, "p": 4500, "e": 9.0},
                    {"r": 10, "i": 10, "t": 3, "p": 1000, "e": 3.0},
                    {"r": 30, "i": 20, "t": 1.5, "p": 12000, "e": 18.0},
                ]
                selected = random.choice(phys_long)
                q_text = f"An electric heater of resistance {selected['r']} Ohms draws a current of {selected['i']} A from the service mains. Calculate the rate at which heat is developed in the heater over {selected['t']} hours and total electrical energy in kWh ({prompt.unit_name})."
                ans = f"Rate of heat P = I²R = {selected['i']}² * {selected['r']} = {selected['p']} W. Energy E = P * t = {selected['p']/1000} kW * {selected['t']} h = {selected['e']} kWh."
        elif "chem" in subj:
            if marks <= 2:
                reactions = [
                    {"eq": "CaCO3(s) --[Heat]--> CaO(s) + CO2(g)", "sub": "calcium carbonate"},
                    {"eq": "2Pb(NO3)2(s) --[Heat]--> 2PbO(s) + 4NO2(g) + O2(g)", "sub": "lead nitrate"},
                    {"eq": "2FeSO4(s) --[Heat]--> Fe2O3(s) + SO2(g) + SO3(g)", "sub": "ferrous sulphate"},
                ]
                sel = random.choice(reactions)
                q_text = f"Write the balanced chemical equation for the thermal decomposition of {sel['sub']} on heating ({prompt.unit_name})."
                ans = f"Chemical equation: {sel['eq']}."
            elif marks <= 4:
                moles = [
                    {"mass": 44, "gas": "Carbon Dioxide (CO2)", "molar": 44, "n": 1.0},
                    {"mass": 18, "gas": "Water Vapor (H2O)", "molar": 18, "n": 1.0},
                    {"mass": 36, "gas": "Water Vapor (H2O)", "molar": 18, "n": 2.0},
                    {"mass": 17, "gas": "Ammonia (NH3)", "molar": 17, "n": 1.0},
                    {"mass": 32, "gas": "Oxygen Gas (O2)", "molar": 32, "n": 1.0},
                ]
                sel = random.choice(moles)
                q_text = f"Calculate the number of moles and molecules present in {sel['mass']} grams of {sel['gas']} gas ({prompt.unit_name})."
                ans = f"Molar mass of {sel['gas']} = {sel['molar']} g/mol. Moles n = {sel['mass']}/{sel['molar']} = {sel['n']} mol. Molecules = {sel['n']} * 6.022 * 10²³ = {sel['n'] * 6.022} * 10²³ molecules."
            else:
                chem_long = [
                    "Explain the principle of electrolytic refining of copper with a neat labeled diagram and reactions occurring at cathode and anode.",
                    "Describe the Haber process for industrial synthesis of ammonia, including the balanced chemical equation, optimal pressure/temperature, and catalyst used.",
                    "Explain the extraction of zinc from zinc blende ore, describing the roasting, reduction, and refining reactions with balanced equations."
                ]
                q_text = f"{random.choice(chem_long)} ({prompt.unit_name})."
                ans = "Detailed description covering industrial parameters, anode/cathode half-reactions, and chemical equations."
        elif "computer" in subj or "cs" in subj:
            if marks <= 2:
                cs_shorts = [
                    {"expr": "[x**2 for x in range(5) if x % 2 != 0]", "ans": "[1, 9] (squares of odd numbers 1 and 3)"},
                    {"expr": "[x + 10 for x in [1, 2, 3]]", "ans": "[11, 12, 13]"},
                    {"expr": "str(1234)[::-1]", "ans": "'4321' (reversed string representation)"},
                    {"expr": "set([1, 2, 2, 3, 3, 3])", "ans": "{1, 2, 3} (unique elements)"},
                ]
                sel = random.choice(cs_shorts)
                q_text = f"What will be the output of the Python expression: `print({sel['expr']})`? ({prompt.unit_name})"
                ans = f"Output: {sel['ans']}."
            else:
                cs_longs = [
                    {"desc": "Write a Python function to search for a record in a binary file 'STUDENT.DAT' based on admission number.", "code": "import pickle\ndef search_record(adm_no):\n  with open('STUDENT.DAT', 'rb') as f:\n    try:\n      while True:\n        rec = pickle.load(f)\n        if rec['adm_no'] == adm_no: return rec\n    except EOFError: return None"},
                    {"desc": "Write a Python function to count the occurrences of words starting with an uppercase letter in a text file 'STORY.TXT'.", "code": "def count_caps():\n  with open('STORY.TXT', 'r') as f:\n    words = f.read().split()\n    return sum(1 for w in words if w and w[0].isupper())"},
                    {"desc": "Write a Python function to insert and retrieve student names using a stack structure.", "code": "stack = []\ndef push_name(name):\n  stack.append(name)\ndef pop_name():\n  return stack.pop() if stack else None"},
                ]
                sel = random.choice(cs_longs)
                q_text = f"{sel['desc']} ({prompt.unit_name})"
                ans = f"Code solution:\n{sel['code']}"
        else:
            templates = [
                f"Analyze the key concepts of {prompt.unit_name} ({prompt.topic_name or 'Core Syllabus'}) and explain their practical implications ({prompt.board} {prompt.class_name}).",
                f"Critically evaluate the significance of {prompt.unit_name} in modern academic and real-world contexts, illustrating with suitable examples.",
                f"Discuss the foundational principles and historical evolution of {prompt.unit_name} and describe how it shapes current methodology.",
                f"Formulate a detailed case study illustrating the core components of {prompt.unit_name} and propose solutions to associated challenges."
            ]
            q_text = random.choice(templates)
            ans = f"Detailed explanation covering core pedagogical principles of {prompt.unit_name} with relevant real-world illustrations."

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
