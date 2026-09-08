"""Structured Syllabus Ingestion Engine and Pre-Populated Multi-Board Curriculum Catalog."""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from sqlalchemy.orm import Session

from app.database.database import Base, SessionLocal, engine
from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.board import Board
from app.models.stream import Stream
from app.models.subject import Subject
from app.models.topic import Topic
from app.models.unit import Unit

# Authoritative Educational Board Definitions
OFFICIAL_BOARDS_REGISTRY = [
    {
        "code": "CBSE",
        "name": "Central Board of Secondary Education",
        "state": "All India",
        "website_url": "https://cbseacademic.nic.in",
        "description": "National level board of education in India for public and private schools.",
    },
    {
        "code": "TNSB",
        "name": "Tamil Nadu State Board of School Examination",
        "state": "Tamil Nadu",
        "website_url": "https://www.dge.tn.gov.in",
        "description": "State board governing school education in Tamil Nadu (Samacheer Kalvi & Higher Secondary).",
    },
    {
        "code": "KBPE",
        "name": "Kerala Board of Public Examinations",
        "state": "Kerala",
        "website_url": "https://keralapareekshabhavan.in",
        "description": "State education board governing SSLC and Higher Secondary education in Kerala.",
    },
    {
        "code": "KSEEB",
        "name": "Karnataka School Examination and Assessment Board",
        "state": "Karnataka",
        "website_url": "https://kseab.karnataka.gov.in",
        "description": "State board conducting SSLC and PUC examinations in Karnataka.",
    },
    {
        "code": "BIEAP",
        "name": "Andhra Pradesh Board of Intermediate & School Education",
        "state": "Andhra Pradesh",
        "website_url": "https://bie.ap.gov.in",
        "description": "State board for secondary and intermediate education in Andhra Pradesh.",
    },
    {
        "code": "TSBIE",
        "name": "Telangana State Board of Intermediate & Secondary Education",
        "state": "Telangana",
        "website_url": "https://tsbie.cgg.gov.in",
        "description": "State board governing secondary and senior secondary education in Telangana.",
    },
    {
        "code": "MSBSHSE",
        "name": "Maharashtra State Board of Secondary and Higher Secondary Education",
        "state": "Maharashtra",
        "website_url": "https://mahahsscboard.in",
        "description": "State board conducting SSC (Class 10) and HSC (Class 12) examinations in Maharashtra.",
    },
]


def generate_standard_curriculum_catalog() -> List[Dict[str, Any]]:
    """
    Generate comprehensive, structured syllabus catalog datasets for CBSE and State Boards across Classes 1 to 12.
    """
    catalog = []

    # 1. CBSE (Classes 1 to 12)
    cbse_entries = [
        # Class 1 to 5 (Primary)
        {
            "board": "CBSE",
            "class": 1,
            "subjects": [
                {
                    "name": "Mathematics",
                    "code": "CBSE-01-MATH",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Shapes and Space", "topics": ["Inside-Outside", "Bigger-Smaller", "Top-Bottom", "Shapes Around Us"]},
                        {"number": 2, "name": "Unit 2 - Numbers from One to Nine", "topics": ["Counting", "More or Less", "Making Groups"]},
                        {"number": 3, "name": "Unit 3 - Addition & Subtraction (1 to 9)", "topics": ["One more", "Adding together", "Taking away"]},
                        {"number": 4, "name": "Unit 4 - Measurement & Patterns", "topics": ["Longer-Shorter", "Heavier-Lighter", "Pattern sequences"]},
                    ],
                },
                {
                    "name": "Environmental Studies (EVS)",
                    "code": "CBSE-01-EVS",
                    "units": [
                        {"number": 1, "name": "Unit 1 - My Family and Me", "topics": ["About Myself", "My Body Parts", "My Family Members"]},
                        {"number": 2, "name": "Unit 2 - Plants and Animals Around Us", "topics": ["Green Friends", "Animal Kingdom", "Pet and Wild Animals"]},
                        {"number": 3, "name": "Unit 3 - Food, Water and Shelter", "topics": ["Healthy Food", "Clean Water", "Our Sweet Home"]},
                    ],
                },
                {
                    "name": "English",
                    "code": "CBSE-01-ENG",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Phonics and Letter Recognition", "topics": ["Alphabet Sounds", "Vowels and Consonants", "Simple 3-letter Words"]},
                        {"number": 2, "name": "Unit 2 - Rhymes and Short Stories", "topics": ["Story Comprehension", "Action Words", "Naming Words"]},
                    ],
                },
            ],
        },
        {
            "board": "CBSE",
            "class": 5,
            "subjects": [
                {
                    "name": "Mathematics",
                    "code": "CBSE-05-MATH",
                    "units": [
                        {"number": 1, "name": "Unit 1 - The Fish Tale (Large Numbers & Place Value)", "topics": ["Lakhs and Crores", "Speed and Distance Problems", "Fish Market Calculations"]},
                        {"number": 2, "name": "Unit 2 - Shapes and Angles", "topics": ["Right Angles", "Acute and Obtuse Angles", "Angle Testers"]},
                        {"number": 3, "name": "Unit 3 - How Many Squares? (Area and Perimeter)", "topics": ["Area of Irregular Shapes", "Grid Area Calculations", "Perimeter of Polygons"]},
                        {"number": 4, "name": "Unit 4 - Parts and Wholes (Fractions & Decimals)", "topics": ["Equivalent Fractions", "Fractional Division", "Decimal Representation"]},
                        {"number": 5, "name": "Unit 5 - Be My Multiple, I'll Be Your Factor (LCM & HCF)", "topics": ["Common Multiples", "Factor Trees", "LCM and HCF Applications"]},
                    ],
                },
                {
                    "name": "Environmental Studies (EVS)",
                    "code": "CBSE-05-EVS",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Super Senses in Animals", "topics": ["Sense of Smell and Hearing", "Animal Sounds and Sleep", "Endangered Species"]},
                        {"number": 2, "name": "Unit 2 - A Snake Charmer's Story & Tasting to Digesting", "topics": ["Poisonous Snakes", "Digestive System Pathways", "Glucose and Energy"]},
                        {"number": 3, "name": "Unit 3 - Experiments with Water & Every Drop Counts", "topics": ["Floating and Sinking", "Solubility Experiments", "Rainwater Harvesting History"]},
                        {"number": 4, "name": "Unit 4 - Sunita in Space & What if it Finishes?", "topics": ["Gravity in Space", "Petroleum Conservation", "Renewable Energy Sources"]},
                    ],
                },
            ],
        },
        # Class 8 (Middle)
        {
            "board": "CBSE",
            "class": 8,
            "subjects": [
                {
                    "name": "Mathematics",
                    "code": "CBSE-08-MATH",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Rational Numbers", "topics": ["Properties of Rational Numbers", "Representation on Number Line", "Rational Numbers between Two Numbers"]},
                        {"number": 2, "name": "Unit 2 - Linear Equations in One Variable", "topics": ["Solving Linear Equations", "Word Problems", "Equations Reducible to Linear Form"]},
                        {"number": 3, "name": "Unit 3 - Understanding Quadrilaterals", "topics": ["Polygons and Angle Sum", "Parallelograms and Properties", "Special Quadrilaterals"]},
                        {"number": 4, "name": "Unit 4 - Squares and Square Roots & Cubes", "topics": ["Square Properties", "Division Method for Roots", "Cube Roots by Prime Factorisation"]},
                        {"number": 5, "name": "Unit 5 - Algebraic Expressions and Identities", "topics": ["Multiplication of Polynomials", "Standard Algebraic Identities", "Factorisation"]},
                        {"number": 6, "name": "Unit 6 - Mensuration (Area and Surface Volume)", "topics": ["Area of Trapezium", "Surface Area of Cube, Cuboid, Cylinder", "Volume of Solids"]},
                        {"number": 7, "name": "Unit 7 - Exponents and Powers & Direct/Inverse Proportions", "topics": ["Laws of Exponents", "Scientific Notation", "Proportion Calculations"]},
                    ],
                },
                {
                    "name": "Science",
                    "code": "CBSE-08-SCI",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Crop Production and Management", "topics": ["Agricultural Practices", "Soil Preparation & Sowing", "Manures, Fertilizers & Irrigation"]},
                        {"number": 2, "name": "Unit 2 - Microorganisms: Friend and Foe", "topics": ["Classification of Microbes", "Nitrogen Cycle & Fixation", "Food Preservation"]},
                        {"number": 3, "name": "Unit 3 - Coal and Petroleum & Combustion/Flame", "topics": ["Fossil Fuels", "Fractional Distillation", "Types of Combustion and Fire Safety"]},
                        {"number": 4, "name": "Unit 4 - Cell - Structure and Functions", "topics": ["Plant vs Animal Cell", "Cell Organelles", "Cell Membrane & Nucleus"]},
                        {"number": 5, "name": "Unit 5 - Force, Pressure and Friction", "topics": ["Contact and Non-contact Forces", "Atmospheric Pressure", "Friction as a Necessary Evil"]},
                        {"number": 6, "name": "Unit 6 - Sound & Chemical Effects of Electric Current", "topics": ["Vibrations and Pitch", "Audible and Inaudible Sound", "Electroplating Applications"]},
                        {"number": 7, "name": "Unit 7 - Light (Reflection, Laws & Human Eye)", "topics": ["Laws of Reflection", "Multiple Images and Kaleidoscopes", "Structure of Human Eye"]},
                    ],
                },
            ],
        },
        # Class 10 (Secondary)
        {
            "board": "CBSE",
            "class": 10,
            "subjects": [
                {
                    "name": "Mathematics",
                    "code": "041",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Real Numbers", "topics": ["Fundamental Theorem of Arithmetic", "Revisiting Irrational Numbers", "Decimal Expansions"]},
                        {"number": 2, "name": "Unit 2 - Polynomials", "topics": ["Geometrical Meaning of Zeroes", "Relationship between Zeroes and Coefficients", "Quadratic & Cubic Polynomials"]},
                        {"number": 3, "name": "Unit 3 - Pair of Linear Equations in Two Variables", "topics": ["Graphical Method", "Substitution Method", "Elimination Method", "Word Problems"]},
                        {"number": 4, "name": "Unit 4 - Quadratic Equations", "topics": ["Standard Form", "Factorisation Method", "Quadratic Formula", "Nature of Roots"]},
                        {"number": 5, "name": "Unit 5 - Arithmetic Progressions", "topics": ["nth Term of an AP", "Sum of First n Terms", "Real-Life AP Applications"]},
                        {"number": 6, "name": "Unit 6 - Coordinate Geometry", "topics": ["Distance Formula", "Section Formula", "Midpoint Coordinates"]},
                        {"number": 7, "name": "Unit 7 - Triangles (Geometry)", "topics": ["Basic Proportionality Theorem (Thales)", "Criteria for Similarity (AAA, SSS, SAS)", "Similarity Proofs"]},
                        {"number": 8, "name": "Unit 8 - Circles", "topics": ["Tangent to a Circle", "Number of Tangents from a Point", "Circle Theorems"]},
                        {"number": 9, "name": "Unit 9 - Introduction to Trigonometry & Applications", "topics": ["Trigonometric Ratios", "Specific Angles (0, 30, 45, 60, 90)", "Trigonometric Identities", "Heights and Distances"]},
                        {"number": 10, "name": "Unit 10 - Mensuration (Areas Related to Circles & Volumes)", "topics": ["Area of Sector and Segment", "Surface Area of Combinations", "Volume of Combined Solids"]},
                        {"number": 11, "name": "Unit 11 - Statistics and Probability", "topics": ["Mean of Grouped Data (Direct & Assumed Mean)", "Mode and Median of Grouped Data", "Theoretical Probability"]},
                    ],
                },
                {
                    "name": "Science",
                    "code": "086",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Chemical Reactions and Equations", "topics": ["Chemical Equations", "Types of Chemical Reactions", "Corrosion and Rancidity"]},
                        {"number": 2, "name": "Unit 2 - Acids, Bases and Salts", "topics": ["Chemical Properties of Acids and Bases", "pH Scale & Importance", "Salts (Bleaching Powder, Baking Soda, POP)"]},
                        {"number": 3, "name": "Unit 3 - Metals and Non-metals", "topics": ["Physical & Chemical Properties", "Reactivity Series", "Ionic Compounds", "Metallurgy Basics"]},
                        {"number": 4, "name": "Unit 4 - Carbon and its Compounds", "topics": ["Covalent Bonding in Carbon", "Versatile Nature of Carbon", "Homologous Series", "Functional Groups", "Soaps and Detergents"]},
                        {"number": 5, "name": "Unit 5 - Life Processes", "topics": ["Autotrophic and Heterotrophic Nutrition", "Respiration in Plants and Animals", "Human Circulatory System", "Excretion in Humans & Plants"]},
                        {"number": 6, "name": "Unit 6 - Control and Coordination", "topics": ["Human Nervous System & Reflex Arc", "Human Brain Anatomy", "Plant Hormones (Tropic Movements)", "Animal Hormones & Endocrine Glands"]},
                        {"number": 7, "name": "Unit 7 - How do Organisms Reproduce?", "topics": ["Asexual Modes of Reproduction", "Sexual Reproduction in Flowering Plants", "Human Reproductive System", "Reproductive Health"]},
                        {"number": 8, "name": "Unit 8 - Heredity and Evolution", "topics": ["Mendel's Laws of Inheritance", "Monohybrid and Dihybrid Crosses", "Sex Determination in Humans"]},
                        {"number": 9, "name": "Unit 9 - Light - Reflection and Refraction", "topics": ["Spherical Mirrors & Mirror Formula", "Refraction & Snell's Law", "Lens Formula & Magnification", "Power of a Lens"]},
                        {"number": 10, "name": "Unit 10 - Human Eye and Colourful World", "topics": ["Structure of Human Eye & Defects", "Refraction through Prism", "Dispersion of White Light", "Atmospheric Refraction & Scattering"]},
                        {"number": 11, "name": "Unit 11 - Electricity", "topics": ["Electric Current & Potential Difference", "Ohm's Law & Resistance", "Resistors in Series and Parallel", "Joule's Heating Effect & Electric Power"]},
                        {"number": 12, "name": "Unit 12 - Magnetic Effects of Electric Current", "topics": ["Magnetic Field Lines", "Right-Hand Thumb Rule", "Solenoid & Electromagnet", "Force on Current-Carrying Conductor", "Electromagnetic Safety (Fuse & Earthing)"]},
                        {"number": 13, "name": "Unit 13 - Our Environment", "topics": ["Ecosystem and Food Chains", "Trophic Levels & 10% Energy Law", "Ozone Layer Depletion", "Waste Management"]},
                    ],
                },
                {
                    "name": "Social Science",
                    "code": "087",
                    "units": [
                        {"number": 1, "name": "Unit 1 - History: Rise of Nationalism in Europe & India", "topics": ["French Revolution and Nation State", "Non-Cooperation Movement", "Civil Disobedience Movement"]},
                        {"number": 2, "name": "Unit 2 - Geography: Resources, Agriculture & Manufacturing", "topics": ["Types of Resources & Soil Classification", "Cropping Seasons & Major Crops", "Manufacturing Industries & Pollution"]},
                        {"number": 3, "name": "Unit 3 - Political Science: Power Sharing, Federalism & Political Parties", "topics": ["Belgium and Sri Lanka Models", "Federal Structure in India", "Role and Functions of Political Parties"]},
                        {"number": 4, "name": "Unit 4 - Economics: Development, Money and Credit, Globalisation", "topics": ["National Income & Human Development Index", "Formal vs Informal Credit", "MNCs and World Trade Organisation"]},
                    ],
                },
                {
                    "name": "Information Technology",
                    "code": "402",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Digital Documentation (Advanced)", "topics": ["Styles and Formatting in LibreOffice/Word", "Images and Objects", "Table of Contents", "Mail Merge"]},
                        {"number": 2, "name": "Unit 2 - Electronic Spreadsheet (Advanced)", "topics": ["Scenarios and Goal Seek", "Linking Data and Consolidating", "Macros in Spreadsheets"]},
                        {"number": 3, "name": "Unit 3 - Database Management System (RDBMS)", "topics": ["Relational Concepts & Primary Key", "Table Creation and Data Types", "SQL Queries (SELECT, INSERT, UPDATE, DELETE)"]},
                        {"number": 4, "name": "Unit 4 - Web Applications and Security", "topics": ["Accessibility Options", "Networking Concepts & Topology", "Instant Messaging & Blogs", "Cyber Safety and Workplace Hazards"]},
                    ],
                },
            ],
        },
        # Class 12 (Senior Secondary)
        {
            "board": "CBSE",
            "class": 12,
            "subjects": [
                {
                    "name": "Physics",
                    "code": "042",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Electrostatics (Electric Charges, Fields & Potential)", "topics": ["Coulomb's Law & Principle of Superposition", "Gauss's Theorem and Applications", "Electric Potential and Equipotential Surfaces", "Capacitors and Dielectrics"]},
                        {"number": 2, "name": "Unit 2 - Current Electricity", "topics": ["Drift Velocity and Ohm's Law", "Temperature Dependence of Resistance", "Kirchhoff's Laws & Wheatstone Bridge", "Potentiometer Applications"]},
                        {"number": 3, "name": "Unit 3 - Magnetic Effects of Current and Magnetism", "topics": ["Biot-Savart Law and Applications", "Ampere's Circuital Law", "Force on Moving Charge & Solenoid", "Moving Coil Galvanometer", "Earth's Magnetic Field Elements"]},
                        {"number": 4, "name": "Unit 4 - Electromagnetic Induction and Alternating Currents", "topics": ["Faraday's Laws & Lenz's Law", "Self and Mutual Inductance", "LCR Series Circuit & Resonance", "AC Generator and Transformers"]},
                        {"number": 5, "name": "Unit 5 - Electromagnetic Waves", "topics": ["Displacement Current", "Characteristics of EM Waves", "Electromagnetic Spectrum & Uses"]},
                        {"number": 6, "name": "Unit 6 - Optics (Ray & Wave Optics)", "topics": ["Total Internal Reflection & Optical Fibres", "Lens Maker's Formula & Combinations", "Astronomical Telescope & Compound Microscope", "Huygens Principle & Wavefronts", "Young's Double Slit Experiment & Diffraction"]},
                        {"number": 7, "name": "Unit 7 - Dual Nature of Radiation and Matter", "topics": ["Photoelectric Effect & Hertz Observations", "Einstein's Photoelectric Equation", "de Broglie Wavelength of Matter Waves"]},
                        {"number": 8, "name": "Unit 8 - Atoms and Nuclei", "topics": ["Rutherford Alpha Scattering", "Bohr Model of Hydrogen Atom", "Nuclear Binding Energy Curve", "Nuclear Fission and Fusion"]},
                        {"number": 9, "name": "Unit 9 - Electronic Devices (Semiconductors)", "topics": ["Energy Bands in Solids", "p-n Junction Diode Characteristics", "Diode as a Half/Full Wave Rectifier"]},
                    ],
                },
                {
                    "name": "Chemistry",
                    "code": "043",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Solutions", "topics": ["Concentration Terms (Molarity, Molality)", "Raoult's Law & Ideal Solutions", "Colligative Properties & Osmotic Pressure", "Van't Hoff Factor & Abnormal Molecular Mass"]},
                        {"number": 2, "name": "Unit 2 - Electrochemistry", "topics": ["Nernst Equation & Cell EMF", "Conductance & Kohlrausch's Law", "Faraday's Laws of Electrolysis", "Batteries, Fuel Cells and Corrosion"]},
                        {"number": 3, "name": "Unit 3 - Chemical Kinetics", "topics": ["Rate of Reaction and Rate Law", "Order and Molecularity", "Integrated Rate Equations (Zero and First Order)", "Arrhenius Equation & Activation Energy"]},
                        {"number": 4, "name": "Unit 4 - The d- and f-Block Elements", "topics": ["Electronic Configurations & Variable Oxidation", "Lanthanoid Contraction", "Preparation and Properties of KMnO4 & K2Cr2O7"]},
                        {"number": 5, "name": "Unit 5 - Coordination Compounds", "topics": ["Werner's Theory & IUPAC Nomenclature", "Isomerism in Coordination Complexes", "Valence Bond Theory and Crystal Field Theory"]},
                        {"number": 6, "name": "Unit 6 - Haloalkanes and Haloarenes", "topics": ["SN1 and SN2 Mechanisms", "Stereochemistry of Halogen Compounds", "Electrophilic Substitution in Haloarenes"]},
                        {"number": 7, "name": "Unit 7 - Alcohols, Phenols and Ethers", "topics": ["Preparation of Alcohols and Phenols", "Acidity of Phenols & Kolbe's Reaction", "Williamson Ether Synthesis Mechanism"]},
                        {"number": 8, "name": "Unit 8 - Aldehydes, Ketones and Carboxylic Acids", "topics": ["Nucleophilic Addition Reactions", "Aldol Condensation & Cannizzaro Reaction", "Acidity of Carboxylic Acids & HVZ Reaction"]},
                        {"number": 9, "name": "Unit 9 - Amines", "topics": ["Basicity of Aliphatic and Aromatic Amines", "Hoffmann Bromamide Degradation", "Diazonium Salts and Synthetic Applications"]},
                        {"number": 10, "name": "Unit 10 - Biomolecules", "topics": ["Carbohydrates (Glucose, Fructose, Sucrose)", "Proteins (Peptide Linkage, Denaturation)", "Nucleic Acids (DNA vs RNA)"]},
                    ],
                },
                {
                    "name": "Mathematics",
                    "code": "041",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Relations and Functions & Inverse Trig", "topics": ["Equivalence Relations", "One-One and Onto Functions", "Principal Value Branches of Inverse Trig Functions"]},
                        {"number": 2, "name": "Unit 2 - Matrices and Determinants", "topics": ["Matrix Operations and Inverses", "Properties of Determinants", "Adjoint and Solution of Linear Equations"]},
                        {"number": 3, "name": "Unit 3 - Calculus (Continuity and Differentiability)", "topics": ["Continuity & Chain Rule", "Implicit and Parametric Differentiation", "Logarithmic Differentiation"]},
                        {"number": 4, "name": "Unit 4 - Applications of Derivatives", "topics": ["Rate of Change of Quantities", "Increasing and Decreasing Functions", "Maxima and Minima Practical Problems"]},
                        {"number": 5, "name": "Unit 5 - Integrals (Definite & Indefinite)", "topics": ["Integration by Substitution & Parts", "Integration by Partial Fractions", "Fundamental Theorem of Calculus & Definite Integrals Properties"]},
                        {"number": 6, "name": "Unit 6 - Applications of Integrals & Differential Equations", "topics": ["Area bounded by Curves, Lines and Parabolas", "Order and Degree of DEs", "Separable Variables & Homogeneous DEs", "Linear Differential Equations"]},
                        {"number": 7, "name": "Unit 7 - Vectors and Three-Dimensional Geometry", "topics": ["Scalar and Vector Products", "Direction Cosines and Lines in 3D", "Shortest Distance between Skew Lines"]},
                        {"number": 8, "name": "Unit 8 - Linear Programming & Probability", "topics": ["Mathematical Formulation of LPP & Graphical Solutions", "Conditional Probability & Bayes' Theorem", "Independent Events & Probability Distributions"]},
                    ],
                },
                {
                    "name": "Computer Science",
                    "code": "083",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Computational Thinking and Programming - 2 (Python)", "topics": ["Functions, Scope and Parameter Passing", "File Handling (Text, Binary, CSV)", "Data Structures (Stack operations: Push, Pop)"]},
                        {"number": 2, "name": "Unit 2 - Computer Networks", "topics": ["Network Topologies and Devices", "OSI & TCP/IP Model Protocols (HTTP, FTP, DNS)", "Network Security and Cyber Forensics"]},
                        {"number": 3, "name": "Unit 3 - Database Management (SQL & Python Connectivity)", "topics": ["Relational Data Model & Keys", "SQL Queries (GROUP BY, HAVING, JOINs)", "Python-MySQL Connector Interface"]},
                    ],
                },
            ],
        },
    ]
    catalog.extend(cbse_entries)

    # 2. State Boards: Tamil Nadu, Kerala, Karnataka, Maharashtra, AP, Telangana (Classes 10 & 12)
    state_board_configs = [
        ("TNSB", "Tamil Nadu State Board"),
        ("KBPE", "Kerala Board of Public Examinations"),
        ("KSEEB", "Karnataka School Examination Board"),
        ("MSBSHSE", "Maharashtra State Board"),
        ("BIEAP", "Andhra Pradesh State Board"),
        ("TSBIE", "Telangana State Board"),
    ]

    for b_code, b_name in state_board_configs:
        # Class 10
        catalog.append({
            "board": b_code,
            "class": 10,
            "subjects": [
                {
                    "name": "Mathematics",
                    "code": f"{b_code}-10-MAT",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Relations and Functions & Number Theory", "topics": ["Functions", "Sequences and Series", "Modular Arithmetic"]},
                        {"number": 2, "name": "Unit 2 - Algebra (Polynomials, Quadratics & Matrices)", "topics": ["Quadratic Equations", "Matrix Operations", "Linear Inequations"]},
                        {"number": 3, "name": "Unit 3 - Coordinate Geometry & Trigonometry", "topics": ["Straight Line Equations", "Trigonometric Identities", "Heights and Distances"]},
                        {"number": 4, "name": "Unit 4 - Geometry & Mensuration", "topics": ["Similarity Theorems", "Circles and Tangents", "Surface Area and Volume of Solids"]},
                        {"number": 5, "name": "Unit 5 - Statistics and Probability", "topics": ["Standard Deviation & Variance", "Addition Theorem of Probability"]},
                    ],
                },
                {
                    "name": "Science",
                    "code": f"{b_code}-10-SCI",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Physics: Laws of Motion, Electricity & Optics", "topics": ["Newton's Laws", "Current and Circuits", "Lenses and Refraction"]},
                        {"number": 2, "name": "Unit 2 - Chemistry: Reactions, Acids/Bases & Carbon", "topics": ["Types of Reactions", "pH Scale Applications", "Carbon Allotropes and Hydrocarbons"]},
                        {"number": 3, "name": "Unit 3 - Biology: Physiology, Genetics & Ecology", "topics": ["Plant Anatomy and Respiration", "Mendelian Genetics", "Environmental Conservation"]},
                    ],
                },
                {
                    "name": "Social Science",
                    "code": f"{b_code}-10-SOC",
                    "units": [
                        {"number": 1, "name": "Unit 1 - History & Freedom Struggle", "topics": ["State and National Freedom Movements", "Social Reform Movements"]},
                        {"number": 2, "name": "Unit 2 - Geography & Natural Resources", "topics": ["State Topography & Climate", "Agricultural Patterns & Industries"]},
                        {"number": 3, "name": "Unit 3 - Civics and Economics", "topics": ["Constitution of India", "State Governance and GDP Growth"]},
                    ],
                },
            ],
        })

        # Class 12
        catalog.append({
            "board": b_code,
            "class": 12,
            "subjects": [
                {
                    "name": "Physics",
                    "code": f"{b_code}-12-PHY",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Electrostatics & Current Electricity", "topics": ["Electric Field and Potential", "Kirchhoff's Laws and Networks"]},
                        {"number": 2, "name": "Unit 2 - Magnetism, EMI and Alternating Current", "topics": ["Magnetic Dipole", "Electromagnetic Induction", "AC Circuits and Power"]},
                        {"number": 3, "name": "Unit 3 - Optics & Wave Theory", "topics": ["Ray Optics and Wavefronts", "Interference and Polarization"]},
                        {"number": 4, "name": "Unit 4 - Modern Physics & Semiconductor Electronics", "topics": ["Photoelectric Emission", "Nuclear Physics", "Diodes, Transistors and Logic Gates"]},
                    ],
                },
                {
                    "name": "Chemistry",
                    "code": f"{b_code}-12-CHE",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Physical Chemistry (Solutions, Kinetics, Electrochemistry)", "topics": ["Colligative Properties", "Reaction Rates", "Electrochemical Cells"]},
                        {"number": 2, "name": "Unit 2 - Inorganic Chemistry (d/f-block, Coordination Chemistry)", "topics": ["Transition Metals", "Coordination Compounds Nomenclature"]},
                        {"number": 3, "name": "Unit 3 - Organic Chemistry (Halogen Derivatives, Carbonyls, Amines)", "topics": ["Reaction Mechanisms", "Carbonyl Additions", "Organic Synthesis"]},
                    ],
                },
                {
                    "name": "Mathematics",
                    "code": f"{b_code}-12-MAT",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Matrices, Determinants and Complex Numbers", "topics": ["Matrix Inversion", "Complex Number Geometry"]},
                        {"number": 2, "name": "Unit 2 - Differential and Integral Calculus", "topics": ["Derivatives and Applications", "Definite Integrals and Area Calculations"]},
                        {"number": 3, "name": "Unit 3 - Vector Algebra and 3D Analytical Geometry", "topics": ["Vectors Dot and Cross Products", "Lines and Planes in Space"]},
                        {"number": 4, "name": "Unit 4 - Differential Equations and Probability Distributions", "topics": ["First Order Differential Equations", "Binomial and Normal Distributions"]},
                    ],
                },
                {
                    "name": "Computer Science",
                    "code": f"{b_code}-12-CS",
                    "units": [
                        {"number": 1, "name": "Unit 1 - Advanced Python Programming & OOP", "topics": ["Object-Oriented Concepts", "File Handling and Exception Handling"]},
                        {"number": 2, "name": "Unit 2 - Relational Databases and SQL", "topics": ["Data Definition and Manipulation", "Nested SQL Queries"]},
                        {"number": 3, "name": "Unit 3 - Computer Networking & Web Security", "topics": ["Network Architectures", "Web Security and Cybersecurity"]},
                    ],
                },
            ],
        })

    return catalog


def import_syllabus_data(db: Session, syllabus_json_or_dict: Any) -> Dict[str, Any]:
    """
    Ingest a structured syllabus JSON/YAML dictionary into the database idempotently.
    Ensures Boards, Classes, Subjects, Units, and Topics are created and linked cleanly.
    """
    if isinstance(syllabus_json_or_dict, str):
        try:
            data = json.loads(syllabus_json_or_dict)
        except Exception:
            data = yaml.safe_load(syllabus_json_or_dict)
    else:
        data = syllabus_json_or_dict

    if not isinstance(data, list):
        data = [data]

    # Pre-register official boards
    board_objs = {}
    for b_info in OFFICIAL_BOARDS_REGISTRY:
        b_code = b_info["code"]
        board_rec = db.query(Board).filter(Board.code == b_code).first()
        if not board_rec:
            board_rec = Board(
                code=b_code,
                name=b_info["name"],
                state=b_info["state"],
                website_url=b_info.get("website_url"),
                description=b_info.get("description"),
                active=True,
            )
            db.add(board_rec)
            db.flush()
        board_objs[b_code] = board_rec

    # Ensure Academic Year exists (e.g. 2026-27)
    for b_rec in board_objs.values():
        ay = db.query(AcademicYear).filter(AcademicYear.board_id == b_rec.id, AcademicYear.year_code == "2026-27").first()
        if not ay:
            ay = AcademicYear(board_id=b_rec.id, year_code="2026-27", is_current=True)
            db.add(ay)
            db.flush()

    total_classes = 0
    total_subjects = 0
    total_units = 0
    total_topics = 0

    for entry in data:
        board_code = entry.get("board", "CBSE").upper()
        class_num = int(entry.get("class", 10))
        class_name_str = f"Class {class_num}"

        board_rec = board_objs.get(board_code)
        if not board_rec:
            board_rec = db.query(Board).filter(Board.code == board_code).first()
            if not board_rec:
                board_rec = Board(code=board_code, name=f"{board_code} Education Board", state="India", active=True)
                db.add(board_rec)
                db.flush()
            board_objs[board_code] = board_rec

        # Ensure AcademicClass exists
        class_rec = (
            db.query(AcademicClass)
            .filter(AcademicClass.board_id == board_rec.id, AcademicClass.class_number == class_num)
            .first()
        )
        if not class_rec:
            class_rec = AcademicClass(
                board_id=board_rec.id,
                class_code=class_name_str,
                class_number=class_num,
                active=True,
            )
            db.add(class_rec)
            db.flush()
            total_classes += 1

        ay_rec = db.query(AcademicYear).filter(AcademicYear.board_id == board_rec.id).first()

        # Ingest subjects
        for sub_data in entry.get("subjects", []):
            sub_name = sub_data["name"]
            sub_code = sub_data.get("code")
            sub_type = sub_data.get("subject_type", "core")

            subject_rec = (
                db.query(Subject)
                .filter(
                    Subject.board_id == board_rec.id,
                    Subject.class_id == class_rec.id,
                    Subject.subject_name == sub_name,
                )
                .first()
            )

            if not subject_rec:
                # Check legacy subject matching by name + class
                legacy = (
                    db.query(Subject)
                    .filter(Subject.subject_name == sub_name, Subject.class_name == str(class_num))
                    .first()
                )
                if legacy:
                    subject_rec = legacy
                    subject_rec.board_id = board_rec.id
                    subject_rec.class_id = class_rec.id
                    subject_rec.academic_year_id = ay_rec.id if ay_rec else None
                    subject_rec.subject_code = sub_code
                    subject_rec.subject_type = sub_type
                    subject_rec.active = True
                else:
                    subject_rec = Subject(
                        subject_name=sub_name,
                        class_name=str(class_num),
                        board=board_rec.code,
                        board_id=board_rec.id,
                        academic_year_id=ay_rec.id if ay_rec else None,
                        class_id=class_rec.id,
                        subject_code=sub_code,
                        subject_type=sub_type,
                        active=True,
                    )
                    db.add(subject_rec)
                    db.flush()
                    total_subjects += 1
            else:
                subject_rec.subject_code = sub_code
                subject_rec.subject_type = sub_type
                subject_rec.active = True

            # Ingest Units
            existing_units = {u.unit_name.strip().lower(): u for u in subject_rec.units}
            for u_data in sub_data.get("units", []):
                u_name = u_data["name"]
                u_num = u_data.get("number")
                u_desc = u_data.get("description")

                unit_rec = existing_units.get(u_name.strip().lower())
                if not unit_rec:
                    unit_rec = Unit(
                        subject_id=subject_rec.id,
                        unit_name=u_name,
                        unit_number=u_num,
                        description=u_desc,
                        active=True,
                    )
                    db.add(unit_rec)
                    db.flush()
                    existing_units[u_name.strip().lower()] = unit_rec
                    total_units += 1
                else:
                    unit_rec.unit_number = u_num
                    unit_rec.description = u_desc

                # Ingest Topics
                existing_topics = {t.topic_name.strip().lower() for t in unit_rec.topics}
                for t_item in u_data.get("topics", []):
                    t_name = t_item if isinstance(t_item, str) else t_item.get("name")
                    if t_name and t_name.strip().lower() not in existing_topics:
                        topic_rec = Topic(
                            unit_id=unit_rec.id,
                            topic_name=t_name.strip(),
                            active=True,
                        )
                        db.add(topic_rec)
                        existing_topics.add(t_name.strip().lower())
                        total_topics += 1

    db.commit()
    return {
        "status": "success",
        "imported_classes": total_classes,
        "imported_subjects": total_subjects,
        "imported_units": total_units,
        "imported_topics": total_topics,
        "message": f"Successfully imported structured curriculum catalog: {total_subjects} subjects, {total_units} units, {total_topics} topics.",
    }


def seed_all_standard_curriculums(db: Session) -> Dict[str, Any]:
    """Seed comprehensive standard curriculum across all 7 Indian boards and Classes 1 to 12."""
    catalog = generate_standard_curriculum_catalog()
    return import_syllabus_data(db, catalog)


def main():
    """CLI entrypoint for structured syllabus ingestion."""
    parser = argparse.ArgumentParser(description="Import structured syllabus data into AQPG.")
    parser.add_argument("--board", default="all", help="Board code or 'all' to seed standard catalog")
    parser.add_argument("--file", default=None, help="Path to custom JSON/YAML syllabus file")

    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    # Ensure schema migrations
    from sqlalchemy import text
    with engine.connect() as conn:
        for t, col, cdef in [
            ("boards", "active", "BOOLEAN DEFAULT 1"),
            ("academic_classes", "active", "BOOLEAN DEFAULT 1"),
            ("subjects", "subject_type", "VARCHAR(50) DEFAULT 'core'"),
            ("subjects", "active", "BOOLEAN DEFAULT 1"),
            ("units", "description", "TEXT NULL"),
            ("units", "active", "BOOLEAN DEFAULT 1"),
            ("topics", "active", "BOOLEAN DEFAULT 1"),
            ("questions", "is_ai_generated", "BOOLEAN DEFAULT 0"),
            ("questions", "approved", "BOOLEAN DEFAULT 1"),
            ("questions", "active", "BOOLEAN DEFAULT 1"),
            ("questions", "numerical_data", "TEXT NULL"),
            ("questions", "application_context", "TEXT NULL"),
        ]:
            try:
                conn.execute(text(f"ALTER TABLE {t} ADD COLUMN {col} {cdef}"))
                conn.commit()
            except Exception:
                pass

    db = SessionLocal()

    try:
        if args.file and os.path.exists(args.file):
            print(f"Reading structured syllabus from '{args.file}'...")
            with open(args.file, "r", encoding="utf-8") as f:
                content = f.read()
            res = import_syllabus_data(db, content)
            print(f"Status: {res['status'].upper()} - {res['message']}")
        else:
            print("Seeding full multi-board standard curriculum catalog (CBSE + 6 State Boards, Classes 1-12)...")
            res = seed_all_standard_curriculums(db)
            print(f"Status: {res['status'].upper()} - {res['message']}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
