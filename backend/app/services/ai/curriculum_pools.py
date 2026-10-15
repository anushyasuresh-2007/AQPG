"""
curriculum_pools.py
Authoritative, syllabus-grounded curriculum questions and answer keys for
CBSE and Tamil Nadu State Board (TNSB) (Classes 10 & 12).

Provides rich, academically authentic question pools for:
1. English (Prose, Poetry, Supplementary, Grammar, Writing Tasks, Comprehension)
2. Social Science (History, Geography, Civics/Political Science, Economics, Map Skills)
3. Biology / Life Sciences (Physiology, Genetics, Reproduction, Biotechnology)
4. Economics (Macroeconomics, National Income, Money & Banking, Fiscal Policy)
5. Accountancy & Commerce / Business Studies (Transactions, Shares, Management)
"""

import random
import re
from typing import Dict, Any, List, Optional, Iterable, Set
from app.services.bloom_service import BLOOM_HIERARCHY


# =============================================================================
# 1. ENGLISH QUESTION POOLS (Class 10 & Class 12 - CBSE & TNSB)
# =============================================================================

ENGLISH_PROSE_QUESTIONS = [
    # Class 10 (CBSE: A Letter to God, Nelson Mandela, Two Stories about Flying, Anne Frank, Valli, Benares, The Proposal)
    # Class 10 (TNSB: His First Flight, The Night the Ghost Got In, The Attic, Tech Bloomers, Empowered Women)
    {
        "board": "CBSE", "class": 10, "unit": "Prose", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Why did Lencho write a letter to God, and why did he refer to the post office employees as a 'bunch of crooks'?",
        "a": "Lencho wrote to God asking for 100 pesos after a hailstorm destroyed his entire corn crop. When he received only 70 pesos sent by the kind postmaster, his unshakeable faith made him believe God could not make a mistake, leading him to conclude the post office staff had stolen the remaining 30 pesos."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Prose", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "How does Nelson Mandela define 'courage' in 'Long Walk to Freedom', and what are the twin obligations he describes?",
        "a": "Mandela explains that courage is not the absence of fear, but the triumph over it. The twin obligations every man has are: obligations to his family, parents, wife and children; and obligations to his people, community and country."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Prose", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "What lesson does the Buddha convey to Kisa Gotami in 'The Sermon at Benares'? How did the mustard seed signify universal grief?",
        "a": "The Buddha asked Kisa Gotami to procure mustard seeds from a house where no one had died. When she could find no such house, she realized that death is common to all mortals and that grief and lamentation only increase pain rather than bringing peace of mind."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Prose", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "How did the young seagull's parents motivate him to take his first flight in Liam O'Flaherty's 'His First Flight'?",
        "a": "The parents scolded him, threatened to let him starve on his ledge, and ultimately his mother tempted him with a piece of fish just out of reach, forcing him to dive in desperation and discover his natural ability to fly."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Prose", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Why did Aditya decide to visit the attic in his ancestral house in Satyajit Ray's story 'The Attic'?",
        "a": "Aditya wished to retrieve the antique silver medal won by Sasanka Sanyal twenty-nine years earlier, which Aditya had taken and never returned, in order to relieve his lingering sense of guilt and restore justice."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Prose", "bloom": "Understand", "type": "Short Answer", "marks": 2,
        "q": "Describe the humorous chaos created when the grandfather mistook the police officers for deserters in 'The Night the Ghost Got In'.",
        "a": "The grandfather, believing the police officers were deserters from Meade's army, jumped out of bed, seized a gun, and shot a policeman in the shoulder before being subdued."
    },
    # Class 12 (CBSE: The Last Lesson, Lost Spring, Deep Water, The Rattrap, Indigo)
    # Class 12 (TNSB: Two Gentlemen of Verona, A Nice Cup of Tea, In Celebration of Being Alive)
    {
        "board": "CBSE", "class": 12, "unit": "Prose", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "In 'The Last Lesson', how did Franz's feelings about school and M. Hamel change when he learned that French would no longer be taught in Alsace?",
        "a": "Franz felt deep remorse for neglecting his studies and wasting time. His books, which had seemed like burdens, suddenly felt like old friends, and his resentment toward M. Hamel's strict ruler vanished into respect and sympathy."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Prose", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Contrast the lives of Saheb-e-Alam in Seemapuri and Mukesh in Firozabad in Anees Jung's 'Lost Spring'. How do their attitudes toward their destiny differ?",
        "a": "Saheb resigns himself to ragpicking and loses his freedom when he takes a tea stall job. In contrast, Mukesh dares to dream of breaking the vicious cycle of poverty and exploitation by declaring his ambition to become a motor mechanic."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Prose", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "How does the metaphor of the rattrap serve as the central theme in Selma Lagerlöf's story? How does Edla Willmansson bring about a transformation in the peddler?",
        "a": "The peddler views the world as a giant rattrap offering riches and joy as bait. Edla treats him with unconditional kindness, respect, and dignity, which awakens his self-worth and leads him to return the stolen thirty kronor."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Prose", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "In A.J. Cronin's 'Two Gentlemen of Verona', justify the title with reference to the self-sacrificing nature of Nicola and Jacopo.",
        "a": "Despite their tender age and devastation caused by war, Nicola and Jacopo take on various odd jobs—selling fruit, shining shoes, hawking newspapers—without complaint to fund the medical treatment for their sister Lucia suffering from tuberculosis of the spine."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Prose", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "State any four golden rules George Orwell prescribes for making the perfect cup of tea in 'A Nice Cup of Tea'.",
        "a": "1. Use Indian or Ceylonese tea. 2. Make tea in a teapot (earthenware or china). 3. The pot should be warmed beforehand. 4. Pour water while it is still boiling and stir well."
    },
]

ENGLISH_POETRY_QUESTIONS = [
    {
        "board": "CBSE", "class": 10, "unit": "Poetry", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "How does Leslie Norris contrast the tiger in the cage with the tiger in the wild in 'A Tiger in the Zoo'?",
        "a": "In the cage, the tiger is confined behind concrete walls, stalking quietly with suppressed rage and ignoring visitors. In the wild, he is free, lurking in shadows near water holes to hunt deer and terrorizing village outskirts."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Poetry", "bloom": "Understand", "type": "Very Short Answer", "marks": 2,
        "q": "Identify the poetic device in the line 'Has given my heart / A change of mood' from Robert Frost's 'Dust of Snow' and explain its significance.",
        "a": "Alliteration ('Has given my heart'). It signifies a sudden psychological shift from melancholy and regret to renewed optimism brought about by the gentle touch of nature."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Poetry", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "What attitude towards life does Henry Van Dyke advocate in his poem 'Life'?",
        "a": "The poet advocates living life with courage, forward-looking determination, and an unreluctant soul—neither hurrying towards nor turning back from one's goal, trusting that youth and age will both bring adventure and joy."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Poetry", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Explain the significance of the lines: 'We can pull and haul and push and lift and drive... But remember, please, the Law by which we live' in Kipling's 'The Secret of the Machines'.",
        "a": "The machines boast of their immense physical power and utility to humankind, but issue a solemn warning that they lack human feelings like love, pity, or forgiveness, and a single mistake in handling them can cause fatal destruction."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Poetry", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "What does the imagery of 'young trees sprinting' and 'merry children spilling out of their homes' contrast with in Kamala Das's 'My Mother at Sixty-Six'?",
        "a": "It sharply contrasts the vibrant energy, vitality, and youth of the outside world with the frail, pale, and lifeless appearance of the poet's aging mother sitting beside her in the car."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Poetry", "bloom": "Evaluate", "type": "Short Answer", "marks": 3,
        "q": "In Pablo Neruda's 'Keeping Quiet', what does the poet mean by 'huge silence' and how can it heal human suffering?",
        "a": "The 'huge silence' represents a collective pause for introspection. It halts destructive activities (war, environmental exploitation) and allows humans to overcome the sadness of never understanding themselves and threatening themselves with death."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Poetry", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Examine how Adrienne Rich uses the symbol of 'tigers' in 'Aunt Jennifer's Tigers' to portray resistance against patriarchal oppression.",
        "a": "Aunt Jennifer's needlework tigers are fierce, proud, and unafraid of men, moving with chivalric certainty. They embody the inner freedom, vitality, and defiance that Aunt Jennifer herself is denied due to the crushing weight of her marriage band."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Poetry", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "How was the impregnable castle captured in Edwin Muir's poem 'The Castle'?",
        "a": "The castle had thick walls, brave soldiers, and plentiful provisions, but an aged, treacherous warder let the enemy through a little wicked wicket gate in exchange for a bribe of gold."
    },
]

ENGLISH_SUPPLEMENTARY_QUESTIONS = [
    {
        "board": "CBSE", "class": 10, "unit": "Supplementary", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Why was Dr. Herriot tempted to keep Tricki as a permanent guest in 'A Triumph of Surgery'?",
        "a": "Mrs. Pumphrey sent fresh eggs, wine, and brandy regularly to build Tricki's strength. Dr. Herriot and his partners enjoyed these luxurious treats during breakfast and lunch, tempting them to prolong Tricki's stay."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Supplementary", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "In 'The Thief's Story', what prompted Hari Singh to return to Anil after stealing the money at the railway station?",
        "a": "Hari Singh remembered Anil's trusting nature, kindness, and genuine effort to teach him how to read, write, and add numbers. He realized that a life of respectability and literacy was far more valuable than a few hundred stolen rupees."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Supplementary", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Describe the extraordinary talent of the bird 'Zigzag' in Asha Nehemiah's story.",
        "a": "Zigzag was a rare, multilingual bird gifted by Dr. Somu. Though he initially fell asleep and snored deafeningly, he later spoke twenty-one languages and efficiently managed Dr. Krishnan's chaotic clinic by comforting agitated patients."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Supplementary", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Discuss the conflict Dr. Sadao Hoki faces between his duty as a doctor and his patriotism as a Japanese citizen in Pearl S. Buck's 'The Enemy'.",
        "a": "When an injured American prisoner of war washes ashore, Sadao faces the dilemma of saving his enemy or turning him in. Upholding medical ethics and universal human compassion, he operates on the soldier, conceals him in his home, and eventually aids his escape."
    },
]

ENGLISH_GRAMMAR_QUESTIONS = [
    {
        "board": "COMMON", "class": 10, "unit": "Grammar", "bloom": "Apply", "type": "Short Answer", "marks": 2,
        "q": "Rewrite the following sentence in Reported Speech: The teacher said to the students, 'Have you submitted your laboratory journals today?'",
        "a": "The teacher asked the students if they had submitted their laboratory journals that day."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Grammar", "bloom": "Apply", "type": "Very Short Answer", "marks": 1,
        "q": "Fill in the blank with the appropriate modal verb: You _______ abide by the traffic regulations to ensure road safety. (must / might / would)",
        "a": "must"
    },
    {
        "board": "COMMON", "class": 10, "unit": "Grammar", "bloom": "Apply", "type": "Very Short Answer", "marks": 1,
        "q": "Identify and correct the error in the following sentence: 'Each of the participants have been awarded a certificate of merit.'",
        "a": "Error: 'have' -> Correction: 'has' (Subject 'Each' is singular)."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Grammar", "bloom": "Apply", "type": "Short Answer", "marks": 2,
        "q": "Change the voice from Active to Passive: 'The municipal corporation has reconstructed the damaged flyover.'",
        "a": "The damaged flyover has been reconstructed by the municipal corporation."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Grammar", "bloom": "Apply", "type": "Short Answer", "marks": 2,
        "q": "Transform the following compound sentence into a complex sentence: 'Work hard and you will pass the examination with distinction.'",
        "a": "If you work hard, you will pass the examination with distinction."
    },
]

ENGLISH_WRITING_QUESTIONS = [
    {
        "board": "CBSE", "class": 10, "unit": "Writing", "bloom": "Create", "type": "Long Answer", "marks": 5,
        "q": "Write a formal letter to the Editor of a national daily expressing concern over the rampant reckless driving and increasing road accidents in your city. Suggest constructive safety measures. (100-120 words)",
        "a": "Formal letter format: Sender address, Date, Receiver designation & address, Subject, Salutation, Body (cause, consequences, remedy), Subscription, Name."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Writing", "bloom": "Create", "type": "Long Answer", "marks": 5,
        "q": "Write an Analytical Paragraph based on a survey report showing that 65% of school students prefer digital e-learning over physical textbooks. Analyze the trend and state its pedagogical implications. (100-120 words)",
        "a": "Structure: Clear introductory topic sentence, comparative data analysis (percentages, trends), contrast of benefits vs limitations, balanced concluding statement."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Writing", "bloom": "Create", "type": "Short Answer", "marks": 4,
        "q": "Draft a formal Notice for your school notice board informing senior students about an upcoming Inter-School Debate Competition. (50 words)",
        "a": "Notice format: Issuing authority/school name, the word 'NOTICE', Date, Catchy Title, Body with Date/Time/Venue/Eligibility, Contact person's designation."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Writing", "bloom": "Create", "type": "Long Answer", "marks": 5,
        "q": "Draft a formal Job Application with a comprehensive Bio-data for the post of Post-Graduate Teacher (PGT) in Computer Science advertised by Sunrise Public School, Chennai.",
        "a": "Covering letter with reference to advertisement, qualification summary, followed by structured Bio-data: Personal details, Educational qualifications (tabular), Experience, References."
    },
]


# =============================================================================
# 2. SOCIAL SCIENCE QUESTION POOLS (Class 10 - CBSE & TNSB)
# =============================================================================

SOCIAL_SCIENCE_HISTORY_QUESTIONS = [
    {
        "board": "CBSE", "class": 10, "unit": "History", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Explain the major factors that led to the launch of the Non-Cooperation Movement in 1920. Why did Mahatma Gandhi decide to withdraw it in 1922?",
        "a": "Factors: Anger over the Rowlatt Act, the Jallianwala Bagh massacre, and the Khilafat grievance. Gandhiji called off the movement in February 1922 following the violent Chauri Chaura incident where a police station was set on fire, violating the principle of non-violence."
    },
    {
        "board": "CBSE", "class": 10, "unit": "History", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain how the Treaty of Vienna of 1815 sought to restore conservative order across Europe.",
        "a": "The Bourbon dynasty was restored to power in France. A series of buffer states were set up around France's borders (e.g. Kingdom of Netherlands including Belgium in north, Genoa added to Piedmont in south) to prevent future French expansion."
    },
    {
        "board": "TNSB", "class": 10, "unit": "History", "bloom": "Understand", "type": "Short Answer", "marks": 2,
        "q": "What were the three main organs of the League of Nations established after the First World War?",
        "a": "The Assembly, the Council, and the Permanent Secretariat (supported by the Permanent Court of International Justice)."
    },
    {
        "board": "TNSB", "class": 10, "unit": "History", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Examine the role of V.O. Chidambaram Pillai in the Indian Freedom Movement with special reference to the Swadeshi Steam Navigation Company.",
        "a": "V.O.C. pioneered indigenous enterprise by purchasing two ships (S.S. Galia and S.S. Lawoe) to run between Tuticorin and Colombo, challenging the monopoly of the British India Steam Navigation Company. He organized the Coral Mill strike in 1908 and suffered severe imprisonment."
    },
    {
        "board": "TNSB", "class": 10, "unit": "History", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "State the key socio-religious contributions of Ramalinga Adigal (Vallalar) in 19th century Tamil Nadu.",
        "a": "He established the Samarasa Suddha Sanmarga Sangam in 1865, advocated universal love and compassion (Jeevakarunya), showed that service to living beings is service to God, and established a free feeding hall (Sathya Gnana Sabai) at Vadalur."
    },
]

SOCIAL_SCIENCE_GEOGRAPHY_QUESTIONS = [
    {
        "board": "COMMON", "class": 10, "unit": "Geography", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Distinguish between the Khadar and Bhangar soils of the Northern Plains of India.",
        "a": "Khadar: Newer alluvium, fine-textured, highly fertile, deposited in floodplains annually. Bhangar: Older alluvium, coarser, contains calcareous deposits called 'kankar', situated above the flood levels."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Geography", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Explain the geographical conditions (temperature, rainfall, and soil) required for the cultivation of rice in India.",
        "a": "Temperature: High temperature above 25°C. Rainfall: High rainfall above 100 cm (or canal irrigation/tube-wells). Soil: Deep fertile clayey or loamy soils with water-retaining capacity."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Geography", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "What is rainwater harvesting? Explain any two traditional methods of water conservation practiced in India.",
        "a": "Rainwater harvesting is the technique of capturing and storing rainwater for future utilization. Traditional methods include 'Guls' or 'Kuls' in the Western Himalayas, and 'Khadins' and 'Johads' in Rajasthan."
    },
    {
        "board": "TNSB", "class": 10, "unit": "Geography", "bloom": "Remember", "type": "Map-based", "marks": 2,
        "q": "On an outline map of India, locate and label: (i) Tuticorin Port, (ii) Mettur Dam.",
        "a": "Tuticorin (V.O.C.) Port: Located in Gulf of Mannar, southern Tamil Nadu coast. Mettur Dam: Located across Cauvery river in Salem district, Tamil Nadu."
    },
]

SOCIAL_SCIENCE_CIVICS_QUESTIONS = [
    {
        "board": "COMMON", "class": 10, "unit": "Civics", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "What is the Preamble to the Indian Constitution? State the four core values declared in it.",
        "a": "The Preamble is the introductory statement that sets out the guiding purpose, principles, and philosophy of the Constitution. Its core values are Justice (Social, Economic, Political), Liberty, Equality, and Fraternity."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Civics", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Explain how power sharing between the Union and the States is structured under the Indian Constitution (Union List, State List, and Concurrent List).",
        "a": "Seventh Schedule divides legislative powers: 1. Union List (97 subjects like Defence, Foreign Affairs, Currency; Parliament legislates). 2. State List (66 subjects like Police, Agriculture, Health; State legislature legislates). 3. Concurrent List (47 subjects like Education, Forests; both legislate, Union law prevails in case of conflict)."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Civics", "bloom": "Evaluate", "type": "Short Answer", "marks": 3,
        "q": "Compare the power-sharing arrangements adopted by Belgium with the majoritarian policy of Sri Lanka.",
        "a": "Belgium adopted accommodation: equal representation of Dutch and French-speaking ministers, community government, avoiding civil strife. Sri Lanka adopted Sinhala majoritarianism: preferential policies for jobs and university admissions, leading to civil war."
    },
]

SOCIAL_SCIENCE_ECONOMICS_QUESTIONS = [
    {
        "board": "COMMON", "class": 10, "unit": "Economics", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "What is Per Capita Income? Why is it considered an inadequate indicator of human development on its own?",
        "a": "Per Capita Income = Total National Income / Total Population. It is inadequate because it hides disparities in wealth distribution, and ignores crucial qualitative measures such as health, life expectancy, and literacy rates."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Economics", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Distinguish between formal and informal sources of credit in India. Why do rural households depend heavily on informal sources?",
        "a": "Formal sources (Commercial Banks, Cooperatives): Low interest, RBI supervision, require collateral. Informal sources (Moneylenders, traders): High interest rates, exploitative, require no formal documentation or collateral, hence easily accessible to poor rural borrowers."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Economics", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain what is meant by 'disguised unemployment' and give an example from the Indian agricultural sector.",
        "a": "Disguised unemployment is a situation where more people are engaged in a job than actually required. For example, if a small family farm requires only 3 members to cultivate crops but all 6 family members work on it, the marginal productivity of the extra 3 workers is zero."
    },
]


# =============================================================================
# 3. BIOLOGY / LIFE SCIENCES QUESTION POOLS (Class 10 & 12)
# =============================================================================

BIOLOGY_QUESTIONS = [
    {
        "board": "COMMON", "class": 10, "unit": "Life Processes", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the pathway of double circulation in human beings with the help of a schematic flow chart.",
        "a": "Double circulation consists of: (1) Pulmonary circulation: Deoxygenated blood from right ventricle -> pulmonary artery -> lungs -> pulmonary veins -> left atrium. (2) Systemic circulation: Oxygenated blood from left ventricle -> aorta -> body tissues -> vena cava -> right atrium."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Life Processes", "bloom": "Apply", "type": "Diagram-based", "marks": 5,
        "q": "Draw a neat, labeled diagram of a nephron and explain the three steps involved in urine formation.",
        "a": "Steps: 1. Glomerular Ultrafiltration (filtration of blood under pressure in Bowman's capsule). 2. Tubular Reabsorption (glucose, amino acids, salts, water reabsorbed in PCT and loop of Henle). 3. Tubular Secretion (potassium, hydrogen ions secreted into filtrate in DCT)."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Control and Coordination", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "What is a reflex arc? Trace the sequence of events that occur when a person touches a hot object accidentally.",
        "a": "Receptor (thermoreceptors in skin) -> Sensory neuron -> Spinal cord (relay neuron) -> Motor neuron -> Effector (arm muscles contract, pulling hand away). This involuntary response protects tissues from damage."
    },
    {
        "board": "COMMON", "class": 10, "unit": "Heredity", "bloom": "Apply", "type": "Numerical", "marks": 3,
        "q": "A pure tall pea plant (TT) is crossed with a pure dwarf plant (tt). Represent the F1 and F2 generations using a Punnett square and state the phenotypic and genotypic ratios.",
        "a": "F1: All Tt (Tall). F2 (Tt x Tt): TT, Tt, Tt, tt. Phenotypic ratio: 3 Tall : 1 Dwarf. Genotypic ratio: 1 TT : 2 Tt : 1 tt."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Molecular Basis of Inheritance", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Explain the operational mechanism of the Lac Operon in Escherichia coli in the presence and absence of lactose (inducer).",
        "a": "In absence of lactose: Repressor protein binds to operator gene (o), preventing RNA polymerase from transcribing structural genes (z, y, a). In presence of lactose (allolactose): Inducer binds to repressor, inactivating it. RNA polymerase transcribes lacZ (beta-galactosidase), lacY (permease), and lacA (transacetylase)."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Biotechnology", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Describe the three major steps of the Polymerase Chain Reaction (PCR) and state the role of Taq polymerase.",
        "a": "1. Denaturation (heating DNA to 94°C to separate strands). 2. Annealing (primers bind to complementary sequences at 50-60°C). 3. Extension (Taq polymerase synthesizes new strands at 72°C using dNTPs). Taq polymerase is thermostable and survives repeated thermal cycles."
    },
    {'a': 'Parthenocarpy is the formation and development of fruit without prior fertilization of ovules, resulting in '
      'seedless fruits. Natural example: Banana. Commercially induced example: Grapes or watermelon treated with '
      'gibberellins.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define parthenocarpy. Give one natural and one commercially induced example.',
 'type': 'Short Answer',
 'unit': 'Reproduction in Organisms'},
    {'a': 'Double fertilization involves syngamy (fertilization of egg cell to form diploid zygote) and triple fusion '
      '(fusion of second male gamete with two polar nuclei to form triploid primary endosperm nucleus). The PEN '
      'undergoes repeated mitotic divisions to form nutritive endosperm tissue that nourishes the developing embryo.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the significance of double fertilization in angiosperms and describe the fate of the triploid primary '
      'endosperm nucleus (PEN).',
 'type': 'Short Answer',
 'unit': 'Reproduction in Organisms'},
    {'a': 'Sertoli cells provide nutritional support and regulation to developing spermatozoa during spermatogenesis. '
      'Leydig (interstitial) cells synthesize and secrete male steroid hormones called androgens, primarily '
      'testosterone.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the functions of Sertoli cells and Leydig cells in the human male reproductive system.',
 'type': 'Short Answer',
 'unit': 'Human Reproduction'},
    {'a': '1. Follicular phase: Pituitary FSH stimulates growth of ovarian follicles, which secrete Estrogen. Estrogen '
      'repairs and thickens uterine endometrium. 2. Ovulatory phase: Mid-cycle LH surge triggers ovulation (release of '
      'ovum from Graafian follicle). 3. Luteal phase: Ruptured follicle transforms into corpus luteum, secreting '
      'Progesterone to maintain secretory endometrium for implantation. 4. Menstrual phase: If fertilization does not '
      'occur, corpus luteum degenerates, progesterone drops, and endometrial lining sheds.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Describe the hormonal regulation of the human menstrual cycle, detailing the roles of FSH, LH, Estrogen, and '
      'Progesterone.',
 'type': 'Long Answer',
 'unit': 'Human Reproduction'},
    {'a': "Mother's genotype: X_H X_h (carrier, since her father was X_h Y). Father's genotype: X_H Y. Offspring: 25% X_H "
      'X_H (normal daughter), 25% X_H X_h (carrier daughter), 25% X_H Y (normal son), 25% X_h Y (hemophilic son). '
      'Probability of hemophilia among sons = 50%; among daughters = 0%.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'In humans, normal blood clotting is dominant over hemophilia (X-linked recessive). A normal woman whose father '
      'was hemophilic marries a normal man. Determine the probability of hemophilia among their sons and daughters.',
 'type': 'Numerical',
 'unit': 'Principles of Inheritance'},
    {'a': 'Homologous organs share common anatomical structure and embryonic origin but perform different functions (e.g. '
      'forelimbs of human, cheetah, bat, and whale); they reflect divergent evolution. Analogous organs perform '
      'similar functions but have different anatomical structures and origins (e.g. wings of butterfly and wings of '
      'bird); they reflect convergent evolution.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Distinguish between homologous and analogous organs with one example each. What type of evolution does each '
      'reflect?',
 'type': 'Short Answer',
 'unit': 'Evolution'},
    {'a': '1. In human host: Infected female Anopheles injects sporozoites during bite -> sporozoites reach liver cells '
      'via blood -> asexual reproduction in hepatocytes releases merozoites -> merozoites invade RBCs, reproduce '
      'asexually, and burst RBCs, releasing hemozoin toxic granules that cause periodic chills and fever -> some '
      'merozoites differentiate into gametocytes. 2. In mosquito vector: Mosquito ingests gametocytes during blood '
      'meal -> fertilization and development occur in mosquito gut -> mature infective sporozoites escape gut and '
      'migrate to salivary glands, ready for transmission.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Explain the life cycle of Plasmodium vivax in the human host and the female Anopheles mosquito vector.',
 'type': 'Long Answer',
 'unit': 'Human Health and Diseases'},
    {'a': 'Restriction endonucleases act as molecular scissors, cutting double-stranded DNA at specific palindromic '
      "recognition sequences. EcoRI recognizes 5'-GAATTC-3' and cuts between G and A on both strands, leaving "
      'single-stranded overhanging sticky ends (AATT) that facilitate base-pairing and ligation with vector DNA via '
      'DNA ligase.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the role of restriction endonucleases in recombinant DNA technology and describe how EcoRI produces '
      'sticky ends.',
 'type': 'Short Answer',
 'unit': 'Biotechnology'},
    {'a': 'RNAi silences specific mRNA translation through complementary double-stranded RNA (dsRNA). In tobacco plants, '
      'nematode-specific genes were introduced via Agrobacterium vectors such that both sense and antisense RNA were '
      'produced, forming dsRNA. This triggered the host RNAi machinery to cleave nematode-specific mRNA, preventing '
      'the parasite from surviving.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain how RNA interference (RNAi) operates as a cellular defense mechanism and how it was used to confer '
      'resistance against Meloidogyne incognita in tobacco plants.',
 'type': 'Short Answer',
 'unit': 'Biotechnology'},
    {'a': "Lindeman's 10% Law states that only about 10% of the energy entering a trophic level is assimilated and "
      'transferred to the next higher trophic level; the remaining 90% is dissipated as metabolic heat and '
      'respiration. Because energy declines exponentially across successive levels, insufficient energy remains after '
      '4 or 5 levels to sustain a viable higher carnivore population.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': "Explain Lindeman's 10% law of energy transfer in an ecosystem and state why food chains rarely exceed four or "
      'five trophic levels.',
 'type': 'Short Answer',
 'unit': 'Ecosystem and Environment'},
    {'a': 'The Evil Quartet encompasses: 1. Habitat loss and fragmentation, 2. Over-exploitation, 3. Alien species '
      'invasions, and 4. Co-extinctions. Habitat loss and fragmentation poses the single greatest threat (e.g. '
      'clearing of Amazonian tropical rainforests), because organisms deprived of their primary ecological niche '
      'cannot survive or reproduce, leading directly to species extirpation.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': "Critically evaluate the 'Evil Quartet' causes of biodiversity loss and assess which factor poses the greatest "
      'threat to modern biodiversity.',
 'type': 'Short Answer',
 'unit': 'Ecosystem and Environment'},
]


# =============================================================================
# 4. ECONOMICS QUESTION POOLS (Class 12 Macroeconomics & Microeconomics)
# =============================================================================

ECONOMICS_CLASS_12_QUESTIONS = [
    {
        "board": "COMMON", "class": 12, "unit": "National Income", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the difference between Real GDP and Nominal GDP. Which of the two is considered a better indicator of economic welfare and why?",
        "a": "Nominal GDP is evaluated at current market prices, while Real GDP is calculated using base-year constant prices, eliminating inflationary distortion. Real GDP is a better indicator of economic welfare because an increase in Real GDP reflects an actual rise in the physical output of goods and services produced in the economy."
    },
    {
        "board": "COMMON", "class": 12, "unit": "National Income", "bloom": "Apply", "type": "Numerical", "marks": 4,
        "q": "Calculate Gross National Product at Market Price (GNP_MP) given: GDP_FC = Rs 5000 crores, Net Indirect Taxes (NIT) = Rs 600 crores, and Net Factor Income from Abroad (NFIA) = Rs -150 crores.",
        "a": "Formula: GNP_MP = GDP_FC + NFIA + NIT = 5000 + (-150) + 600 = Rs 5450 crores."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Money and Banking", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the process of money creation (credit creation) by commercial banks using the Legal Reserve Ratio (LRR).",
        "a": "Money Multiplier = 1 / LRR. If primary deposits are Rs 1,000 and LRR is 10% (0.10), total money created = 1,000 * (1 / 0.10) = Rs 10,000. Banks lend out the excess reserves, generating derivative deposits across the banking system."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Government Budget", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Distinguish between Revenue Deficit and Fiscal Deficit. What does a high fiscal deficit signify for an economy?",
        "a": "Revenue Deficit = Revenue Expenditure - Revenue Receipts (indicates government is dissaving). Fiscal Deficit = Total Expenditure - Total Receipts excluding borrowings (indicates total borrowing requirement of the government, which can lead to inflationary pressures and debt traps)."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Balance of Payments", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Distinguish between autonomous transactions and accommodating transactions in the Balance of Payments.",
        "a": "Autonomous transactions: International economic transactions undertaken for economic motives (profit), independent of the BoP position. Accommodating transactions: Transactions undertaken by monetary authorities to cover the deficit or surplus in autonomous transactions."
    },
    {'a': 'GVA at Basic Prices is the value of output minus the value of intermediate consumption, including net '
      'production taxes (production taxes minus production subsidies). GVA at Basic Prices = GVA at Factor Cost + '
      'Production Taxes - Production Subsidies.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define Gross Value Added at Basic Prices and state how it relates to Gross Value Added at Factor Cost.',
 'type': 'Short Answer',
 'unit': 'National Income'},
    {'a': 'Households supply factor services (land, labor, capital, enterprise) to firms (real flow), and firms reward '
      'households with factor payments (rent, wages, interest, profit) (money flow). In turn, firms produce goods and '
      'services for households (real flow), and households spend their factor income on consumption expenditure buying '
      'these goods (money flow). Total factor payments = Total consumption spending.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the circular flow of income in a simple two-sector economy with households and producer firms, '
      'illustrating real flows and money flows.',
 'type': 'Short Answer',
 'unit': 'National Income'},
    {'a': 'Multiplier formula: k = 1 / (1 - MPC) = 1 / (1 - 0.75) = 1 / 0.25 = 4. Increase in income: Delta Y = k * Delta '
      'I = 4 * 500 = Rs 2,000 crores.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'In an economy, the Marginal Propensity to Consume (MPC) is 0.75. If investment increases by Rs 500 crores, '
      'calculate the resulting increase in total national income and the investment multiplier (k).',
 'type': 'Numerical',
 'unit': 'Theories of Employment and Income'},
    {'a': 'Deficient demand occurs when Aggregate Demand (AD) falls short of Aggregate Supply (AS) at full employment '
      'level, creating an output-employment gap and deflationary downward pressure. Fiscal remedy: Increase government '
      'capital expenditure and reduce direct taxes to boost disposable income. Monetary remedy: Central Bank reduces '
      'the Repo Rate and purchases government securities in open market operations (OMO) to expand commercial credit.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': "Explain the concept of 'Deficient Demand' (Deflationary Gap) in Keynesian macroeconomics. Describe one fiscal "
      'and one monetary measure to correct it.',
 'type': 'Long Answer',
 'unit': 'Theories of Employment and Income'},
    {'a': '1. Cash Reserve Ratio (CRR): When RBI increases the CRR, commercial banks must keep a larger fraction of their '
      'net demand and time liabilities with the central bank as non-lendable cash reserves, directly reducing credit '
      'availability. 2. Reverse Repo Rate: Raising the reverse repo rate incentivizes banks to park excess liquidity '
      'with the RBI, siphoning active lending funds out of the banking system.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain how the Reserve Bank of India (RBI) utilizes the Cash Reserve Ratio (CRR) and Reverse Repo Rate to '
      'control inflationary credit expansion.',
 'type': 'Short Answer',
 'unit': 'Monetary Economics, Banking and Inflation'},
    {'a': 'Revenue receipts neither create a liability nor cause a reduction in government assets (e.g. Income Tax '
      'receipts, GST, dividend from PSUs). Capital receipts either create a liability or cause a reduction in '
      'government assets (e.g. market borrowing from public/RBI, disinvestment proceeds from selling PSU equity, '
      'recovery of loans).',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Distinguish between Capital Receipts and Revenue Receipts in a government budget with two examples of each.',
 'type': 'Short Answer',
 'unit': 'Fiscal Economics & Public Finance'},
    {'a': 'Depreciation refers to the decrease in the value of the domestic currency relative to foreign currencies driven '
      'by market demand and supply forces without government intervention. Devaluation is the deliberate, official '
      'downward revision in the value of the domestic currency enacted by the government or central bank under a fixed '
      'exchange rate system.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Distinguish between Currency Depreciation under a flexible exchange rate regime and Currency Devaluation under '
      'a fixed exchange rate regime.',
 'type': 'Short Answer',
 'unit': 'International Economics & Trade'},
    {'a': 'The 1991 NEP dismantled the License-Permit Raj, abolishing industrial licensing across most sectors, removing '
      'quantitative trade restrictions, allowing Foreign Direct Investment (FDI), and instituting PSU disinvestment. '
      'Positive outcomes: High economic growth rates (reaching 7-9%), surging foreign exchange reserves, and robust '
      'expansion in service exports (IT/BPO). Structural drawbacks: Relative stagnation and distress in the '
      'agricultural sector, uneven regional industrial growth, and rising economic inequality.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Critically assess the structural transformation brought about by the New Economic Policy (NEP) of 1991 in India '
      'through Liberalisation, Privatisation, and Globalisation (LPG).',
 'type': 'Long Answer',
 'unit': 'Fiscal Planning and Development Economics in India'},
]


# =============================================================================
# 5. COMMERCE / ACCOUNTANCY / BUSINESS STUDIES QUESTION POOLS (Class 12)
# =============================================================================

COMMERCE_ACCOUNTANCY_QUESTIONS = [
    {
        "board": "COMMON", "class": 12, "unit": "Accounting for Share Capital", "bloom": "Apply", "type": "Numerical", "marks": 4,
        "q": "Pass the necessary journal entry for the forfeiture of 500 equity shares of Rs 10 each, Rs 8 called up, on which application and allotment money of Rs 5 per share has been paid.",
        "a": "Equity Share Capital A/c Dr. (500 * Rs 8) Rs 4,000\n  To Calls-in-Arrears A/c (500 * Rs 3) Rs 1,500\n  To Share Forfeiture A/c (500 * Rs 5) Rs 2,500\n(Being 500 equity shares forfeited for non-payment of call money)."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Cash Flow Statement", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Classify the following into Operating, Investing, or Financing activities: (i) Purchase of Machinery, (ii) Issue of Debentures, (iii) Cash received from Debtors.",
        "a": "(i) Purchase of Machinery: Cash Outflow from Investing Activity. (ii) Issue of Debentures: Cash Inflow from Financing Activity. (iii) Cash received from Debtors: Cash Inflow from Operating Activity."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Principles of Management", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain Henri Fayol's principle of 'Unity of Command' and state one consequence of violating this principle.",
        "a": "Unity of Command states that an employee should receive orders from and be accountable to only one superior. Violation leads to confusion, authority conflicts, indiscipline, and overlapping duties."
    },
    {
        "board": "COMMON", "class": 12, "unit": "Marketing Management", "bloom": "Analyze", "type": "Short Answer", "marks": 3,
        "q": "Explain the '4 Ps' of the Marketing Mix in Business Studies.",
        "a": "1. Product (goods or services satisfying consumer needs). 2. Price (monetary value charged for the product). 3. Place (distribution channels ensuring product availability). 4. Promotion (advertising, personal selling, sales promotion communicating product benefits)."
    },
    {'a': 'Scalar chain is the formal line of authority and communication running from the highest executive to the lowest '
      'subordinate in an unbroken chain. Gang Plank is an exception allowing direct communication between two '
      'employees of equal rank across departments to prevent communication delays during emergencies.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': "What is the 'Scalar Chain' principle formulated by Henri Fayol? What is 'Gang Plank'?",
 'type': 'Short Answer',
 'unit': 'Principles and Functions of Management'},
    {'a': '1. Focus: Taylor focused on shop floor productivity and efficiency; Fayol focused on top-level management '
      'functions. 2. Perspective: Taylor worked from bottom to top; Fayol worked from top to bottom. 3. Applicability: '
      "Taylor's principles apply specifically to manufacturing/production; Fayol's principles are universally "
      'applicable to all organizations. 4. Wage system: Taylor advocated differential piece-wage systems; Fayol '
      'advocated fair remuneration with profit sharing.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': "Compare F.W. Taylor's Scientific Management with Henri Fayol's Administrative Theory on basis of focus, "
      'perspective, applicability, and wage payment system.',
 'type': 'Long Answer',
 'unit': 'Principles and Functions of Management'},
    {'a': '1. Nature of securities: Primary market deals with new issue of shares and debentures for initial capital '
      'formation; Secondary market provides liquidity by trading existing securities. 2. Capital flow: Primary market '
      'channels funds directly from investors to enterprise; Secondary market transfers ownership between investors '
      'without direct capital inflow to the company. 3. Price determination: Primary issue price is set by '
      'management/SEBI guidelines; Secondary market prices fluctuate based on real-time market demand and supply.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Distinguish between the Primary Market and Secondary Market in the Indian financial system.',
 'type': 'Short Answer',
 'unit': 'Financial Markets & Capital Market'},
    {'a': '1. Regulatory functions: Registration of brokers, collective investment schemes, and stock exchanges. 2. '
      'Developmental functions: Training of intermediaries, promoting investor education and electronic trading. 3. '
      'Protective functions: Prohibiting insider trading, checking fraudulent market manipulations, and protecting '
      'investor rights.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'State the three main categories of functions performed by the Securities and Exchange Board of India (SEBI).',
 'type': 'Short Answer',
 'unit': 'Financial Markets & Capital Market'},
    {'a': 'Formula: Profit = Closing Capital + Drawings - Additional Capital - Opening Capital.\n'
      'Calculation: Profit = 2,10,000 + 30,000 - 20,000 - 1,50,000 = Rs 70,000 profit.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'A trader maintains books on Single Entry. Capital on 1st April 2025 was Rs 1,50,000. Capital on 31st March 2026 '
      'was Rs 2,10,000. During the year, he withdrew Rs 30,000 for domestic use and introduced Rs 20,000 fresh '
      'capital. Calculate his Profit or Loss for the year.',
 'type': 'Numerical',
 'unit': 'Accounts from Incomplete Records'},
    {'a': 'Subscription Income = Subscriptions Received (50,000) - Outstanding at beginning (4,000) + Outstanding at end '
      '(6,000) + Advance at beginning (2,000) - Advance at end (3,000) = Rs 51,000.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'A club received Rs 50,000 as subscription during 2025-26. Subscriptions outstanding on 31st March 2025: Rs '
      '4,000. Subscriptions outstanding on 31st March 2026: Rs 6,000. Subscriptions received in advance on 31st March '
      '2025: Rs 2,000. Subscriptions received in advance on 31st March 2026: Rs 3,000. Calculate subscription income '
      'to be credited to Income & Expenditure Account.',
 'type': 'Numerical',
 'unit': 'Accounts of Not-for-Profit Organisation'},
    {'a': 'Under the Indian Partnership Act, 1932: (i) Profits and losses are shared equally among all partners. (ii) '
      "Interest on partner's loan is allowed at the rate of 6% per annum, irrespective of profits or losses.",
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the accounting rules applicable in a partnership firm when there is no Partnership Deed regarding: (i) '
      "Profit sharing ratio, (ii) Interest on Partner's Loan.",
 'type': 'Short Answer',
 'unit': 'Accounts of Partnership Firms - Fundamentals'},
    {'a': 'Normal Profit = Capital Employed * Normal Rate of Return = 4,00,000 * 10% = Rs 40,000.\n'
      'Super Profit = Average Profit - Normal Profit = 55,000 - 40,000 = Rs 15,000.\n'
      'Goodwill = Super Profit * Number of Years Purchase = 15,000 * 3 = Rs 45,000.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'The capital of a firm is Rs 4,00,000 and the normal rate of return is 10%. The average profit for the last 4 '
      "years is Rs 55,000. Calculate the value of Goodwill using 3 years' purchase of Super Profit.",
 'type': 'Numerical',
 'unit': 'Goodwill in Partnership Accounts'},
    {'a': 'Let total profit = 1. Remaining share for A and B = 1 - 1/5 = 4/5.\n'
      "A's new share = 3/5 * 4/5 = 12/25.\n"
      "B's new share = 2/5 * 4/5 = 8/25.\n"
      "C's share = 1/5 = 5/25.\n"
      'New Ratio = 12 : 8 : 5.\n'
      'Sacrificing Ratio between A and B = Old Share - New Share = 3:2 (remains same since incoming partner takes '
      'share proportionately).',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'A and B are partners sharing profits in ratio of 3:2. They admit C into partnership for 1/5th share. Calculate '
      'the New Profit Sharing Ratio and the Sacrificing Ratio.',
 'type': 'Numerical',
 'unit': 'Admission of a Partner'},
    {'a': 'Ratio analysis is the quantitative analysis of financial information contained in financial statements. Current '
      'Ratio (Current Assets / Current Liabilities) assesses short-term liquidity and ability to meet immediate debt '
      "obligations (standard 2:1). Debt-Equity Ratio (Long-term Debt / Shareholders' Funds) evaluates long-term "
      'financial solvency and the margin of safety available to external creditors.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'What is Ratio Analysis? Explain the significance of Current Ratio and Debt-Equity Ratio to a prospective '
      'lender.',
 'type': 'Short Answer',
 'unit': 'Financial Statement Analysis'},
]


# =============================================================================
# 6. COMPUTER SCIENCE & IT QUESTION POOLS (Class 10 & Class 12 - TNSB & CBSE)
# =============================================================================

COMPUTER_SCIENCE_QUESTIONS = [
    # -------------------------------------------------------------------------
    # TNSB Class 12 - Unit 1: Problem Solving Techniques & Functions in Python
    # -------------------------------------------------------------------------
    # Chapter 1: Function
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "Define a pure function in Python. State the primary condition for a function to be considered pure.",
        "a": "A pure function is a function that returns the same result whenever called with the same arguments and has no side effects, meaning it does not modify any external state, global variables, or input arguments."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is an impure function in Python? Give an example.",
        "a": "An impure function is a function whose return value may vary for identical arguments or which causes side effects such as modifying a global variable or performing I/O. For example, a function that returns a random number or alters an external list."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "State the difference between formal parameters and actual arguments in a Python function definition.",
        "a": "Parameters are the variable names specified in the function definition header that receive values, whereas arguments are the actual values, variables, or expressions passed to the function when it is invoked."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Differentiate between pure functions and impure functions with suitable Python code examples.",
        "a": "Pure functions (e.g. `def square(x): return x * x`) have no side effects and always produce the exact same output for the same input. Impure functions (e.g. `def get_random(): return random.randint(1, 10)` or modifying a global list) produce side effects or non-deterministic outputs."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the difference between an Interface and an Implementation in the context of functions.",
        "a": "An interface is a set of declarations of the operations that an object or function can perform (specifying what it does). The implementation provides the internal code that carries out the operations defined in the interface (specifying how it does it)."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write a Python function `def is_pure_hypot(a, b):` that computes the hypotenuse math.sqrt(a**2 + b**2) demonstrating the concept of a pure function without side effects.",
        "a": "import math\ndef is_pure_hypot(a, b):\n    return math.sqrt(a**2 + b**2)"
    },

    # Chapter 2: Data Abstraction
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is an Abstract Data Type (ADT)? State the roles of constructors and selectors.",
        "a": "An Abstract Data Type is a specification of a set of data and the set of operations that can be performed on the data, independent of implementation. Constructors build the data type, while selectors retrieve parts of the information."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Describe how pairs, tuples, or lists can be used to construct a Point ADT with coordinates (x, y) in Python using constructors and selectors.",
        "a": "A Point ADT can be constructed using a pair: `def make_point(x, y): return [x, y]`. The selectors `def get_x(p): return p[0]` and `def get_y(p): return p[1]` retrieve the x and y coordinates respectively without exposing internal data representation."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write Python constructor `make_rational(n, d)` and selectors `numer(r)` and `denom(r)` implementing a Rational Number Abstract Data Type.",
        "a": "def make_rational(n, d):\n    return [n, d]\ndef numer(r):\n    return r[0]\ndef denom(r):\n    return r[1]"
    },

    # Chapter 3: Scoping
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "State the LEGB rule for variable scope resolution in Python programs.",
        "a": "The LEGB rule determines the order of scope resolution: Local scope (inside current function), Enclosing scope (inside outer/enclosing functions), Global scope (module level), and Built-in scope (predefined Python names)."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain how the `global` keyword affects variable scope and modification inside a Python function.",
        "a": "By default, assigning a variable inside a function creates a local variable. Declaring `global var_name` inside the function informs Python that the identifier refers to the module-level global variable, permitting modification of the global state."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write a Python program demonstrating the LEGB scoping rule where a local variable shadows an enclosing and a global variable of the same name.",
        "a": "val = 'global'\ndef outer():\n    val = 'enclosed'\n    def inner():\n        val = 'local'\n        return val\n    return inner()"
    },

    # Chapter 4: Algorithmic Strategies
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "Define the asymptotic notation Big-O (O) in the context of algorithm analysis.",
        "a": "Big-O notation describes the upper bound or worst-case execution time of an algorithm, indicating the maximum amount of time an algorithm takes to complete as a function of input size n."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "List any four essential characteristics of an algorithm according to the TNSB curriculum.",
        "a": "1. Input (zero or more inputs supplied), 2. Output (at least one output produced), 3. Finiteness (must terminate after a finite number of steps), and 4. Definiteness (all steps must be clearly defined and unambiguous)."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is memoization in dynamic programming algorithmic design?",
        "a": "Memoization is an optimization technique used in dynamic programming where the results of expensive function calls are cached and returned when the identical inputs occur again, eliminating redundant calculations."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the step-by-step working and time complexity of the Binary Search algorithm compared to Linear Search.",
        "a": "Binary Search requires a sorted collection and repeatedly divides the search interval in half. In each step, the middle element is compared with the key. If unequal, half the list is eliminated, giving O(log n) worst-case time compared to O(n) for Linear Search."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write a Python function to perform Binary Search on a sorted list of numbers `arr` for a target value `key` returning the index or -1.",
        "a": "def binary_search(arr, key):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == key: return mid\n        elif arr[mid] < key: low = mid + 1\n        else: high = mid - 1\n    return -1"
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write a Python function `fib_memo(n, memo=None)` implementing dynamic programming with memoization to compute the n-th Fibonacci number efficiently.",
        "a": "def fib_memo(n, memo=None):\n    if memo is None: memo = {}\n    if n in memo: return memo[n]\n    if n <= 1: return n\n    memo[n] = fib_memo(n - 1, memo) + fib_memo(n - 2, memo)\n    return memo[n]"
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Compare and contrast Linear Search and Binary Search algorithms regarding data prerequisites, best-case, average-case, and worst-case asymptotic time complexity.",
        "a": "Linear search requires no specific ordering of elements and checks each element sequentially, yielding O(1) best-case and O(n) worst-case time complexity. Binary search requires pre-sorted elements and repeatedly halves the search space, giving O(1) best-case and O(log n) worst-case time complexity, making it exponentially more efficient for large sorted datasets."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Analyze the time complexity and memory overhead of calculating the n-th Fibonacci number using naive recursion versus dynamic programming with memoization.",
        "a": "Naive recursion exhibits exponential time complexity O(2^n) because it repeatedly recalculates identical subproblems across branches, leading to stack overflow for larger n. Dynamic programming with memoization stores intermediate results in a dictionary or array, reducing time complexity to linear O(n) with auxiliary space complexity O(n)."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Analyze", "type": "Long Answer", "marks": 4,
        "q": "Analyze the execution differences and variable lifetimes between Local, Enclosed, Global, and Built-in namespaces during nested function calls in Python.",
        "a": "Local namespaces are created upon function invocation and destroyed upon return. Enclosed namespaces persist for the lifetime of outer functions, allowing closures to capture outer bindings. Global namespaces persist across the module execution lifetime, while Built-in namespaces remain active throughout interpreter execution."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Analyze", "type": "Long Answer", "marks": 4,
        "q": "Compare and contrast iterative algorithms versus recursive algorithmic strategies regarding call stack overhead, execution speed, and space complexity.",
        "a": "Iterative algorithms use explicit loop structures with constant O(1) auxiliary space complexity and lower overhead. Recursive algorithms repeatedly push activation records onto the call stack, incurring O(n) call stack memory overhead and risk of RecursionError/stack overflow for deep recursions, though they provide concise solutions for divide-and-conquer structures."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the advantages of pure functions and modular interface-implementation separation in developing reliable, concurrent software.",
        "a": "Pure functions provide referential transparency and eliminate side effects, making concurrent execution thread-safe and predictable. Interface-implementation separation guarantees that changes to internal data structures (e.g. replacing a tuple with a linked list in an ADT) do not break external client code relying on constructor and selector contracts."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the computational efficiency and practical trade-offs of using Abstract Data Types (ADTs) with constructors and selectors versus direct data structure manipulation in Python.",
        "a": "While direct manipulation of data structures (like indexing raw lists or tuples) may reduce function call overhead slightly, using ADTs with constructors and selectors provides encapsulation, data hiding, and modularity. This abstraction shields programs from internal implementation modifications and simplifies debugging and system scaling."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Evaluate", "type": "Long Answer", "marks": 4,
        "q": "Critically evaluate the trade-offs of using dynamic programming with memoization versus divide-and-conquer strategy for overlapping subproblems.",
        "a": "Divide-and-conquer solves independent subproblems recursively, but leads to exponential O(2^n) time when subproblems overlap. Dynamic programming with memoization stores solutions to overlapping subproblems in memory, reducing time complexity to polynomial or linear O(n) at the cost of O(n) auxiliary memory."
    },
    {
        "board": "TNSB", "class": 12, "unit": "Problem Solving Techniques & Functions in Python", "bloom": "Evaluate", "type": "Long Answer", "marks": 4,
        "q": "Justify why encapsulation and information hiding through Abstract Data Types (ADTs) are essential for large-scale software maintenance.",
        "a": "Encapsulation bundles data and the functions that manipulate it while hiding internal representation via constructors and selectors. This prevents external client code from directly accessing or corrupting internal state, allowing developers to change internal structures without breaking external contracts."
    },


    # -------------------------------------------------------------------------
    # CBSE Class 12 Computer Science (Computational Thinking & Programming)
    # -------------------------------------------------------------------------
    {
        "board": "CBSE", "class": 12, "unit": "Computational Thinking", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is the difference between mutable and immutable data types in Python? Give one example of each.",
        "a": "Mutable types (e.g. list, dictionary, set) can be modified in-place after creation without changing their memory id. Immutable types (e.g. int, float, string, tuple) cannot be altered once created; any operation creates a new object."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Computational Thinking", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the difference between positional arguments and default arguments in Python functions with an example.",
        "a": "Positional arguments must be passed in the exact order and quantity defined in the function header. Default arguments provide fallback values in the parameter list (e.g. `def greet(name, msg='Hello'):`), making them optional when calling the function."
    },
    {
        "board": "CBSE", "class": 12, "unit": "Computational Thinking", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write a Python function `push_element(stack, item)` and `pop_element(stack)` to implement stack operations using a Python list.",
        "a": "def push_element(stack, item):\n    stack.append(item)\ndef pop_element(stack):\n    return stack.pop() if stack else None"
    },

    # -------------------------------------------------------------------------
    # Class 10 Information Technology (Subject Code 402 - Units 1 to 5)
    # -------------------------------------------------------------------------
    # Unit 1: Employability Skills
    {
        "board": "CBSE", "class": 10, "unit": "Employability Skills", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "Define non-verbal communication and state any two of its elements.",
        "a": "Non-verbal communication is the exchange of information or feelings without the use of spoken words, using facial expressions, body language, postures, gestures, and eye contact."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Employability Skills", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain any three effective stress management techniques that enhance emotional well-being.",
        "a": "1. Time management (prioritizing tasks and avoiding procrastination), 2. Physical exercise and yoga (releasing tension and boosting endorphins), 3. Positivity and healthy hobby engagement (focusing on constructive outcomes and relaxation)."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Employability Skills", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Demonstrate how the 7 Cs of effective communication can be applied to draft a professional email to a team leader.",
        "a": "By ensuring the email is Clear (unambiguous purpose), Concise (brief and relevant), Concrete (specific facts), Correct (accurate grammar/data), Coherent (logical flow), Complete (all details included), and Courteous (polite tone)."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Employability Skills", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Compare and contrast internal motivation and external motivation in the context of self-management and personal goal setting.",
        "a": "Internal motivation originates from personal desire, passion, and intrinsic satisfaction without expecting external rewards, resulting in long-term resilience. External motivation is driven by rewards, recognition, or fear of penalties, which provides short-term incentives but may fade without external reinforcement."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Employability Skills", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the role of green skills and sustainable development practices in modern workplace management.",
        "a": "Adopting green skills minimizes resource consumption, reduces environmental carbon footprints, optimizes energy efficiency, and ensures compliance with ecological standards, creating sustainable competitive advantages."
    },
    # Unit 2: Digital Documentation (Advanced)
    {
        "board": "CBSE", "class": 10, "unit": "Digital Documentation", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is a Style in a word processor? Name any two categories of styles.",
        "a": "A style is a set of predefined formatting features (font, size, color, spacing) applied to text or pages to ensure document consistency. Categories include Paragraph styles and Character styles."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Digital Documentation", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the advantages of creating and using templates in a digital word processor.",
        "a": "Templates save time by providing a pre-formatted structure with standard layout and branding, prevent repetitive formatting tasks, and ensure consistency across organizational documents."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Digital Documentation", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Demonstrate the step-by-step procedure to perform Mail Merge in a word processor to generate personalized admission letters.",
        "a": "1. Create the main document (letter body), 2. Create or connect the data source (recipient list with fields like Name, Address), 3. Insert merge fields into the letter, 4. Preview and merge to produce individual letters."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Digital Documentation", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Analyze the differences between linking an image and embedding an image in a digital document regarding file size and portability.",
        "a": "Embedding stores the actual image data inside the document file, increasing document size but ensuring the image remains visible when shared. Linking stores only a reference path to the external image file, keeping the document size small but breaking display if the external image is moved or deleted."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Digital Documentation", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the utility of an automatic Table of Contents (TOC) versus manually typing chapter titles in long professional reports.",
        "a": "Automatic TOC parses document heading levels dynamically, maintaining exact page accuracy even when text shifts, and provides hyperlinked navigation. Manual TOC is error-prone, labor-intensive to update, and lacks dynamic synchronization."
    },
    # Unit 3: Electronic Spreadsheet (Advanced)
    {
        "board": "CBSE", "class": 10, "unit": "Electronic Spreadsheet", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is Goal Seek in spreadsheet software? Give an example of where it is used.",
        "a": "Goal Seek is a what-if analysis tool that calculates the input value required to achieve a specific target result formula (e.g. finding the sales volume needed to achieve $10,000 profit)."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Electronic Spreadsheet", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the purpose of consolidating data from multiple worksheets in a spreadsheet.",
        "a": "Data consolidation combines information from multiple separate worksheets or workbooks into a single master summary sheet, allowing aggregate functions (sum, average, count) across distributed reports."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Electronic Spreadsheet", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Demonstrate how to record and run a Macro in a spreadsheet to automate repetitive header formatting.",
        "a": "1. Select Tools > Macros > Record Macro, 2. Perform the desired formatting actions (set font, background color, cell borders), 3. Click Stop Recording and save macro with a descriptive name, 4. Run the macro on any selected target range to apply formatting instantly."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Electronic Spreadsheet", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Analyze the operational differences and capabilities of Goal Seek versus Solver in spreadsheet what-if analysis.",
        "a": "Goal Seek works with only one input variable and one target formula without constraints. Solver is a multi-variable optimization tool that handles multiple adjustable cells simultaneously subject to specific upper, lower, and integer constraints."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Electronic Spreadsheet", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Assess the benefits and security risks of enabling spreadsheet macros in financial data processing.",
        "a": "Macros significantly boost productivity and eliminate human calculation errors, but enabling unrestricted macros exposes systems to malicious scripts (macro viruses). Organizations mitigate risk by using digitally signed certificates and restricted execution policies."
    },
    # Unit 4: Database Management System (RDBMS)
    {
        "board": "CBSE", "class": 10, "unit": "Database Management System", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "Define Primary Key and Foreign Key in a Relational Database Management System (RDBMS).",
        "a": "A Primary Key uniquely identifies each record in a table and cannot contain null values. A Foreign Key is a field in one table that references the primary key of another table to establish referential integrity between them."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Database Management System", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain the differences between Data Definition Language (DDL) and Data Manipulation Language (DML) with examples.",
        "a": "DDL commands (e.g. CREATE, ALTER, DROP) define and modify database schema structures. DML commands (e.g. SELECT, INSERT, UPDATE, DELETE) query and manipulate data records within existing structures."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Database Management System", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Write SQL queries to (a) create a Student table with RollNo and Name, and (b) insert a record into it.",
        "a": "(a) CREATE TABLE Student (RollNo INT PRIMARY KEY, Name VARCHAR(50)); (b) INSERT INTO Student VALUES (101, 'Anita');"
    },
    {
        "board": "CBSE", "class": 10, "unit": "Database Management System", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Analyze how relational database normalization reduces data redundancy and prevents update anomalies compared to flat-file storage.",
        "a": "Flat files duplicate repeating information across rows, causing high storage waste and update anomalies where changes must be manually propagated everywhere. Normalization organizes data into related tables linked by keys, eliminating redundancy and ensuring atomic updates."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Database Management System", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the significance of database integrity constraints (Entity, Referential, Domain) in enterprise data management.",
        "a": "Integrity constraints enforce business rules and data correctness at the database engine level, rejecting invalid entries, orphan records, and mismatched types before data corrupts downstream applications."
    },
    # Unit 5: Web Applications and Security
    {
        "board": "CBSE", "class": 10, "unit": "Web Applications and Security", "bloom": "Remember", "type": "Short Answer", "marks": 2,
        "q": "What is a Firewall in computer network security? State its primary function.",
        "a": "A firewall is a network security system (hardware or software) that monitors and filters incoming and outgoing network traffic based on predetermined security rules to block unauthorized access."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Web Applications and Security", "bloom": "Understand", "type": "Short Answer", "marks": 3,
        "q": "Explain any three best practices for creating and maintaining strong passwords for online accounts.",
        "a": "1. Use at least 8-12 characters combining uppercase, lowercase, numbers, and special symbols, 2. Avoid personal information like birthdates or phone numbers, 3. Do not reuse the same password across multiple websites and change passwords periodically."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Web Applications and Security", "bloom": "Apply", "type": "Short Answer", "marks": 3,
        "q": "Demonstrate the proper safety actions and emergency procedures a workplace employee must take in the event of an electrical fire.",
        "a": "1. Immediately raise the alarm and disconnect the electrical power supply if safe, 2. Never use water on an electrical fire; use a CO2 or dry chemical powder extinguisher, 3. Evacuate via emergency routes and assemble at the designated assembly point."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Web Applications and Security", "bloom": "Analyze", "type": "Long Answer", "marks": 5,
        "q": "Analyze the mechanisms of Phishing versus Spyware attacks and their respective impact on user privacy.",
        "a": "Phishing deceives users into volunteering credentials via spoofed websites and fraudulent emails. Spyware secretly installs itself to monitor keystrokes, browsing habits, and data without user consent. Both lead to identity theft, financial loss, and compromised confidentiality."
    },
    {
        "board": "CBSE", "class": 10, "unit": "Web Applications and Security", "bloom": "Evaluate", "type": "Long Answer", "marks": 5,
        "q": "Critically evaluate the necessity of data encryption and SSL/TLS certificates for secure online e-commerce transactions.",
        "a": "SSL/TLS encrypts sensitive communication (such as credit card numbers and passwords) between client browser and server, preventing man-in-the-middle eavesdropping and packet tampering, thereby verifying merchant identity and establishing consumer trust."
    },
]



# Additional Computer Science Questions (Units 2-5 & Networks)
COMPUTER_SCIENCE_QUESTIONS.extend([
{'board': 'COMMON', 'class': 12, 'unit': 'Core Python', 'bloom': 'Remember', 'type': 'Short Answer', 'marks': 2, 'q': 'State the difference between mutable and immutable data types in Python with two examples of each.', 'a': 'Mutable types can be modified in-place after creation (e.g. lists, dictionaries, sets). Immutable types cannot be altered once created; any modification returns a new object (e.g. integers, floats, strings, tuples).'},
{'board': 'COMMON', 'class': 12, 'unit': 'Core Python', 'bloom': 'Understand', 'type': 'Short Answer', 'marks': 3, 'q': 'Explain the difference between `read()`, `readline()`, and `readlines()` file handling methods in Python.', 'a': '`read(n)` reads at most n bytes or the entire file as a single string. `readline()` reads one line up to the newline character as a string. `readlines()` reads all lines from the file and returns them as a list of strings.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Core Python', 'bloom': 'Apply', 'type': 'Short Answer', 'marks': 3, 'q': 'Write a Python function `def count_words(filename):` that reads a text file and returns the total number of words present.', 'a': "def count_words(filename):\n    with open(filename, 'r') as f:\n        content = f.read()\n        words = content.split()\n        return len(words)"},
{'board': 'COMMON', 'class': 12, 'unit': 'Core Python', 'bloom': 'Analyze', 'type': 'Long Answer', 'marks': 4, 'q': 'Compare and contrast linear search and binary search algorithms regarding data prerequisites and asymptotic time complexity.', 'a': 'Linear search inspects elements sequentially without requiring sorted data, giving O(1) best case and O(n) average/worst case. Binary search requires sorted elements and repeatedly halves the search space, giving O(1) best case and O(log n) average/worst case.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Core Python', 'bloom': 'Evaluate', 'type': 'Long Answer', 'marks': 5, 'q': 'Critically evaluate the performance trade-offs of using list comprehensions versus traditional for-loops with append operations in Python data processing.', 'a': 'List comprehensions are executed at C-level in Python bytecode, minimizing interpreter loop overhead and attribute lookup, making them faster and syntactically cleaner for transformations. However, complex comprehensions reduce code readability and build entire collections in memory simultaneously, where generators or traditional loops may prevent memory exhaustion.'},
{'a': 'A class is a user-defined blueprint or prototype from which objects are created, bundling data and methods. An '
      'object is an instance of a class. The __init__() method is a special constructor automatically invoked upon '
      'object instantiation to initialize instance attributes.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define a class and an object in Python and state the purpose of the __init__() constructor method.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Class variables are defined within the class construction but outside any methods; they are shared across all '
      'instances of the class. Instance variables are defined inside constructor methods prefixed with self; each '
      'object possesses its own independent copy.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define class variable and instance variable in Python and state the scope and memory allocation of each.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'The super() built-in function returns a temporary proxy object of the parent class, allowing access to '
      'inherited methods and delegating constructor calls without naming the parent class explicitly.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the purpose of the super() function in Python class inheritance.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Method Resolution Order (MRO) is the deterministic order in which Python searches for attributes or methods in '
      'a class hierarchy under multiple inheritance using C3 Linearization. It can be inspected using '
      'ClassName.__mro__ or ClassName.mro().',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'What is Method Resolution Order (MRO) in Python multiple inheritance, and how can it be inspected?',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': '__str__() returns an informal, readable string representation intended for end-user display (called by print() '
      'and str()). __repr__() returns an unambiguous, formal string representation primarily intended for debugging '
      'and development.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the purpose of special dunder methods __str__() and __repr__() in Python classes.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Attributes without leading underscores are public and directly accessible. Attributes prefixed with a double '
      'underscore (e.g. __balance) are private. Python applies name mangling, transforming __balance internally into '
      '_ClassName__balance to prevent accidental external access.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the concept of private and public class attributes in Python and describe how name mangling achieves '
      'data encapsulation.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Instance methods receive self as first argument and access/modify instance state. Class methods receive cls as '
      'first argument and access/modify class state across all objects. Static methods receive neither self nor cls '
      'and behave like regular functions bound to the class namespace.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the difference between an instance method, a class method decorated with @classmethod, and a static '
      'method decorated with @staticmethod in Python.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'The @property decorator allows a getter method to be accessed like an attribute. A companion @attribute.setter '
      'decorator validates or transforms incoming values before mutating the private backing field, preventing invalid '
      'state.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain how the @property decorator is used to achieve data encapsulation and attribute validation in Python '
      'with a code example.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'The __del__() method is called when an object reference count drops to zero and the object is '
      'garbage-collected. It is used to release external resources such as open file handles or network connections.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Describe the role of the __del__() destructor method in Python object lifecycle and garbage collection.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'A shallow copy (copy.copy) constructs a new compound object but inserts references to the original nested '
      'objects. A deep copy (copy.deepcopy) recursively copies all nested objects, producing a fully independent '
      'duplicate.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the difference between shallow copy and deep copy when duplicating object instances in Python.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class Student:\n'
      '    def __init__(self, name, marks):\n'
      '        self.name = name\n'
      '        self.marks = marks\n'
      '    def compute_grade(self):\n'
      "        return 'A' if self.marks >= 80 else 'B'",
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class Student with attributes name and marks, a constructor method, and a method compute_grade() '
      "that returns 'A' if marks >= 80 else 'B'.",
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class BankAccount:\n'
      '    def __init__(self, account_number, holder_name, initial_balance=0):\n'
      '        self.account_number = account_number\n'
      '        self.holder_name = holder_name\n'
      '        self.__balance = initial_balance\n'
      '    def deposit(self, amount):\n'
      '        if amount > 0: self.__balance += amount\n'
      '    def withdraw(self, amount):\n'
      '        if 0 < amount <= self.__balance:\n'
      '            self.__balance -= amount\n'
      '            return True\n'
      '        return False\n'
      '    def get_balance(self):\n'
      '        return self.__balance',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class BankAccount with attributes account_number, holder_name, and private attribute __balance. '
      'Include methods deposit(amount), withdraw(amount) with balance validation, and get_balance().',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class Rectangle:\n'
      '    def __init__(self, length, breadth):\n'
      '        self.length = length\n'
      '        self.breadth = breadth\n'
      '    def __add__(self, other):\n'
      '        return Rectangle(self.length + other.length, self.breadth + other.breadth)\n'
      '    def area(self):\n'
      '        return self.length * self.breadth',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class Rectangle with attributes length and breadth, implementing operator overloading for the + '
      'operator using __add__() to return a new Rectangle with sum of lengths and breadths.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class Vehicle:\n'
      '    def __init__(self, brand, model):\n'
      '        self.brand = brand\n'
      '        self.model = model\n'
      '    def display_info(self):\n'
      "        return f'{self.brand} {self.model}'\n"
      '\n'
      'class ElectricCar(Vehicle):\n'
      '    def __init__(self, brand, model, battery_capacity):\n'
      '        super().__init__(brand, model)\n'
      '        self.battery_capacity = battery_capacity\n'
      '    def display_info(self):\n'
      "        return f'{super().display_info()} with {self.battery_capacity} kWh battery'",
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class hierarchy where base class Vehicle has attributes brand and model with method '
      'display_info(), and derived class ElectricCar inherits from Vehicle, adds battery_capacity, and overrides '
      'display_info() using super().',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class Book:\n'
      '    def __init__(self, title, author, price):\n'
      '        self.title = title\n'
      '        self.author = author\n'
      '        self.price = price\n'
      '    def __str__(self):\n'
      "        return f'{self.title} by {self.author} (Rs. {self.price})'\n"
      '    def __eq__(self, other):\n'
      '        return isinstance(other, Book) and self.price == other.price',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class Book with attributes title, author, and price. Implement __str__() to return a formatted '
      'string and __eq__() to compare two Book objects for price equality.',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'class Employee:\n'
      '    total_employees = 0\n'
      '    def __init__(self, name, emp_id):\n'
      '        self.name = name\n'
      '        self.emp_id = emp_id\n'
      '        Employee.total_employees += 1\n'
      '    @classmethod\n'
      '    def get_total(cls):\n'
      '        return cls.total_employees',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write a Python class Employee with a class attribute total_employees that automatically increments whenever a '
      'new Employee object is instantiated, and a class method get_total().',
 'type': 'Short Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Single inheritance derives a child from one parent (class B(A)). Multilevel inheritance derives through a chain '
      '(class C(B), class B(A)). Multiple inheritance derives from multiple independent parents (class C(A, B)), '
      'requiring C3 Linearization MRO to resolve attribute lookups.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Compare and contrast single inheritance, multiple inheritance, and multilevel inheritance in Python with '
      'structural code illustrations.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'The diamond problem occurs when class D inherits from B and C, both inheriting from A. If B and C override a '
      'method from A, ambiguity arises as to which method D calls. Python uses C3 Linearization to produce a monotonic '
      'list where subclasses precede parents and local precedence order is preserved.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': "Analyze the diamond problem in Python multiple inheritance and explain how Python's C3 Linearization algorithm "
      'resolves method ambiguities.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'By default, Python instances store attributes in a dynamic __dict__, which incurs significant per-instance '
      'memory overhead. Declaring __slots__ reserves fixed descriptors for instance attributes, suppressing __dict__ '
      'creation, reducing memory footprint by up to 60%, and slightly speeding attribute access.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze the memory management implications and performance differences between using __slots__ versus the '
      'default __dict__ in Python classes with large numbers of instances.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Inheritance couples child to parent implementation, which can violate encapsulation if base classes change. '
      'Composition delegates functionality to embedded object instances, providing looser coupling, flexibility to '
      'swap components at runtime, and better adherence to the Single Responsibility Principle.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': "Compare and contrast composition ('has-a' relationship) and inheritance ('is-a' relationship) in Python "
      'software architecture, examining when composition is preferable.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Encapsulation hides internal representation and restricts direct unauthorized modification, enabling localized '
      'debugging and modular maintenance. Inheritance and polymorphism promote code reusability and extensible '
      'frameworks. Procedural programming lacks data protection and exhibits tight coupling between procedures and '
      'global state.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Critically evaluate the advantages and design implications of object-oriented encapsulation and inheritance '
      'versus procedural programming for large-scale enterprise applications.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Python name mangling does not enforce absolute cryptographic security; it simply renames __var to '
      '_ClassName__var. Any caller can still inspect and mutate the attribute directly. It relies on the convention '
      'that developers respect privacy boundaries, unlike Java/C++ compiler-enforced access specifiers.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': "Critically evaluate the effectiveness of Python's name mangling mechanism (__private_var) in enforcing true "
      'access control compared to strictly compiled languages like Java or C++.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'a': 'Deep hierarchies create fragile base class vulnerabilities where modifications ripple unpredictably. Idiomatic '
      'Python prefers flat hierarchies, duck typing (EAFP - Easier to Ask for Forgiveness than Permission), and '
      'lightweight composition, promoting code testability and agility.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Assess the design implications of deep inheritance hierarchies versus interface composition and duck typing in '
      'idiomatic Python applications.',
 'type': 'Long Answer',
 'unit': 'Object Oriented Programming'},
{'board': 'COMMON', 'class': 12, 'unit': 'Database Concepts', 'bloom': 'Remember', 'type': 'Short Answer', 'marks': 2, 'q': 'Define Primary Key and Foreign Key in a relational database management system.', 'a': 'A Primary Key is a column or set of columns that uniquely identifies each record in a relational table, disallowing null values. A Foreign Key is an attribute in a table that references the primary key of another table, establishing referential integrity between the two relations.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Database Concepts', 'bloom': 'Understand', 'type': 'Short Answer', 'marks': 3, 'q': 'Explain the difference between Data Definition Language (DDL) and Data Manipulation Language (DML) commands in SQL with two examples of each.', 'a': 'DDL commands define and modify the database schema and structure (e.g. `CREATE TABLE`, `ALTER TABLE`, `DROP TABLE`), automatically committed. DML commands manage and manipulate data stored within tables (e.g. `INSERT INTO`, `UPDATE`, `DELETE`, `SELECT`), requiring explicit transaction control.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Database Concepts', 'bloom': 'Apply', 'type': 'Short Answer', 'marks': 3, 'q': 'Write an SQL query to retrieve employee names and salaries from an `Employees` table for employees earning more than 50000, ordered in descending order of salary.', 'a': 'SELECT name, salary FROM Employees WHERE salary > 50000 ORDER BY salary DESC;'},
{'board': 'COMMON', 'class': 12, 'unit': 'Database Concepts', 'bloom': 'Analyze', 'type': 'Long Answer', 'marks': 4, 'q': 'Analyze the functional difference between the `WHERE` clause and the `HAVING` clause in SQL queries that use aggregate functions and `GROUP BY`.', 'a': 'The `WHERE` clause filters individual rows before grouping takes place and cannot accept aggregate functions. The `HAVING` clause filters aggregated groups after the `GROUP BY` operation has computed summary statistics (such as `COUNT()`, `AVG()`, `SUM()`).'},
{'board': 'COMMON', 'class': 12, 'unit': 'Database Concepts', 'bloom': 'Evaluate', 'type': 'Long Answer', 'marks': 5, 'q': 'Critically assess the importance and consequences of database normalization from First Normal Form (1NF) through Third Normal Form (3NF) on data redundancy and update anomalies.', 'a': '1NF eliminates repeating groups ensuring atomic values. 2NF removes partial functional dependencies on composite keys. 3NF removes transitive dependencies where non-key attributes determine other non-key attributes. Normalization systematically eliminates insertion, deletion, and update anomalies while reducing disk redundancy, though excessively normalized schemas can increase query join latency.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Python-MySQL Integration', 'bloom': 'Remember', 'type': 'Short Answer', 'marks': 2, 'q': 'State the purpose of the `cursor` object and the `commit()` method in the Python `mysql.connector` library.', 'a': 'The `cursor` object acts as an intermediary working environment to execute SQL statements and traverse query result sets. The `commit()` method permanently saves all changes made by INSERT, UPDATE, or DELETE transactions to the database.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Python-MySQL Integration', 'bloom': 'Understand', 'type': 'Short Answer', 'marks': 3, 'q': 'Explain the difference between `fetchone()`, `fetchall()`, and `fetchmany()` methods of a MySQL cursor in Python.', 'a': '`fetchone()` retrieves the next single row from the executed query result as a tuple, returning None when no more rows remain. `fetchall()` retrieves all remaining rows as a list of tuples. `fetchmany(size)` retrieves the specified number of rows as a list.'},
{'board': 'COMMON', 'class': 12, 'unit': 'Python-MySQL Integration', 'bloom': 'Apply', 'type': 'Short Answer', 'marks': 3, 'q': 'Write a Python script using `mysql.connector` to connect to a local database `school`, execute `SELECT * FROM Students`, and print each fetched record.', 'a': "import mysql.connector\nconn = mysql.connector.connect(host='localhost', user='root', password='', database='school')\ncur = conn.cursor()\ncur.execute('SELECT * FROM Students')\nfor row in cur.fetchall():\n    print(row)\ncur.close()\nconn.close()"},
{'board': 'COMMON', 'class': 12, 'unit': 'Python-MySQL Integration', 'bloom': 'Analyze', 'type': 'Long Answer', 'marks': 4, 'q': 'Analyze the security vulnerabilities of string concatenation in SQL queries and explain how parameterized queries prevent SQL injection attacks in Python.', 'a': "String concatenation allows malicious SQL fragments injected through user input to alter the syntactic structure of the query command. Parameterized queries (`cur.execute('SELECT * FROM Users WHERE id = %s', (uid,))`) separate SQL code from data literals, compelling the database engine to treat inputs strictly as parameter values rather than executable syntax."},
{'board': 'COMMON', 'class': 12, 'unit': 'Python-MySQL Integration', 'bloom': 'Evaluate', 'type': 'Long Answer', 'marks': 5, 'q': 'Evaluate the importance of transaction management using `commit()` and `rollback()` under `try-except` blocks during multi-table database operations in Python.', 'a': 'Transactions ensure ACID compliance (Atomicity, Consistency, Isolation, Durability). Wrapping multi-table operations in a `try-except` block guarantees that if any step fails, `conn.rollback()` restores the database to its pristine pre-transaction state, preventing partial data writes and orphan records.'},
{'board': 'CBSE', 'class': 12, 'unit': 'Computer Networks', 'bloom': 'Remember', 'type': 'Short Answer', 'marks': 2, 'q': 'State the difference between packet switching and circuit switching in computer communication networks.', 'a': 'Circuit switching establishes a dedicated physical path between sender and receiver for the entire transmission duration (e.g. traditional telephone). Packet switching divides data into discrete packets routed independently along dynamic optimal paths sharing network bandwidth.'},
{'board': 'CBSE', 'class': 12, 'unit': 'Computer Networks', 'bloom': 'Understand', 'type': 'Short Answer', 'marks': 3, 'q': 'Explain the functions of network devices: Switch, Router, and Gateway in data communications.', 'a': 'A switch connects multiple devices within a local area network (LAN) forwarding frames based on MAC addresses. A router connects distinct networks together forwarding packets based on IP routing tables. A gateway connects heterogeneous networks using different network protocols, translating protocols between dissimilar systems.'},
{'board': 'CBSE', 'class': 12, 'unit': 'Computer Networks', 'bloom': 'Apply', 'type': 'Short Answer', 'marks': 3, 'q': 'Suggest an optimal cable layout and server location for an educational institution having four blocks: Admin (100 m, 50 computers), Accounts (80 m, 30 computers), Exam (120 m, 80 computers), and Library (60 m, 20 computers) using Star topology.', 'a': 'Place the server in the Exam block because it houses the maximum number of computers (80), minimizing overall network traffic latency. Connect all other blocks (Admin, Accounts, Library) directly to the central switch in the Exam block in a Star topology with repeaters where distance exceeds 100 meters.'},
{'board': 'CBSE', 'class': 12, 'unit': 'Computer Networks', 'bloom': 'Analyze', 'type': 'Long Answer', 'marks': 4, 'q': 'Compare and contrast IPv4 and IPv6 addressing schemes with respect to address length, total available addresses, and security features.', 'a': 'IPv4 uses 32-bit addresses formatted as 4 decimal octets, providing 2^32 (~4.3 billion) addresses, now exhausted globally. IPv6 uses 128-bit addresses formatted as 8 hexadecimal groups, providing 2^128 addresses, and includes native mandatory IPSec cryptographic security support.'},
{'board': 'CBSE', 'class': 12, 'unit': 'Computer Networks', 'bloom': 'Evaluate', 'type': 'Long Answer', 'marks': 5, 'q': 'Critically evaluate the effectiveness of network firewalls and proxy servers in mitigating cyber security threats across enterprise local area networks.', 'a': 'Firewalls filter incoming and outgoing traffic based on stateful packet inspection rules, blocking unauthorized ports and malicious IP intrusions. Proxy servers mask internal client IP addresses, cache web resources, and filter content. Together they provide layered defense-in-depth, though they must be supplemented with endpoint antivirus and encryption against application-layer exploits.'}
])

# =============================================================================
# PHYSICS QUESTION POOL (Class 12 - CBSE & TNSB - All 9 Units, All 5 Bloom Levels)
# =============================================================================
PHYSICS_QUESTIONS = [{'a': "Coulomb's Law states that the electrostatic force between two point charges is directly proportional to the "
      'product of their charges and inversely proportional to the square of the distance between them: F = (1 / (4 * '
      'pi * epsilon_0)) * (q1 * q2 / r^2).',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': "State Coulomb's Law of electrostatics for two point charges in vacuum.",
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Electric dipole moment is the product of the magnitude of either charge and the separation vector between them: '
      'p = q * 2a. Its SI unit is coulomb-meter (C m), and its direction points from the negative charge to the '
      'positive charge along the dipole axis.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define electric dipole moment and state its SI unit and vector direction.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': "Gauss's Law states that the total electric flux passing through any closed Gaussian surface in vacuum is equal "
      'to 1/epsilon_0 times the net charge enclosed by the surface: closed integral (E . dA) = Q_enclosed / epsilon_0.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': "State Gauss's Law in electrostatics and express it in mathematical integral form.",
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'An equipotential surface is a surface having the same electric potential at all points. Key characteristics: 1. '
      'No work is done in moving a test charge between any two points on the surface (W = 0). 2. Electric field lines '
      'are always perpendicular to an equipotential surface at every point.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define an equipotential surface and state any two important characteristics of equipotential surfaces.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Quantization states that all observable electric charges are integral multiples of the elementary charge e: q = '
      '+/- n * e (where n is an integer and e = 1.6 x 10^-19 C). Conservation of charge states that the total electric '
      'charge of an isolated system remains constant over time.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the principle of quantization of electric charge and conservation of charge.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'If two electric field lines intersected, there would be two tangents at the intersection point indicating two '
      'different directions of the net electric field simultaneously, which is physically impossible. Electric flux '
      'represents the total number of field lines crossing a given area.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain why electric field lines never intersect each other and describe the physical significance of electric '
      'flux.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'At a distance r from the dipole center along the axial line: E_axial = (1 / (4 * pi * epsilon_0)) * [q / (r - '
      'a)^2 - q / (r + a)^2] = (1 / (4 * pi * epsilon_0)) * [4 * a * r * q / (r^2 - a^2)^2]. For r >> a, this '
      'simplifies to E_axial = (2 * p) / (4 * pi * epsilon_0 * r^3).',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Derive an expression for the electric field intensity at a point on the axial line of an electric dipole of '
      'length 2a.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'The forces on charges +q and -q are equal and opposite (qE and -qE), resulting in zero net force. The '
      'perpendicular distance between the lines of action of the forces is 2a * sin(theta). Torque tau = force * '
      'perpendicular distance = qE * 2a * sin(theta) = p * E * sin(theta), or tau = p x E.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Derive an expression for the torque experienced by an electric dipole placed in a uniform external electric '
      'field.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Inside a conductor in electrostatic equilibrium, the net electric field is zero (E = 0). Since E = -dV/dr, E = '
      '0 implies dV/dr = 0, meaning potential V does not vary with position inside the conductor, remaining constant '
      'and equal to its value on the surface.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain why the electrostatic potential is constant throughout the volume of a charged metallic conductor and '
      'equal to its surface value.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'In the absence of an electric field, centers of positive and negative charges in non-polar molecules coincide. '
      'An external field displaces positive charges along the field and negative charges opposite to it, inducing '
      'atomic dipole moments aligned with the field, creating a net polarization vector P.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Describe how electric polarization occurs in a non-polar dielectric slab placed inside an external electric '
      'field.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'F = (9e9 * 2e-6 * 4e-6) / (0.3)^2 = 0.072 / 0.09 = 0.8 N (repulsive force).',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Calculate the electrostatic force between two point charges of +2 microcoulombs and +4 microcoulombs placed 0.3 '
      "m apart in vacuum using Coulomb's law.",
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Using Gauss law formula for an infinite wire: E = lambda / (2 * pi * epsilon_0 * r) = (2 * k * lambda) / r = (2 '
      '* 9e9 * 4e-6) / 0.2 = 72000 / 0.2 = 3.6 x 10^5 N/C.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Calculate the electric field intensity at a distance of 0.2 m from an infinitely long straight wire having '
      'uniform linear charge density lambda = 4 x 10^-6 C/m.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Dipole moment p = q * 2a = (5 x 10^-6 C) * (0.04 m) = 2 x 10^-7 C m. Torque tau = p * E * sin(30 deg) = (2 x '
      '10^-7) * (2 x 10^5) * 0.5 = 0.02 N m.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Two point charges +5 microcoulombs and -5 microcoulombs are separated by 4 cm. Calculate the electric dipole '
      'moment and the torque when placed at 30 degrees to a uniform field of 2 x 10^5 N/C.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'C0 = epsilon_0 * A / d = 8 pF. When d is halved (d/2) and dielectric K is inserted, C = K * epsilon_0 * A / '
      '(d/2) = 2 * K * C0 = 2 * 6 * 8 pF = 96 pF.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'A parallel plate capacitor with air between its plates has capacitance 8 pF. Calculate the new capacitance if '
      'plate separation is halved and space is filled with dielectric constant K = 6.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': '(a) In series: 1/Cs = 1/2 + 1/4 + 1/6 = 6/12 + 3/12 + 2/12 = 11/12 => Cs = 12/11 = 1.09 microfarad. (b) In '
      'parallel: Cp = 2 + 4 + 6 = 12 microfarads.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Calculate the equivalent capacitance of three capacitors of capacitances 2 microfarad, 4 microfarad, and 6 '
      'microfarad connected in (a) series and (b) parallel.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'Potential V = (1 / 4pi*epsilon0) * q1 / r = (9 x 10^9) * (4 x 10^-5) / 0.09 = 360000 / 0.09 = 4 x 10^6 V. Work '
      'done W = q2 * V = (2 x 10^-9 C) * (4 x 10^6 V) = 8 x 10^-3 J.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Calculate the work done in bringing an electric charge of 2 x 10^-9 C from infinity to a point 9 cm away from a '
      'point charge of 4 x 10^-5 C in vacuum.',
 'type': 'Short Answer',
 'unit': 'Electrostatics'},
{'a': 'When disconnected: charge Q remains constant; capacitance increases from C0 to K * C0; potential difference '
      'decreases from V0 to V0 / K; electric field decreases from E0 to E0 / K; stored electrostatic energy decreases '
      'by a factor of 1/K.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze the effect of inserting a dielectric slab of dielectric constant K between the plates of a charged '
      'parallel plate capacitor when disconnected from the battery.',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': 'Inside (r < R): E = 0, and V = constant = q / (4 * pi * epsilon_0 * R). On surface (r = R): E = q / (4 * pi * '
      'epsilon_0 * R^2), V = q / (4 * pi * epsilon_0 * R). Outside (r > R): E proportional to 1/r^2, V proportional to '
      '1/r.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze the variation of electric field E and electrostatic potential V with radial distance r from the center '
      'of a uniformly charged thin spherical shell of radius R.',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': 'At distance r >> a: E_axial = (2p) / (4pi*eps0*r^3), oriented in direction of dipole moment p. E_equatorial = p '
      '/ (4pi*eps0*r^3), oriented antiparallel to p. Hence, E_axial = -2 * E_equatorial.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Compare and contrast the electric field produced by an electric dipole at a point on its axial line versus its '
      'equatorial line at the same distance r (for r >> a).',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': 'Capacitance C = eps0*A/d is halved (C/2). Since charge Q is conserved on isolated plates, stored energy U = Q^2 '
      '/ (2C) doubles. The external mechanical work performed against electrostatic attraction to separate plates '
      'accounts for the increase in stored potential energy.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze the changes in stored electrostatic energy and capacitance when the plate separation of an isolated '
      'charged capacitor is doubled without a battery.',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': "Gauss's law provides an elegant calculation for symmetric configurations (spherical, cylindrical, planar) where "
      "closed integral (E . dA) reduces algebraically, whereas Coulomb's law requires complex vector integration.",
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': "Evaluate the validity and importance of Gauss's Law in calculating electric fields for highly symmetric charge "
      "distributions compared to Coulomb's Law.",
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': 'Work dW = V dq = (q/C) dq. Total work W = integral (q/C dq from 0 to Q) = Q^2 / (2C) = (1/2)CV^2. Substituting '
      'C = eps0*A/d and V = E*d yields U = (1/2)*eps0*E^2*(A*d). The energy is physically localized across the space '
      'between plates with energy density u = (1/2)*eps0*E^2.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Derive the expression for the energy stored in a charged capacitor U = (1/2)CV^2 and critically evaluate where '
      'this energy is localized within the electric field.',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
{'a': 'Electrostatic shielding exploits the property that electric field inside a metallic cavity is strictly zero '
      '(Faraday cage effect). External electric flux lines terminate on outer surface induced charges without '
      'penetrating the interior. This protects delicate circuits, coaxial cables, and high-voltage laboratories from '
      'destructive static fields.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Critically evaluate the phenomenon of electrostatic shielding and assess its practical engineering applications '
      'in safeguarding sensitive electronic instruments.',
 'type': 'Long Answer',
 'unit': 'Electrostatics'},
 {'a': "Ohm's Law states that electric current flowing through a conductor is directly proportional to the potential "
       'difference across its ends, provided temperature remains constant. Drift velocity is the average velocity '
       'acquired by free electrons in a conductor opposite to the applied electric field.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Ohm's Law and define drift velocity of free electrons in a metallic conductor.",
  'type': 'Short Answer',
  'unit': 'Current Electricity'},
 {'a': "Kirchhoff's Current Rule (Junction rule) states that total current entering a junction equals total current "
       "leaving, based on conservation of charge. Kirchhoff's Voltage Rule (Loop rule) states that the algebraic sum "
       'of changes in potential around any closed loop is zero, based on conservation of energy.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Explain Kirchhoff's current and voltage rules and describe their underlying conservation principles.",
  'type': 'Short Answer',
  'unit': 'Current Electricity'},
 {'a': 'Since P/Q = 2/4 = 1/2 and R/S = 3/6 = 1/2, the bridge is balanced and no current flows through the '
       'galvanometer. Equivalent resistance is (P + Q) in parallel with (R + S): (6 * 9) / (6 + 9) = 54 / 15 = 3.6 '
       'ohms.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the equivalent resistance of a Wheatstone bridge circuit when four arm resistors are P = 2 ohms, Q = '
       '4 ohms, R = 3 ohms, and S = 6 ohms.',
  'type': 'Short Answer',
  'unit': 'Current Electricity'},
 {'a': 'In metals, resistivity increases with temperature because relaxation time tau decreases due to increased '
       'lattice collisions. In semiconductors, resistivity decreases exponentially with temperature because charge '
       'carrier density n increases dramatically.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the temperature dependence of electrical resistivity for metallic conductors versus semiconductor '
       'materials.',
  'type': 'Long Answer',
  'unit': 'Current Electricity'},
 {'a': 'A potentiometer is fundamentally superior because at balance point it draws zero current from the source cell, '
       'measuring true open-circuit EMF without internal resistance loading, whereas an ordinary voltmeter draws '
       'finite current causing a terminal voltage drop.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Critically assess the validity and sensitivity of a potentiometer compared to an ordinary voltmeter for '
       'measuring cell electromotive force.',
  'type': 'Long Answer',
  'unit': 'Current Electricity'},
 {'a': 'Biot-Savart Law states dB = (mu_0 / (4 * pi)) * (I * dl * sin(theta) / r^2), where dl is the current element, '
       'r is distance to the observation point, and theta is the angle between dl and the position vector.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State Biot-Savart Law for the magnetic field produced by an infinitesimal current element.',
  'type': 'Short Answer',
  'unit': 'Magnetism'},
 {'a': 'A moving coil galvanometer operates on the principle that a current-carrying coil placed in a uniform radial '
       'magnetic field experiences a deflecting torque tau = NIAB balanced by a restoring torque C*theta. It is '
       'converted into an ammeter by connecting a low resistance shunt resistor in parallel with the galvanometer '
       'coil.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the principle and working of a moving coil galvanometer and describe how it is converted into an '
       'ammeter.',
  'type': 'Short Answer',
  'unit': 'Magnetism'},
 {'a': 'F = q * v * B * sin(90) = (1.6e-19 C) * (2e6 m/s) * 0.5 T = 1.6 x 10^-13 N.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the magnetic force experienced by a proton moving with velocity 2 x 10^6 m/s perpendicular to a '
       'uniform magnetic field of 0.5 T.',
  'type': 'Short Answer',
  'unit': 'Magnetism'},
 {'a': 'Diamagnetic materials have small negative susceptibility independent of temperature and are repelled by '
       'magnetic fields. Paramagnetic materials have small positive susceptibility inversely proportional to '
       "temperature (Curie's law). Ferromagnetic materials have very large positive susceptibility displaying magnetic "
       'hysteresis.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the magnetic behavior and susceptibility differences among diamagnetic, paramagnetic, and '
       'ferromagnetic materials.',
  'type': 'Long Answer',
  'unit': 'Magnetism'},
 {'a': 'A cylindrical soft iron core and concave magnetic pole pieces ensure the magnetic field is always '
       'perpendicular to the area vector of the coil (theta = 90 degrees), making deflecting torque directly '
       'proportional to current (I proportional to deflection theta), ensuring a strictly linear scale.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the effectiveness of using radial magnetic field geometry in moving coil galvanometers for linear '
       'scale calibration.',
  'type': 'Long Answer',
  'unit': 'Magnetism'},
 {'a': "Faraday's first law states that an induced EMF is produced whenever magnetic flux linked with a circuit "
       'changes. The second law states the magnitude of induced EMF is proportional to rate of change of magnetic '
       "flux. Lenz's law states the induced current always opposes the flux change that produced it.",
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Faraday's laws of electromagnetic induction and Lenz's Law.",
  'type': 'Short Answer',
  'unit': 'Electromagnetic Induction'},
 {'a': 'Resonance occurs when inductive reactance XL equals capacitive reactance XC (omega * L = 1 / (omega * C)). At '
       'this resonant frequency f0 = 1 / (2 * pi * sqrt(LC)), the impedance of the circuit is minimum and purely '
       'resistive (Z = R), resulting in maximum current amplitude.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the phenomenon of electrical resonance in a series LCR alternating current circuit and describe the '
       'condition for resonance.',
  'type': 'Short Answer',
  'unit': 'Electromagnetic Induction'},
 {'a': 'f0 = 1 / (2 * pi * sqrt(L * C)) = 1 / (2 * pi * sqrt(0.1 * 10e-6)) = 1 / (2 * pi * 1e-3) = 1000 / (2 * pi) = '
       '159.15 Hz.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the resonant frequency of a series LCR circuit containing an inductor L = 0.1 H, capacitor C = 10 '
       'microfarads, and resistor R = 20 ohms.',
  'type': 'Short Answer',
  'unit': 'Electromagnetic Induction'},
 {'a': '1. Copper loss (I^2*R heat in windings) minimized using thick wires. 2. Eddy current loss in the core '
       'minimized by using laminated core sheets. 3. Hysteresis loss minimized using soft iron with narrow hysteresis '
       'loop. 4. Flux leakage minimized by winding primary and secondary coils over each other.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the primary sources of energy loss in an electrical transformer and explain how each loss is '
       'minimized.',
  'type': 'Long Answer',
  'unit': 'Electromagnetic Induction'},
 {'a': 'The Q-factor (omega_0 * L / R) characterizes circuit damping. A higher Q-factor sharpens the resonance peak, '
       'reducing bandwidth and dramatically enhancing receiver selectivity against adjacent frequency channels.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the importance of the Quality factor (Q-factor) in determining sharpness of resonance and selectivity '
       'in radio receiver circuits.',
  'type': 'Long Answer',
  'unit': 'Electromagnetic Induction'},
 {'a': 'Displacement current ID = epsilon_0 * (dPhi_E / dt) arises from a time-varying electric field. The generalized '
       'Ampere-Maxwell law is: line integral of B dot dl = mu_0 * (I_c + epsilon_0 * dPhi_E / dt).',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Maxwell's concept of displacement current and write the generalized Ampere-Maxwell law.",
  'type': 'Short Answer',
  'unit': 'Electromagnetic Waves'},
 {'a': 'Electromagnetic waves are transverse because the electric field vector E and magnetic field vector B oscillate '
       'perpendicular to each other and perpendicular to the direction of wave propagation (given by the Poynting '
       'vector E x B).',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the transverse nature of electromagnetic waves and describe the orientation of electric and magnetic '
       'fields relative to propagation direction.',
  'type': 'Short Answer',
  'unit': 'Electromagnetic Waves'},
 {'a': 'Wavelength lambda = c / f = (3 x 10^8 m/s) / (3 x 10^10 Hz) = 10^-2 m = 1 cm (microwave region).',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the wavelength of an electromagnetic wave of frequency 3 x 10^10 Hz propagating in vacuum.',
  'type': 'Short Answer',
  'unit': 'Electromagnetic Waves'},
 {'a': 'Frequency order: Microwave < Infrared < Ultraviolet < X-rays. Microwaves: klystron/magnetron tubes. Infrared: '
       'thermal vibration of molecules. Ultraviolet: inner shell electron transitions and mercury lamps. X-rays: '
       'bombarding high-Z target with fast electrons.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the electromagnetic spectrum by arranging microwave, infrared, ultraviolet, and X-ray radiations in '
       'increasing order of frequency and comparing their production methods.',
  'type': 'Long Answer',
  'unit': 'Electromagnetic Waves'},
 {'a': "Maxwell's theory confirms EM waves carry momentum p = U / c. When completely absorbed, radiation pressure P = "
       'I / c; when completely reflected, P = 2I / c. Experimental confirmation in comet tails verifies physical '
       'momentum transfer.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate whether electromagnetic radiation exerts radiation pressure and momentum transfer upon absorption by '
       'a target surface.',
  'type': 'Long Answer',
  'unit': 'Electromagnetic Waves'},
 {'a': "Snell's Law states n1 * sin(i) = n2 * sin(r). The critical angle is the angle of incidence in a denser medium "
       'for which the angle of refraction in the rarer medium is 90 degrees.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Snell's Law of refraction and define the critical angle for total internal reflection.",
  'type': 'Short Answer',
  'unit': 'Optics'},
 {'a': "Huygens' principle states every point on a primary wavefront acts as a source of secondary spherical wavelets "
       'spreading in all directions with wave speed. The forward envelope tangent to these secondary wavelets at a '
       'later time forms the new wavefront.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Explain Huygens' principle of wave propagation and describe how secondary wavelets construct a refracted "
       'wavefront.',
  'type': 'Short Answer',
  'unit': 'Optics'},
 {'a': 'Fringe width beta = (lambda * D) / d = (600e-9 * 1) / (0.5e-3) = 1.2 x 10^-3 m = 1.2 mm.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Calculate the fringe width in Young's double-slit experiment where slit separation d = 0.5 mm, screen distance "
       'D = 1 m, and wavelength lambda = 600 nm.',
  'type': 'Short Answer',
  'unit': 'Optics'},
 {'a': 'Interference results from superposition of wavelets from two distinct coherent sources, giving equal fringe '
       'width and uniform bright fringe intensity. Diffraction results from wavelets originating across different '
       'parts of the same wavefront, producing unequal fringe widths and rapidly decaying intensity away from the '
       'central maximum.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Compare and contrast interference and diffraction of light with respect to source of wavelets, fringe width, '
       'and intensity distribution.',
  'type': 'Long Answer',
  'unit': 'Optics'},
 {'a': 'Reflecting telescopes eliminate chromatic aberration completely, minimize spherical aberration using parabolic '
       'mirrors, allow lightweight mechanical mounting supporting large primary mirrors, and achieve vastly superior '
       'light-gathering power.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the merits of a reflecting telescope compared to a refracting telescope for astronomical '
       'observations.',
  'type': 'Long Answer',
  'unit': 'Optics'},
 {'a': 'Threshold frequency (nu_0) is the minimum frequency of incident radiation required to eject photoelectrons '
       'from a metal surface without kinetic energy. Work function (Phi) is the minimum energy required: Phi = h * '
       'nu_0.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State the definition of threshold frequency and work function in the context of the photoelectric effect.',
  'type': 'Short Answer',
  'unit': 'Dual Nature'},
 {'a': "Einstein's equation h*nu = Phi + K_max posits one photon transfers all its energy instantaneously to a single "
       'electron in an elastic collision, accounting for zero time lag and explaining why kinetic energy depends on '
       'frequency rather than intensity.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Explain Einstein's photoelectric equation and describe how it resolves the wave theory failure regarding "
       'instantaneous emission.',
  'type': 'Short Answer',
  'unit': 'Dual Nature'},
 {'a': 'lambda = 1.227 / sqrt(V) nm = 1.227 / sqrt(100) = 1.227 / 10 = 0.1227 nm = 1.227 Angstroms.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the de Broglie wavelength of an electron accelerated from rest through a potential difference of 100 '
       'V.',
  'type': 'Short Answer',
  'unit': 'Dual Nature'},
 {'a': 'Varying intensity at constant frequency yields different saturation currents proportional to intensity, but '
       'identical stopping potential V0. Varying frequency at constant intensity yields identical saturation current, '
       'but stopping potential becomes more negative as frequency increases.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the experimental graphs of photoelectric current versus collector potential for varying radiation '
       'intensity and varying radiation frequency.',
  'type': 'Long Answer',
  'unit': 'Dual Nature'},
 {'a': 'The experimental demonstration of electron diffraction through a nickel crystal lattice showed intensity '
       "maxima matching Bragg's diffraction law for X-rays, providing conclusive empirical proof of electron wave "
       'properties.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': "Evaluate the significance of the Davisson-Germer experiment in validating de Broglie's hypothesis of matter "
       'waves.',
  'type': 'Long Answer',
  'unit': 'Dual Nature'},
 {'a': '1. Electrons revolve in non-radiating stationary orbits where orbital angular momentum L = m*v*r = n*h / '
       '(2*pi). 2. Radiation is emitted or absorbed only when an electron transitions between discrete energy levels: '
       'E2 - E1 = h*nu.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Bohr's postulates for the hydrogen atom regarding stationary orbits and electron angular momentum "
       'quantization.',
  'type': 'Short Answer',
  'unit': 'Atoms and Nuclei'},
 {'a': 'Binding energy per nucleon measures average stability. The curve peaks around A = 56 (Iron, ~8.75 '
       'MeV/nucleon), indicating maximum stability. Fission of heavy nuclei (A > 200) and fusion of light nuclei (A < '
       '20) both move toward higher binding energy per nucleon, releasing vast energy.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the concept of nuclear binding energy per nucleon and describe what the binding energy curve reveals '
       'about nuclear stability.',
  'type': 'Short Answer',
  'unit': 'Atoms and Nuclei'},
 {'a': 'r1 = (epsilon_0 * h^2) / (pi * m * e^2) = 0.529 x 10^-10 m = 0.529 Angstroms.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the radius of the first Bohr orbit of a hydrogen atom given h = 6.63 x 10^-34 J s, m = 9.1 x 10^-31 '
       'kg, and e = 1.6 x 10^-19 C.',
  'type': 'Short Answer',
  'unit': 'Atoms and Nuclei'},
 {'a': 'Lyman series: transitions to n1=1 (ultraviolet region). Balmer series: transitions to n1=2 (visible region). '
       'Paschen (n1=3), Brackett (n1=4), and Pfund (n1=5): infrared region. Wavenumber 1/lambda = R * (1/n1^2 - '
       '1/n2^2).',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the hydrogen spectral series (Lyman, Balmer, Paschen, Brackett, Pfund) by comparing their spectral '
       'regions and transition quantum numbers.',
  'type': 'Long Answer',
  'unit': 'Atoms and Nuclei'},
 {'a': 'Fusion produces no long-lived radioactive waste and uses abundant hydrogen fuel isotopes, releasing greater '
       'energy per unit mass than fission. However, achieving thermonuclear fusion requires maintaining plasma at '
       'temperatures above 10^7 K and achieving stable magnetic or inertial confinement.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Critically assess the advantages and challenges of nuclear fusion compared to nuclear fission as an energy '
       'source.',
  'type': 'Long Answer',
  'unit': 'Atoms and Nuclei'},
 {'a': 'Intrinsic semiconductors are pure semiconductors (e.g. pure Si, Ge) where electron and hole concentrations are '
       'equal. Extrinsic semiconductors are doped with trivalent (p-type) or pentavalent (n-type) impurities to '
       'increase electrical conductivity.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State the difference between intrinsic and extrinsic semiconductors and define doping.',
  'type': 'Short Answer',
  'unit': 'Semiconductors'},
 {'a': 'When a p-n junction is formed, holes diffuse from p to n and electrons diffuse from n to p. Recombination near '
       'the junction leaves uncompensated ionized donor cations on the n-side and acceptor anions on the p-side, '
       'setting up a space-charge depletion layer and an internal electric field creating a barrier potential.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the formation of a depletion region and potential barrier across an unbiased p-n junction diode.',
  'type': 'Short Answer',
  'unit': 'Semiconductors'},
 {'a': 'In a full-wave rectifier, both positive and negative half-cycles of input AC are rectified in the same '
       'direction. Output frequency = 2 * input frequency = 2 * 50 Hz = 100 Hz.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the output frequency of a full-wave bridge rectifier when connected to an input alternating current '
       'supply of 50 Hz.',
  'type': 'Short Answer',
  'unit': 'Semiconductors'},
 {'a': 'Under forward bias, external voltage opposes barrier potential; current remains negligibly small until knee '
       'voltage (0.7V for Si) and then increases exponentially. Under reverse bias, external voltage reinforces '
       'barrier potential; only a tiny reverse saturation current flows until breakdown voltage is reached.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the current-voltage (I-V) characteristics of a p-n junction diode under forward bias versus reverse '
       'bias conditions.',
  'type': 'Long Answer',
  'unit': 'Semiconductors'},
 {'a': 'When operated in reverse breakdown beyond Vz, the Zener diode maintains an almost constant terminal voltage '
       'across substantial variations in reverse current, effectively clamping load voltage against fluctuating DC '
       'inputs.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the effectiveness of a Zener diode as a constant DC voltage regulator under varying input line '
       'voltages.',
  'type': 'Long Answer',
  'unit': 'Semiconductors'}]

# =============================================================================
# CHEMISTRY QUESTION POOL (Class 12 - CBSE & TNSB - All Units, All 5 Bloom Levels)
# =============================================================================
CHEMISTRY_QUESTIONS = [{'a': "Raoult's Law states that for a solution of volatile liquids, the partial vapor pressure of each component is "
       'directly proportional to its mole fraction in the solution: P_i = P_i_0 * x_i. An ideal solution obeys '
       "Raoult's law over the entire range of concentration with Delta_H_mix = 0 and Delta_V_mix = 0.",
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Raoult's Law for a solution of volatile liquids and define an ideal solution.",
  'type': 'Short Answer',
  'unit': 'Solutions'},
 {'a': 'Positive deviation occurs when solute-solvent (A-B) attractive forces are weaker than A-A and B-B '
       'interactions, increasing escaping tendency and vapor pressure (Delta_H_mix > 0). Negative deviation occurs '
       'when A-B interactions are stronger than A-A and B-B, decreasing escaping tendency (Delta_H_mix < 0).',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Explain why non-ideal solutions exhibit positive or negative deviations from Raoult's law with reference to "
       'intermolecular interactions.',
  'type': 'Short Answer',
  'unit': 'Solutions'},
 {'a': 'Moles of glucose n = 18 / 180 = 0.1 mol. Volume V = 0.5 L. Osmotic pressure pi = (n / V) * R * T = (0.1 / 0.5) '
       '* 0.0821 * 300 = 0.2 * 24.63 = 4.926 atm.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the osmotic pressure of an aqueous solution containing 18 g of glucose (C6H12O6, molar mass = 180 '
       'g/mol) dissolved in 500 mL of water at 300 K.',
  'type': 'Short Answer',
  'unit': 'Solutions'},
 {'a': 'When a solute dissociates (e.g. NaCl in water), number of particles increases, colligative property increases, '
       'and experimental molar mass is lower than theoretical (i > 1). When a solute associates (e.g. benzoic acid in '
       "benzene), particle count decreases and observed molar mass is higher (i < 1). Van 't Hoff factor i = Normal "
       'molar mass / Abnormal molar mass.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the abnormal molar masses observed for solutes undergoing association or dissociation in solution '
       "using the Van 't Hoff factor (i).",
  'type': 'Long Answer',
  'unit': 'Solutions'},
 {'a': 'Ethylene glycol dissolves non-volatiles in water, creating depression in freezing point Delta_T_f = K_f * m, '
       'lowering the freezing point of radiator fluid well below 0 degrees Celsius to prevent engine block cracking, '
       'while its high boiling point simultaneously prevents boiling over in summer.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the effectiveness and practical significance of using ethylene glycol as an antifreeze in automobile '
       'radiators during extreme winter conditions.',
  'type': 'Long Answer',
  'unit': 'Solutions'},
 {'a': "Kohlrausch's law states that the limiting molar conductivity of an electrolyte is equal to the sum of the "
       'individual contributions of the cation and the anion: Lambda^0_m = nu_+ * lambda^0_+ + nu_- * lambda^0_-. '
       'Molar conductivity is the conducting power of all ions produced by dissolving one mole of electrolyte.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Kohlrausch's Law of independent migration of ions and define molar conductivity.",
  'type': 'Short Answer',
  'unit': 'Electrochemistry'},
 {'a': 'The SHE consists of platinum foil coated with platinum black immersed in a 1 M H+ solution with pure H2 gas '
       'bubbled at 1 bar pressure. It provides a standardized reference electrode whose half-cell potential is '
       'arbitrarily defined as exactly 0.00 V at all temperatures, enabling relative potential measurement of other '
       'electrodes.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain the working principle of the standard hydrogen electrode (SHE) and describe why its potential is '
       'assigned zero volts.',
  'type': 'Short Answer',
  'unit': 'Electrochemistry'},
 {'a': 'E_cell = E0_cell - (0.0591 / 2) * log([Zn2+] / [Cu2+]) = 1.10 - 0.02955 * log(0.1 / 0.01) = 1.10 - 0.02955 * '
       'log(10) = 1.10 - 0.02955 = 1.070 V.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the cell potential of a Daniel cell at 298 K using the Nernst equation when [Zn2+] = 0.1 M and '
       '[Cu2+] = 0.01 M, given E0_cell = 1.10 V.',
  'type': 'Short Answer',
  'unit': 'Electrochemistry'},
 {'a': 'For strong electrolytes, molar conductivity increases linearly and slowly with dilution due to decreasing '
       'interionic attractions (Lambda_m = Lambda^0_m - A * sqrt(c)). For weak electrolytes, molar conductivity '
       'increases steeply near infinite dilution because degree of dissociation alpha increases dramatically '
       "(Ostwald's dilution law).",
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the variation of molar conductivity with concentration for strong electrolytes versus weak '
       'electrolytes using the Debye-Huckel-Onsager model.',
  'type': 'Long Answer',
  'unit': 'Electrochemistry'},
 {'a': 'Fuel cells convert chemical energy of redox reactions directly into electrical energy with theoretical '
       'efficiency exceeding 70% (compared to ~40% for thermal plants), produce zero carbon emissions with water as '
       'the only byproduct, and operate continuously without recharging as long as reactants are supplied.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the advantages and technological importance of hydrogen-oxygen fuel cells over conventional '
       'fossil-fuel power generators.',
  'type': 'Long Answer',
  'unit': 'Electrochemistry'},
 {'a': 'Order of a reaction is the sum of powers of concentration terms in the experimental rate law equation (can be '
       'zero, fractional, or negative). Molecularity is the number of reacting species colliding simultaneously in an '
       'elementary step (always a non-zero whole integer 1, 2, or 3).',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State the difference between order of a reaction and molecularity of a reaction.',
  'type': 'Short Answer',
  'unit': 'Chemical Kinetics'},
 {'a': 'Arrhenius equation k = A * exp(-Ea / (R * T)) explains that the rate constant depends exponentially on '
       'negative activation energy divided by thermal energy RT. Raising temperature increases the fraction of '
       'molecules possessing kinetic energy greater than or equal to Ea, increasing effective collision frequency and '
       'reaction rate.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain Arrhenius equation and describe how temperature and activation energy govern the rate constant of a '
       'reaction.',
  'type': 'Short Answer',
  'unit': 'Chemical Kinetics'},
 {'a': 'For a first-order reaction: t_1/2 = 0.693 / k = 0.693 / (2.31 x 10^-3) = 300 seconds.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the half-life period of a first-order reaction having a rate constant k = 2.31 x 10^-3 s^-1.',
  'type': 'Short Answer',
  'unit': 'Chemical Kinetics'},
 {'a': 'A catalyst provides an alternate reaction pathway with lower activation energy Ea. In energy profile diagrams, '
       'the transition state peak is significantly lowered, exponentially increasing the fraction of reactant '
       'molecules that can surmount the energy barrier without altering Delta_H or chemical equilibrium.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the mechanism of chemical catalysis using the intermediate complex theory and energy profile diagrams.',
  'type': 'Long Answer',
  'unit': 'Chemical Kinetics'},
 {'a': 'The overall stoichiometric equation indicates only mass balance, not reaction pathway. Complex reactions '
       'proceed through multiple elementary steps with varying speeds; the rate law is determined exclusively by the '
       'slowest rate-determining step (RDS) and must be verified experimentally.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate whether the rate law of a multi-step complex reaction can be predicted purely from its overall '
       'balanced chemical equation.',
  'type': 'Long Answer',
  'unit': 'Chemical Kinetics'},
 {'a': 'Lanthanoid contraction is the steady decrease in atomic and ionic radii of lanthanoid elements with increasing '
       'atomic number from Lanthanum to Lutetium, caused by the poor shielding effect of intervening 4f electrons '
       'against increasing nuclear charge.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'Define Lanthanoid contraction and state its primary cause in f-block chemistry.',
  'type': 'Short Answer',
  'unit': 'Transition Elements'},
 {'a': 'Variable oxidation states arise because the energy difference between (n-1)d and ns subshells is minimal, '
       'allowing electrons from both to participate. Catalytic activity stems from variable valence and ability to '
       'adopt intermediate complexes. Color results from d-d electron transitions absorbing visible light when '
       'd-orbitals split in ligand fields.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain why transition metals exhibit variable oxidation states, high catalytic activity, and colored '
       'complexes.',
  'type': 'Short Answer',
  'unit': 'Transition Elements'},
 {'a': 'Mn2+ has 5 unpaired electrons (n = 5). Spin-only magnetic moment mu = sqrt(n * (n + 2)) = sqrt(5 * (5 + 2)) = '
       'sqrt(35) = 5.92 BM.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the spin-only magnetic moment in Bohr Magnetons (BM) for an aqueous ion with electronic '
       'configuration 3d^5 (Mn2+).',
  'type': 'Short Answer',
  'unit': 'Transition Elements'},
 {'a': 'Lanthanoids exhibit predominantly +3 oxidation state due to large energy separation of 4f from 5d/6s, with '
       'lower basicity and radioactivity only in Promethium. Actinoids show multiple higher oxidation states (+3, +4, '
       '+5, +6, +7) because 5f, 6d, and 7s energies are comparable, exhibit greater complexing tendency, and are all '
       'radioactive.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Compare and contrast the chemical reactivity and oxidation state stability of Lanthanoids versus Actinoids.',
  'type': 'Long Answer',
  'unit': 'Transition Elements'},
 {'a': 'Both serve as versatile, powerful oxidizing agents in acidic media. K2Cr2O7 is a primary standard because it '
       'is stable and non-hygroscopic. KMnO4 acts as its own self-indicator through intense pink coloration, providing '
       'high analytical accuracy without external indicators.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the importance of potassium permanganate (KMnO4) and potassium dichromate (K2Cr2O7) as primary redox '
       'titrants in volumetric analysis.',
  'type': 'Long Answer',
  'unit': 'Transition Elements'},
 {'a': "Werner's theory states metals possess primary valency (ionizable, corresponds to oxidation state, satisfied by "
       'negative ions) and secondary valency (non-ionizable, corresponds to coordination number, directed in space '
       'toward fixed positions, satisfied by neutral molecules or anions).',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': "State Werner's coordination theory regarding primary and secondary valencies of central metal atoms.",
  'type': 'Short Answer',
  'unit': 'Coordination Compounds'},
 {'a': 'In an octahedral field, six ligands approach along Cartesian axes, splitting degenerate d-orbitals into '
       'lower-energy t2g orbitals (dxy, dyz, dzx) and higher-energy eg orbitals (dx2-y2, dz2) by energy gap Delta_o. '
       'The spectrochemical series arranges ligands in order of increasing crystal field splitting energy (I- < Br- < '
       'Cl- < F- < H2O < NH3 < CN- < CO).',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain crystal field splitting in octahedral coordination complexes and describe the spectrochemical series.',
  'type': 'Short Answer',
  'unit': 'Coordination Compounds'},
 {'a': 'IUPAC name: hexaamminecobalt(III) chloride. In [Co(NH3)6]3+, Co3+ is 3d^6. NH3 is a strong field ligand '
       'causing pairing of d-electrons, using two 3d, one 4s, and three 4p orbitals forming d2sp3 inner orbital '
       'octahedral complex with zero unpaired electrons (diamagnetic).',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Determine the IUPAC name and magnetic nature of the coordination complex [Co(NH3)6]Cl3 using valence bond '
       'theory.',
  'type': 'Short Answer',
  'unit': 'Coordination Compounds'},
 {'a': '[Pt(NH3)2Cl2] has square planar geometry exhibiting cis- and trans- geometrical isomers, but is optically '
       'inactive due to a plane of symmetry. [Co(en)3]3+ has octahedral geometry with bidentate ligands, lacking '
       'geometrical isomers but possessing non-superimposable mirror images (dextro and laevo optical enantiomers).',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze geometrical and optical isomerism in coordination compounds of type [Pt(NH3)2Cl2] and [Co(en)3]3+.',
  'type': 'Long Answer',
  'unit': 'Coordination Compounds'},
 {'a': 'VBT successfully predicts geometry and magnetic character (paramagnetic vs diamagnetic) using hybridization, '
       'but completely fails to explain complex color, absorption spectra, temperature-dependent magnetic moments, or '
       'the order of ligand field strengths in the spectrochemical series, which CFT explains by electrostatic orbital '
       'splitting.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Critically assess the validity and limitations of Valence Bond Theory compared to Crystal Field Theory in '
       'explaining coordination complexes.',
  'type': 'Long Answer',
  'unit': 'Coordination Compounds'},
 {'a': 'Froth flotation is based on the differential wetting properties of sulfide ore particles and gangue: sulfide '
      'ore particles are preferentially wetted by pine oil and collectors, rising with froth, while gangue particles '
      'are preferentially wetted by water and settle to the bottom.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the principle of froth flotation process used in concentration of sulfide ores.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Calcination is heating the concentrated ore strongly below melting point in absence or limited supply of air to '
      'expel volatile matter and moisture (e.g. CaCO3 -> CaO + CO2). Roasting is heating strongly in excess air below '
      'melting point, typically for sulfide ores (e.g. 2 ZnS + 3 O2 -> 2 ZnO + 2 SO2).',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the difference between calcination and roasting with one balanced chemical equation for each.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'The inert pair effect is the reluctance of outermost s-electrons to participate in chemical bonding due to poor '
      'shielding by intervening d and f electrons. Consequently, lower oxidation states (+3 in Group 15, +4 in Group '
      '16) become progressively more stable down the group (e.g. Bi3+ > Bi5+, Pb2+ > Pb4+).',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'State the inert pair effect and describe how it influences the oxidation state stability in Group 15 and Group '
      '16 elements.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Bauxite containing impurities (SiO2, Fe2O3, TiO2) is digested with concentrated NaOH at 473-523 K and 35 bar '
      'pressure. Al2O3 dissolves as soluble sodium aluminate Na[Al(OH)4], while insoluble iron and titanium oxides '
      'remain as red mud and are filtered out.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': "State the composition and principle of leaching in Bayer's process for the concentration of bauxite ore.",
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': '1. Orthophosphoric acid (H3PO4): oxidation state of phosphorus is +5. 2. Orthophosphorous acid (H3PO3): '
      'oxidation state of phosphorus is +3.',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Name any two oxoacids of phosphorus and state the oxidation state of phosphorus in each.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Interhalogen compounds are binary compounds formed by reaction between two different halogen elements. They '
      'have general formula XX_n (where n = 1, 3, 5, 7 and X is the larger, less electronegative halogen, e.g. ClF, '
      'BrF3, IF5, IF7).',
 'bloom': 'Remember',
 'board': 'COMMON',
 'class': 12,
 'marks': 2,
 'q': 'Define interhalogen compounds and state their general formula and geometry categories.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Ellingham diagrams plot standard Gibbs free energy change Delta_G^0 of oxide formation against temperature T. A '
      'metal can reduce the oxide of another metal whose Delta_G^0 line lies above its own line on the diagram, '
      'because the net Delta_G^0 of the combined reaction is negative at that temperature.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the role of Ellingham diagrams in selecting appropriate reducing agents for metal extraction at high '
      'temperatures.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Alumina (Al2O3) has an extremely high melting point (~2348 K) and is a poor electrical conductor. Adding '
      'cryolite (Na3AlF6) and fluorspar (CaF2) lowers the melting point to ~1173 K and enhances electrical '
      'conductivity. Carbon anodes are oxidized to CO/CO2 while molten Al deposits at the cathode.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the extraction of aluminium from purified alumina using the Hall-Heroult electrolytic process and '
      'describe the role of cryolite.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Ammonia molecules form strong intermolecular hydrogen bonds due to high electronegativity of nitrogen, whereas '
      'phosphorus cannot form hydrogen bonds. Nitrogen lone pair in NH3 is concentrated in a compact 2p-orbital, '
      'making it a stronger Lewis base than PH3 whose lone pair is diffused over a larger 3p-orbital.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain why phosphine (PH3) has a lower boiling point than ammonia (NH3) and is less basic.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'SO2 is catalytically oxidized to SO3 using V2O5 catalyst at 720 K and 2 bar pressure: 2 SO2 + O2 <-> 2 SO3 '
      '(Delta H = -196.6 kJ). SO3 is absorbed in concentrated H2SO4 to form oleum (H2S2O7), which is then diluted with '
      'water to obtain sulfuric acid of desired concentration.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Describe the preparation of sulfuric acid by the Contact process, stating the catalyst and optimum '
      'temperature-pressure conditions.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'XeF2: Xe has 8 valence electrons; forms 2 bond pairs and 3 lone pairs in equatorial positions (sp3d '
      'hybridization), giving a linear molecular shape. XeF4: Xe forms 4 bond pairs and 2 axial lone pairs (sp3d2 '
      'hybridization), giving a square planar molecular shape.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the preparation and structures of xenon fluorides XeF2 and XeF4 using VSEPR theory.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Mond process: Impure nickel is heated with CO at 330-350 K to form volatile nickel tetracarbonyl Ni(CO)4, which '
      'decomposes at 450-470 K to yield pure Ni. Van Arkel method: Crude Zr is heated with I2 to form volatile ZrI4, '
      'which decomposes on an incandescent tungsten filament at 1800 K to deposit pure Zr.',
 'bloom': 'Understand',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Explain the Mond process for the refining of nickel and the Van Arkel method for the purification of zirconium.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Low temp zone (500-800 K): 3 Fe2O3 + CO -> 2 Fe3O4 + CO2, and Fe3O4 + 4 CO -> 3 Fe + 4 CO2. Middle zone '
      '(900-1500 K): CaCO3 -> CaO + CO2, and CaO + SiO2 -> CaSiO3 (slag). High temp zone (1500 K): C + CO2 -> 2 CO, '
      'and FeO + C -> Fe + CO.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write the balanced chemical equations for the extraction of iron from hematite ore in a blast furnace at '
      'different temperature zones.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': '(a) NH3 + 3 Cl2 (excess) -> NCl3 + 3 HCl (forming explosive nitrogen trichloride). (b) 2 NaN3 -> 2 Na + 3 N2 '
      '(under gentle heating, producing ultrapure dinitrogen gas).',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write balanced chemical equations for: (a) Reaction of ammonia with excess chlorine, and (b) Thermal '
      'decomposition of sodium azide (NaN3) to produce very pure nitrogen.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Smelting: 2 CuFeS2 + O2 -> Cu2S + 2 FeS + SO2, and FeO + SiO2 -> FeSiO3 (slag). Bessemerization '
      '(auto-reduction): 2 Cu2S + 3 O2 -> 2 Cu2O + 2 SO2, followed by 2 Cu2O + Cu2S -> 6 Cu + SO2 (producing blister '
      'copper).',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write the chemical reactions involved in the extraction of copper from copper pyrites in a reverberatory '
      'furnace (matte smelting and bessemerization).',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Step 1: 4 NH3 + 5 O2 -> 4 NO + 6 H2O (over Pt/Rh catalyst gauze at 500 K, 9 bar). Step 2: 2 NO + O2 -> 2 NO2. '
      'Step 3: 3 NO2 + H2O -> 2 HNO3 + NO.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Write the chemical equation for the preparation of nitric acid by the catalytic oxidation of ammonia in '
      "Ostwald's process.",
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'XeF6: 6 bond pairs + 1 lone pair = sp3d3 hybridization; distorted octahedral shape. XeO3: 3 double bonds (bond '
      'pairs) + 1 lone pair = sp3 hybridization; pyramidal shape.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Predict the geometry and hybridization of XeF6 and XeO3 and draw their molecular shapes using VSEPR theory.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': '(a) P4 + 3 NaOH + 3 H2O -> PH3 + 3 NaH2PO2 (sodium hypophosphite, disproportionation reaction). (b) Cu + 4 HNO3 '
      '(conc) -> Cu(NO3)2 + 2 NO2 + 2 H2O.',
 'bloom': 'Apply',
 'board': 'COMMON',
 'class': 12,
 'marks': 3,
 'q': 'Complete and balance the chemical equations for: (a) P4 + 3 NaOH + 3 H2O -> ?, and (b) Cu + 4 HNO3 '
      '(concentrated) -> ?.',
 'type': 'Short Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Nitrogen exhibits unique behavior due to small size, high electronegativity, high ionization enthalpy, and '
      'absence of vacant d-orbitals. It forms strong p-pi p-pi multiple bonds (N#N diatomic gas), has maximum '
      'covalency of 4, cannot form pentahalides, and its hydrides have high boiling points due to intermolecular '
      'hydrogen bonding.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze the anomalous properties of nitrogen in Group 15 compared to phosphorus, arsenic, and antimony.',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Nitrogen exists as a diatomic molecule with a strong triple bond (bond dissociation energy 941.4 kJ/mol), '
      'making it exceptionally inert at ambient temperatures. White phosphorus exists as a tetrahedral P4 molecule '
      'with severe angular strain (bond angle 60 deg instead of 109.5 deg), rendering it highly unstable and '
      'spontaneously combustible.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze why nitrogen is chemically inert at room temperature whereas white phosphorus is highly reactive and '
      'catches fire spontaneously in air.',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Down the group from H2O to H2Te, E-H bond length increases and bond dissociation enthalpy decreases. '
      'Consequently: 1. Acidic strength increases (H2O < H2S < H2Se < H2Te). 2. Thermal stability decreases (H2O > H2S '
      '> H2Se > H2Te). 3. Reducing character increases (H2O is non-reducing, H2Te is strongest).',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Compare and contrast the acidic character, thermal stability, and reducing power of the hydrides of Group 16 '
      'elements (H2O, H2S, H2Se, H2Te).',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'In interhalogen compounds X-X_prime, the bond between two different halogens is weaker and more polar than the '
      'homoatomic X-X bond in pure halogens (due to electronegativity difference and size mismatch), facilitating '
      'easier bond cleavage. Fluorine (F2) is the sole exception because the small size of F creates extreme '
      'non-bonding lone pair repulsions.',
 'bloom': 'Analyze',
 'board': 'COMMON',
 'class': 12,
 'marks': 4,
 'q': 'Analyze why interhalogen compounds are generally more reactive than pure halogens (except fluorine).',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Zone refining exploits fractional crystallization where impurities are more soluble in the molten melt than '
      'solid metal, achieving purity exceeding 99.999% essential for silicon and germanium. The Van Arkel method '
      'purifies titanium and zirconium by converting them into volatile iodides that decompose on tungsten filaments, '
      'removing all interstitial oxygen/nitrogen.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Evaluate the effectiveness of zone refining and Van Arkel methods in producing ultra-pure semiconductor-grade '
      'metals.',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'Below 1073 K, the standard Gibbs free energy curve for 2 CO + O2 -> 2 CO2 lies below the curve for 2 C + O2 -> '
      '2 CO, and also lies below the FeO formation curve, making Delta G negative for reduction by CO. Above 1073 K, '
      'the C -> CO line slopes downward due to positive entropy change (Delta S > 0) and intersects below the FeO '
      'line, making carbon energetically superior.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': 'Using an Ellingham diagram, evaluate why carbon monoxide (CO) is a better reducing agent than carbon (C) for '
      'iron oxide below 1073 K, whereas carbon is better above 1073 K.',
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
{'a': 'N2 + 3 H2 <-> 2 NH3 (Delta H = -92.4 kJ/mol). The forward reaction is exothermic and involves a decrease in '
      'number of moles (4 mol -> 2 mol). By Le Chatelier principle, high pressure (200 atm) shifts equilibrium toward '
      'fewer moles, and moderate temperature (~700 K) with iron catalyst containing K2O/Al2O3 promoters optimizes '
      'yield without retarding kinetic reaction rate.',
 'bloom': 'Evaluate',
 'board': 'COMMON',
 'class': 12,
 'marks': 5,
 'q': "Evaluate the industrial significance and chemical equilibrium conditions (Le Chatelier's principle) for "
      "maximizing the yield of ammonia in Haber's process.",
 'type': 'Long Answer',
 'unit': 'Metallurgy & p-Block Elements'},
 {'a': 'Crystalline solids have long-range order of constituent particles, sharp melting points, and anisotropic '
       'physical properties. Amorphous solids have only short-range order, soften gradually over a temperature range '
       '(pseudo-solids), and exhibit isotropic properties.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State the differences between crystalline solids and amorphous solids regarding order of arrangement and '
       'melting points.',
  'type': 'Short Answer',
  'unit': 'Solid State'},
 {'a': 'Schottky defect occurs when an equal number of cations and anions are missing from their lattice sites, '
       'creating vacancies and decreasing crystal density (e.g. NaCl, KCl). Frenkel defect occurs when a smaller ion '
       '(usually cation) is dislocated to an interstitial site, leaving crystal density unchanged (e.g. AgCl, ZnS).',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain Schottky defect and Frenkel defect in ionic solids and describe their effect on crystal density.',
  'type': 'Short Answer',
  'unit': 'Solid State'},
 {'a': 'In FCC, face diagonal = 4r = a * sqrt(2), so a = 2 * sqrt(2) * r. Volume of unit cell = a^3 = 16 * sqrt(2) * '
       'r^3. Number of atoms per unit cell Z = 4. Volume of 4 spheres = 4 * (4/3) * pi * r^3 = (16/3) * pi * r^3. '
       'Packing efficiency = ((16/3) * pi * r^3) / (16 * sqrt(2) * r^3) = pi / (3 * sqrt(2)) = 74%.',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Calculate the packing efficiency of a face-centered cubic (FCC) unit cell showing the relationship between '
       'atomic radius r and edge length a.',
  'type': 'Short Answer',
  'unit': 'Solid State'},
 {'a': 'In conductors, valence band and conduction band overlap or the band gap is zero, allowing free electron '
       'conduction. In insulators, a large forbidden energy gap (Eg > 3 eV) prevents valence electrons from being '
       'excited to the conduction band. In semiconductors, the band gap is small (Eg < 3 eV), enabling thermal '
       'excitation of electrons at room temperature.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Analyze the electrical conductivity differences among conductors, semiconductors, and insulators using band '
       'theory of solids.',
  'type': 'Long Answer',
  'unit': 'Solid State'},
 {'a': 'Doping silicon with group 15 pentavalent donors (P, As) introduces donor energy levels just below the '
       'conduction band, vastly increasing free electron concentration (n_e >> n_h). Doping with group 13 trivalent '
       'acceptors (B, Al) creates acceptor levels just above the valence band, vastly increasing hole concentration '
       '(n_h >> n_e). Both enhance conductivity by orders of magnitude.',
  'bloom': 'Evaluate',
  'board': 'COMMON',
  'class': 12,
  'marks': 5,
  'q': 'Evaluate the impact of n-type versus p-type doping on the carrier concentrations and electrical conductivity '
       'of crystalline silicon.',
  'type': 'Long Answer',
  'unit': 'Solid State'},
 {'a': 'SN1 is a two-step unimolecular mechanism involving a carbocation intermediate, following first-order kinetics '
       'with racemization in chiral centers. SN2 is a single-step bimolecular concerted mechanism with a '
       'pentacoordinate transition state, following second-order kinetics with complete Walden inversion.',
  'bloom': 'Remember',
  'board': 'COMMON',
  'class': 12,
  'marks': 2,
  'q': 'State the key characteristics of SN1 and SN2 nucleophilic substitution reactions.',
  'type': 'Short Answer',
  'unit': 'Haloalkanes'},
 {'a': 'Tertiary alkyl halides form stable 3-degree carbocations due to inductive (+I) and hyperconjugation effects of '
       'three alkyl groups, while steric hindrance prevents backside nucleophilic attack. Primary halides form '
       'unstable 1-degree carbocations but have minimal steric hindrance, facilitating concerted backside attack in '
       'SN2.',
  'bloom': 'Understand',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': 'Explain why tertiary alkyl halides undergo substitution via SN1 mechanism whereas primary alkyl halides '
       'proceed via SN2 mechanism.',
  'type': 'Short Answer',
  'unit': 'Haloalkanes'},
 {'a': 'Phenol + NaOH -> Sodium phenoxide. Sodium phenoxide + CO2 (under 4-7 atm, 400 K) followed by acidification '
       '(H+) -> Salicylic acid (2-hydroxybenzoic acid).',
  'bloom': 'Apply',
  'board': 'COMMON',
  'class': 12,
  'marks': 3,
  'q': "Write the chemical equation for the preparation of salicylic acid from phenol via Kolbe's reaction.",
  'type': 'Short Answer',
  'unit': 'Haloalkanes'},
 {'a': 'Aldol condensation occurs in aldehydes/ketones possessing at least one alpha-hydrogen in dilute alkali, '
       'forming beta-hydroxy aldehydes (aldols) which dehydrate to alpha,beta-unsaturated carbonyls. Cannizzaro '
       'reaction occurs in aldehydes lacking alpha-hydrogens (e.g. HCHO, C6H5CHO) in concentrated alkali, undergoing '
       'disproportionation into a primary alcohol and a carboxylate salt.',
  'bloom': 'Analyze',
  'board': 'COMMON',
  'class': 12,
  'marks': 4,
  'q': 'Compare and contrast Aldol condensation and Cannizzaro reaction with respect to presence of alpha-hydrogen '
       'atoms and reaction products.',
  'type': 'Long Answer',
  'unit': 'Haloalkanes'},
  {'a': 'Enzymes are highly specific globular protein biocatalysts that lower activation energy by stabilizing '
        'the transition state through precise substrate binding at active sites (induced fit/lock-and-key models). '
        'Unlike non-specific inorganic catalysts requiring harsh temperature and pressure, enzymes exhibit immense '
        'catalytic acceleration (up to 10^8-fold) under mild physiological conditions. Enzyme activity displays optimum '
        'temperature (~37 deg C) and optimum pH, outside of which tertiary conformation denatures. Competitive inhibitors '
        'structurally resemble natural substrates and reversibly bind active sites (e.g. malonate inhibiting succinate '
        'dehydrogenase). A coenzyme is a loosely bound, dialyzable non-protein organic cofactor (e.g. NAD+, coenzyme A), '
        'whereas a prosthetic group is tightly and permanently covalently bound to the apoenzyme (e.g. haem in '
        'catalase/peroxidase).',
   'bloom': 'Evaluate',
   'board': 'COMMON',
   'class': 12,
   'marks': 5,
   'q': 'Critically evaluate the mechanism of enzyme catalysis and explain the factors responsible for their exceptional '
        'catalytic efficiency and specificity compared to inorganic catalysts. Assess the influence of temperature, pH, '
        'and competitive inhibitors on enzyme action, and differentiate between a coenzyme and a prosthetic group with '
        'representative examples.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  # -------------------------------------------------------------------------
  # Class 12 Chemistry Unit 10: Biomolecules (CBSE & TNSB Aligned)
  # -------------------------------------------------------------------------
  {'a': 'B) Uracil. In RNA, uracil forms base pairs with adenine, replacing thymine which is exclusively found in DNA.',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 1,
   'q': 'Which of the following nitrogenous bases is found only in RNA and is absent in DNA? (A) Thymine (B) Uracil (C) Adenine (D) Guanine',
   'type': 'MCQ',
   'unit': 'Biomolecules'},
  {'a': 'B) Glycosidic linkage. An oxide linkage formed by condensation between the cyclic hemiacetal hydroxyl group of one monosaccharide and a hydroxyl group of another.',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 1,
   'q': 'The covalent bond that holds two monosaccharide units together through an oxygen atom in oligosaccharides and polysaccharides is called: (A) Peptide linkage (B) Glycosidic linkage (C) Phosphodiester linkage (D) Ester bond',
   'type': 'MCQ',
   'unit': 'Biomolecules'},
  {'a': 'Reducing sugars reduce Fehling solution and Tollens reagent due to free or potential aldehydic or ketonic hemiacetal groups (e.g. D-glucose, maltose, lactose). Non-reducing sugars have reducing groups involved in glycosidic bond formation and cannot reduce these reagents (e.g. sucrose).',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 2,
   'q': 'State what is meant by reducing and non-reducing sugars. Give one example of each.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'A peptide linkage is an amide bond (-CO-NH-) formed between the alpha-carboxyl group of one amino acid and the alpha-amino group of an adjacent amino acid with elimination of a water molecule.',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 2,
   'q': 'Define a peptide linkage and write its characteristic structural representation.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'Essential amino acids cannot be synthesized by the human body and must be supplied through diet (e.g. valine, leucine, lysine). Non-essential amino acids are synthesized internally by metabolic pathways and are not mandatory in diet (e.g. glycine, alanine).',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 2,
   'q': 'Distinguish between essential and non-essential amino acids. Give one representative example of each.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'In neutral aqueous solution, the carboxyl group (-COOH) of an amino acid loses a proton while the amino group (-NH2) gains a proton, forming an internal dipolar ion called a Zwitterion: R-CH(NH3+)-COO-. It exhibits both positive and negative formal charges with zero net charge at its isoelectric point.',
   'bloom': 'Remember',
   'board': 'COMMON',
   'class': 12,
   'marks': 2,
   'q': 'What is a Zwitterion? Illustrate the dipolar structure of an alpha-amino acid in aqueous medium.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'Anomers are cyclic diastereomers of monosaccharides that differ in spatial configuration exclusively around the hemiacetal or hemiketal carbonyl carbon atom (C-1 in aldoses such as D-glucose, C-2 in ketoses such as D-fructose). The C-1 carbon in D-glucose is the anomeric carbon.',
   'bloom': 'Understand',
   'board': 'COMMON',
   'class': 12,
   'marks': 2,
   'q': 'What are anomers? Identify the anomeric carbon atom in D-glucose.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'Denaturation is the process where a native protein loses its higher-order tertiary and secondary folded conformations due to physical changes (temperature) or chemical changes (pH), leading to loss of biological activity. The covalent primary peptide sequence remains intact.',
   'bloom': 'Understand',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Explain the phenomenon of protein denaturation. Which levels of structural organization are disrupted, and which remains intact?',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'Fibrous proteins consist of linear polypeptide chains running parallel held together by hydrogen and disulfide bonds; they are insoluble in water (e.g. keratin in hair, myosin in muscle). Globular proteins have chains folded into compact spherical conformations; they are soluble in water (e.g. insulin, albumin).',
   'bloom': 'Understand',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Differentiate between fibrous proteins and globular proteins with respect to molecular shape, intermolecular forces, and aqueous solubility.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'A nucleoside contains a nitrogenous base (purine or pyrimidine) attached to the C-1 position of a pentose sugar via an N-beta-glycosidic bond. A nucleotide contains a nucleoside esterified with a phosphate group at the C-5 position of the pentose sugar via a phosphoester linkage.',
   'bloom': 'Understand',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Explain the structural differences between a nucleoside and a nucleotide, specifying the positions and types of chemical linkages involved.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'Water-soluble vitamins (Vitamin B-complex, Vitamin C) cannot be stored in the body and are excreted regularly in urine, requiring daily dietary supply. Fat-soluble vitamins (Vitamins A, D, E, K) are stored in the liver and adipose tissue, so excessive intake can accumulate and cause hypervitaminosis.',
   'bloom': 'Understand',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Explain why water-soluble vitamins must be supplied regularly in the diet whereas fat-soluble vitamins should not be taken in excessive amounts.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': '(i) D-glucose + NH2OH -> Glucose oxime (HO-CH2-(CHOH)4-CH=N-OH), confirming carbonyl group. (ii) D-glucose + Br2 water -> Gluconic acid (HO-CH2-(CHOH)4-COOH), confirming aldehydic -CHO group. (iii) D-glucose + conc. HNO3 -> Saccharic acid (HOOC-(CHOH)4-COOH), confirming presence of primary alcohol (-CH2OH).',
   'bloom': 'Apply',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Write the balanced chemical equations for the reaction of D-glucose with: (i) Hydroxylamine (NH2OH), (ii) Bromine water (Br2/H2O), and (iii) Concentrated nitric acid (HNO3).',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': '(i) Prolonged heating with HI reduces D-glucose to n-hexane (CH3-CH2-CH2-CH2-CH2-CH3), confirming that all six carbon atoms are linked in an unbranched chain. (ii) Reaction with excess acetic anhydride yields Glucose pentaacetate, confirming the presence of five -OH groups on distinct carbon atoms.',
   'bloom': 'Apply',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'State the products formed and write chemical equations when D-glucose is treated with: (i) Prolonged heating with HI in the presence of red phosphorus, and (ii) Acetic anhydride in pyridine.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': 'According to Chargaff rules for double-stranded DNA: %G = %C and %A = %T. Given Cytosine = 28%, Guanine = 28%. Total G + C = 56%. Remaining A + T = 100% - 56% = 44%. Since Adenine equals Thymine: Adenine = 22% and Thymine = 22%.',
   'bloom': 'Apply',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'A sample of double-stranded DNA contains 28% cytosine bases. Applying Chargaff rules of base equivalence, calculate the percentages of guanine, adenine, and thymine in this sample.',
   'type': 'Numerical',
   'unit': 'Biomolecules'},
  {'a': 'Open-chain D-glucose fails to explain: 1. It does not react with NaHSO3 or give 2,4-DNP test despite having a formal -CHO group. 2. Glucose pentaacetate does not react with NH2OH, indicating absence of free -CHO. 3. Glucose exists in two crystalline alpha and beta anomeric forms having different melting points and optical rotations, proving it exists predominantly as a cyclic hemiacetal pyranose ring.',
   'bloom': 'Apply',
   'board': 'COMMON',
   'class': 12,
   'marks': 4,
   'q': 'Demonstrate why the open-chain structure of D-glucose was inadequate to explain its chemical behavior, citing three experimental observations.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  {'a': 'In an alpha-helix, the polypeptide chain coils into a right-handed spiral stabilized by intramolecular hydrogen bonds between the -NH group of each amino acid residue and the >C=O group of the fourth preceding residue (i+4). In a beta-pleated sheet, polypeptide chains lie side-by-side in extended conformation stabilized by intermolecular hydrogen bonds between adjacent chains.',
   'bloom': 'Analyze',
   'board': 'COMMON',
   'class': 12,
   'marks': 3,
   'q': 'Analyze the structural differences between alpha-helix and beta-pleated sheet secondary structures of proteins with respect to polypeptide arrangement and hydrogen bonding orientation.',
   'type': 'Short Answer',
   'unit': 'Biomolecules'},
  {'a': '(i) Sugar: DNA has beta-D-2-deoxyribose; RNA has beta-D-ribose. (ii) Bases: DNA contains adenine, guanine, cytosine, and thymine; RNA contains adenine, guanine, cytosine, and uracil. (iii) Helical structure: DNA is a double-stranded antiparallel double helix; RNA is typically single-stranded. (iv) Biological role: DNA stores genetic information; RNA directs protein biosynthesis.',
   'bloom': 'Analyze',
   'board': 'COMMON',
   'class': 12,
   'marks': 4,
   'q': 'Compare and contrast DNA and RNA regarding: (i) Pentose sugar structure, (ii) Pyrimidine base pairing, (iii) Higher-order secondary structure, and (iv) Primary biological role.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  {'a': 'Pure alpha-D-glucopyranose has specific rotation of +112 degrees while beta-D-glucopyranose has +19 degrees. When either anomer is dissolved in water, the hemiacetal ring opens reversibly to the open-chain aldehyde form and re-closes, establishing a dynamic equilibrium containing 36% alpha and 64% beta anomers with a constant optical rotation of +52.7 degrees. This spontaneous change in optical rotation is mutarotation.',
   'bloom': 'Analyze',
   'board': 'COMMON',
   'class': 12,
   'marks': 4,
   'q': 'Analyze the molecular mechanism of mutarotation observed in aqueous solutions of alpha-D-glucose and beta-D-glucose, explaining the dynamic equilibrium established.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  {'a': 'Sucrose is dextrorotatory (+66.5 degrees). On hydrolysis with dilute acid or invertase enzyme, the glycosidic bond between alpha-D-glucose and beta-D-fructose is cleaved, producing equimolar D-glucose (+52.7 degrees) and D-fructose (-92.4 degrees). Because the levorotation of fructose exceeds the dextrorotation of glucose, the resulting mixture is net levorotatory (-39.7 degrees), inverting the optical sign.',
   'bloom': 'Evaluate',
   'board': 'COMMON',
   'class': 12,
   'marks': 4,
   'q': 'Critically evaluate why sucrose is dextrorotatory, but undergoes inversion upon hydrolysis to yield a levorotatory mixture (invert sugar). State the enzyme involved.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  {'a': 'Proteins are organized hierarchically: primary (amino acid sequence), secondary (alpha-helices and beta-sheets), tertiary (3D folding via disulfide, ionic, and hydrophobic interactions), and quaternary (multimeric subunit assembly). Denaturation disrupts quaternary, tertiary, and secondary conformations through thermal or chemical disruption of non-covalent interactions, exposing hydrophobic interiors that aggregate irreversibly (coagulation of egg albumin), while primary covalent peptide bonds remain completely unbroken.',
   'bloom': 'Evaluate',
   'board': 'COMMON',
   'class': 12,
   'marks': 5,
   'q': 'Critically evaluate the structural hierarchy of proteins from primary to quaternary levels. Assess the biochemical consequences of denaturation on each structural level and explain why boiling an egg is an irreversible denaturation process.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'},
  {'a': '(i) Heating with HI/red P gives n-hexane, proving a continuous 6-carbon unbranched chain. (ii) Reaction with NH2OH gives an oxime and with HCN gives a cyanohydrin, proving presence of a carbonyl group. (iii) Mild oxidation with Br2 water gives gluconic acid, proving the carbonyl group is an aldehyde (-CHO). (iv) Acetylation with acetic anhydride gives glucose pentaacetate, proving presence of five -OH groups on distinct carbons. (v) Oxidation with conc. HNO3 yields saccharic acid, proving one of the -OH groups is a primary alcohol (-CH2OH).',
   'bloom': 'Evaluate',
   'board': 'COMMON',
   'class': 12,
   'marks': 5,
   'q': 'Evaluate how sequential chemical evidence established the structural formula of D-glucose. Formulate the reactions that proved: (i) 6-carbon straight chain, (ii) Carbonyl group, (iii) Aldehyde group, (iv) Five hydroxyl groups, and (v) One primary alcohol.',
   'type': 'Long Answer',
   'unit': 'Biomolecules'}]


def normalize_text_for_comparison(text: str) -> str:
    """Normalize question text for deduplication matching."""
    if not text:
        return ""
    text = re.sub(r"\s*\([^)]*(?:unit|chapter|variation)[^)]*\)", "", text, flags=re.IGNORECASE)
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return " ".join(text.split())


def match_curriculum_question(
    board: str,
    class_name: str,
    subject_name: str,
    unit_name: str,
    bloom_level: Optional[str] = None,
    marks: Optional[int] = None,
    exclude_texts: Optional[Iterable[str]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Find a syllabus-grounded, academically rigorous question from the authentic pool.
    Matches board, class, subject, unit/topic, bloom cognitive level, and marks.
    Filters out any question whose normalized text matches exclude_texts.
    """
    s_lower = subject_name.lower()
    b_norm = "TNSB" if "tn" in board.lower() or "tamil" in board.lower() else "CBSE"
    c_str = str(class_name).lower()
    if "12" in c_str or "xii" in c_str:
        c_num = 12
    elif "10" in c_str or "x" in c_str:
        c_num = 10
    else:
        c_num = 12
    u_lower = unit_name.lower()

    pool: List[Dict[str, Any]] = []

    # 1. English
    if "english" in s_lower:
        if any(w in u_lower for w in ["prose", "first flight", "letter to god", "mandela", "buddha"]):
            pool = ENGLISH_PROSE_QUESTIONS
        elif any(w in u_lower for w in ["poem", "poet"]):
            pool = ENGLISH_POETRY_QUESTIONS
        elif any(w in u_lower for w in ["supplementary", "reader", "story", "stories", "footprints", "vistas"]):
            pool = ENGLISH_SUPPLEMENTARY_QUESTIONS
        elif any(w in u_lower for w in ["grammar", "vocabulary", "language"]):
            pool = ENGLISH_GRAMMAR_QUESTIONS
        elif any(w in u_lower for w in ["writing", "composition", "notice", "article"]) or ("letter" in u_lower and "letter to god" not in u_lower):
            pool = ENGLISH_WRITING_QUESTIONS
        else:
            # General or prose
            pool = ENGLISH_PROSE_QUESTIONS + ENGLISH_POETRY_QUESTIONS + ENGLISH_GRAMMAR_QUESTIONS

    # 2. Social Science
    elif "social" in s_lower or any(w in s_lower for w in ["history", "geography", "civic", "political"]):
        if any(w in u_lower for w in ["history", "war", "revolt", "movement", "nationalism"]):
            pool = SOCIAL_SCIENCE_HISTORY_QUESTIONS
        elif any(w in u_lower for w in ["geography", "soil", "climate", "resource", "water", "agriculture"]):
            pool = SOCIAL_SCIENCE_GEOGRAPHY_QUESTIONS
        elif any(w in u_lower for w in ["civic", "constitution", "politic", "government", "democracy"]):
            pool = SOCIAL_SCIENCE_CIVICS_QUESTIONS
        elif any(w in u_lower for w in ["economy", "economic", "money", "credit", "sector"]):
            pool = SOCIAL_SCIENCE_ECONOMICS_QUESTIONS
        else:
            pool = (
                SOCIAL_SCIENCE_HISTORY_QUESTIONS
                + SOCIAL_SCIENCE_GEOGRAPHY_QUESTIONS
                + SOCIAL_SCIENCE_CIVICS_QUESTIONS
                + SOCIAL_SCIENCE_ECONOMICS_QUESTIONS
            )

    # 3. Biology / Science
    elif "bio" in s_lower or ("science" in s_lower and any(w in u_lower for w in ["life", "cell", "reproduction", "heredity", "plant", "organism", "bio"])):
        pool = BIOLOGY_QUESTIONS

    # 4. Economics
    elif "econom" in s_lower:
        if c_num == 12:
            pool = ECONOMICS_CLASS_12_QUESTIONS
        else:
            pool = SOCIAL_SCIENCE_ECONOMICS_QUESTIONS

    # 5. Commerce / Accountancy / Business
    elif any(w in s_lower for w in ["account", "commerc", "business"]):
        pool = COMMERCE_ACCOUNTANCY_QUESTIONS

    # 6. Computer Science / IT / Programming
    elif "computer" in s_lower or "information technology" in s_lower or re.search(r"\b(cs|ip|it)\b", s_lower):
        pool = COMPUTER_SCIENCE_QUESTIONS

    # 7. Physics
    elif "physic" in s_lower:
        pool = PHYSICS_QUESTIONS

    # 8. Chemistry
    elif "chem" in s_lower:
        pool = CHEMISTRY_QUESTIONS

    if not pool:
        return None

    norm_excludes: Set[str] = set()
    if exclude_texts:
        for t in exclude_texts:
            norm_t = normalize_text_for_comparison(str(t))
            if norm_t:
                norm_excludes.add(norm_t)

    # Filter out pool candidates that match any excluded text
    available_candidates = [
        q for q in pool
        if normalize_text_for_comparison(q.get("q", "")) not in norm_excludes
    ]
    if not available_candidates:
        return None

    # Filter candidates by board, class, and unit relevance
    STOP_WORDS = {
        "unit", "chapter", "part", "class", "term", "section", "elements",
        "principles", "concepts", "theory", "studies", "skills", "python", "with", "into", "from",
        "compounds", "compound", "organic", "inorganic"
    }
    unit_matched_candidates = []
    for q in available_candidates:
        cand_unit = q.get("unit", "").lower()
        cand_kws = [w for w in cand_unit.split() if len(w) > 3 and w not in STOP_WORDS]
        is_cs = "computer" in s_lower or "programming" in s_lower or bool(re.search(r"\b(cs|ip|it)\b", s_lower))
        is_chem = "chem" in s_lower
        is_u_match = (
            (cand_unit in u_lower)
            or (u_lower in cand_unit)
            or (any(w in u_lower for w in cand_kws) if cand_kws else False)
            or (is_cs and "unit 1" in u_lower and "problem solving" in cand_unit)
            or (is_cs and "unit 2" in u_lower and "core" in cand_unit)
            or (is_cs and "unit 3" in u_lower and "object oriented" in cand_unit)
            or (is_cs and "unit 4" in u_lower and "database" in cand_unit)
            or (is_cs and "unit 5" in u_lower and "mysql" in cand_unit)
            or (is_chem and "biomolecule" in u_lower and "biomolecule" in cand_unit)
            or (is_chem and ("unit 10" in u_lower or "unit 8" in u_lower) and "biomolecule" in cand_unit)
        )
        if cand_unit and is_u_match:
            unit_matched_candidates.append(q)

    # If the pool has unit-specific entries (Physics, Chemistry, CS, Biology), disallow returning wrong unit
    has_specific_units = any(q.get("unit") for q in available_candidates)
    if has_specific_units and not unit_matched_candidates:
        return None

    candidate_pool = unit_matched_candidates if unit_matched_candidates else available_candidates

    def score_candidate(item: Dict[str, Any]) -> int:
        score = 0
        cand_board = item.get("board", "COMMON")
        cand_class = item.get("class")
        if cand_board in (b_norm, "COMMON"):
            score += 4
        else:
            return -100  # Disallow conflicting board

        if cand_class in (c_num, None):
            score += 3
        else:
            return -100  # Disallow conflicting class

        if bloom_level:
            c_bl = item.get("bloom", "").title()
            t_bl = bloom_level.strip().title()
            if c_bl == t_bl:
                score += 15
            elif c_bl in BLOOM_HIERARCHY and t_bl in BLOOM_HIERARCHY:
                diff = abs(BLOOM_HIERARCHY[c_bl] - BLOOM_HIERARCHY[t_bl])
                if diff == 1 and not (t_bl == "Remember" and BLOOM_HIERARCHY[c_bl] >= 4) and not (t_bl in ("Evaluate", "Create") and BLOOM_HIERARCHY[c_bl] <= 2):
                    score += 5
                else:
                    return -100
            else:
                score += 2
        if marks and abs(item.get("marks", 3) - marks) <= 1:
            score += 3

        cand_unit = item.get("unit", "").lower()
        cand_kws = [w for w in cand_unit.split() if len(w) > 3 and w not in STOP_WORDS]
        is_exact_u = (cand_unit in u_lower) or (u_lower in cand_unit)
        is_u_match = (
            is_exact_u
            or (any(w in u_lower for w in cand_kws) if cand_kws else False)
            or (is_cs and "unit 1" in u_lower and "problem solving" in cand_unit)
            or (is_cs and "unit 2" in u_lower and "core" in cand_unit)
            or (is_cs and "unit 3" in u_lower and "object oriented" in cand_unit)
            or (is_cs and "unit 4" in u_lower and "database" in cand_unit)
            or (is_cs and "unit 5" in u_lower and "mysql" in cand_unit)
            or (is_chem and "biomolecule" in u_lower and "biomolecule" in cand_unit)
            or (is_chem and ("unit 10" in u_lower or "unit 8" in u_lower) and "biomolecule" in cand_unit)
        )
        if cand_unit and is_exact_u:
            score += 25
        elif cand_unit and is_u_match:
            score += 15

        return score

    scored = [(score_candidate(q), q) for q in candidate_pool]
    scored = [s for s in scored if s[0] > 0]
    if not scored:
        return None

    scored.sort(key=lambda x: x[0], reverse=True)
    best_score = scored[0][0]
    top_tier = [q for score, q in scored if score >= max(1, best_score - 2)]
    return random.choice(top_tier)


# =============================================================================
# 6. MATHEMATICS CURRICULUM TEMPLATES (All 11 Categories, All 5 Bloom Levels)
# =============================================================================

MATH_CURRICULUM_TEMPLATES = {   'ALGEBRA_QUADRATICS': {   'Analyze': [   {   'a': 'When p^2 = 4q, roots are equal real numbers -p/2. When p^2 < '
                                                      '4q, roots are complex conjugates.',
                                                 'q': 'Analyze the nature of the roots of the quadratic equation x^2 + '
                                                      'px + q = 0 when p^2 - 4q = 0 versus p^2 - 4q < 0.'},
                                             {   'a': 'xy = 14 and y - x = 5 gives x = 2, y = 7. Number is 27.',
                                                 'q': 'Analyze a two-digit number problem where the product of digits '
                                                      'is 14 and interchanging digits increases the number by 45, '
                                                      'examining the constraints on single-digit solutions.'}],
                              'Apply': [   {   'a': 'D = 25 - 16 = 9 > 0. Roots are x = (5 +/- 3)/4 => x = 2 or x = '
                                                    '1/2.',
                                               'q': 'Solve the quadratic equation 2x^2 - 5x + 2 = 0 using the '
                                                    'quadratic formula and state the nature of roots.'},
                                           {   'a': '(x + 2)(x + 5) = 0 => zeroes are -2 and -5. Sum = -7 = -b/a, '
                                                    'Product = 10 = c/a.',
                                               'q': 'Find the zeroes of the quadratic polynomial x^2 + 7x + 10 and '
                                                    'verify the relationship between zeroes and coefficients.'},
                                           {   'a': 'kx^2 - 2kx + 6 = 0. D = 4k^2 - 24k = 0 => k = 6 (as k != 0).',
                                               'q': 'Find the value of k for which the quadratic equation kx(x - 2) + '
                                                    '6 = 0 has two real and equal roots.'},
                                           {   'a': 'A^2 = [[7, 10], [15, 22]], 5A = [[5, 10], [15, 20]], 7I = [[7, '
                                                    '0], [0, 7]]. Result is [[9, 0], [0, 9]].',
                                               'q': 'If matrix A = [[1, 2], [3, 4]], calculate the matrix expression '
                                                    'A^2 - 5A + 7I.'},
                                           {   'a': 'det(A) = -11. X = A^-1B => x = 1, y = 1.',
                                               'q': 'Solve the system of linear equations 2x + 3y = 5 and 3x - y = 2 '
                                                    'using matrix inversion method.'},
                                           {   'a': 'x^2 - (sum)x + product = 0 => x^2 - 4x + 1 = 0.',
                                               'q': 'Form the quadratic polynomial whose zeroes are 2 + sqrt(3) and 2 - sqrt(3).'},
                                           {   'a': '3x - 5y = 4 and 9x - 2y = 7 => x = 9/13, y = -5/13.',
                                               'q': 'Solve the pair of linear equations 3x - 5y - 4 = 0 and 9x = 2y + 7 using the elimination method.'}],
                              'Evaluate': [   {   'a': 'x^2 + 2x + 1 = 2x - 6 => x^2 + 7 = 0. It is quadratic, but has '
                                                       'no real roots since D = -28 < 0.',
                                                  'q': 'Evaluate whether the equation (x + 1)^2 = 2(x - 3) is a '
                                                       'quadratic equation, and assess whether every second-degree '
                                                       'equation must have real solutions.'},
                                              {   'a': 'Unique if det(A) != 0; infinite or inconsistent if det(A) = 0 '
                                                       'depending on (adj A)*B.',
                                                  'q': 'Assess whether a given system of linear equations has a unique '
                                                       'solution, infinitely many solutions, or no solution using '
                                                       'determinant rank criteria.'}],
                              'Remember': [   {   'a': 'x = [-b +/- sqrt(b^2 - 4ac)] / (2a).',
                                                  'q': 'State the quadratic formula for finding the roots of ax^2 + bx '
                                                       '+ c = 0.'},
                                              {   'a': 'Sum of zeroes alpha + beta = -b/a, Product of zeroes alphabeta '
                                                       '= c/a.',
                                                  'q': 'State the relationship between the zeroes and coefficients of '
                                                       'a quadratic polynomial ax^2 + bx + c.'},
                                              {   'a': 'D > 0: two distinct real roots. D = 0: two equal real roots. D '
                                                       '< 0: no real roots.',
                                                  'q': 'Define the discriminant D = b^2 - 4ac and state the three '
                                                       'conditions for the nature of roots.'}],
                              'Understand': [   {   'a': 'Since the square root of a positive number is real, zero is '
                                                         'unique, and negative is non-real in R.',
                                                    'q': 'Explain how the sign of the discriminant determines whether '
                                                         'a quadratic equation has real, distinct, or no real roots.'},
                                                {   'a': 'A parabola opening upward (a > 0) or downward (a < 0); '
                                                         'x-intercepts are real zeroes of polynomial.',
                                                    'q': 'Describe the graphical representation of a quadratic '
                                                         'polynomial and explain what its x-intercepts represent.'}]},
    'CALCULUS': {   'Analyze': [   {   'a': "f'(x) = 6(x - 1)(x - 2). Increasing on (-infinity, 1)  U  (2, infinity), "
                                            'decreasing on (1, 2).',
                                       'q': 'Analyze the derivative dy/dx of f(x) = 2x^3 - 9x^2 + 12x + 15 to find '
                                            'critical points and determine where the function is strictly increasing '
                                            'or decreasing.'},
                                   {   'a': "y'' = 6x - 6 = 0 => x = 1 is the point of inflection where concavity "
                                            'changes.',
                                       'q': 'Examine the points of inflection and concavity of the curve y = x^3 - '
                                            '3x^2 + 2 using second derivatives.'}],
                    'Apply': [   {   'a': 'Using property I = integral [0 to pi/2] cos^2 x dx. 2I = pi/2 => I = pi/4.',
                                     'q': 'Evaluate the definite integral: integral  from 0 to pi/2 of (sin^2 x) dx.'},
                                 {   'a': 'dy/dx = (sin x)^(cos x) * [cos x * cot x - sin x * ln(sin x)].',
                                     'q': 'Find the derivative dy/dx if y = (sin x)^(cos x) using logarithmic '
                                          'differentiation.'},
                                 {   'a': 'IF = e^(2x). y * e^(2x) = e^x + C => y = e^(-x) + C*e^(-2x).',
                                     'q': 'Find the general solution of the differential equation: dy/dx + 2y = '
                                          'e^(-x).'},
                                 {   'a': 'Completing square: (x + 2)^2 + 9. Integral = (1/3) tan^-1((x + 2)/3) + C.',
                                     'q': 'Evaluate the indefinite integral: integral  [1 / (x^2 + 4x + 13)] dx.'}],
                    'Evaluate': [   {   'a': 'LHD = -1, RHD = +1. Since LHD != RHD, f is not differentiable at x = 0.',
                                        'q': 'Evaluate whether the function f(x) = |x| is differentiable at x = 0, and '
                                             'justify your answer using left-hand and right-hand derivative '
                                             'definitions.'},
                                    {   'a': 'Both M and N are degree 2. Substitute y = vx to solve: x^2 - y^2 = Cx.',
                                        'q': 'Assess whether the differential equation (x^2 + y^2)dx - 2xy dy = 0 is '
                                             'homogeneous, and evaluate its general solution.'}],
                    'Remember': [   {   'a': "Product: (uv)' = u'v + uv'. Quotient: (u/v)' = (u'v - uv')/v^2. Chain: "
                                             "d/dx[f(g(x))] = f'(g(x))*g'(x).",
                                        'q': 'State the product rule, quotient rule, and chain rule for finding the '
                                             'derivative of functions.'},
                                    {   'a': "If f is continuous on [a, b] and F' = f, then integral [a to b] f(x) dx "
                                             '= F(b) - F(a).',
                                        'q': 'State the Fundamental Theorem of Calculus relating definite integrals '
                                             'and anti-derivatives.'},
                                    {   'a': 'lim_{x->c} f(x) exists and equals f(c).',
                                        'q': 'Define continuity of a function f(x) at a point x = c in terms of '
                                             'limits.'}],
                    'Understand': [   {   'a': 'Limit of secant slopes as deltax -> 0 yields the instantaneous rate of '
                                               'change and tangent slope.',
                                          'q': 'Explain the geometric meaning of the derivative dy/dx as the slope of '
                                               'the tangent to the curve.'},
                                      {   'a': 'Riemann sum of infinitesimal rectangles f(x)*dx sums positive area '
                                               'above x-axis and negative area below.',
                                          'q': 'Describe why the definite integral integral [a to b] f(x) dx '
                                               'represents the net signed area under the curve.'}]},
    'COORDINATE_GEOMETRY': {   'Analyze': [   {   'a': 'Slope AB = -2, Slope BC = 7/2. Since slopes are not equal, the '
                                                       'points are not collinear.',
                                                  'q': 'Analyze whether the points A(1, 5), B(2, 3), and C(-2, -11) '
                                                       'are collinear by examining their slopes in the Cartesian '
                                                       'plane.'},
                                              {   'a': 'All four sides equal 2*sqrt(2) and diagonals are equal, '
                                                       'proving it is a square.',
                                                  'q': 'Analyze the type of quadrilateral formed by the vertices A(-1, '
                                                       '-2), B(1, 0), C(-1, 2), and D(-3, 0) by comparing their side '
                                                       'lengths and diagonals.'}],
                               'Apply': [   {   'a': 'd = sqrt((4-2)^2 + (1-3)^2) = sqrt(4 + 4) = 2*sqrt(2) units.',
                                                'q': 'Find the distance between the points A(2, 3) and B(4, 1) in the '
                                                     'Cartesian coordinate plane.'},
                                            {   'a': 'x = (2*4 + 3*-1)/5 = 1, y = (2*-3 + 3*7)/5 = 3. Point P is (1, '
                                                     '3).',
                                                'q': 'Find the coordinates of the point P which divides the line '
                                                     'segment joining A(-1, 7) and B(4, -3) in the ratio 2:3 '
                                                     'internally.'},
                                            {   'a': 'Ratio k:1 gives k = 2/9. The ratio is 2:9.',
                                                'q': 'Determine the ratio in which the line 2x + y - 4 = 0 divides the '
                                                     'line segment joining the points A(2, -2) and B(3, 7).'},
                                            {   'a': 'Midpoint M = ((-5+7)/2, (4-8)/2) = (1, -2).',
                                                'q': 'Find the midpoint of the line segment joining the points P(-5, '
                                                     '4) and Q(7, -8) in the coordinate plane.'},
                                            {   'a': 'Centroid G = ((3 - 7 + 10)/3, (-5 + 4 - 2)/3) = (2, -1).',
                                                'q': 'Find the coordinates of the centroid of triangle ABC with '
                                                     'vertices A(3, -5), B(-7, 4), and C(10, -2).'}],
                               'Evaluate': [   {   'a': 'AB^2 = 25, BC^2 = 50, AC^2 = 25. AB^2 + AC^2 = BC^2 and AB = '
                                                        'AC, so it is an isosceles right triangle.',
                                                   'q': 'Evaluate whether the points A(3, 0), B(6, 4), and C(-1, 3) '
                                                        'form an isosceles right-angled triangle in the Cartesian '
                                                        'plane, justifying your answer.'},
                                               {   'a': 'Calculate midpoints of diagonals AC and BD. Since midpoints '
                                                        'coincide, the diagonals bisect each other.',
                                                   'q': 'Assess the validity of the statement that the diagonals of a '
                                                        'parallelogram always bisect each other using coordinate '
                                                        'geometry proof.'}],
                               'Remember': [   {   'a': 'Distance d = sqrt((x2 - x1)^2 + (y2 - y1)^2).',
                                                   'q': 'State the distance formula between two points (x1, y1) and '
                                                        '(x2, y2) in the Cartesian coordinate plane.'},
                                               {   'a': 'P(x, y) = ((m*x2 + n*x1)/(m+n), (m*y2 + n*y1)/(m+n)).',
                                                   'q': 'State the section formula for a point dividing a line segment '
                                                        'in the ratio m:n internally in the coordinate plane.'},
                                               {   'a': 'Midpoint M = ((x1+x2)/2, (y1+y2)/2). Centroid G = '
                                                        '((x1+x2+x3)/3, (y1+y2+y3)/3).',
                                                   'q': 'Define the coordinates of the midpoint of a line segment and '
                                                        'centroid of a triangle in the Cartesian plane.'}],
                               'Understand': [   {   'a': 'Form a right triangle with horizontal leg |x2 - x1| and '
                                                          'vertical leg |y2 - y1|. Hypotenuse gives distance.',
                                                     'q': 'Explain how the distance formula is derived using '
                                                          'Pythagoras Theorem in the Cartesian coordinate plane.'},
                                                 {   'a': 'Points are collinear if slope AB = slope BC, or '
                                                          'equivalently the area of triangle ABC formed by the points '
                                                          'is 0.',
                                                     'q': 'Describe the condition under which three points in the '
                                                          'coordinate plane are collinear using slopes or area.'}]},
    'GEOMETRY': {   'Analyze': [   {   'a': 'By SSS similarity criterion, the triangles are similar, which implies all '
                                            'corresponding angles are equal.',
                                       'q': 'Analyze the similarity of two triangles ABC and PQR given that AB/PQ = '
                                            'BC/QR = CA/RP, and examine whether their corresponding angles must be '
                                            'equal.'},
                                   {   'a': 'As the two intersection points of a secant move closer and coincide, the '
                                            'secant becomes a tangent line.',
                                       'q': 'Compare the properties of chords, secants, and tangents of a circle, and '
                                            'examine the conditions under which a secant degenerates into a tangent.'},
                                   {   'a': '7^2 + 24^2 = 49 + 576 = 625 = 25^2. By converse of Pythagoras Theorem, it '
                                            'forms a right triangle.',
                                       'q': 'Analyze whether a triangle with side lengths 7 cm, 24 cm, and 25 cm forms '
                                            'a right-angled triangle, and examine the relationship between the squares '
                                            'of the sides using Pythagoras Theorem.'},
                                   {   'a': 'Using equal lengths of tangents from external vertices gives AB + CD = AD '
                                            '+ BC.',
                                       'q': 'Examine the geometric consequences when a quadrilateral is circumscribed '
                                            'about a circle, and prove that the sums of opposite sides are equal (AB + '
                                            'CD = AD + BC).'},
                                   {   'a': 'Since the sum of angles of a triangle is always 180 deg, two pairs of '
                                            'equal angles guarantee the third pair is equal.',
                                       'q': 'Compare the AAA, SAS, and SSS similarity criteria of triangles and '
                                            'analyze why AAA similarity is equivalent to AA similarity.'}],
                    'Apply': [   {   'a': 'AD/DB = AE/EC => 1.5/3 = 1/EC => EC = 2 cm.',
                                     'q': 'In triangle ABC, DE is parallel to BC with D on AB and E on AC. If AD = 1.5 '
                                          'cm, DB = 3 cm, and AE = 1 cm, calculate the length of EC using Thales '
                                          'Theorem.'},
                                 {   'a': 'In right triangle with radius 3 and 5, half chord = sqrt(25 - 9) = 4 cm. '
                                          'Full chord = 8 cm.',
                                     'q': 'Two concentric circles have radii 5 cm and 3 cm. Calculate the length of '
                                          'the chord of the larger circle which touches the smaller circle.'},
                                 {   'a': 'PQ = sqrt(OQ^2 - OP^2) = sqrt(144 - 25) = sqrt(119) cm.',
                                     'q': 'A tangent PQ at a point P of a circle of radius 5 cm meets a line through '
                                          'the center O at a point Q so that OQ = 12 cm. Calculate the length of PQ.'},
                                 {   'a': 'Ratio of sides = sqrt(64/121) = 8/11. Perimeter ratio is also 8/11.',
                                     'q': 'If two similar triangles have areas in the ratio 64:121, calculate the '
                                          'ratio of their corresponding sides and perimeters.'},
                                 {   'a': 'Hypotenuse AC = 10 cm. Incircle radius r = (a + b - c)/2 = (6 + 8 - 10)/2 = '
                                          '2 cm.',
                                     'q': 'In a right triangle ABC right-angled at B with AB = 6 cm and BC = 8 cm, '
                                          'calculate the radius of the incircle touching all three sides.'}],
                    'Evaluate': [   {   'a': 'AB + CD = AD + BC and AB = CD, AD = BC implies 2AB = 2AD => AB = AD. '
                                             'Since adjacent sides are equal, the parallelogram is a rhombus.',
                                        'q': 'Evaluate whether the statement that every parallelogram circumscribing a '
                                             'circle must be a rhombus is universally valid, and justify your '
                                             'conclusion with geometric proof.'},
                                    {   'a': 'Construct diameter through vertex and use exterior angle property of '
                                             'isosceles triangles formed by radii.',
                                        'q': 'Assess the validity of the theorem that the angle subtended by an arc at '
                                             'the center is double the angle subtended by it at any point on the '
                                             'remaining part of the circle, justifying each geometric step.'},
                                    {   'a': 'If similar triangles have equal perimeters, their scale factor is 1, '
                                             'meaning they are congruent, so areas are equal.',
                                        'q': 'Evaluate the claim that two triangles having equal corresponding '
                                             'perimeters must have equal areas, and justify whether this holds for '
                                             'similar triangles.'},
                                    {   'a': 'Opposite angles must be supplementary. In any rectangle, opposite angles '
                                             'are 90 deg + 90 deg = 180 deg, so every rectangle is cyclic.',
                                        'q': 'Critically evaluate the geometric conditions required for four points on '
                                             'a plane to be concyclic, and assess whether every rectangle is a cyclic '
                                             'quadrilateral.'},
                                    {   'a': 'If a line divides two sides proportionally, assume it is not parallel '
                                             'and draw a parallel line, deriving a contradiction.',
                                        'q': 'Evaluate whether the converse of the Basic Proportionality Theorem holds '
                                             'true for all triangles, justifying your conclusion.'}],
                    'Remember': [   {   'a': 'If a line is drawn parallel to one side of a triangle to intersect the '
                                             'other two sides in distinct points, the other two sides are divided in '
                                             'the same ratio.',
                                        'q': 'State the Basic Proportionality Theorem (Thales Theorem) for triangles.'},
                                    {   'a': 'In a right triangle, the square of the hypotenuse is equal to the sum of '
                                             'the squares of the other two sides.',
                                        'q': 'State Pythagoras Theorem for a right-angled triangle and define its '
                                             'converse.'},
                                    {   'a': 'The angle between a tangent and a chord through the point of contact is '
                                             'equal to the angle subtended by the chord in the alternate segment.',
                                        'q': 'State the Alternate Segment Theorem for a chord and tangent of a '
                                             'circle.'},
                                    {   'a': 'The internal bisector of an angle of a triangle divides the opposite '
                                             'side internally in the ratio of the sides containing the angle.',
                                        'q': 'Define the Angle Bisector Theorem for a triangle.'},
                                    {   'a': '1. Their corresponding angles are equal. 2. Their corresponding sides '
                                             'are in the same ratio.',
                                        'q': 'State the two conditions for two geometric polygons to be similar.'}],
                    'Understand': [   {   'a': 'Congruent triangles have equal shape and size (ratio 1:1), while '
                                               'similar triangles only have proportional sides and equal angles.',
                                          'q': 'Explain why all congruent triangles are similar, but all similar '
                                               'triangles need not be congruent.'},
                                      {   'a': 'Tangents drawn from an external point to a circle are equal in length '
                                               'and subtend equal angles at the center.',
                                          'q': 'Describe the relationship between the lengths of two tangents drawn '
                                               'from a single external point to a circle.'},
                                      {   'a': 'Any point on the tangent other than the point of contact lies outside '
                                               'the circle; hence the radius is the shortest distance to the tangent '
                                               'line, making it perpendicular.',
                                          'q': 'Explain why the tangent at any point of a circle is perpendicular to '
                                               'the radius through the point of contact.'},
                                      {   'a': 'A secant intersects a circle at two distinct points, whereas a tangent '
                                               'touches the circle at exactly one point of contact.',
                                          'q': 'Explain the difference between a secant and a tangent to a circle with '
                                               'geometric descriptions.'},
                                      {   'a': 'The opposite angles of a cyclic quadrilateral sum to 180 deg because '
                                               'the angle subtended by an arc at the center is double the angle '
                                               'subtended on the circle.',
                                          'q': 'Illustrate with reasoning why the opposite angles of a cyclic '
                                               'quadrilateral are supplementary.'}]},
    'LINEAR_PROGRAMMING': {   'Analyze': [   {   'a': 'Feasible region shrinks, which may decrease or preserve the '
                                                      'maximum value but can never increase it.',
                                                 'q': 'Analyze the effect on the maximum value of Z = 4x + 3y when an '
                                                      'additional constraint x + y <= 3 is added to the feasible '
                                                      'region.'},
                                             {   'a': 'A minimum may exist if open half plane ax + by < m has no '
                                                      'common points with feasible region, but maximum may not.',
                                                 'q': 'Compare the solution behavior of an unbounded feasible region '
                                                      'when looking for a maximum versus a minimum value of the '
                                                      'objective function.'}],
                              'Apply': [   {   'a': 'Vertices: (0,0), (4,0), (0,4). Z values: 0, 12, 16. Max Z = 16 at '
                                                    '(0,4).',
                                               'q': 'Maximize Z = 3x + 4y subject to constraints: x + y <= 4, x >= 0, '
                                                    'y >= 0 using the corner point method.'},
                                           {   'a': 'Vertices: (0,5), (0,6), (4,3). Min Z = 2300 at (4,3).',
                                               'q': 'Minimize the objective function Z = 200x + 500y subject to '
                                                    'constraints: x + 2y >= 10, 3x + 4y <= 24, x >= 0, y >= 0.'},
                                           {   'a': 'Vertices include (0,0), (2,0), (0,3), (20/19, 45/19). Max Z = '
                                                    '235/19.',
                                               'q': 'Determine the maximum value of Z = 5x + 3y subject to '
                                                    'constraints: 3x + 5y <= 15, 5x + 2y <= 10, x >= 0, y >= 0.'}],
                              'Evaluate': [   {   'a': 'Check if open half plane has points in common with feasible '
                                                       'region.',
                                                  'q': 'Evaluate whether an unbounded linear programming problem has '
                                                       'an optimal solution for the objective function Z = 3x + 2y, '
                                                       'justifying your conclusion.'},
                                              {   'a': 'False; if objective function is parallel to a binding '
                                                       'constraint, infinitely many optimal solutions exist along the '
                                                       'edge.',
                                                  'q': 'Assess the validity of the statement that every linear '
                                                       'programming problem has a unique optimal solution, justifying '
                                                       'with alternative optima examples.'}],
                              'Remember': [   {   'a': 'Objective function Z = ax + by is maximized/minimized subject '
                                                       'to linear inequality constraints.',
                                                  'q': 'Define objective function, constraints, and feasible region in '
                                                       'a Linear Programming Problem.'},
                                              {   'a': 'Optimal value of objective function on a bounded feasible '
                                                       'region occurs at a corner point (vertex).',
                                                  'q': 'State the Corner Point Theorem for solving a linear '
                                                       'programming problem.'},
                                              {   'a': 'x >= 0, y >= 0 representing non-negative physical quantities.',
                                                  'q': 'State the non-negativity constraints in a standard linear '
                                                       'programming problem formulation.'}],
                              'Understand': [   {   'a': 'Linear level curves Z = c reach extremum at boundary '
                                                         'vertices of the convex polygonal feasible set.',
                                                    'q': 'Explain why the optimal solution of a bounded linear '
                                                         'programming problem must occur at a corner point of the '
                                                         'feasible region.'},
                                                {   'a': 'Bounded region can be enclosed in a circle; unbounded '
                                                         'extends infinitely in at least one direction.',
                                                    'q': 'Describe the difference between a bounded and an unbounded '
                                                         'feasible region in linear programming.'}]},
    'MENSURATION': {   'Analyze': [   {   'a': "Volume V' = pi(2r)^2(h/2) = 2pir^2h (doubled). Curved surface area "
                                               'remains 2pi(2r)(h/2) = 2pirh (unchanged).',
                                          'q': 'Analyze how the volume and surface area of a cylinder change when its '
                                               'radius is doubled and its height is halved.'},
                                      {   'a': 'The sphere has the minimal surface area among all shapes of equal '
                                               'volume.',
                                          'q': 'Compare the surface area to volume ratio of a sphere and a cube having '
                                               'equal volumes, and examine which has the smaller surface area.'}],
                       'Apply': [   {   'a': 'Area = (60/360) * (22/7) * 36 = 18.86 cm^2.',
                                        'q': 'Calculate the area of a sector of a circle of radius 6 cm if the central '
                                             'angle is 60 deg.'},
                                    {   'a': 'Volume = (1/3)pi(1)^3 + (2/3)pi(1)^3 = pi cm^3.',
                                        'q': 'A solid is in the shape of a cone standing on a hemisphere of radius 1 '
                                             'cm and height of cone equals radius. Find the volume of the solid.'},
                                    {   'a': 'h = (4/3)*pi*(4.2)^3 / [pi*6^2] = 2.74 cm.',
                                        'q': 'A metallic sphere of radius 4.2 cm is melted and recast into a cylinder '
                                             'of radius 6 cm. Find the height of the cylinder.'},
                                    {   'a': 'Volume = pir^2h - 2*(2/3)pir^3 = pi*(3.5)^2*(10 - 4/3*3.5) = 205.33 '
                                             'cm^3.',
                                        'q': 'Find the volume of a solid formed by scooping out a hemisphere from each '
                                             'end of a solid cylinder of height 10 cm and base radius 3.5 cm.'}],
                       'Evaluate': [   {   'a': 'Volume is conserved, but surface area changes depending on dimensions '
                                                'and shape boundaries.',
                                           'q': 'Evaluate whether melting a cone and reshaping it into a cylinder '
                                                'alters its total surface area, and justify your answer with '
                                                'mathematical calculations.'},
                                       {   'a': 'False. Area increases by a factor related to slant height, but volume '
                                                'octuples if height is also scaled, or quadruples if height is fixed.',
                                           'q': 'Assess the validity of the claim that doubling the radius of a cone '
                                                'quadruples both its curved surface area and its volume.'}],
                       'Remember': [   {   'a': 'Cylinder: 2pirh, 2pir(h+r), pir^2h. Cone: pirl, pir(l+r), '
                                                '(1/3)pir^2h. Hemisphere: 2pir^2, 3pir^2, (2/3)pir^3.',
                                           'q': 'State the formulas for the curved surface area, total surface area, '
                                                'and volume of a cylinder, cone, and hemisphere.'},
                                       {   'a': 'Slant height l = sqrt(r^2 + h^2).',
                                           'q': 'Define the slant height of a right circular cone and state its '
                                                'relationship with radius and height.'},
                                       {   'a': 'Area = (theta/360 deg)*pir^2, Arc length = (theta/360 deg)*2pir.',
                                           'q': 'State the formula for the area of a sector and length of an arc of a '
                                                'circle of radius r with central angle theta.'}],
                       'Understand': [   {   'a': 'Total surface area includes the flat circular base of area pir^2 in '
                                                  'addition to curved surface 2pir^2.',
                                             'q': 'Explain why the total surface area of a solid hemisphere is 3pir^2 '
                                                  'while its curved surface area is 2pir^2.'},
                                         {   'a': 'Conservation of matter guarantees that the volume of metal before '
                                                  'and after recasting is identical.',
                                             'q': 'Describe how the volume remains invariant when a metallic sphere is '
                                                  'melted and recast into a cylinder.'}]},
    'NUMBERS_SEQUENCES': {   'Analyze': [   {   'a': '4 + (n-1)*5 = 301 => 5(n-1) = 297 => n = 60.4 (not an integer). '
                                                     '301 is not a term.',
                                                'q': 'Analyze the pattern of terms in the Arithmetic Progression 4, 9, '
                                                     '14, 19... and examine whether 301 can be a term of this '
                                                     'sequence.'},
                                            {   'a': 'Arithmetic growth is linear O(n), whereas geometric progression '
                                                     'growth is exponential O(2^n).',
                                                'q': 'Compare the growth rates of an arithmetic progression with '
                                                     'common difference 5 and a geometric progression with common '
                                                     'ratio 2.'},
                                            {   'a': '5b^2 = a^2 implies 5 divides a and b, contradicting the co-prime '
                                                     'assumption.',
                                                'q': 'Analyze why sqrt(5) cannot be represented as a ratio of two '
                                                     'integers by examining the contradictions in prime factor '
                                                     'powers.'}],
                             'Apply': [   {   'a': '96 = 2^5 * 3, 404 = 2^2 * 101. HCF = 2^2 = 4. LCM = (96 * 404) / 4 '
                                                   '= 9696.',
                                              'q': 'Find the HCF and LCM of 96 and 404 using the prime factorization '
                                                   'method.'},
                                          {   'a': '12576 = 4052*3 + 420; 4052 = 420*9 + 272; 420 = 272*1 + 148; 272 = '
                                                   '148*1 + 124; 148 = 124*1 + 24; 124 = 24*5 + 4; 24 = 4*6 + 0. HCF = '
                                                   '4.',
                                              'q': "Use Euclid's division algorithm to find the HCF of 4052 and "
                                                   '12576.'},
                                          {   'a': 'Assume sqrt(5) = a/b co-prime. 5b^2 = a^2 => 5 divides a. Let a = '
                                                   '5c => 5b^2 = 25c^2 => b^2 = 5c^2 => 5 divides b. Contradicts '
                                                   'co-prime assumption. Thus sqrt(5) is irrational.',
                                              'q': 'Prove that sqrt(5) is an irrational number using the method of '
                                                   'contradiction.'},
                                          {   'a': 'First term a = 3, common difference d = 5. a_20 = a + 19d = 3 + '
                                                   '19(5) = 3 + 95 = 98.',
                                              'q': 'Find the 20th term of the Arithmetic Progression: 3, 8, 13, 18...'},
                                          {   'a': 'First term a = 2, common difference d = 5, n = 20. S_20 = (n/2)[2a '
                                                   '+ (n-1)d] = 10[4 + 19(5)] = 10[4 + 95] = 990.',
                                              'q': 'Find the sum of the first 20 terms of the Arithmetic Progression: '
                                                   '2, 7, 12, 17...'},
                                          {   'a': 'a = 21, d = -3. a_n = a + (n-1)d = -81 => 21 + (n-1)(-3) = -81 => '
                                                   '-3(n-1) = -102 => n - 1 = 34 => n = 35th term.',
                                              'q': 'Which term of the Arithmetic Progression 21, 18, 15... is -81?'},
                                          {   'a': 'First term a = 2, common ratio r = 3. a_10 = a * r^(n-1) = 2 * 3^9 '
                                                   '= 2 * 19683 = 39366.',
                                              'q': 'Find the 10th term of the Geometric Progression (G.P.): 2, 6, 18, '
                                                   '54...'},
                                          {   'a': 'First term a = 3, common ratio r = 2. S_6 = a(r^n - 1)/(r - 1) = '
                                                   '3(2^6 - 1)/(2 - 1) = 3(64 - 1) = 3 * 63 = 189.',
                                              'q': 'Find the sum of the first 6 terms of the Geometric Progression: 3, '
                                                   '6, 12, 24...'},
                                          {   'a': '2^4 = 16 == -1 (mod 17) (congruent to -1 modulo 17). 2^81 = '
                                                   '(2^4)^20 * 2^1 == (-1)^20 * 2 == 1 * 2 = 2 (mod 17). Remainder is '
                                                   '2.',
                                              'q': 'Find the remainder when 2^81 is divided by 17 using modular '
                                                   'arithmetic.'},
                                          {   'a': 'Calculating terms: a1=2, a2=7, a3=22, a4=67. Pattern gives general '
                                                   'term a_n = (5 * 3^(n-1) - 1) / 2.',
                                              'q': 'Determine the general term a_n of the sequence defined by a_1 = 2 '
                                                   'and a_n = 3 * a_{n-1} + 1 for n > 1.'},
                                          {   'a': 'a + 2d = 4 and a + 8d = -8 => 6d = -12 => d = -2, a = 8. a_13 = a '
                                                   '+ 12d = 8 + 12(-2) = 8 - 24 = -16.',
                                              'q': 'If the 3rd and 9th terms of an Arithmetic Progression are 4 and -8 '
                                                   'respectively, find its 13th term.'},
                                          {   'a': 'Assume 3 + 2sqrt(5) = r (rational). Then sqrt(5) = (r - 3)/2 which '
                                                   'is rational, contradicting irrationality of sqrt(5). Thus 3 + '
                                                   '2sqrt(5) is irrational.',
                                              'q': 'Prove that 3 + 2sqrt(5) is an irrational number given that sqrt(5) '
                                                   'is irrational.'}],
                             'Evaluate': [   {   'a': 'False. For example, (3 + sqrt(2)) + (3 - sqrt(2)) = 6, which is '
                                                      'rational.',
                                                 'q': 'Evaluate the truth of the statement that the sum of any two '
                                                      'irrational numbers is always irrational, and justify your '
                                                      'conclusion with suitable examples.'},
                                             {   'a': 'a_n = S_n - S_{n-1} = 2n + 1. Common difference is constant '
                                                      '(2), so it is a valid AP.',
                                                 'q': 'Assess whether the formula S_n = n^2 + 2n can represent the sum '
                                                      'of the first n terms of an Arithmetic Progression, justifying '
                                                      'your conclusion.'}],
                             'Remember': [   {   'a': 'For any positive integers a and b, there exist unique integers '
                                                      'q and r such that a = bq + r where 0 <= r < b.',
                                                 'q': "State Euclid's Division Lemma for positive integers a and b."},
                                             {   'a': 'Every composite number can be expressed uniquely as a product '
                                                      'of primes, up to the order of factors.',
                                                 'q': 'State the Fundamental Theorem of Arithmetic regarding prime '
                                                      'factorization of composite numbers.'},
                                             {   'a': 'a_n = a + (n - 1)d, where a is first term and d is common '
                                                      'difference.',
                                                 'q': 'Define the n-th term formula and common difference of an '
                                                      'Arithmetic Progression (A.P.).'},
                                             {   'a': 'A sequence where each term after the first is found by '
                                                      'multiplying previous by common ratio r. a_n = a * r^(n-1).',
                                                 'q': 'Define a Geometric Progression (G.P.) and state the formula for '
                                                      'its general term.'}],
                             'Understand': [   {   'a': 'Powers of 2 and 5 can be converted to powers of 10 in the '
                                                        'denominator, resulting in terminating decimal fractions.',
                                                   'q': 'Explain why the decimal expansion of a rational number p/q '
                                                        'terminates if and only if the prime factorization of q is of '
                                                        'the form 2^n * 5^m.'},
                                               {   'a': 'Apply a = bq + r repeatedly until remainder r = 0; the last '
                                                        'divisor is the HCF.',
                                                   'q': "Describe how Euclid's division algorithm is applied "
                                                        'repeatedly to compute the highest common factor (HCF) of two '
                                                        'numbers.'},
                                               {   'a': 'An arithmetic sequence adds a constant common difference; a '
                                                        'geometric sequence multiplies by a common ratio.',
                                                   'q': 'Explain the difference between an arithmetic sequence and a '
                                                        'geometric sequence with illustrative examples.'}]},
    'RELATIONS_FUNCTIONS': {   'Analyze': [   {   'a': 'Reflexive fails for 1/2 <= 1/4. Symmetric fails for (1,2) in R '
                                                       'but (2,1) not. Not an equivalence relation.',
                                                  'q': 'Analyze whether the relation R on real numbers defined by R = '
                                                       '{(a,b): a <= b^2} is reflexive, symmetric, or transitive.'},
                                              {   'a': 'Injective on N, but not surjective since non-squares have no '
                                                       'pre-image. On R, neither injective nor surjective.',
                                                  'q': 'Analyze whether the function f: N -> N defined by f(x) = x^2 '
                                                       'is injective, surjective, or bijective, contrasting it with f: '
                                                       'R -> R.'}],
                               'Apply': [   {   'a': 'Reflexive: x-x=0 divisible by 5. Symmetric: -(x-y) divisible. '
                                                     'Transitive: sum divisible. Equivalence relation.',
                                                'q': 'Determine whether the relation R = {(x,y): x - y is divisible by '
                                                     '5} on integers Z is an equivalence relation.'},
                                            {   'a': '3x1+2=3x2+2 => x1=x2 (one-one). y = 3x+2 => x=(y-2)/3 in R '
                                                     '(onto).',
                                                'q': 'Show that the function f: R -> R defined by f(x) = 3x + 2 is '
                                                     'one-one and onto (bijective).'},
                                            {   'a': '(g o f)(x) = 4x^2 + 4x - 1, (f o g)(x) = 2x^2 - 3.',
                                                'q': 'Find the composite functions (g o f)(x) and (f o g)(x) for f(x) '
                                                     '= 2x + 1 and g(x) = x^2 - 2.'},
                                            {   'a': 'pi/3 - (pi - pi/3) = pi/3 - 2pi/3 = -pi/3.',
                                                'q': 'Find the principal value of the inverse trigonometric '
                                                     'expression: tan^-1(sqrt3) - sec^-1(-2).'},
                                            {   'a': 'y = (x-2)/(x-3) => x = (3y - 2)/(y - 1). f^-1(x) = (3x - 2)/(x - '
                                                     '1).',
                                                'q': 'Find the inverse function f^-1(x) of f(x) = (x - 2)/(x - 3) on R '
                                                     '- {3}.'}],
                               'Evaluate': [   {   'a': 'Not invertible because f(1) = f(-1) = 1 (fails injectivity) '
                                                        'and negative numbers have no pre-images (fails surjectivity).',
                                                   'q': 'Evaluate whether the function f: R -> R given by f(x) = |x| '
                                                        'is invertible, justifying your conclusion.'},
                                               {   'a': 'Valid only when xy < 1; if xy > 1, an additional pi or -pi '
                                                        'term must be included.',
                                                   'q': 'Assess whether the inverse trigonometric identity tan^-1 x + '
                                                        'tan^-1 y = tan^-1[(x+y)/(1-xy)] is universally valid for all '
                                                        'real numbers.'}],
                               'Remember': [   {   'a': 'Reflexive: (a,a)  in  R for all a. Symmetric: (a,b)  in  R => '
                                                        '(b,a)  in  R. Transitive: (a,b),(b,c)  in  R => (a,c)  in  R.',
                                                   'q': 'Define reflexive, symmetric, and transitive relations on a '
                                                        'set A.'},
                                               {   'a': 'A relation that is reflexive, symmetric, and transitive. [a] '
                                                        '= {x  in  A : (x,a)  in  R}.',
                                                   'q': 'Define an equivalence relation and an equivalence class for a '
                                                        'relation R.'},
                                               {   'a': 'Injective: f(x1)=f(x2) => x1=x2. Surjective: Range = '
                                                        'Codomain. Bijective: Both injective and surjective.',
                                                   'q': 'Define one-one (injective), onto (surjective), and bijective '
                                                        'functions.'},
                                               {   'a': 'sin^-1 x: [-pi/2, pi/2]. tan^-1 x: (-pi/2, pi/2).',
                                                   'q': 'State the principal value branch for the inverse '
                                                        'trigonometric functions sin^-1 x and tan^-1 x.'}],
                               'Understand': [   {   'a': 'Injectivity ensures inverse is single-valued (function '
                                                          'property); surjectivity ensures domain of inverse is whole '
                                                          'codomain.',
                                                     'q': 'Explain why a function f must be bijective in order to '
                                                          'possess an inverse function f^-1.'},
                                                 {   'a': 'Empty relation contains no ordered pairs; universal '
                                                          'relation contains all possible pairs A  x  A.',
                                                     'q': 'Describe the difference between an empty relation and a '
                                                          'universal relation on a set.'},
                                                 {   'a': 'Injective composition preserves distinct outputs; '
                                                          'surjective composition covers final codomain.',
                                                     'q': 'Explain why the composition of two bijective functions is '
                                                          'also a bijective function.'}]},
    'STATISTICS_PROBABILITY': {   'Analyze': [   {   'a': 'The mean is heavily influenced by outliers, whereas the '
                                                          'median remains robust and resistant.',
                                                     'q': 'Analyze the impact on the mean and median of a dataset when '
                                                          'an extreme outlier is introduced.'},
                                                 {   'a': 'By the Law of Large Numbers, relative frequency converges '
                                                          'toward theoretical probability 0.5.',
                                                     'q': 'Compare the theoretical probability and experimental '
                                                          'frequency when a coin is tossed 10 times versus 10,000 '
                                                          'times.'}],
                                  'Apply': [   {   'a': 'Primes = {2, 3, 5} (3 outcomes). Total = 6. P = 3/6 = 1/2.',
                                                   'q': 'A die is thrown once. Calculate the probability of getting a '
                                                        'prime number.'},
                                               {   'a': 'Midpoints: 5, 15, 25, 35. sum(fx) = 25 + 120 + 375 + 420 = '
                                                        '940. sumf = 40. Mean = 940/40 = 23.5.',
                                                   'q': 'Find the mean of the frequency distribution: Class 0-10, '
                                                        '10-20, 20-30, 30-40 with frequencies 5, 8, 15, 12 '
                                                        'respectively.'},
                                               {   'a': 'Favorable pairs: (2,6), (3,5), (4,4), (5,3), (6,2) (5 '
                                                        'outcomes). P = 5/36.',
                                                   'q': 'Two dice are thrown simultaneously. Calculate the probability '
                                                        'of getting a sum of 8.'},
                                               {   'a': 'Red face cards = 6. Total = 52. P = 6/52 = 3/26.',
                                                   'q': 'One card is drawn at random from a deck of 52 cards. '
                                                        'Calculate the probability of getting a red face card.'}],
                                  'Evaluate': [   {   'a': 'Elementary events partition the sample space completely '
                                                           'with no overlap, so the sum equals P(S) = 1.',
                                                      'q': 'Evaluate whether the sum of probabilities of all '
                                                           'elementary events of an experiment is always equal to 1, '
                                                           'justifying your conclusion.'},
                                                  {   'a': 'If mean = median = mode, symmetrical; if mean > median > '
                                                           'mode, positively skewed.',
                                                      'q': 'Assess whether a given frequency distribution is '
                                                           'symmetrical or skewed by evaluating the relative positions '
                                                           'of mean, median, and mode.'}],
                                  'Remember': [   {   'a': 'Mode = 3 * Median - 2 * Mean.',
                                                      'q': 'Define the empirical relationship between mean, median, '
                                                           'and mode for a moderately skewed frequency distribution.'},
                                                  {   'a': 'P(E) = Number of outcomes favorable to E / Total number of '
                                                           'possible outcomes.',
                                                      'q': 'State the classical definition of probability of an event '
                                                           'E.'},
                                                  {   'a': 'Mean = sum(f_i * x_i) / sumf_i, where x_i is class mark '
                                                           'and f_i is frequency.',
                                                      'q': 'State the formula for calculating the mean of grouped data '
                                                           'using the direct method.'}],
                                  'Understand': [   {   'a': 'Favorable outcomes cannot be negative and cannot exceed '
                                                             'the total number of outcomes.',
                                                        'q': 'Explain why the probability of any event E always '
                                                             'satisfies 0 <= P(E) <= 1.'},
                                                    {   'a': 'Mutually exclusive cannot occur together (P(A  '
                                                             'intersection  B) = 0); independent satisfy P(A  '
                                                             'intersection  B) = P(A)*P(B).',
                                                        'q': 'Describe the difference between mutually exclusive '
                                                             'events and independent events with suitable probability '
                                                             'examples.'}]},
    'TRIGONOMETRY': {   'Analyze': [   {   'a': 'Shadow s = h * cot theta. Since cot(30 deg) = sqrt(3) > cot(60 deg) = '
                                                '1/sqrt(3), the shadow triples in length.',
                                           'q': 'Analyze how the length of the shadow of a vertical tower changes as '
                                                'the angle of elevation of the sun decreases from 60 deg to 30 deg.'},
                                       {   'a': 'Both ratios have cos theta in denominator, which approaches 0 as '
                                                'theta approaches 90 deg.',
                                           'q': 'Compare the behavior and values of tan theta and sec theta as theta '
                                                'approaches 90 deg, and examine why both functions become undefined.'}],
                        'Apply': [   {   'a': '2(1)^2 + (sqrt(3)/2)^2 - (sqrt(3)/2)^2 = 2 + 3/4 - 3/4 = 2.',
                                         'q': 'Evaluate the trigonometric expression: 2 tan^2(45 deg) + cos^2(30 deg) '
                                              '- sin^2(60 deg).'},
                                     {   'a': 'tan(60 deg) = h/15 => sqrt(3) = h/15 => h = 15*sqrt(3) m.',
                                         'q': 'From a point on the ground 15 m away from the foot of a tower, the '
                                              'angle of elevation of its top is 60 deg. Calculate the height of the '
                                              'tower.'},
                                     {   'a': 'sin theta(1 - 2 sin^2 theta) / [cos theta(2 cos^2 theta - 1)] = tan '
                                              'theta * (cos 2theta / cos 2theta) = tan theta.',
                                         'q': 'Prove the trigonometric identity: (sin theta - 2 sin^3 theta) / (2 '
                                              'cos^3 theta - cos theta) = tan theta.'},
                                     {   'a': 'Distance d = 7/tan(45 deg) = 7 m. Tower height = 7 + 7*tan(60 deg) = '
                                              '7(1 + sqrt(3)) m.',
                                         'q': 'From the top of a 7 m high building, the angle of elevation of a cable '
                                              'tower is 60 deg and depression of foot is 45 deg. Find the height of '
                                              'the tower.'}],
                        'Evaluate': [   {   'a': 'sec^2 theta / cosec^2 theta = (1/cos^2 theta) / (1/sin^2 theta) = '
                                                 'sin^2 theta / cos^2 theta = tan^2 theta.',
                                            'q': 'Evaluate whether the identity (1 + tan^2 theta)/(1 + cot^2 theta) = '
                                                 'tan^2 theta holds for all angles theta in (0 deg, 90 deg), '
                                                 'justifying each algebraic step.'},
                                        {   'a': 'Yes, using h = d / (cot alpha - cot beta) where d is the distance '
                                                 'between observation points.',
                                            'q': 'Assess whether the height of an inaccessible tower can be determined '
                                                 'using trigonometric ratios and angles of elevation from two '
                                                 'collinear points, justifying your mathematical reasoning.'}],
                        'Remember': [   {   'a': 'sin^2 theta + cos^2 theta = 1, 1 + tan^2 theta = sec^2 theta, 1 + '
                                                 'cot^2 theta = cosec^2 theta.',
                                            'q': 'State the fundamental Pythagorean trigonometric identities relating '
                                                 'sin theta, cos theta, sec theta, and tan theta.'},
                                        {   'a': 'Angle of elevation is angle above horizontal line of sight; angle of '
                                                 'depression is angle below horizontal.',
                                            'q': 'Define the angle of elevation and angle of depression in heights and '
                                                 'distances.'},
                                        {   'a': 'sin: 0, 1/2, 1/sqrt(2), sqrt(3)/2, 1. cos: 1, sqrt(3)/2, 1/sqrt(2), '
                                                 '1/2, 0. tan: 0, 1/sqrt(3), 1, sqrt(3), undefined.',
                                            'q': 'State the exact trigonometric values of sin, cos, and tan for '
                                                 'standard angles 0 deg, 30 deg, 45 deg, 60 deg, and 90 deg.'}],
                        'Understand': [   {   'a': 'As angle increases in a right triangle, the opposite side grows '
                                                   'toward hypotenuse length while adjacent side shrinks toward 0.',
                                              'q': 'Explain why the value of sin theta increases from 0 to 1 as theta '
                                                   'increases from 0 deg to 90 deg, while cos theta decreases.'},
                                          {   'a': 'In a right triangle with acute angles A and B, A + B = 90 deg. sin '
                                                   'A = opposite/hypotenuse = adjacent_B/hypotenuse = cos B = cos(90 '
                                                   'deg - A).',
                                              'q': 'Describe how trigonometric ratios of complementary angles are '
                                                   'related with geometric justification.'}]},
    'VECTORS_3D': {   'Analyze': [   {   'a': 'Check side vectors AB, BC, CA and show dot product of two sides is 0.',
                                         'q': 'Analyze whether the vectors a = 2i - j + k, b = i - 3j - 5k, and c = 3i '
                                              '- 4j - 4k form the vertices of a right-angled triangle in 3D.'},
                                     {   'a': 'Parallel distance uses |(a2 - a1)  x  b| / |b|, whereas skew distance '
                                              'uses |(b1  x  b2) * (a2 - a1)| / |b1  x  b2|.',
                                         'q': 'Compare the distance between two parallel lines versus two skew lines '
                                              'in three-dimensional space using vector formulas.'}],
                      'Apply': [   {   'a': '|a| = sqrt(4 + 9 + 1) = sqrt(14). Unit vector a_hat = (2i + 3j + k) / '
                                            'sqrt(14).',
                                       'q': 'Find the unit vector in the direction of the vector a = 2i + 3j + k.'},
                                   {   'a': 'a * b = 3 + 4 + 3 = 10. |a| = sqrt(14), |b| = sqrt(14). cos theta = 10/14 '
                                            '= 5/7 => theta = cos^-1(5/7).',
                                       'q': 'Calculate the angle between vectors a = i - 2j + 3k and b = 3i - 2j + k '
                                            'using dot product.'},
                                   {   'a': 'a  x  b = -17i + 13j + 7k.',
                                       'q': 'Calculate the vector product a  x  b for a = 2i + j + 3k and b = 3i + 5j '
                                            '- 2k.'},
                                   {   'a': 'Projection = (a * b) / |b| = 10 / sqrt(6) = (5*sqrt(6))/3.',
                                       'q': 'Find the projection of the vector a = 2i + 3j + 2k on the vector b = i + '
                                            '2j + k.'}],
                      'Evaluate': [   {   'a': 'Lines are coplanar if and only if (a2 - a1) * (b1  x  b2) = 0.',
                                          'q': 'Evaluate whether two lines r = a1 + lambdab1 and r = a2 + mub2 are '
                                               'coplanar, justifying your conclusion using the scalar triple product.'},
                                      {   'a': 'If distance is 0 and lines are not parallel, they must intersect at a '
                                               'unique point.',
                                          'q': 'Assess whether the shortest distance between two skew lines in space '
                                               'can be zero without the lines being parallel.'}],
                      'Remember': [   {   'a': 'a * b = |a||b| cos theta, a  x  b = |a||b| sin theta n_hat.',
                                          'q': 'State the formula for the scalar dot product and vector cross product '
                                               'of two vectors a and b.'},
                                      {   'a': 'Direction cosines l = cos alpha, m = cos beta, n = cos gamma where l^2 '
                                               '+ m^2 + n^2 = 1.',
                                          'q': 'Define the direction cosines and direction ratios of a vector in '
                                               'three-dimensional space.'},
                                      {   'a': 'r = a + lambdab, where lambda is a real scalar parameter.',
                                          'q': 'State the vector equation of a line passing through a point with '
                                               'position vector a and parallel to vector b.'}],
                      'Understand': [   {   'a': 'Magnitude |a  x  b| = |a||b| sin theta = base * height = Area of '
                                                 'parallelogram.',
                                            'q': 'Explain the geometric significance of the cross product of two '
                                                 'vectors representing the area of a parallelogram.'},
                                        {   'a': 'Perpendicular if a * b = 0. Collinear if a  x  b = 0.',
                                            'q': 'Describe the condition for two non-zero vectors to be perpendicular '
                                                 'or collinear using dot product and cross product.'}]}}

def get_math_curriculum_question(
    category: str,
    bloom_level: Optional[str] = None,
    exclude_texts: Optional[Iterable[str]] = None,
) -> Optional[Dict[str, str]]:
    """Retrieve a verified mathematics curriculum question aligned with category and Bloom level."""
    category_pools = MATH_CURRICULUM_TEMPLATES.get(category)
    if not category_pools:
        return None

    norm_excludes = {normalize_text_for_comparison(str(t)) for t in (exclude_texts or [])}

    # Select candidates for the requested bloom level
    b_key = None
    if bloom_level:
        for k in category_pools:
            if k.lower() == bloom_level.lower():
                b_key = k
                break

    candidates: List[Dict[str, str]] = []
    if b_key and b_key in category_pools:
        candidates = category_pools[b_key]
    else:
        for pool in category_pools.values():
            candidates.extend(pool)

    unexcluded = [c for c in candidates if normalize_text_for_comparison(c.get("q", "")) not in norm_excludes]
    if unexcluded:
        return random.choice(unexcluded)

    # If all in requested bloom are excluded, check other bloom levels in the same category
    all_cat: List[Dict[str, str]] = []
    for pool in category_pools.values():
        all_cat.extend(pool)
    unex_all = [c for c in all_cat if normalize_text_for_comparison(c.get("q", "")) not in norm_excludes]
    if unex_all:
        return random.choice(unex_all)

    # All questions in this category have been used; return None so caller handles exhaustion cleanly
    return None
