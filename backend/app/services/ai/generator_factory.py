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

        # Subject-specific realistic questions
        if "math" in subj:
            from app.services.question_generator import classify_unit_category
            category = classify_unit_category(prompt.unit_name, prompt.unit_description, prompt.topics_list)

            # Check unit category for unit-grounded fallback templates
            if category == "COORDINATE_GEOMETRY":
                coord_templates = [
                    {
                        "q": "Find the distance between the points A(2, 3) and B(4, 1) in the Cartesian coordinate plane.",
                        "a": "Distance d = √[(4-2)² + (1-3)²] = √(2² + (-2)²) = √8 = 2√2 units."
                    },
                    {
                        "q": "Find the coordinates of the point P which divides the line segment joining A(-1, 7) and B(4, -3) in the ratio 2:3 internally.",
                        "a": "Using Section Formula: x = (2*4 + 3*-1)/5 = 1, y = (2*-3 + 3*7)/5 = 3. Point P is (1, 3)."
                    },
                    {
                        "q": "Determine the ratio in which the line 2x + y - 4 = 0 divides the line segment joining the points A(2, -2) and B(3, 7).",
                        "a": "Let ratio be k:1. Point on line is P((3k+2)/(k+1), (7k-2)/(k+1)). Substituting into line equation gives k = 2/9."
                    },
                    {
                        "q": "Find the midpoint of the line segment joining the points P(-5, 4) and Q(7, -8).",
                        "a": "Midpoint M = ((x1+x2)/2, (y1+y2)/2) = ((-5+7)/2, (4-8)/2) = (1, -2)."
                    },
                    {
                        "q": "Check whether the points A(1, 5), B(2, 3), and C(-2, -11) are collinear using distance formula or slopes.",
                        "a": "Slope AB = (3-5)/(2-1) = -2. Slope BC = (-11-3)/(-2-2) = -14/-4 = 7/2. Since slopes are not equal, points are not collinear."
                    },
                    {
                        "q": "Find the area of the triangle whose vertices are (2, 3), (-1, 0), and (2, -4) using coordinate geometry.",
                        "a": "Area = 0.5 * |x1(y2 - y3) + x2(y3 - y1) + x3(y1 - y2)| = 0.5 * |2(0 - (-4)) + (-1)(-4 - 3) + 2(3 - 0)| = 0.5 * |8 + 7 + 6| = 10.5 sq units."
                    },
                    {
                        "q": "Find the coordinates of the centroid of triangle ABC with vertices A(3, -5), B(-7, 4), and C(10, -2).",
                        "a": "Centroid G = ((3 - 7 + 10)/3, (-5 + 4 - 2)/3) = (6/3, -3/3) = (2, -1)."
                    },
                ]
                selected = random.choice(coord_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "TRIGONOMETRY":
                trig_templates = [
                    {
                        "q": "Evaluate the trigonometric expression: 2 tan²(45°) + cos²(30°) - sin²(60°).",
                        "a": "2(1)² + (√3/2)² - (√3/2)² = 2 + 3/4 - 3/4 = 2."
                    },
                    {
                        "q": "A tower stands vertically on the ground. From a point on the ground 15 m away from the foot of the tower, the angle of elevation of the top of the tower is 60°. Find the height of the tower.",
                        "a": "tan(60°) = h / 15 => √3 = h / 15 => h = 15√3 m ≈ 25.98 m."
                    },
                    {
                        "q": "Prove the trigonometric identity: (sin θ - 2 sin³ θ) / (2 cos³ θ - cos θ) = tan θ.",
                        "a": "LHS = sin θ(1 - 2 sin² θ) / [cos θ(2 cos² θ - 1)] = (sin θ / cos θ) * (cos 2θ / cos 2θ) = tan θ = RHS."
                    },
                    {
                        "q": "If sin(A - B) = 1/2 and cos(A + B) = 1/2 for 0° < A + B ≤ 90° and A > B, find the angles A and B.",
                        "a": "sin(A - B) = sin(30°) => A - B = 30°. cos(A + B) = cos(60°) => A + B = 60°. Adding gives 2A = 90° => A = 45°, B = 15°."
                    },
                    {
                        "q": "Prove that (1 + cot θ - cosec θ)(1 + tan θ + sec θ) = 2.",
                        "a": "Converting to sin and cos: [(sin θ + cos θ - 1)/sin θ] * [(cos θ + sin θ + 1)/cos θ] = [(sin θ + cos θ)² - 1] / (sin θ cos θ) = 2 sin θ cos θ / (sin θ cos θ) = 2."
                    },
                    {
                        "q": "From the top of a 7 m high building, the angle of elevation of the top of a cable tower is 60° and the angle of depression of its foot is 45°. Determine the height of the tower.",
                        "a": "tan(45°) = 7/d => d = 7 m. tan(60°) = (H - 7)/d => √3 = (H - 7)/7 => H = 7(√3 + 1) m ≈ 19.12 m."
                    },
                    {
                        "q": "If sec θ + tan θ = p, prove that sin θ = (p² - 1) / (p² + 1).",
                        "a": "sec θ - tan θ = 1/p. Adding gives 2 sec θ = p + 1/p. Subtracting gives 2 tan θ = p - 1/p. Dividing gives sin θ = tan θ / sec θ = (p² - 1)/(p² + 1)."
                    },
                ]
                selected = random.choice(trig_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "STATISTICS_PROBABILITY":
                stats_templates = [
                    {
                        "q": "A die is thrown once. Find the probability of getting a prime number.",
                        "a": "Total outcomes = 6. Prime numbers = {2, 3, 5} (3 outcomes). P(prime) = 3/6 = 1/2."
                    },
                    {
                        "q": "A box contains 90 discs numbered 1 to 90. If one disc is drawn at random from the box, find the probability that it bears a two-digit number.",
                        "a": "Total outcomes = 90. Two-digit numbers = 10 to 90 (81 outcomes). P(two-digit) = 81/90 = 9/10."
                    },
                    {
                        "q": "Find the mean of the following frequency distribution: Class intervals 0-10, 10-20, 20-30, 30-40, 40-50 with frequencies 5, 8, 15, 12, 10 respectively.",
                        "a": "Using ∑(f*x)/∑f: Midpoints x = 5, 15, 25, 35, 45. ∑(f*x) = 25+120+375+420+450 = 1390. ∑f = 50. Mean = 1390/50 = 27.8."
                    },
                    {
                        "q": "Two dice are thrown simultaneously. What is the probability that the sum of the numbers appearing on the top is 8?",
                        "a": "Total possible outcomes = 36. Favorable outcomes for sum 8: (2,6), (3,5), (4,4), (5,3), (6,2) (5 outcomes). P(sum=8) = 5/36."
                    },
                    {
                        "q": "One card is drawn from a well-shuffled deck of 52 cards. Calculate the probability of drawing a red face card.",
                        "a": "Total cards = 52. Red face cards = Kings, Queens, Jacks of hearts and diamonds = 2 * 3 = 6. P(red face) = 6/52 = 3/26."
                    },
                    {
                        "q": "If the mean of five observations x, x+2, x+4, x+6, x+8 is 11, find the value of x and the median of the observations.",
                        "a": "Sum = 5x + 20 = 5 * 11 = 55 => 5x = 35 => x = 7. Observations are 7, 9, 11, 13, 15. Median = 11."
                    },
                    {
                        "q": "The median of a frequency distribution is 28.5 and its mean is 27.9. Calculate the mode using the empirical relationship between mean, median, and mode.",
                        "a": "Empirical formula: Mode = 3 * Median - 2 * Mean = 3(28.5) - 2(27.9) = 85.5 - 55.8 = 29.7."
                    },
                ]
                selected = random.choice(stats_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "ALGEBRA_QUADRATICS":
                algebra_templates = [
                    # A. Polynomial zeroes
                    {
                        "q": "Find the zeroes of the quadratic polynomial x² + 7x + 10.",
                        "a": "x² + 7x + 10 = (x + 2)(x + 5) = 0 => zeroes are -2 and -5."
                    },
                    # B. Quadratic equation solving
                    {
                        "q": "Solve the quadratic equation 2x² - 5x + 2 = 0 using the quadratic formula and state the nature of roots.",
                        "a": "Using x = [-b ± √(b² - 4ac)] / 2a, D = 25 - 16 = 9 > 0. Roots are real and distinct: x = 2 or x = 1/2."
                    },
                    # C. Relationship between zeroes and coefficients
                    {
                        "q": "Find the zeroes of the polynomial x² - 3 and verify the relationship between the zeroes and coefficients.",
                        "a": "Zeroes are √3 and -√3. Sum of zeroes = 0 = -b/a, Product of zeroes = -3 = c/a."
                    },
                    # D. Equal-root / discriminant problem
                    {
                        "q": "Find the value of k for which the quadratic equation kx(x - 2) + 6 = 0 has two equal roots.",
                        "a": "kx² - 2kx + 6 = 0. For equal roots D = b² - 4ac = 0 => 4k² - 24k = 0 => k = 6 (as k ≠ 0)."
                    },
                    # E. Two-digit number Algebra word problem
                    {
                        "q": "A two-digit number is such that the product of its digits is 14. When 45 is added to the number, the digits interchange their places. Find the number.",
                        "a": "Let tens digit be x and units digit be y. xy = 14 and (10x + y) + 45 = 10y + x => y - x = 5. Solving gives x = 2, y = 7. The number is 27."
                    },
                    # F. Matrix evaluation
                    {
                        "q": "If matrix A = [[1, 2], [3, 4]], calculate the matrix expression A² - 5A + 7I.",
                        "a": "A² = [[7, 10], [15, 22]], 5A = [[5, 10], [15, 20]], 7I = [[7, 0], [0, 7]]. A² - 5A + 7I = [[9, 0], [0, 9]]."
                    },
                    # G. Matrix inverse
                    {
                        "q": "Find the inverse of the matrix A = [[2, 3], [1, 4]] using determinant methods.",
                        "a": "det(A) = 8 - 3 = 5 ≠ 0. adj(A) = [[4, -3], [-1, 2]]. A⁻¹ = (1/5) * [[4, -3], [-1, 2]]."
                    },
                    # H. System of linear equations using matrices
                    {
                        "q": "Solve the system of linear equations 2x + 3y = 5 and 3x - y = 2 using matrix inversion method.",
                        "a": "AX = B where A = [[2, 3], [3, -1]], X = [[x], [y]], B = [[5], [2]]. det(A) = -11. X = A⁻¹B => x = 1, y = 1."
                    }
                ]
                selected = random.choice(algebra_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "NUMBERS_SEQUENCES":
                num_templates = [
                    {
                        "q": "Find the HCF and LCM of 96 and 404 using the prime factorization method.",
                        "a": "96 = 2^5 * 3, 404 = 2^2 * 101. HCF = 2^2 = 4. LCM = (96 * 404) / 4 = 9696."
                    },
                    {
                        "q": "Use Euclid's division algorithm to find the HCF of 4052 and 12576.",
                        "a": "12576 = 4052*3 + 420; 4052 = 420*9 + 272; 420 = 272*1 + 148; 272 = 148*1 + 124; 148 = 124*1 + 24; 124 = 24*5 + 4; 24 = 4*6 + 0. HCF = 4."
                    },
                    {
                        "q": "Prove that sqrt(5) is an irrational number using the method of contradiction.",
                        "a": "Assume sqrt(5) = a/b co-prime. 5b^2 = a^2 => 5 divides a. Let a = 5c => 5b^2 = 25c^2 => b^2 = 5c^2 => 5 divides b. Contradicts co-prime assumption. Thus sqrt(5) is irrational."
                    },
                    {
                        "q": "Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18...",
                        "a": "First term a = 3, common difference d = 5. a_20 = a + 19d = 3 + 19(5) = 3 + 95 = 98."
                    },
                    {
                        "q": "Find the sum of the first 20 terms of the Arithmetic Progression: 2, 7, 12, 17...",
                        "a": "First term a = 2, common difference d = 5, n = 20. S_20 = (n/2)[2a + (n-1)d] = 10[4 + 19(5)] = 10[4 + 95] = 990."
                    },
                    {
                        "q": "Which term of the Arithmetic Progression 21, 18, 15... is -81?",
                        "a": "a = 21, d = -3. a_n = a + (n-1)d = -81 => 21 + (n-1)(-3) = -81 => -3(n-1) = -102 => n - 1 = 34 => n = 35th term."
                    },
                    {
                        "q": "Find the 10th term of the Geometric Progression (G.P.): 2, 6, 18, 54...",
                        "a": "First term a = 2, common ratio r = 3. a_10 = a * r^(n-1) = 2 * 3^9 = 2 * 19683 = 39366."
                    },
                    {
                        "q": "Find the sum of the first 6 terms of the Geometric Progression: 3, 6, 12, 24...",
                        "a": "First term a = 3, common ratio r = 2. S_6 = a(r^n - 1)/(r - 1) = 3(2^6 - 1)/(2 - 1) = 3(64 - 1) = 3 * 63 = 189."
                    },
                    {
                        "q": "Find the remainder when 2^81 is divided by 17 using modular arithmetic.",
                        "a": "2^4 = 16 == -1 (mod 17) (congruent to -1 modulo 17). 2^81 = (2^4)^20 * 2^1 == (-1)^20 * 2 == 1 * 2 = 2 (mod 17). Remainder is 2."
                    },
                    {
                        "q": "Determine the general term a_n of the sequence defined by a_1 = 2 and a_n = 3 * a_{n-1} + 1 for n > 1.",
                        "a": "Calculating terms: a1=2, a2=7, a3=22, a4=67. Pattern gives general term a_n = (5 * 3^(n-1) - 1) / 2."
                    },
                    {
                        "q": "If the 3rd and 9th terms of an Arithmetic Progression are 4 and -8 respectively, find its 13th term.",
                        "a": "a + 2d = 4 and a + 8d = -8 => 6d = -12 => d = -2, a = 8. a_13 = a + 12d = 8 + 12(-2) = 8 - 24 = -16."
                    },
                    {
                        "q": "Prove that 3 + 2sqrt(5) is an irrational number given that sqrt(5) is irrational.",
                        "a": "Assume 3 + 2sqrt(5) = r (rational). Then sqrt(5) = (r - 3)/2 which is rational, contradicting irrationality of sqrt(5). Thus 3 + 2sqrt(5) is irrational."
                    }
                ]
                selected = random.choice(num_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "GEOMETRY":
                geom_templates = [
                    {
                        "q": "State the Basic Proportionality Theorem (Thales Theorem) for triangles.",
                        "a": "If a line is drawn parallel to one side of a triangle to intersect the other two sides in distinct points, the other two sides are divided in the same ratio."
                    },
                    {
                        "q": "Prove that the lengths of tangents drawn from an external point to a circle are equal.",
                        "a": "Let PA and PB be tangents from P to circle O. In △OAP and △OBP: OA = OB (radii), OP = OP (common), ∠OAP = ∠OBP = 90°. RHS congruence => PA = PB."
                    },
                    {
                        "q": "State and prove Pythagoras Theorem for a right-angled triangle.",
                        "a": "Statement: In a right triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides. Proof via similar triangles △ABD ~ △ABC and △CBD ~ △ABC."
                    },
                    {
                        "q": "In △ABC, DE ∥ BC intersecting AB at D and AC at E. If AD = 1.5 cm, DB = 3 cm, and AE = 1 cm, find the length of EC using Thales Theorem.",
                        "a": "By Basic Proportionality Theorem (Thales Theorem): AD / DB = AE / EC => 1.5 / 3 = 1 / EC => EC = 3 / 1.5 = 2 cm."
                    },
                    {
                        "q": "Prove that the tangent at any point of a circle is perpendicular to the radius through the point of contact.",
                        "a": "Let circle have center O and tangent line XY touching at P. For any other point Q on XY outside the circle, OQ > OP (radius). Thus OP is the shortest distance from O to XY, proving OP ⊥ XY."
                    },
                    {
                        "q": "Two concentric circles are of radii 5 cm and 3 cm. Find the length of the chord of the larger circle which touches the smaller circle.",
                        "a": "Let chord be AB touching inner circle at P. OP ⊥ AB and bisects AB. In right △OPA: OA = 5, OP = 3 => AP = √(5² - 3²) = 4 cm. Length of chord AB = 2 * AP = 8 cm."
                    },
                    {
                        "q": "Prove that the parallelogram circumscribing a circle is a rhombus.",
                        "a": "Let ABCD be parallelogram circumscribing circle. Opposite sides are equal (AB = CD, BC = DA). Lengths of tangents from external points give AB + CD = AD + BC => 2AB = 2AD => AB = AD. Adjacent sides equal implies ABCD is a rhombus."
                    },
                    {
                        "q": "If two similar triangles have areas in the ratio 64:121, find the ratio of their corresponding sides and perimeters.",
                        "a": "The ratio of the areas of two similar triangles is equal to the square of the ratio of their corresponding sides: Area1/Area2 = (side1/side2)² => 64/121 = (side1/side2)² => side1/side2 = 8/11. Perimeter ratio is also 8:11."
                    },
                ]
                selected = random.choice(geom_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "MENSURATION":
                mens_templates = [
                    {
                        "q": "Find the area of a sector of a circle of radius 6 cm if the central angle is 60°.",
                        "a": "Area = (θ/360°) * π * r² = (60/360) * (22/7) * 36 = 18.86 cm²."
                    },
                    {
                        "q": "A solid is in the shape of a cone standing on a hemisphere with both their radii being equal to 1 cm and the height of the cone is equal to its radius. Find the volume of the solid in terms of π.",
                        "a": "Volume = V_cone + V_hemisphere = (1/3)πr²h + (2/3)πr³ = (1/3)π(1)³ + (2/3)π(1)³ = π cm³."
                    },
                    {
                        "q": "A wooden article was made by scooping out a hemisphere from each end of a solid cylinder of height 10 cm and base radius 3.5 cm. Find the total surface area of the article.",
                        "a": "TSA = CSA of cylinder + 2 * CSA of hemisphere = 2πrh + 2*(2πr²) = 2πr(h + 2r) = 2*(22/7)*3.5*(10 + 7) = 374 cm²."
                    },
                    {
                        "q": "A metallic sphere of radius 4.2 cm is melted and recast into the shape of a cylinder of radius 6 cm. Find the height of the cylinder.",
                        "a": "Volume of sphere = Volume of cylinder => (4/3)πr1³ = πr2²h => (4/3)*(4.2)³ = 6² * h => h = (4 * 74.088) / (3 * 36) = 2.74 cm."
                    },
                    {
                        "q": "Find the length of an arc of a circle of radius 21 cm which subtends an angle of 60° at the center.",
                        "a": "Arc length l = (θ/360°) * 2πr = (60/360) * 2 * (22/7) * 21 = (1/6) * 132 = 22 cm."
                    },
                    {
                        "q": "A conical tent is 10 m high and the radius of its base is 24 m. Find the slant height of the tent and cost of canvas required at ₹70 per m².",
                        "a": "Slant height l = √(r² + h²) = √(24² + 10²) = √(576 + 100) = √676 = 26 m. Curved surface area = πrl = (22/7) * 24 * 26 = 1961.14 m². Cost = 1961.14 * 70 = ₹137,280."
                    },
                ]
                selected = random.choice(mens_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "VECTORS_3D":
                vec_templates = [
                    {
                        "q": "Find the unit vector in the direction of the vector a = 2i + 3j + k.",
                        "a": "|a| = √(2² + 3² + 1²) = √(4 + 9 + 1) = √14. Unit vector â = (2i + 3j + k) / √14."
                    },
                    {
                        "q": "Find the angle between two vectors a = i - 2j + 3k and b = 3i - 2j + k using dot product.",
                        "a": "a · b = (1)(3) + (-2)(-2) + (3)(1) = 3 + 4 + 3 = 10. |a| = √14, |b| = √14. cos θ = (a · b) / (|a||b|) = 10 / 14 = 5/7 => θ = cos⁻¹(5/7)."
                    },
                    {
                        "q": "Find the vector product (cross product) of two vectors a = 2i + j + 3k and b = 3i + 5j - 2k.",
                        "a": "a × b = det([[i, j, k], [2, 1, 3], [3, 5, -2]]) = i(-2 - 15) - j(-4 - 9) + k(10 - 3) = -17i + 13j + 7k."
                    },
                    {
                        "q": "Find the projection of the vector a = 2i + 3j + 2k on the vector b = i + 2j + k.",
                        "a": "Projection = (a · b) / |b| = (2*1 + 3*2 + 2*1) / √(1 + 4 + 1) = (2 + 6 + 2) / √6 = 10 / √6 = (5√6) / 3."
                    },
                    {
                        "q": "Find the direction cosines of the vector joining the points A(1, 2, -3) and B(-1, -2, 1) directed from A to B.",
                        "a": "Vector AB = (-1 - 1)i + (-2 - 2)j + (1 - (-3))k = -2i - 4j + 4k. |AB| = √(4 + 16 + 16) = √36 = 6. Direction cosines: l = -2/6 = -1/3, m = -4/6 = -2/3, n = 4/6 = 2/3."
                    },
                    {
                        "q": "Find the vector equation of the line passing through the point with position vector 2i - j + 4k and in the direction of i + 2j - k.",
                        "a": "Vector equation: r = a + λb => r = (2i - j + 4k) + λ(i + 2j - k), where λ is a scalar parameter."
                    },
                ]
                selected = random.choice(vec_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "LINEAR_PROGRAMMING":
                lp_templates = [
                    {
                        "q": "Maximize Z = 3x + 4y subject to constraints: x + y ≤ 4, x ≥ 0, y ≥ 0 using the corner point method.",
                        "a": "Corner points of the feasible region are (0,0), (4,0), and (0,4). Z(0,0)=0, Z(4,0)=12, Z(0,4)=16. Maximum value of Z is 16 at (0,4)."
                    },
                    {
                        "q": "Minimize the objective function Z = 200x + 500y subject to constraints: x + 2y ≥ 10, 3x + 4y ≤ 24, x ≥ 0, y ≥ 0.",
                        "a": "Plotting lines and finding intersection: (4,3). Corner points: (0,5), (0,6), (4,3). Z(0,5)=2500, Z(0,6)=3000, Z(4,3)=2300. Minimum Z = 2300 at (4,3)."
                    },
                    {
                        "q": "Define feasible region, objective function, and state the Corner Point Theorem for a Linear Programming Problem.",
                        "a": "Feasible region is the common region determined by all constraints including non-negativity. The Corner Point Theorem states that if a feasible region is bounded, the optimal value of the objective function occurs at a corner point (vertex)."
                    },
                    {
                        "q": "Determine the maximum value of Z = 5x + 3y subject to constraints: 3x + 5y ≤ 15, 5x + 2y ≤ 10, x ≥ 0, y ≥ 0.",
                        "a": "Corner points: (0,0), (2,0), (0,3), and (20/19, 45/19). Evaluating Z: Z(0,0)=0, Z(2,0)=10, Z(0,3)=9, Z(20/19, 45/19)=235/19 ≈ 12.37. Maximum value is 235/19."
                    },
                    {
                        "q": "Formulate a Linear Programming Problem: A manufacturer produces two products A and B requiring machine time on M1 and M2 with limited capacities.",
                        "a": "Let x and y be units of A and B. Objective function: Maximize Profit Z = c1*x + c2*y subject to machine constraints a11*x + a12*y ≤ T1, a21*x + a22*y ≤ T2, with non-negativity constraints x ≥ 0, y ≥ 0."
                    },
                ]
                selected = random.choice(lp_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "CALCULUS":
                calc_templates = [
                    {
                        "q": "Evaluate the definite integral: ∫ from 0 to π/2 of (sin² x) dx.",
                        "a": "Using property I = ∫[0 to π/2] cos² x dx. 2I = ∫[0 to π/2] (sin² x + cos² x) dx = [x][0 to π/2] = π/2 => I = π/4."
                    },
                    {
                        "q": "Find the derivative dy/dx if y = (sin x)^(cos x) using logarithmic differentiation.",
                        "a": "ln y = cos x * ln(sin x). (1/y)(dy/dx) = -sin x * ln(sin x) + cos x * (cos x / sin x). dy/dx = (sin x)^(cos x) * [cos x * cot x - sin x * ln(sin x)]."
                    },
                    {
                        "q": "Find the general solution of the differential equation: dy/dx + 2y = e^(-x).",
                        "a": "Integrating factor IF = e^(∫ 2 dx) = e^(2x). y * e^(2x) = ∫ e^(-x)*e^(2x) dx = ∫ e^x dx = e^x + C. Solution: y = e^(-x) + C * e^(-2x)."
                    },
                    {
                        "q": "Determine the intervals in which the function f(x) = 2x³ - 9x² + 12x + 15 is strictly increasing or strictly decreasing.",
                        "a": "f'(x) = 6x² - 18x + 12 = 6(x - 1)(x - 2). f'(x) > 0 for x ∈ (-∞, 1) ∪ (2, ∞) (strictly increasing), f'(x) < 0 for x ∈ (1, 2) (strictly decreasing)."
                    },
                    {
                        "q": "Evaluate the indefinite integral: ∫ [1 / (x² + 4x + 13)] dx.",
                        "a": "x² + 4x + 13 = (x + 2)² + 3². Let u = x + 2, du = dx. ∫ [1 / (u² + 3²)] du = (1/3) tan⁻¹(u/3) + C = (1/3) tan⁻¹((x + 2)/3) + C."
                    },
                ]
                selected = random.choice(calc_templates)
                q_text = selected["q"]
                ans = selected["a"]

            elif category == "RELATIONS_FUNCTIONS":
                rel_templates = [
                    {
                        "q": "Determine whether the relation R in the set Z of integers defined by R = {(x,y): x - y is divisible by 5} is an equivalence relation.",
                        "a": "Reflexive: x - x = 0 is divisible by 5. Symmetric: if x - y = 5k, y - x = 5(-k). Transitive: x - y = 5k, y - z = 5m => x - z = 5(k+m). Hence R is an equivalence relation."
                    },
                    {
                        "q": "Let A = {1, 2, 3}. Check whether the relation R = {(1,1), (2,2), (3,3), (1,2), (2,1)} on set A is reflexive, symmetric, and transitive.",
                        "a": "Reflexive: (1,1),(2,2),(3,3) ∈ R. Symmetric: (1,2) ∈ R and (2,1) ∈ R. Transitive: (2,1) and (1,2) in R => (2,2) ∈ R. Thus R is an equivalence relation."
                    },
                    {
                        "q": "Determine the domain, codomain, and range of the relation R = {(x, x³): x is a prime number less than 10}.",
                        "a": "Primes less than 10 are {2, 3, 5, 7}. R = {(2,8), (3,27), (5,125), (7,343)}. Domain = {2, 3, 5, 7}, Range = {8, 27, 125, 343}."
                    },
                    {
                        "q": "Find the principal value of the inverse trigonometric expression: tan⁻¹(√3) - sec⁻¹(-2).",
                        "a": "tan⁻¹(√3) = π/3. sec⁻¹(-2) = π - sec⁻¹(2) = π - π/3 = 2π/3. Value = π/3 - 2π/3 = -π/3."
                    },
                    {
                        "q": "Show that the function f: R -> R defined by f(x) = 3x + 2 is one-one and onto (bijective).",
                        "a": "One-one: f(x1)=f(x2) => 3x1+2=3x2+2 => x1=x2. Onto: For any y ∈ R, x = (y-2)/3 ∈ R such that f(x)=y."
                    },
                    {
                        "q": "Determine whether the function f: N -> N defined by f(x) = x² is one-one (injective) or onto (surjective).",
                        "a": "One-one: For x1, x2 ∈ N, x1² = x2² => x1 = x2 (since N > 0). Onto: 2 ∈ N has no pre-image x in N such that x² = 2. Thus f is one-one but not onto."
                    },
                    {
                        "q": "Show that the modulus function f: R -> R given by f(x) = |x| is neither one-one nor onto.",
                        "a": "f(1) = 1 and f(-1) = 1 => not one-one. Range is [0, ∞), so negative real numbers have no pre-image => not onto."
                    },
                    {
                        "q": "Let f: R -> R and g: R -> R be defined by f(x) = 2x + 1 and g(x) = x² - 2. Find the composite functions (g o f)(x) and (f o g)(x).",
                        "a": "(g o f)(x) = g(f(x)) = (2x+1)² - 2 = 4x² + 4x - 1. (f o g)(x) = f(g(x)) = 2(x²-2) + 1 = 2x² - 3."
                    },
                    {
                        "q": "If f(x) = 8x³ and g(x) = x^(1/3), find the composition of functions (f o g)(x) and (g o f)(x).",
                        "a": "(f o g)(x) = f(g(x)) = 8(x^(1/3))³ = 8x. (g o f)(x) = g(f(x)) = (8x³)^(1/3) = 2x."
                    },
                    {
                        "q": "Show that the function f: R - {3} -> R - {1} defined by f(x) = (x - 2) / (x - 3) is bijective. Find its inverse function f⁻¹(x).",
                        "a": "One-one: (x1-2)/(x1-3) = (x2-2)/(x2-3) => x1 = x2. Onto: y = (x-2)/(x-3) => x = (3y-2)/(y-1) ∈ R-{3} for y ≠ 1. Inverse f⁻¹(x) = (3x-2)/(x-1)."
                    },
                    {
                        "q": "Consider f: [0, ∞) -> [4, ∞) given by f(x) = x² + 4. Show that f is invertible and find the inverse of f.",
                        "a": "One-one: x1² + 4 = x2² + 4 => x1 = x2 (for x ≥ 0). Onto: y = x² + 4 => x = √(y-4) ∈ [0, ∞) for y ≥ 4. Inverse f⁻¹(y) = √(y-4)."
                    },
                    {
                        "q": "Simplify the inverse trigonometric expression: tan⁻¹[(cos x - sin x) / (cos x + sin x)], for -π/4 < x < 3π/4.",
                        "a": "Divide numerator and denominator by cos x: tan⁻¹[(1 - tan x) / (1 + tan x)] = tan⁻¹[tan(π/4 - x)] = π/4 - x."
                    }
                ]
                selected = random.choice(rel_templates)
                q_text = selected["q"]
                ans = selected["a"]

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
        elif "computer" in subj or re.search(r"\b(cs|ip|it)\b", subj):
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
                f"Formulate a detailed case study illustrating the core components of {prompt.unit_name} and propose solutions to associated challenges.",
                f"Examine the primary methodologies used in {prompt.unit_name} and detail how they are applied in practice.",
                f"Describe the structural architecture and core mechanisms of {prompt.unit_name} ({prompt.topic_name or 'Main Topics'}).",
                f"Identify the key constraints, optimization techniques, and best practices associated with {prompt.unit_name}.",
                f"Compare and contrast different operational models within {prompt.unit_name}, giving real-world examples.",
                f"Explain how {prompt.unit_name} integrates into broader theoretical systems, highlighting key trade-offs.",
                f"Construct an analytical summary of the core principles of {prompt.unit_name} for high-level problem solving.",
                f"Assess the impact of recent developments in {prompt.unit_name} on standard domain frameworks.",
                f"Synthesize the fundamental theories of {prompt.unit_name} into a comprehensive conceptual outline."
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
