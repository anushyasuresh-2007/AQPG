"""Seed initial reference data for AQPG development."""

from sqlalchemy.orm import Session

from app.api.v1.endpoints.auth import hash_password
from app.models.academic_class import AcademicClass
from app.models.academic_year import AcademicYear
from app.models.bloom import Bloom
from app.models.board import Board
from app.models.question import Question
from app.models.subject import Subject
from app.models.unit import Unit
from app.models.user import User
from app.services.curriculum.sync import sync_board_curriculum


STANDARD_BLOOMS = [
    "Remember",
    "Understand",
    "Apply",
    "Analyze",
    "Evaluate",
    "Create",
]


def seed_database(db: Session) -> None:
    """Safely seed essential Bloom levels, default teacher user, and sample curriculum data."""
    # 1. Clean up invalid/empty bloom levels and ensure standard Bloom taxonomy exists
    empty_blooms = db.query(Bloom).filter((Bloom.level_name == "") | (Bloom.level_name.is_(None))).all()
    for eb in empty_blooms:
        if not eb.questions:
            db.delete(eb)
    db.commit()

    existing_bloom_names = {b.level_name.lower(): b for b in db.query(Bloom).all()}
    for name in STANDARD_BLOOMS:
        if name.lower() not in existing_bloom_names:
            new_bloom = Bloom(level_name=name)
            db.add(new_bloom)
    db.commit()

    bloom_map = {b.level_name: b for b in db.query(Bloom).all()}

    # 2. Ensure default teacher account exists
    teacher = db.query(User).filter(User.email == "teacher@aqpg.com").first()
    if not teacher:
        teacher_user = User(
            name="Teacher",
            email="teacher@aqpg.com",
            password=hash_password("teacher123"),
            role="teacher",
        )
        db.add(teacher_user)
        db.commit()

    # 3. Synchronize CBSE & TNSB Curricula if not already populated
    cbse_board = db.query(Board).filter(Board.code == "CBSE").first()
    if not cbse_board or db.query(Subject).filter(Subject.board == "CBSE").count() < 5:
        sync_board_curriculum(db, board_key="cbse", academic_year_code="2026-27")

    tn_board = db.query(Board).filter(Board.code == "TNSB").first()
    if not tn_board or db.query(Subject).filter(Subject.board == "TNSB").count() < 4:
        sync_board_curriculum(db, board_key="tnsb", academic_year_code="2026-27")

    # 4. Ensure sample approved questions are seeded for Class X Science (CBSE)
    sci_subject = (
        db.query(Subject)
        .filter(Subject.subject_name == "Science", Subject.class_name == "10", Subject.board == "CBSE")
        .first()
    )
    if sci_subject and sci_subject.units and db.query(Question).filter(Question.subject_id == sci_subject.id).count() < 25:

        units = sci_subject.units
        u1 = units[0]
        u2 = units[1] if len(units) > 1 else u1
        u3 = units[2] if len(units) > 2 else u1
        u4 = units[3] if len(units) > 3 else u1

        sample_science_questions = [
            (u1, "Remember", "State the Law of Conservation of Mass in a chemical reaction.", 1, "easy", "Mass can neither be created nor destroyed in a chemical reaction.", "Fundamental chemistry postulate."),
            (u1, "Remember", "Write the balanced chemical equation for the reaction of iron with steam.", 2, "medium", "3Fe(s) + 4H2O(g) -> Fe3O4(s) + 4H2(g)", "Equation balancing."),
            (u1, "Remember", "Define rancidity and suggest two methods to prevent it.", 2, "easy", "Oxidation of oils and fats. Prevented by antioxidants and nitrogen flushing.", "Oxidation prevention."),
            (u1, "Remember", "What is an indicator? Name two natural and synthetic indicators.", 5, "easy", "Substances that indicate acidic or basic nature. Litmus, Turmeric; Phenolphthalein, Methyl orange.", "Indicator definitions."),
            (u1, "Understand", "Why do copper vessels turn green when exposed to moist air for a long time?", 3, "medium", "Copper reacts with moist carbon dioxide in the air and slowly loses its shiny brown surface and gains a green coat of basic copper carbonate.", "Corrosion explanation."),
            (u1, "Understand", "Explain why respiration is considered an exothermic reaction with a chemical equation.", 3, "medium", "During respiration, glucose combines with oxygen in the cells of our body and provides energy. C6H12O6 + 6O2 -> 6CO2 + 6H2O + Energy.", "Exothermic reaction."),
            (u1, "Understand", "Why is sodium kept immersed in kerosene oil?", 2, "easy", "Sodium reacts vigorously with moisture and oxygen in the air, catching fire.", "Alkali metal reactivity."),
            (u1, "Understand", "Explain the formation of ionic compound Magnesium Oxide (MgO) with electron dot structures.", 3, "medium", "Mg loses 2 electrons to form Mg2+, O gains 2 electrons to form O2-.", "Ionic bonding."),
            (u1, "Understand", "Differentiate between soap and detergents based on chemical composition and cleansing action in hard water.", 4, "medium", "Soaps are sodium salts of fatty acids and form scum in hard water; detergents are ammonium or sulphonate salts.", "Detergents chemistry."),
            (u1, "Apply", "A shiny brown coloured element 'X' on heating in air becomes black in colour. Name the element 'X' and the black coloured compound formed.", 3, "medium", "Element X is Copper (Cu). Black compound is Copper(II) Oxide (CuO). 2Cu + O2 -> 2CuO.", "Analytical application."),
            (u1, "Apply", "A compound 'X' is used in whitewashing. Write its chemical name, formula, and reaction with water.", 2, "easy", "Calcium oxide (CaO, quicklime). CaO + H2O -> Ca(OH)2 + Heat.", "Chemical application."),
            (u1, "Apply", "Equal lengths of magnesium ribbons are taken in test tubes A and B. Hydrochloric acid is added to A and acetic acid to B. In which tube does fizzing occur more vigorously and why?", 5, "medium", "Test tube A with HCl, because HCl is a strong acid that dissociates completely producing H2 gas faster.", "Acid strength application."),
            (u1, "Apply", "Write the chemical formula and two uses of Bleaching powder and Plaster of Paris.", 5, "medium", "CaOCl2 and CaSO4.1/2H2O. Disinfectant and plastering fractured bones.", "Salt applications."),
            (u1, "Analyze", "Differentiate between exothermic and endothermic reactions with suitable examples for each.", 5, "medium", "Exothermic reactions release heat energy while endothermic reactions absorb heat energy.", "Comparative analysis."),
            (u1, "Analyze", "Compare the reactivity of metals Zn, Fe, Cu, and Al based on displacement reactions.", 5, "hard", "Reactivity series order: Al > Zn > Fe > Cu.", "Metal reactivity analysis."),
            (u2, "Remember", "What is the primary function of nephrons in the human excretory system?", 1, "easy", "Filtration of blood and urine formation.", "Anatomy recall."),
            (u2, "Remember", "State the role of saliva in the digestion of food.", 2, "easy", "Salivary amylase breaks down starch into simple sugars.", "Enzyme biology."),
            (u2, "Understand", "Describe the role of bile juice in human digestion.", 2, "easy", "Emulsification of fats and making acidic food alkaline for pancreatic enzymes.", "Digestive physiology."),
            (u2, "Understand", "Explain the double circulation of blood in human beings with a schematic pathway.", 5, "medium", "Blood goes through the heart twice during each cycle (pulmonary and systemic circulation).", "Cardiovascular concepts."),
            (u2, "Apply", "What will happen if the diaphragm of a person gets ruptured in an accident? Justify your answer.", 3, "hard", "The thoracic cavity volume cannot increase, making inhalation impossible, leading to suffocation.", "Physiological application."),
            (u3, "Remember", "State Snell's Law of refraction of light.", 2, "easy", "The ratio of sine of angle of incidence to sine of angle of refraction is constant (n = sin i / sin r).", "Optics definition."),
            (u3, "Understand", "Why does the sun appear reddish early in the morning and at sunset?", 3, "medium", "At sunrise/sunset, sunlight travels longer distances through the atmosphere, scattering blue light away and leaving longer red wavelengths.", "Atmospheric refraction & scattering."),
            (u3, "Apply", "An object 4 cm in height is placed at 15 cm in front of a concave mirror of focal length 10 cm. Find the position and nature of the image formed.", 5, "medium", "Using 1/f = 1/v + 1/u, 1/(-10) = 1/v + 1/(-15) => v = -30 cm. Real, inverted and magnified.", "Numerical ray optics."),
            (u4, "Remember", "Define 1 Ohm of electrical resistance.", 1, "easy", "1 Ohm is the resistance of a conductor when a potential difference of 1 Volt across its ends produces a current of 1 Ampere.", "Electrical definition."),
            (u4, "Understand", "State Ohm's Law and draw the V-I graph for an ohmic conductor.", 3, "medium", "Current is directly proportional to potential difference across ends at constant temperature (V = IR).", "Ohm's Law."),
            (u4, "Apply", "Calculate the equivalent resistance when three resistors of 2 Ohm, 3 Ohm, and 6 Ohm are connected in parallel.", 2, "easy", "1/R = 1/2 + 1/3 + 1/6 = 6/6 = 1. R = 1 Ohm.", "Circuit calculations."),
            (u4, "Analyze", "Two electric bulbs rated 220V, 100W and 220V, 60W are connected in parallel to an electric mains supply. Find the current drawn from the line if the supply voltage is 220V.", 4, "hard", "I1 = 100/220 = 0.45A, I2 = 60/220 = 0.27A. Total I = 0.72A.", "Power analysis."),
        ]


        for u_obj, b_lvl, q_txt, marks, diff, ans, exp in sample_science_questions:
            bloom_rec = bloom_map.get(b_lvl)
            if bloom_rec:
                q_obj = Question(
                    subject_id=sci_subject.id,
                    unit_id=u_obj.id,
                    bloom_level_id=bloom_rec.id,
                    board_id=sci_subject.board_id,
                    academic_year_id=sci_subject.academic_year_id,
                    class_id=sci_subject.class_id,
                    question_text=q_txt,
                    question_type="Short Answer" if marks <= 2 else ("Descriptive" if marks >= 5 else "Medium Answer"),
                    marks=marks,
                    difficulty=diff,
                    answer=ans,
                    explanation=exp,
                    source_type="official_sample",
                    status="approved",
                )
                db.add(q_obj)
        db.commit()

    # 5. Ensure existing legacy questions have status='approved'
    db.query(Question).filter(Question.status.is_(None)).update({"status": "approved", "source_type": "teacher"})
    db.commit()
